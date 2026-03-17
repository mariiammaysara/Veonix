"""
Module: timing
Layer:  Middleware

Performance benchmarking middleware.
Calculates server-side processing time (TTFB) and injects it into response headers.
Used for bottleneck detection and latency monitoring.

Author: Mariam Maysara
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds 'X-Process-Time' to all HTTP responses.
    """
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Wraps the request lifecycle in a performance counter.
        """
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        # Precision formatted to 4 decimal places for accurate sub-millisecond tracking
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        return response
