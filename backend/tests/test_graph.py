"""
Tests for the LangGraph-based analysis flow.
Mocks the Gemini provider to avoid real API calls.
"""

from unittest.mock import AsyncMock, patch
import pytest
from src.agents.graph import run_analysis_graph
from src.providers.vision.base import VisionResult
from PIL import Image
import io


@pytest.fixture(autouse=True)
def mock_settings_key(monkeypatch):
    """
    Ensure settings has a dummy API key to avoid client init crashes.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")


def get_dummy_image_bytes() -> bytes:
    """
    Generates a valid 10x10 JPEG image byte array.
    """
    img = Image.new("RGB", (10, 10), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    return img_byte_arr.getvalue()


@pytest.mark.asyncio
async def test_run_analysis_graph_success():
    mock_result = VisionResult(
        food_name="Apple",
        confidence=0.9,
        ingredients=["apple"],
        estimated_weight_grams=150,
        meal_type="snack",
        cuisine="fruit",
        preparation_method="raw",
        calories=95.0,
        protein=0.5,
        carbs=25.0,
        fat=0.3,
        fiber=4.4,
        sodium=2.0,
        per_100g={"calories": 52.0}
    )
    
    # Mocking the GeminiProvider's analyze method
    with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_result
        
        image_bytes = get_dummy_image_bytes()
        state = await run_analysis_graph(image_bytes)
        
        # Asserts
        assert state["vision_result"] == mock_result
        assert state["error"] is None
        mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_run_analysis_graph_error():
    with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.side_effect = Exception("API connection failure")
        
        image_bytes = get_dummy_image_bytes()
        state = await run_analysis_graph(image_bytes)
        
        # Asserts
        assert state["vision_result"] is None
        assert isinstance(state["error"], Exception)
        assert str(state["error"]) == "API connection failure"
        mock_analyze.assert_called_once()
