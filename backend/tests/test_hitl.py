"""
Tests for Human-in-the-loop (HITL) confirmation via LangGraph breakpoints.
Verifies that the graph halts at the breakpoint and does not write to the database
until user approval/resume is received.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.supervisor import main_graph
from src.providers.vision.base import VisionResult
from src.db.database import SessionLocal
from src.models.meal import Meal


@pytest.mark.asyncio
async def test_hitl_breakpoint_and_confirmation():
    """
    Asserts that the graph interrupts before executing persist_node,
    does not save meals to the database initially, and persists only after
    we resume with confirmation.
    """
    # 1. Setup mock vision result with high confidence to bypass retry loops
    mock_result = VisionResult(
        food_name="Healthy Avocado Toast",
        confidence=0.95,
        calories=350.0,
        protein=12.0,
        carbs=35.0,
        fat=15.0,
        fiber=8.0,
        sodium=200.0,
        estimated_weight_grams=180.0,
        meal_type="breakfast",
        cuisine="american",
        preparation_method="toasted",
        ingredients=["bread", "avocado", "salt"],
        per_100g={}
    )

    thread_id = "test-hitl-thread-id"
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "image_bytes": b"fake-image-payload",
        "vision_result": None,
        "question": None,
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": None
    }

    # Ensure DB is clear of this item before starting
    db = SessionLocal()
    try:
        db.query(Meal).filter(Meal.food_name == "Healthy Avocado Toast").delete()
        db.commit()
        
        # 2. Invoke the graph up to the breakpoint
        with patch("src.agents.graph.compress_image", lambda x: x):
            with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", AsyncMock(return_value=mock_result)):
                state = await main_graph.ainvoke(initial_state, config=config)
        
        # 3. Check that the graph is paused at persist_node and no meal is saved
        state_info = await main_graph.aget_state(config)
        assert "persist_node" in state_info.next
        
        meal_count = db.query(Meal).filter(Meal.food_name == "Healthy Avocado Toast").count()
        assert meal_count == 0, "Meal should not be persisted in DB while pending user approval."

        # 4. Resume the graph (Approve)
        resumed_state = await main_graph.ainvoke(None, config=config)
        
        # 5. Check that the breakpoint is cleared and the meal is now persisted in DB
        state_info_after = await main_graph.aget_state(config)
        assert "persist_node" not in state_info_after.next
        
        meal_count_after = db.query(Meal).filter(Meal.food_name == "Healthy Avocado Toast").count()
        assert meal_count_after == 1, "Meal must be persisted in DB after approval/resume."
        
    finally:
        # Cleanup
        db.query(Meal).filter(Meal.food_name == "Healthy Avocado Toast").delete()
        db.commit()
        db.close()


@pytest.mark.asyncio
async def test_hitl_rejection_discards_state():
    """
    Asserts that if the user rejects/discards a pending recommendation,
    the meal is never persisted in the database.
    """
    mock_result = VisionResult(
        food_name="Discarded Burger",
        confidence=0.95,
        calories=600.0,
        protein=30.0,
        carbs=50.0,
        fat=25.0,
        fiber=3.0,
        sodium=800.0,
        estimated_weight_grams=250.0,
        meal_type="lunch",
        cuisine="american",
        preparation_method="grilled",
        ingredients=["bun", "beef paty", "cheese"],
        per_100g={}
    )

    thread_id = "test-hitl-reject-thread-id"
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "image_bytes": b"fake-image-payload",
        "vision_result": None,
        "question": None,
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": None
    }

    db = SessionLocal()
    try:
        db.query(Meal).filter(Meal.food_name == "Discarded Burger").delete()
        db.commit()
        
        # 1. Run up to breakpoint
        with patch("src.agents.graph.compress_image", lambda x: x):
            with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", AsyncMock(return_value=mock_result)):
                await main_graph.ainvoke(initial_state, config=config)
        
        # 2. Rejection: We do not call resume/ainvoke(None), nothing is persisted
        meal_count = db.query(Meal).filter(Meal.food_name == "Discarded Burger").count()
        assert meal_count == 0, "Rejected meals must not be written to the database."
        
    finally:
        db.query(Meal).filter(Meal.food_name == "Discarded Burger").delete()
        db.commit()
        db.close()
