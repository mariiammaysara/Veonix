"""
Module: meal_service
Layer:  Services

Orchestration layer for the meal analysis pipeline.
Coordinates between vision providers, image processing, and persistent storage.
This layer contains the core business logic and state transitions.

Author: Mariam Maysara
"""

import logging
from sqlalchemy.orm import Session
from src.providers.vision.factory import get_vision_provider
from src.helpers.image_processor import compress_image
from src.db.repository import MealRepository
from src.exceptions import LowConfidenceError

logger = logging.getLogger(__name__)

# Minimum AI confidence required to persist a meal without raising a LowConfidenceError
CONFIDENCE_THRESHOLD = 0.5


class MealService:
    """
    Orchestrates the full lifecycle of a meal analysis request.

    Responsibilities:
        - Image normalization and compression.
        - AI-driven food identification and nutrition estimation.
        - Data persistence via the Repository pattern.

    Dependencies:
        - VisionProvider (via Factory)
        - MealRepository
    """

    async def analyze(self, image_bytes: bytes, db: Session) -> dict:
        """
        Executes the non-linear analysis pipeline: Compress -> Analyze -> Save -> Return.

        Args:
            image_bytes: Raw binary image data from the multipart request.
            db: SQLAlchemy database session.

        Returns:
            A dictionary containing the parsed and persisted analysis results.

        Raises:
            LowConfidenceError: If the AI confidence score is below the system threshold.
            VisionProviderError: If the upstream AI service fails.
        """
        # Step 1: Preprocess image to optimize API payload size
        compressed = compress_image(image_bytes)

        # Step 2: Invoke Gemini for consolidated food + nutrition analysis
        # Resolved lazily (not in __init__) so constructing MealService never
        # requires a configured Gemini client for endpoints that don't need it.
        vision = get_vision_provider()
        result = await vision.analyze(compressed)
        logger.info(f"Gemini: {result.food_name} ({result.confidence:.0%}) — {result.calories} kcal")

        # Step 3: Enforce confidence threshold before persistence
        if result.confidence < CONFIDENCE_THRESHOLD:
            raise LowConfidenceError(result.confidence)

        # Step 4: Persist the result to the database
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

        # Step 5: Format the final response for the Controller layer
        return {
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

    def get_history(self, db: Session, limit: int = 50, offset: int = 0) -> dict:
        """
        Retrieves paginated meal history via the repository.

        Args:
            db: Managed database session.
            limit: Page size.
            offset: Starting record offset.
        """
        meals = MealRepository(db).get_all(limit=limit, offset=offset)
        return {"total": len(meals), "meals": meals}

    def delete_meal(self, meal_id: int, db: Session) -> bool:
        """
        Deletes a specific meal record.

        Returns:
            True if deletion was successful, False otherwise.
        """
        return MealRepository(db).delete(meal_id)

    def get_stats(self, db: Session) -> dict:
        """
        Retrieves aggregated nutrition statistics across the entire history.
        """
        return MealRepository(db).get_stats()
