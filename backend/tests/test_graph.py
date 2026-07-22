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
        assert isinstance(state["error"], dict)
        assert state["error"]["error_type"] == "connection_error"
        assert state["error"]["provider"] == "gemini"
        assert state["error"]["retryable"] is True
        assert state["error"]["message"] == "API connection failure"
        mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_run_analysis_graph_unknown_error():
    with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.side_effect = Exception("Something completely unexpected happened")
        
        image_bytes = get_dummy_image_bytes()
        state = await run_analysis_graph(image_bytes)
        
        # Asserts
        assert state["vision_result"] is None
        assert isinstance(state["error"], dict)
        assert state["error"]["error_type"] == "unknown"
        assert state["error"]["provider"] == "gemini"
        assert state["error"]["retryable"] is False
        assert state["error"]["message"] == "Something completely unexpected happened"
        mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_run_analysis_graph_retry_cap():
    mock_low_confidence_result = VisionResult(
        food_name="Apple",
        confidence=0.4,  # < 0.6 confidence
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
    
    with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_low_confidence_result
        
        image_bytes = get_dummy_image_bytes()
        state = await run_analysis_graph(image_bytes)
        
        # Asserts
        assert state["retry_count"] == 2
        # Starts with 1 call, retries twice, totaling 3 calls
        assert mock_analyze.call_count == 3


@pytest.mark.asyncio
async def test_run_analysis_graph_timeout_error():
    with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.side_effect = Exception("Request timed out: deadline exceeded")
        
        image_bytes = get_dummy_image_bytes()
        state = await run_analysis_graph(image_bytes)
        
        # Asserts
        assert state["vision_result"] is None
        assert isinstance(state["error"], dict)
        assert state["error"]["error_type"] == "timeout"
        assert state["error"]["provider"] == "gemini"
        assert state["error"]["retryable"] is True


@pytest.mark.asyncio
async def test_history_node_structured_error():
    with patch("src.agents.tools.sql_tool.query_meal_history", new_callable=AsyncMock) as mock_query:
        mock_query.side_effect = Exception("Database connection failure")
        
        with patch("src.agents.supervisor.route_request", new_callable=AsyncMock, return_value="history_node"):
            state = await run_analysis_graph(question="how many calories did I eat?")
            
            assert state["history_answer"] is None
            assert isinstance(state["error"], dict)
            assert state["error"]["error_type"] == "connection_error"
            assert state["error"]["provider"] == "sqlite"
            assert state["error"]["retryable"] is True
            assert "Database connection failure" in state["error"]["message"]


@pytest.mark.asyncio
async def test_knowledge_node_structured_error():
    with patch("src.agents.tools.rag_tool.search_nutrition_knowledge", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = Exception("Tavily API quota limit exceeded")
        
        with patch("src.agents.supervisor.route_request", new_callable=AsyncMock, return_value="knowledge_node"):
            state = await run_analysis_graph(question="benefits of avocado")
            
            assert state["history_answer"] is None
            assert isinstance(state["error"], dict)
            assert state["error"]["error_type"] == "quota_exceeded"
            assert state["error"]["provider"] == "tavily"
            assert state["error"]["retryable"] is True
            assert "quota limit exceeded" in state["error"]["message"]
