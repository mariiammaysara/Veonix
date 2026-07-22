"""
Module: analyze
Layer:  Controllers

HTTP layer for food analysis and history management.
Handles request validation, error translation, and response formatting.
This module contains zero business logic; it merely delegates to MealService.

Author: Mariam Maysara
"""

import logging
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.services.meal_service import MealService
from src.db.database import get_db
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
    Coordinates between the multipart file upload and the background analysis pipeline.

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
        import uuid
        from src.agents.supervisor import main_graph
        thread_id = f"meal-{uuid.uuid4()}"
        
        # Step 1: Run the LangGraph flow with thread_id
        from src.agents.graph import run_analysis_graph
        state = await run_analysis_graph(image_bytes, thread_id=thread_id)

        # Step 2: Handle graph errors
        if state.get("error"):
            err = state["error"]
            # Graph nodes now store structured error dicts (error_type, provider, message);
            # unwrap to a real exception so our existing exception handlers still work.
            if isinstance(err, dict):
                raise VisionProviderError(err.get("message", "Unknown graph error"))
            raise err

        result = state["vision_result"]

        # Step 3: Enforce confidence threshold before returning result
        from src.services.meal_service import CONFIDENCE_THRESHOLD
        if result.confidence < CONFIDENCE_THRESHOLD:
            raise LowConfidenceError(result.confidence)

        # Step 4: Format the response shape
        formatted_result = {
            "food_name":   result.food_name,
            "confidence":  result.confidence,
            "ingredients": result.ingredients,
            "weight_grams": result.estimated_weight_grams,
            "meal_type":   result.meal_type,
            "cuisine":     result.cuisine,
            "allergies_warning": state.get("allergies_warning"),
            "nutrition": {
                "calories": result.calories,
                "protein":  result.protein,
                "carbs":    result.carbs,
                "fat":      result.fat,
                "fiber":    result.fiber,
                "sodium":   result.sodium,
                "per_100g": result.per_100g,
                "source":   "Gemini",
                "is_estimated": False,
            },
        }

        # Step 5: Check if graph was interrupted at persist_node breakpoint
        config = {"configurable": {"thread_id": thread_id}}
        state_info = await main_graph.aget_state(config)
        
        if "persist_node" in state_info.next:
            return {
                "status": "pending_confirmation",
                "data": {
                    "thread_id": thread_id,
                    "analysis": formatted_result
                }
            }

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


# ── SSE Streaming Endpoint ────────────────────────────────────────────────────

import json as _json
from fastapi.responses import StreamingResponse


def _sse(event: str, data: dict) -> str:
    """Format a single SSE line: `data: {...}\n\n`"""
    return f"data: {_json.dumps({'event': event, **data})}\n\n"


async def _stream_image_analysis(image_bytes: bytes) -> None:
    """
    Async generator that drives each vision pipeline step manually,
    yielding SSE events between steps so the frontend can display
    real-time progress without polling.

    PERFORMANCE NOTE: Gemini is called ONCE here (Step 3).
    The pre-computed vision_result is then injected directly into the
    LangGraph state so vision_node is bypassed, eliminating the
    previously redundant second Gemini call.

    Yields:
        SSE-formatted strings with named progress events.
    """
    import uuid
    import time
    from src.helpers.image_processor import compress_image
    from src.providers.vision.factory import get_vision_provider
    from src.helpers.prompts import build_vision_prompt
    from src.agents.store import NutritionCoachingStore
    from src.agents.supervisor import main_graph
    from src.services.meal_service import CONFIDENCE_THRESHOLD

    thread_id = f"meal-stream-{uuid.uuid4()}"
    t_request_start = time.perf_counter()

    try:
        # Step 1: compress
        yield _sse("start", {"message": "Compressing image...", "thread_id": thread_id})
        t0 = time.perf_counter()
        compressed = compress_image(image_bytes)
        logger.info(f"[PERF] compress_image: {(time.perf_counter()-t0)*1000:.1f}ms")

        # Step 2: load profile for goal-aware prompt
        yield _sse("profile", {"message": "Loading profile..."})
        t0 = time.perf_counter()
        store = NutritionCoachingStore()
        profile = store.get_profile()
        dietary_goal = profile.get("dietary_goal")
        prompt = build_vision_prompt(dietary_goal)
        logger.info(f"[PERF] profile_load: {(time.perf_counter()-t0)*1000:.1f}ms")

        # Step 3: call vision model — ONLY Gemini call in this pipeline
        yield _sse("vision_start", {"message": "Calling vision model..."})
        t0 = time.perf_counter()
        provider = get_vision_provider()
        result = await provider.analyze(compressed, prompt=prompt)
        logger.info(
            f"[PERF] gemini_vision_call: {(time.perf_counter()-t0)*1000:.1f}ms "
            f"| food='{result.food_name}' confidence={result.confidence:.0%}"
        )
        yield _sse("vision_done", {
            "message": f"Food identified: {result.food_name}",
            "food_name": result.food_name,
            "confidence": result.confidence,
        })

        # Step 4: confidence check
        if result.confidence < CONFIDENCE_THRESHOLD:
            yield _sse("low_confidence", {
                "message": "Low confidence — please retake photo",
                "confidence": result.confidence,
            })
            return

        # Step 5: allergy check
        yield _sse("allergy_check", {"message": "Checking allergies..."})
        allergies = [a.strip().lower() for a in profile.get("allergies", []) if a.strip()]
        food_lower = result.food_name.lower()
        ingredients = [i.lower() for i in (result.ingredients or [])]
        matched = []
        for allergy in allergies:
            if allergy in food_lower or any(allergy in ing for ing in ingredients):
                matched.append(allergy)
        allergies_warning = (
            f"Warning: may contain allergens: {', '.join(matched)}." if matched else None
        )

        # Step 6: format result
        formatted = {
            "food_name": result.food_name,
            "confidence": result.confidence,
            "ingredients": result.ingredients,
            "weight_grams": result.estimated_weight_grams,
            "meal_type": result.meal_type,
            "cuisine": result.cuisine,
            "allergies_warning": allergies_warning,
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

        # Step 7: hand off pre-computed vision_result to the graph.
        # The supervisor detects vision_result in state and skips vision_node,
        # going directly to persist_node — eliminating the redundant Gemini call.
        yield _sse("saving", {"message": "Awaiting confirmation..."})
        t0 = time.perf_counter()
        from src.agents.graph import run_analysis_graph
        state = await run_analysis_graph(
            vision_result=result,
            allergies_warning=allergies_warning,
            thread_id=thread_id,
        )
        logger.info(f"[PERF] langgraph_invoke: {(time.perf_counter()-t0)*1000:.1f}ms")
        config = {"configurable": {"thread_id": thread_id}}
        state_info = await main_graph.aget_state(config)

        logger.info(
            f"[PERF] total_stream_pipeline: {(time.perf_counter()-t_request_start)*1000:.1f}ms"
        )

        if "persist_node" in state_info.next:
            yield _sse("pending_confirmation", {
                "message": "Pending your confirmation before saving.",
                "thread_id": thread_id,
                "result": formatted,
            })
        else:
            yield _sse("done", {
                "message": "Analysis complete.",
                "thread_id": thread_id,
                "result": formatted,
            })

    except LowConfidenceError as e:
        yield _sse("error", {"message": f"Low confidence: {e.confidence:.0%}", "code": "LOW_CONFIDENCE"})
    except Exception as e:
        logger.exception(f"Stream error: {e}")
        yield _sse("error", {"message": "Analysis failed. Please try again.", "code": "INTERNAL_ERROR"})


@router.post("/image/stream")
async def analyze_image_stream(file: UploadFile = File(...)):
    """
    Streams vision analysis progress as Server-Sent Events (SSE).
    Each event is a JSON line: `data: {"event": "...", "message": "..."}\n\n`

    Events in order:
      start → profile → vision_start → vision_done →
      allergy_check → saving → pending_confirmation | done | error
    """
    if file.content_type not in ALLOWED_TYPES:
        return error_response(ErrorCode.INVALID_IMAGE_FORMAT)

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_BYTES:
        return error_response(ErrorCode.IMAGE_TOO_LARGE)

    return StreamingResponse(
        _stream_image_analysis(image_bytes),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for true streaming
        },
    )


# ── Batch Analysis Endpoint ───────────────────────────────────────────────────

from typing import List


@router.post("/images/batch")
async def analyze_images_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload multiple food images and receive parallel nutrition analysis.
    Fan-out: all images analyzed concurrently via asyncio.gather.
    Reduce: aggregate totals (calories, protein, carbs, fat) computed after.

    Bypasses HITL confirmation — batch saves immediately.

    Args:
        files: Up to 10 image files (JPEG, PNG, WEBP), each ≤10 MB.

    Returns:
        { meals: [...per-meal results], aggregate: { total_calories, ... } }
    """
    MAX_BATCH = 10

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
        from src.agents.batch import analyze_images_parallel
        batch_result = await analyze_images_parallel(images)
        return {"status": "success", "data": batch_result}

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
