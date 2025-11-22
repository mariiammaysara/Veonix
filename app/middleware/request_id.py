import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store inside request.state so any layer can access it
        request.state.request_id = request_id

        # Process request
        response: Response = await call_next(request)

        # Add ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
