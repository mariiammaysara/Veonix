"""
Module: analyze
Layer:  Controllers

HTTP layer for food analysis and history management.
Handles request validation, error translation, and response formatting.
This module contains zero business logic; it merely delegates to MealService.

Author: Mariam Maysara
"""

import asyncio
import logging
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.services.meal_service import MealService
from src.db.database import get_db, SessionLocal
from src.db.repository import MealRepository
from src.providers.vision.factory import get_vision_provider
from src.helpers.image_processor import compress_image
from src.exceptions import (
    VisionProviderError,
    LowConfidenceError,
    NoFoodDetectedError,
    NutritionNotFoundError,
    NutritionServiceError,
    ImageProcessingError,
    VeonixException,
)
from src.enums.error_codes import ErrorCode

logger = logging.getLogger(__name__)
# Analysis router grouping all food identification and history endpoints
router = APIRouter(prefix="/analyze", tags=["Analysis"])

# Allowed MIME types for vision analysis.
# Validated at the controller boundary to fail fast.
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB payload limit
MAX_BATCH = 10


def error_response(error_code: ErrorCode, detail: str = "") -> JSONResponse:
    """
    Constructs a standardized JSON error response.
    Returns JSONResponse instead of raising HTTPException to ensure consistent body schema.

    Args:
        error_code: The domain ErrorCode enum.
        detail: Optional low-level detail for debugging or logging.

    Returns:
        Standardized error JSON payload.
    """
    return JSONResponse(
        status_code=error_code.http_status,
        content={
            "status": "error",
            "error": {
                "code": error_code.code,
                "message": error_code.user_message,
                "detail": detail,
            },
        },
    )


@router.post("/image")
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    meal_service: MealService = Depends(MealService),
):
    """
    Upload a food image and receive a full nutrition analysis.
    Coordinates between the multipart file upload and the analysis pipeline.

    Args:
        file: Multipart image file.
        db: SQLite session.
        meal_service: Orchestration service for analysis.

    Returns:
        Full nutrition breakdown and food identification.
    """
    if file.content_type not in ALLOWED_TYPES:
        return error_response(ErrorCode.INVALID_IMAGE_FORMAT)

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_BYTES:
        return error_response(ErrorCode.IMAGE_TOO_LARGE)

    try:
        formatted_result = await meal_service.analyze(image_bytes, db)
        return {"status": "success", "data": formatted_result}

    except LowConfidenceError as e:
        return error_response(e.error_code, f"confidence={e.confidence:.0%}")
    except NoFoodDetectedError as e:
        return error_response(e.error_code)
    except NutritionNotFoundError as e:
        return error_response(e.error_code, e.food_name)
    except (VisionProviderError, NutritionServiceError) as e:
        return error_response(e.error_code, e.detail)
    except ImageProcessingError as e:
        return error_response(e.error_code, e.detail)
    except VeonixException as e:
        logger.error(f"VeonixException: {e.error_code.code} — {e.detail}")
        return error_response(ErrorCode.INTERNAL_ERROR)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR)


# ── Batch Analysis ────────────────────────────────────────────────────────────
#
# Plain asyncio.gather fan-out over the same vision provider used by the single-
# image endpoint. Each image is analyzed independently and concurrently; results
# below the confidence threshold are skipped (not persisted) but still reported
# back so the frontend can show which images failed. Successful meals are then
# persisted in a single batch transaction and totals are aggregated.

CONFIDENCE_THRESHOLD = 0.5


def _format_meal_result(result) -> dict:
    """Formats a VisionResult into the standard API response shape for one meal."""
    return {
        "food_name": result.food_name,
        "confidence": result.confidence,
        "ingredients": result.ingredients,
        "weight_grams": result.estimated_weight_grams,
        "meal_type": result.meal_type,
        "cuisine": result.cuisine,
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


async def _analyze_single_image(image_bytes: bytes, index: int):
    """
    Runs the vision provider on a single image. Returns the raw VisionResult,
    or None if analysis failed (error is logged, not raised, so one bad image
    in a batch doesn't fail the whole request).
    """
    try:
        compressed = compress_image(image_bytes)
        provider = get_vision_provider()
        result = await provider.analyze(compressed)
        logger.info(f"Batch[{index}]: {result.food_name} ({result.confidence:.0%})")
        return result
    except Exception as e:
        logger.error(f"Batch[{index}]: analysis failed: {e}")
        return None


def _aggregate_results(meal_results: list[dict]) -> dict:
    """Reduce step: sums macros across all successfully analyzed meals."""
    totals = {
        "total_calories": 0.0,
        "total_protein": 0.0,
        "total_carbs": 0.0,
        "total_fat": 0.0,
        "total_fiber": 0.0,
        "total_sodium": 0.0,
    }
    for meal in meal_results:
        if meal is None:
            continue
        nutrition = meal.get("nutrition", {})
        totals["total_calories"] += nutrition.get("calories") or 0
        totals["total_protein"] += nutrition.get("protein") or 0
        totals["total_carbs"] += nutrition.get("carbs") or 0
        totals["total_fat"] += nutrition.get("fat") or 0
        totals["total_fiber"] += nutrition.get("fiber") or 0
        totals["total_sodium"] += nutrition.get("sodium") or 0

    return {k: round(v, 1) for k, v in totals.items()}


def _persist_batch_meals(results: list) -> None:
    """Persists all successfully analyzed meals in a single transaction."""
    db = SessionLocal()
    try:
        meals_to_save = []
        for result in results:
            if result is None or result.confidence < CONFIDENCE_THRESHOLD:
                continue
            meals_to_save.append({
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
        if meals_to_save:
            MealRepository(db).save_all(meals_to_save)
            logger.info(f"Batch: persisted {len(meals_to_save)} meals.")
    except Exception as e:
        logger.error(f"Batch: database persistence failed: {e}")
    finally:
        db.close()


@router.post("/images/batch")
async def analyze_images_batch(
    files: List[UploadFile] = File(...),
):
    """
    Upload multiple food images and receive parallel nutrition analysis.
    Fan-out: all images analyzed concurrently via asyncio.gather, calling the
    same vision provider used by the single-image endpoint directly.
    Reduce: aggregate totals (calories, protein, carbs, fat, fiber, sodium).

    Successfully analyzed meals are persisted immediately (no confirmation step).

    Args:
        files: Up to 10 image files (JPEG, PNG, WEBP), each <=10 MB.

    Returns:
        { meals: [...per-meal results | null], aggregate: { total_calories, ... } }
    """
    if len(files) > MAX_BATCH:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {
                    "code": "BATCH_TOO_LARGE",
                    "message": f"Maximum {MAX_BATCH} images per batch.",
                    "detail": f"Received {len(files)}",
                },
            },
        )

    if len(files) == 0:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {
                    "code": "NO_FILES",
                    "message": "At least one image is required.",
                    "detail": "",
                },
            },
        )

    # Validate + read all files upfront before launching parallel jobs
    images: list[bytes] = []
    for i, f in enumerate(files):
        if f.content_type not in ALLOWED_TYPES:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error": {
                        "code": "INVALID_IMAGE_FORMAT",
                        "message": f"File {i + 1} has unsupported type: {f.content_type}",
                        "detail": "",
                    },
                },
            )
        raw = await f.read()
        if len(raw) > MAX_SIZE_BYTES:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error": {
                        "code": "IMAGE_TOO_LARGE",
                        "message": f"File {i + 1} exceeds the 10 MB limit.",
                        "detail": "",
                    },
                },
            )
        images.append(raw)

    try:
        # Fan-out: all images analyzed concurrently
        results = await asyncio.gather(
            *[_analyze_single_image(img, i) for i, img in enumerate(images)]
        )

        # Map: format each result into a standardized meal dict
        meal_results = [
            _format_meal_result(r) if r is not None else None for r in results
        ]

        # Reduce: aggregate nutrition totals
        aggregate = _aggregate_results(meal_results)

        # Persist all successfully analyzed meals in a background thread
        await asyncio.to_thread(_persist_batch_meals, list(results))

        return {
            "status": "success",
            "data": {"meals": meal_results, "aggregate": aggregate},
        }

    except Exception as e:
        logger.exception(f"Batch analysis error: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.get("/history")
def get_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    meal_service: MealService = Depends(MealService),
):
    """
    Returns paginated meal history, sorted by creation date (newest first).

    Args:
        limit: Max records per page.
        offset: Skip records for pagination.
    """
    result = meal_service.get_history(db, limit=limit, offset=offset)
    return {"status": "success", "data": result}


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    meal_service: MealService = Depends(MealService),
):
    """
    Returns aggregated nutrition statistics across all historical meals.
    Used by the dashboard to show average diet trends.
    """
    result = meal_service.get_stats(db)
    return {"status": "success", "data": result}


@router.delete("/{meal_id}")
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    meal_service: MealService = Depends(MealService),
):
    """
    Permanently deletes a specific meal record from history.

    Args:
        meal_id: Unique integrity identifier for the meal.

    Raises:
        404 (mapped internally) if meal does not exist.
    """
    deleted = meal_service.delete_meal(meal_id, db)
    if not deleted:
        return error_response(ErrorCode.INTERNAL_ERROR, f"Meal {meal_id} not found")
    return {"status": "success", "message": f"Meal {meal_id} deleted"}
