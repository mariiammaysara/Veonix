"""
Module: agent_trace
Layer:  Middleware (Agent-Level)

LangChain/LangGraph callback-based middleware for agent observability.
Logs structured JSON events for each node invocation and tool call:

  {"event": "node_start",  "node": "vision_node", "model": "gemini-2.5-flash", ...}
  {"event": "node_end",    "node": "vision_node", "duration_ms": 1234, ...}
  {"event": "tool_start",  "tool": "search_nutrition_knowledge", "node": "knowledge_node"}
  {"event": "tool_end",    "tool": "search_nutrition_knowledge", "duration_ms": 42}

Usage: injected into LangGraph ainvoke() config as a callback, not as HTTP middleware.

  config = {"configurable": {...}, "callbacks": [AgentTraceCallback(request_id=...)]}
  await main_graph.ainvoke(state, config=config)

Author: Antigravity AI
"""

import json
import logging
import time
from typing import Any, Optional
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler

logger = logging.getLogger(__name__)


class AgentTraceCallback(AsyncCallbackHandler):
    """
    Async LangChain/LangGraph callback that emits structured JSON log lines
    at each node and tool boundary.

    This mirrors the request-level RequestLoggerMiddleware/TimingMiddleware pattern
    but operates at the agent graph level, capturing which node, model, and tool
    were used per execution.
    """

    def __init__(self, request_id: Optional[str] = None):
        super().__init__()
        self.request_id = request_id
        # Track active start times keyed by run UUID so nested runs don't collide
        self._node_start_times: dict[str, float] = {}
        self._tool_start_times: dict[str, float] = {}

    def _emit(self, payload: dict) -> None:
        """Emit a structured JSON log line at INFO level."""
        if self.request_id:
            payload["request_id"] = self.request_id
        logger.info(json.dumps(payload))

    # ── Node/Chain hooks ─────────────────────────────────────────────────────

    async def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Fires when a LangGraph node (chain) begins execution."""
        run_key = str(run_id)
        self._node_start_times[run_key] = time.perf_counter()

        # Extract node name from serialized metadata or tags
        node_name = (
            (metadata or {}).get("langgraph_node")
            or (tags[0] if tags else None)
            or (serialized.get("name", "unknown_node") if serialized else "unknown_node")
        )

        self._emit({
            "event": "node_start",
            "node": node_name,
            "run_id": run_key,
        })

    async def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Fires when a LangGraph node (chain) finishes execution."""
        run_key = str(run_id)
        start = self._node_start_times.pop(run_key, None)
        duration_ms = round((time.perf_counter() - start) * 1000, 2) if start else None

        node_name = (
            (metadata or {}).get("langgraph_node")
            or (tags[0] if tags else None)
            or "unknown_node"
        )

        self._emit({
            "event": "node_end",
            "node": node_name,
            "run_id": run_key,
            "duration_ms": duration_ms,
        })

    async def on_chain_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Fires when a node raises an exception."""
        run_key = str(run_id)
        start = self._node_start_times.pop(run_key, None)
        duration_ms = round((time.perf_counter() - start) * 1000, 2) if start else None

        node_name = (
            (metadata or {}).get("langgraph_node")
            or (tags[0] if tags else None)
            or "unknown_node"
        )

        self._emit({
            "event": "node_error",
            "node": node_name,
            "run_id": run_key,
            "duration_ms": duration_ms,
            "error": str(error),
        })

    # ── Tool hooks ───────────────────────────────────────────────────────────

    async def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Fires when a tool (SQL, RAG, Tavily) begins execution."""
        run_key = str(run_id)
        self._tool_start_times[run_key] = time.perf_counter()

        tool_name = serialized.get("name", "unknown_tool")
        self._emit({
            "event": "tool_start",
            "tool": tool_name,
            "run_id": run_key,
        })

    async def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Fires when a tool finishes execution."""
        run_key = str(run_id)
        start = self._tool_start_times.pop(run_key, None)
        duration_ms = round((time.perf_counter() - start) * 1000, 2) if start else None

        self._emit({
            "event": "tool_end",
            "run_id": run_key,
            "duration_ms": duration_ms,
        })

    async def on_tool_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Fires when a tool raises an exception."""
        run_key = str(run_id)
        start = self._tool_start_times.pop(run_key, None)
        duration_ms = round((time.perf_counter() - start) * 1000, 2) if start else None

        self._emit({
            "event": "tool_error",
            "run_id": run_key,
            "duration_ms": duration_ms,
            "error": str(error),
        })
