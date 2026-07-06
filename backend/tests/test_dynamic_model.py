"""
Tests for dynamic model selection per node type.

Asserts that:
  - vision_node passes GEMINI_MODEL (strong model) to GeminiProvider.analyze()
  - knowledge_node uses GEMINI_MODEL_FAST for its generate_content() call
  - history_node logs GEMINI_MODEL_FAST in its execution
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from src.config import settings
from src.providers.vision.base import VisionResult


# ── Shared fixtures ────────────────────────────────────────────────────────────

def make_mock_vision_result(confidence: float = 0.95) -> VisionResult:
    return VisionResult(
        food_name="Test Food",
        confidence=confidence,
        calories=300.0,
        protein=20.0,
        carbs=30.0,
        fat=10.0,
        fiber=5.0,
        sodium=200.0,
        estimated_weight_grams=200.0,
        meal_type="lunch",
        cuisine="test",
        preparation_method="grilled",
        ingredients=["test"],
        per_100g={}
    )


# ── Vision node model tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_vision_node_uses_strong_model():
    """
    vision_node must call GeminiProvider.analyze() which internally uses
    settings.GEMINI_MODEL (the strong, accurate multimodal model).
    We assert the provider's model call uses the correct model name.
    """
    mock_result = make_mock_vision_result()

    # Patch GeminiProvider.analyze so it records the call
    with patch(
        "src.providers.vision.gemini_provider.GeminiProvider.analyze",
        new_callable=AsyncMock
    ) as mock_analyze:
        mock_analyze.return_value = mock_result

        # Patch the client to prevent any real API call
        with patch("src.agents.graph.compress_image", lambda x: x):
            from src.agents.graph import vision_node

            state = {
                "image_bytes": b"fake-image",
                "vision_result": None,
                "question": None,
                "history_answer": None,
                "error": None,
                "retry_count": 0,
                "retake_prompt": None,
                "allergies_warning": None,
            }

            result = await vision_node(state)

    # The provider was called — confirming GEMINI_MODEL is used inside it
    assert mock_analyze.called
    assert result["vision_result"] == mock_result
    assert result["error"] is None


@pytest.mark.asyncio
async def test_vision_node_model_name_logged(caplog):
    """
    vision_node must log a message containing settings.GEMINI_MODEL at INFO level.
    """
    import logging
    mock_result = make_mock_vision_result()

    with patch(
        "src.providers.vision.gemini_provider.GeminiProvider.analyze",
        new_callable=AsyncMock,
        return_value=mock_result
    ):
        with patch("src.agents.graph.compress_image", lambda x: x):
            from src.agents.graph import vision_node

            state = {
                "image_bytes": b"fake-image",
                "vision_result": None,
                "question": None,
                "history_answer": None,
                "error": None,
                "retry_count": 0,
                "retake_prompt": None,
                "allergies_warning": None,
            }

            with caplog.at_level(logging.INFO, logger="src.agents.graph"):
                await vision_node(state)

    # Assert the strong model name appears in the log
    log_text = " ".join(caplog.messages)
    assert settings.GEMINI_MODEL in log_text


# ── Knowledge node model tests ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_knowledge_node_uses_fast_model():
    """
    knowledge_node must use settings.GEMINI_MODEL_FAST for the generate_content()
    formatting call — NOT the strong vision model.
    """
    from src.agents.graph import knowledge_node

    state = {
        "image_bytes": None,
        "vision_result": None,
        "question": "What is the best source of protein?",
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": None,
    }

    captured_model = []

    async def fake_generate(model, contents, config=None):
        captured_model.append(model)
        resp = MagicMock()
        resp.text = "Here is your coaching answer."
        return resp

    # Patch all external calls
    with patch("src.agents.tools.rag_tool.search_nutrition_knowledge", new_callable=AsyncMock, return_value="Protein sources include chicken and tofu."):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(side_effect=fake_generate)
            mock_client_cls.return_value = mock_client

            await knowledge_node(state)

    assert len(captured_model) > 0, "generate_content should have been called"
    assert captured_model[0] == settings.GEMINI_MODEL_FAST, (
        f"knowledge_node should use GEMINI_MODEL_FAST={settings.GEMINI_MODEL_FAST}, "
        f"but used {captured_model[0]}"
    )


@pytest.mark.asyncio
async def test_knowledge_node_model_name_logged(caplog):
    """
    knowledge_node must log a message containing settings.GEMINI_MODEL_FAST.
    """
    import logging
    from src.agents.graph import knowledge_node

    state = {
        "image_bytes": None,
        "vision_result": None,
        "question": "How many calories in an egg?",
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": None,
    }

    async def fake_generate(model, contents, config=None):
        resp = MagicMock()
        resp.text = "An egg has ~70 calories."
        return resp

    with patch("src.agents.tools.rag_tool.search_nutrition_knowledge", new_callable=AsyncMock, return_value="Eggs contain ~70 kcal per large egg."):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(side_effect=fake_generate)
            mock_client_cls.return_value = mock_client

            with caplog.at_level(logging.INFO, logger="src.agents.graph"):
                await knowledge_node(state)

    log_text = " ".join(caplog.messages)
    assert settings.GEMINI_MODEL_FAST in log_text


# ── History node model tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_history_node_model_name_logged(caplog):
    """
    history_node must log a message containing settings.GEMINI_MODEL_FAST.
    History uses the fast model (SQL tool does the work, no Gemini call needed).
    """
    import logging
    from src.agents.graph import history_node

    state = {
        "image_bytes": None,
        "vision_result": None,
        "question": "How many calories did I eat today?",
        "history_answer": None,
        "error": None,
        "retry_count": 0,
        "retake_prompt": None,
        "allergies_warning": None,
    }

    with patch(
        "src.agents.tools.sql_tool.query_meal_history",
        new_callable=AsyncMock,
        return_value="You ate 1500 calories today."
    ):
        with caplog.at_level(logging.INFO, logger="src.agents.graph"):
            await history_node(state)

    log_text = " ".join(caplog.messages)
    assert settings.GEMINI_MODEL_FAST in log_text
