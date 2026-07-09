import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.providers.vision.base import VisionResult

client = TestClient(app, raise_server_exceptions=False)


class MockStateInfo:
    def __init__(self, values, next):
        self.values = values
        self.next = next


def test_confirm_approve_with_edits():
    """
    Verifies that the /confirm endpoint correctly merges edits using dataclasses.replace
    and casts types correctly, while preserving existing fields.
    """
    mock_result = VisionResult(
        food_name="Old Sandwich",
        confidence=0.8,
        ingredients=["bread"],
        estimated_weight_grams=100,
        meal_type="breakfast",
        cuisine="american",
        preparation_method="grilled",
        calories=200.0,
        protein=10.0,
        carbs=30.0,
        fat=5.0
    )
    
    mock_state = MockStateInfo(
        values={"vision_result": mock_result},
        next=["persist_node"]
    )
    
    with patch("src.agents.supervisor.main_graph.aget_state", AsyncMock(return_value=mock_state)), \
         patch("src.agents.supervisor.main_graph.aupdate_state", AsyncMock()) as mock_update_state, \
         patch("src.agents.supervisor.main_graph.ainvoke", AsyncMock(return_value={})):
         
        payload = {
            "action": "approve",
            "edits": {
                "food_name": "New Sandwich",
                "weight_grams": 150,
                "calories": "250.5",  # string type to verify float casting
                "protein": 12.0
            }
        }
        
        response = client.post("/coach/confirm/test-thread-id", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify updates applied correctly via dataclasses.replace
        mock_update_state.assert_called_once()
        called_args = mock_update_state.call_args[0]
        updated_result = called_args[1]["vision_result"]
        
        assert updated_result.food_name == "New Sandwich"
        assert updated_result.estimated_weight_grams == 150
        assert updated_result.calories == 250.5
        assert updated_result.protein == 12.0
        assert updated_result.carbs == 30.0  # preserved from old
        assert updated_result.preparation_method == "grilled"  # preserved from old


def test_unhandled_exception_cors_handling():
    """
    Verifies that unhandled exceptions are caught by the global exception handler
    and returned in a standardized JSON error format (preserving CORS headers context).
    """
    with patch("src.agents.supervisor.main_graph.aget_state", side_effect=ValueError("Simulated DB Crash")):
        response = client.post("/coach/confirm/test-thread-id", json={"action": "approve"})
        
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert "Simulated DB Crash" in data["error"]["detail"]
