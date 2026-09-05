"""
Tests for GeminiProvider's retry-with-backoff behavior on transient
upstream failures (e.g. Gemini's own 503 "high demand" responses).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.genai.errors import APIError

from src.providers.vision.gemini_provider import GeminiProvider
from src.exceptions import VisionProviderError

VALID_JSON = '{"food_name": "Rice", "confidence": 0.9, "ingredients": [], "estimated_weight_grams": 200, "meal_type": "lunch", "cuisine": "unknown", "preparation_method": "boiled", "nutrition": {}}'

FAKE_IMAGE_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0"
    b"\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _api_error(code: int) -> APIError:
    return APIError(code, {"error": {"code": code, "message": "high demand", "status": "UNAVAILABLE"}})


@pytest.mark.asyncio
async def test_retries_on_503_then_succeeds():
    """A 503 followed by a success should retry once and return a result."""
    success_response = MagicMock(text=VALID_JSON)
    mock_generate = AsyncMock(side_effect=[_api_error(503), success_response])

    provider = GeminiProvider()
    with patch.object(type(provider), "client", new=MagicMock(aio=MagicMock(models=MagicMock(generate_content=mock_generate)))), \
         patch("asyncio.sleep", new=AsyncMock()):
        result = await provider.analyze(FAKE_IMAGE_BYTES)

    assert result.food_name == "Rice"
    assert mock_generate.call_count == 2


@pytest.mark.asyncio
async def test_gives_up_after_max_retries():
    """Persistent 503s should eventually raise VisionProviderError, not hang forever."""
    mock_generate = AsyncMock(side_effect=[_api_error(503), _api_error(503), _api_error(503)])

    provider = GeminiProvider()
    with patch.object(type(provider), "client", new=MagicMock(aio=MagicMock(models=MagicMock(generate_content=mock_generate)))), \
         patch("asyncio.sleep", new=AsyncMock()):
        with pytest.raises(VisionProviderError):
            await provider.analyze(FAKE_IMAGE_BYTES)

    assert mock_generate.call_count == 3


@pytest.mark.asyncio
async def test_does_not_retry_non_retryable_errors():
    """A non-transient error (e.g. 400 bad request) should fail immediately, no retry."""
    mock_generate = AsyncMock(side_effect=[_api_error(400)])

    provider = GeminiProvider()
    with patch.object(type(provider), "client", new=MagicMock(aio=MagicMock(models=MagicMock(generate_content=mock_generate)))), \
         patch("asyncio.sleep", new=AsyncMock()):
        with pytest.raises(VisionProviderError):
            await provider.analyze(FAKE_IMAGE_BYTES)

    assert mock_generate.call_count == 1
