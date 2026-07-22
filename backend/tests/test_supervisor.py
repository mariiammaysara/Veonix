"""
Tests for the Supervisor Routing and specialized retry loop.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.agents.supervisor import route_request, main_graph
from src.providers.vision.base import VisionResult


@pytest.fixture(autouse=True)
def mock_settings_key(monkeypatch):
    """
    Dummy API Keys to pass checks.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setenv("TAVILY_API_KEY", "dummy-tavily-key")


@pytest.mark.asyncio
async def test_supervisor_routing_table():
    """
    Table-driven tests verifying that the supervisor routes inputs appropriately.
    """
    cases = [
        # Case 1: Image present -> always routes to vision_node
        {"image": b"fake-img", "query": "what is this?", "expected": "vision_node", "mock_intent": None},
        # Case 2: Keyword override -> knowledge_node
        {"image": None, "query": "search latest hydration guidelines", "expected": "knowledge_node", "mock_intent": None},
        # Case 3: Personal logs query -> history_node
        {"image": None, "query": "what did I eat today?", "expected": "history_node", "mock_intent": "history_node"},
        # Case 4: General knowledge query -> knowledge_node
        {"image": None, "query": "benefits of vitamins", "expected": "knowledge_node", "mock_intent": "knowledge_node"},
    ]
    
    for case in cases:
        if case["mock_intent"]:
            # Mock the Gemini classification call
            with patch("src.providers.vision.factory.get_gemini_client") as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client
                mock_resp = MagicMock()
                mock_resp.text = case["mock_intent"]
                mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
                
                route = await route_request(case["image"], case["query"])
                assert route == case["expected"], f"Failed for query '{case['query']}'. Expected {case['expected']}, got {route}"
        else:
            route = await route_request(case["image"], case["query"])
            assert route == case["expected"], f"Failed for query '{case['query']}'. Expected {case['expected']}, got {route}"


@pytest.mark.asyncio
async def test_supervisor_retry_loop_limit():
    """
    Ensure the confidence-based retry loop runs and terminates after exactly 2 retries.
    """
    # Build initial state
    initial_state = {
        "image_bytes": b"low-confidence-image",
        "vision_result": None,
        "question": None,
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None
    }
    
    # Mock vision provider analyze to return low confidence (0.4)
    mock_result = VisionResult(
        food_name="Mystery Food",
        confidence=0.4,
        calories=100.0,
        protein=2.0,
        carbs=10.0,
        fat=1.0,
        fiber=1.0,
        sodium=50.0,
        estimated_weight_grams=150.0,
        meal_type="snack",
        cuisine="unknown",
        preparation_method="raw",
        ingredients=[],
        per_100g={}
    )
    
    with patch("src.agents.graph.compress_image", lambda x: x):
        with patch("src.providers.vision.gemini_provider.GeminiProvider.analyze", AsyncMock(return_value=mock_result)):
            # Invoke the supervisor main_graph with required checkpointer config
            final_state = await main_graph.ainvoke(
                initial_state, 
                config={"configurable": {"thread_id": "test-supervisor-thread"}}
            )
            
            # Verify it terminated and went to END
            # Total retry attempts must be 2, and retake_prompt must be set
            assert final_state["retry_count"] == 2
            assert final_state["retake_prompt"] is not None
            assert "retake the photo" in final_state["retake_prompt"].lower()


@pytest.mark.asyncio
async def test_supervisor_text_only_routing():
    """
    Verifies that a text-only request with no image bytes correctly routes
    to history_node/knowledge_node and returns a valid history_answer.
    """
    initial_state = {
        "image_bytes": None,
        "vision_result": None,
        "question": "What is the protein content of salmon?",
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": None,
    }

    # Mock the Gemini classification to return "knowledge_node"
    # Mock the search knowledge RAG tool and formatting LLM call
    with patch("src.agents.supervisor.get_gemini_client") as mock_get_client_sup, \
         patch("src.agents.graph.get_gemini_client") as mock_get_client_graph:
        mock_client = MagicMock()
        mock_get_client_sup.return_value = mock_client
        mock_get_client_graph.return_value = mock_client
        
        # Mock classication response
        mock_classify_resp = MagicMock()
        mock_classify_resp.text = "knowledge_node"
        
        # Mock formatting response
        mock_format_resp = MagicMock()
        mock_format_resp.text = "Salmon contains about 20g of protein per 100g."
        
        # Set up side effects for generate_content (1st call: classification, 2nd call: formatting)
        mock_client.aio.models.generate_content = AsyncMock(
            side_effect=[mock_classify_resp, mock_format_resp]
        )

        with patch("src.agents.tools.rag_tool.search_nutrition_knowledge", AsyncMock(return_value="Salmon nutrition data.")):
            final_state = await main_graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": "test-text-thread"}}
            )
            
            assert final_state["error"] is None
            assert final_state["history_answer"] == "Salmon contains about 20g of protein per 100g."
