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
        # Step 1: Run the LangGraph flow
        from src.agents.graph import run_analysis_graph
        state = await run_analysis_graph(image_bytes)

        # Step 2: Handle graph errors
        if state.get("error"):
            raise state["error"]

        result = state["vision_result"]

        # Step 3: Enforce confidence threshold before persistence
        from src.services.meal_service import CONFIDENCE_THRESHOLD
        if result.confidence < CONFIDENCE_THRESHOLD:
            raise LowConfidenceError(result.confidence)

        # Step 4: Persist the result to the database
        from src.db.repository import MealRepository
        MealRepository(db).save({
            "food_name":          result.food_name,
            "cuisine":            result.cuisine,
            "meal_type":          result.meal_type,
            "preparation_method": result.preparation_method,
            "weight_grams":       result.estimated_weight_grams,
            "confidence":         result.confidence,
            "calories":           result.calories,
            "protein":            result.protein,
            "carbs":              result.carbs,
            "fat":                result.fat,
            "fiber":              result.fiber,
            "sodium":             result.sodium,
            "ingredients":        result.ingredients,
            "per_100g":           result.per_100g,
            "nutrition_source":   "Gemini",
            "is_estimated":       0,
        })

        # Step 5: Format the response in the exact same shape
        formatted_result = {
            "food_name":   result.food_name,
            "confidence":  result.confidence,
            "ingredients": result.ingredients,
            "weight_grams": result.estimated_weight_grams,
            "meal_type":   result.meal_type,
            "cuisine":     result.cuisine,
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
