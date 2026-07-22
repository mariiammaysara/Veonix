"""
Module: graph_errors
Layer:  Enums

Structured error classification for graph-level errors stored in AnalysisState.
Instead of raw exception strings, errors are stored as small structured objects
so they can be consistently filtered and classified in Langfuse traces.

Author: Antigravity AI
"""

from enum import Enum
from typing import Any


class GraphErrorType(str, Enum):
    """
    Canonical error type categories for graph execution errors.
    Used as the `error_type` field in structured error dicts.
    """
    CONNECTION_ERROR = "connection_error"
    TIMEOUT = "timeout"
    INVALID_RESPONSE = "invalid_response"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN = "unknown"


def classify_exception(exc: Exception) -> GraphErrorType:
    """
    Classify an exception into one of the canonical GraphErrorType categories.
    """
    exc_str = str(exc).lower()
    if "429" in exc_str or "resource_exhausted" in exc_str or "quota" in exc_str:
        return GraphErrorType.QUOTA_EXCEEDED
    if "timeout" in exc_str or "deadline" in exc_str:
        return GraphErrorType.TIMEOUT
    if "connection" in exc_str or "network" in exc_str or "handshake" in exc_str:
        return GraphErrorType.CONNECTION_ERROR
    if "json" in exc_str or "parse" in exc_str or "invalid" in exc_str or "malformed" in exc_str:
        return GraphErrorType.INVALID_RESPONSE
    return GraphErrorType.UNKNOWN


def build_graph_error(exc: Exception, provider: str = "gemini", retryable: bool = None) -> dict:
    """
    Build a structured error dict from an exception for storage in graph state.

    Args:
        exc: The caught exception.
        provider: The upstream provider name (e.g. "gemini", "tavily").
        retryable: Whether this error is likely retryable. Inferred automatically if None.

    Returns:
        A JSON-serializable dict with error_type, provider, retryable, and message fields.
    """
    error_type = classify_exception(exc)

    if retryable is None:
        retryable = error_type in (GraphErrorType.CONNECTION_ERROR, GraphErrorType.TIMEOUT, GraphErrorType.QUOTA_EXCEEDED)

    return {
        "error_type": error_type.value,
        "provider": provider,
        "retryable": retryable,
        "message": str(exc),
    }
