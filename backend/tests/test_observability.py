"""
Unit tests for Langfuse observability integrations.
Verifies that the Langfuse CallbackHandler is correctly attached to graph executions.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.graph import run_analysis_graph
from langfuse.langchain import CallbackHandler


@pytest.fixture(autouse=True)
def mock_langfuse_env(monkeypatch):
    """
    Mock Langfuse environment keys for tests to avoid network calls or warnings.
    """
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-testkey123")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-testkey123")
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3001")


@pytest.mark.asyncio
async def test_langfuse_callback_handler_attached():
    """
    Verifies that CallbackHandler is injected into compiled main_graph ainvoke calls.
    """
    with patch("src.agents.supervisor.main_graph.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = {}

        # Run graph execution helper
        await run_analysis_graph(
            image_bytes=None,
            question="What is the protein content of salmon?",
            thread_id="test-observability-thread"
        )

        mock_ainvoke.assert_called_once()
        _, kwargs = mock_ainvoke.call_args
        config = kwargs.get("config")

        assert config is not None
        assert "callbacks" in config
        callbacks = config["callbacks"]

        # Assert CallbackHandler is in the list of callbacks
        langfuse_handlers = [cb for cb in callbacks if isinstance(cb, CallbackHandler)]
        assert len(langfuse_handlers) == 1, "Langfuse CallbackHandler was not injected."
