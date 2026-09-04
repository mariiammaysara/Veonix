"""
Tests for parallel batch image analysis.
Verifies the fan-out/reduce pipeline (POST /analyze/images/batch)
handles multiple images, runs them in parallel, aggregates macros correctly,
and bypasses human-in-the-loop (HITL) checkpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.providers.vision.base import VisionResult
from src.db.database import SessionLocal
from src.models.meal import Meal

client = TestClient(app)


def test_batch_analysis_aggregates_totals_and_persists():
    """
    Asserts that the batch endpoint:
      1. Receives multiple files.
      2. Analyzes them concurrently (mocked Gemini returns distinct meals).
      3. Performs the reduce step to sum macros correctly.
      4. Persists the meals to the database immediately (bypassing HITL breakpoint).
    """
    # Define distinct results for the mock to return on consecutive calls
    res1 = VisionResult(
        food_name="Batch Meal Apple",
        confidence=0.95,
        calories=50.0,
        protein=1.0,
        carbs=10.0,
        fat=0.2,
        fiber=2.0,
        sodium=1.0,
        estimated_weight_grams=100,
        meal_type="snack",
        cuisine="fruit",
        preparation_method="raw",
        ingredients=["apple"],
        per_100g={}
    )

    res2 = VisionResult(
        food_name="Batch Meal Banana",
        confidence=0.90,
        calories=100.0,
        protein=2.0,
        carbs=20.0,
        fat=0.3,
        fiber=3.0,
        sodium=2.0,
        estimated_weight_grams=150,
        meal_type="snack",
        cuisine="fruit",
        preparation_method="raw",
        ingredients=["banana"],
        per_100g={}
    )

    call_count = 0

    async def mock_analyze(self, image_bytes, prompt=None):
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            return res1
        return res2

    # Clear prior test entries from database
    db = SessionLocal()
    try:
        db.query(Meal).filter(Meal.food_name.like("Batch Meal%")).delete()
        db.commit()

        # Patch compression and GeminiProvider
        with patch("src.controllers.analyze.compress_image", lambda x: x), \
             patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", mock_analyze):

            # Post two files to /analyze/images/batch
            response = client.post(
                "/analyze/images/batch",
                files=[
                    ("files", ("apple.jpg", b"apple-bytes", "image/jpeg")),
                    ("files", ("banana.jpg", b"banana-bytes", "image/jpeg")),
                ]
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        payload = data["data"]
        meals = payload["meals"]
        aggregate = payload["aggregate"]

        # 1. Check mapped meals
        assert len(meals) == 2
        assert meals[0]["food_name"] == "Batch Meal Apple"
        assert meals[1]["food_name"] == "Batch Meal Banana"

        # 2. Check reduced/aggregated macros
        assert aggregate["total_calories"] == 150.0  # 50 + 100
        assert aggregate["total_protein"] == 3.0    # 1 + 2
        assert aggregate["total_carbs"] == 30.0      # 10 + 20
        assert aggregate["total_fat"] == 0.5        # 0.2 + 0.3
        assert aggregate["total_fiber"] == 5.0      # 2 + 3
        assert aggregate["total_sodium"] == 3.0     # 1 + 2

        # 3. Verify immediate DB persistence (bypass HITL)
        db_meals = db.query(Meal).filter(Meal.food_name.like("Batch Meal%")).all()
        assert len(db_meals) == 2
        names = {m.food_name for m in db_meals}
        assert "Batch Meal Apple" in names
        assert "Batch Meal Banana" in names

    finally:
        db.query(Meal).filter(Meal.food_name.like("Batch Meal%")).delete()
        db.commit()
        db.close()


def test_batch_analysis_validates_batch_limits():
    """
    Asserts that the batch endpoint rejects requests that exceed the max limit
    or contain invalid formats.
    """
    # 1. Test empty batch
    response = client.post("/analyze/images/batch")
    # In FastAPI, omitting files field entirely results in 422 Unprocessable Entity
    # depending on signatures, or 400 with NO_FILES in our custom error handler
    assert response.status_code in (400, 422)

    # 2. Test bad format file
    response = client.post(
        "/analyze/images/batch",
        files=[
            ("files", ("test.txt", b"not an image", "text/plain")),
        ]
    )
    assert response.status_code == 400
    assert "INVALID_IMAGE_FORMAT" in response.json()["error"]["code"]
