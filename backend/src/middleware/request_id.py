"""
Module: request_id
Layer:  Middleware

Request correlation middleware.
Injects a unique UUID into every request and response header.
Crucial for tracing requests in logs and debugging race conditions.

Author: Mariam Maysara
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique X-Request-ID to every incoming request.
    """
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Generates a UUID, stores it in the request state, and attaches it to the response.
        """
        request_id = str(uuid.uuid4())

        # Store for access in logging middleware or services
        request.state.request_id = request_id
        response = await call_next(request)

        # Mirror the ID in the response headers for client-side logging
        response.headers["X-Request-ID"] = request_id
        return response
