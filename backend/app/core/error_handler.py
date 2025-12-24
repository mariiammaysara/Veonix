import logging
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """
    Handle HTTP exceptions (404, 401, 403, etc.).
    """

    logger.warning(
        "HTTP error",
        extra={
            "path": request.url.path,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )


def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle request validation errors.
    """

    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Catch-all handler for unexpected errors.
    """

    logger.exception(
        "Unhandled exception",
        extra={
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
        },
    )
