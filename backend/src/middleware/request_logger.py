"""
Module: request_logger
Layer:  Middleware

HTTP observability middleware.
Standardizes log formatting for every incoming request.
Records method, path, status, and duration for performance monitoring.

Author: Mariam Maysara
"""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging summary details of every handled request.
    """
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Captures the request duration and logs it with correlation IDs.
        """
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        # Extract request_id injected by RequestIdMiddleware
        request_id = getattr(request.state, "request_id", None)

        logger.info(
            "Request completed",
            extra={
                "method":      request.method,
                "path":        request.url.path,
                "status_code": response.status_code,
                "duration":    f"{duration:.4f}s",
                "request_id":  request_id,
            },
        )

        return response
