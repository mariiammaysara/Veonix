"""
Tests for the Tavily Web Search tool.
Mocks HTTP API calls to verify direct answer extraction and snippet assembly.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.tools.tavily_tool import search_tavily


@pytest.fixture(autouse=True)
def mock_settings_tavily(monkeypatch):
    """
    Ensure settings has a dummy API key to pass check.
    """
    monkeypatch.setenv("TAVILY_API_KEY", "dummy-tavily-key")


@pytest.mark.asyncio
async def test_search_tavily_missing_key(monkeypatch):
    """
    Verify behavior when the Tavily API key is not configured.
    """
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    # Re-import settings or patch settings attribute directly
    with patch("src.agents.tools.tavily_tool.settings") as mock_settings:
        mock_settings.TAVILY_API_KEY = ""
        ans = await search_tavily("hydration target")
        assert "not configured" in ans


@pytest.mark.asyncio
async def test_search_tavily_direct_answer():
    """
    Verify direct answer is returned from JSON response if present.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "answer": "Adults should drink 2-3 liters of water daily.",
        "results": []
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        result = await search_tavily("how much water to drink")
        assert result == "Adults should drink 2-3 liters of water daily."
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_search_tavily_snippets_fallback():
    """
    Verify snippets are assembled if direct answer is absent.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {"content": "Water maintains body temperature."},
            {"content": "Hydration lubricates joints."}
        ]
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        result = await search_tavily("benefits of water")
        assert "body temperature" in result
        assert "lubricates joints" in result
        mock_post.assert_called_once()
