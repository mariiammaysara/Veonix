"""
Module: batch
Layer:  Agents

Parallel batch image analysis using asyncio.gather for true fan-out.
Invokes the compiled vision_graph subgraph independently per image,
then aggregates totals in a reduce step.

Bypasses the supervisor routing and HITL breakpoint by calling
vision_graph directly — batch analysis saves immediately.

Author: Antigravity AI
"""

import asyncio
import logging
import uuid
from typing import Any

from src.providers.vision.base import VisionResult

logger = logging.getLogger(__name__)


def _format_meal_result(state: dict) -> dict | None:
    """
    Extracts and formats a single meal result from a vision subgraph state dict.
    Returns None if the state has an error or no vision_result.
    """
    result: VisionResult | None = state.get("vision_result")
    if not result:
        return None

    return {
        "food_name": result.food_name,
        "confidence": result.confidence,
        "ingredients": result.ingredients,
        "weight_grams": result.estimated_weight_grams,
        "meal_type": result.meal_type,
        "cuisine": result.cuisine,
        "allergies_warning": state.get("allergies_warning"),
        "nutrition": {
            "calories": result.calories,
            "protein": result.protein,
            "carbs": result.carbs,
            "fat": result.fat,
            "fiber": result.fiber,
            "sodium": result.sodium,
            "per_100g": result.per_100g,
            "source": "Gemini",
            "is_estimated": False,
        },
    }


def _aggregate_results(meal_results: list[dict]) -> dict:
    """
    Reduce step: sums macros across all successfully analyzed meals.

    Args:
        meal_results: List of formatted meal dicts (None entries are skipped).

    Returns:
        Aggregate totals dict.
    """
    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    total_fiber = 0.0
    total_sodium = 0.0

    for meal in meal_results:
        if meal is None:
            continue
        nutrition = meal.get("nutrition", {})
        total_calories += nutrition.get("calories", 0) or 0
        total_protein += nutrition.get("protein", 0) or 0
        total_carbs += nutrition.get("carbs", 0) or 0
        total_fat += nutrition.get("fat", 0) or 0
        total_fiber += nutrition.get("fiber", 0) or 0
        total_sodium += nutrition.get("sodium", 0) or 0

    return {
        "total_calories": round(total_calories, 1),
        "total_protein": round(total_protein, 1),
        "total_carbs": round(total_carbs, 1),
        "total_fat": round(total_fat, 1),
        "total_fiber": round(total_fiber, 1),
        "total_sodium": round(total_sodium, 1),
    }


async def _analyze_single_image(image_bytes: bytes, index: int) -> dict:
    """
    Runs vision_graph for a single image.
    Uses a unique thread_id per image to isolate checkpointer state.

    Args:
        image_bytes: Raw compressed image bytes.
        index: Position in the batch, used for logging.

    Returns:
        Raw vision subgraph state dict.
    """
    from src.agents.graph import vision_graph, AnalysisState
    from src.helpers.image_processor import compress_image

    thread_id = f"batch-{uuid.uuid4()}"

    initial_state: AnalysisState = {
        "image_bytes": compress_image(image_bytes),
        "vision_result": None,
        "question": None,
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": None,
    }

    logger.info(f"Batch: starting vision_graph for image[{index}] thread={thread_id}")

    try:
        # vision_graph is a compiled subgraph — invoke directly (no checkpointer needed)
        result_state = await vision_graph.ainvoke(initial_state)
        logger.info(f"Batch: completed image[{index}]")
        return result_state
    except Exception as e:
        logger.error(f"Batch: error on image[{index}]: {e}")
        return {"vision_result": None, "error": str(e), "allergies_warning": None}


async def analyze_images_parallel(
    images: list[bytes],
) -> dict[str, Any]:
    """
    Fan-out: analyze N images in parallel via asyncio.gather.
    Reduce: aggregate nutrition totals across all results.

    Args:
        images: List of raw image byte arrays.

    Returns:
        {
            "meals": [formatted_meal_dict | None, ...],
            "aggregate": {total_calories, total_protein, ...}
        }
    """
    logger.info(f"Batch analysis: fanning out {len(images)} images in parallel")

    # Fan-out: all images analyzed concurrently
    raw_states = await asyncio.gather(
        *[_analyze_single_image(img, i) for i, img in enumerate(images)],
        return_exceptions=False,
    )

    # Map: format each raw state into a standardized meal dict
    meal_results = [_format_meal_result(state) for state in raw_states]

    # Reduce: aggregate nutrition totals
    aggregate = _aggregate_results(meal_results)

    logger.info(
        f"Batch complete: {sum(1 for m in meal_results if m)} / {len(images)} "
        f"meals analyzed. Total calories: {aggregate['total_calories']} kcal"
    )

    # Persist all successfully analyzed meals to the database
    _persist_batch_meals(meal_results, raw_states)

    return {
        "meals": meal_results,
        "aggregate": aggregate,
    }


def _persist_batch_meals(
    meal_results: list[dict | None],
    raw_states: list[dict],
) -> None:
    """
    Saves all batch meals to the database.
    Batch bypasses HITL — meals are saved immediately without user confirmation.
    """
    from src.db.repository import MealRepository
    from src.db.database import SessionLocal

    db = SessionLocal()
    try:
        repo = MealRepository(db)
        saved_count = 0
        for meal, state in zip(meal_results, raw_states):
            if meal is None:
                continue
            result = state.get("vision_result")
            if result is None:
                continue
            try:
                repo.save({
                    "food_name": result.food_name,
                    "cuisine": result.cuisine,
                    "meal_type": result.meal_type,
                    "preparation_method": result.preparation_method,
                    "weight_grams": result.estimated_weight_grams,
                    "confidence": result.confidence,
                    "calories": result.calories,
                    "protein": result.protein,
                    "carbs": result.carbs,
                    "fat": result.fat,
                    "fiber": result.fiber,
                    "sodium": result.sodium,
                    "ingredients": result.ingredients,
                    "per_100g": result.per_100g,
                    "nutrition_source": "Gemini",
                    "is_estimated": 0,
                })
                saved_count += 1
            except Exception as e:
                logger.error(f"Batch: failed to persist meal '{result.food_name}': {e}")

        db.commit()
        logger.info(f"Batch: persisted {saved_count} meals to database.")
    except Exception as e:
        logger.error(f"Batch: database commit failed: {e}")
        db.rollback()
    finally:
        db.close()
