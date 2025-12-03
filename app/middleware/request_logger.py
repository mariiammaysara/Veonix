import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs requests with request_id injected by RequestIDMiddleware.
    """

    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger("app.request")

        # Retrieve request_id from RequestIDMiddleware
        request_id = getattr(request.state, "request_id", "-")

        # Start log
        logger.info(
            f"[START] {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )

        # Process request
        response: Response = await call_next(request)

        # End log
        logger.info(
            f"[END] {request.method} {request.url.path} → {response.status_code}",
            extra={"request_id": request_id}
        )

        return response
