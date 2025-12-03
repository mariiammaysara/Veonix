from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.core.logging_config import logger
from app.core.error_handler import init_error_handlers

from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_logger import RequestLoggingMiddleware
from app.middleware.timing import TimingMiddleware

from app.routers import analyze, status


def create_app() -> FastAPI:

    # -----------------------------
    # Disable Swagger in Production
    # -----------------------------
    if settings.ENV == "production":
        app = FastAPI(
            docs_url=None,
            redoc_url=None,
            openapi_url=None
        )
    else:
        app = FastAPI()

    # -----------------------------
    # SECURITY: Remove server header
    # -----------------------------
    @app.middleware("http")
    async def remove_server_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["Server"] = ""
        return response

    # -----------------------------
    # SECURITY: Limit upload size
    # -----------------------------
    @app.middleware("http")
    async def limit_upload_size(request: Request, call_next):
        max_size = settings.MAX_IMAGE_SIZE
        content_length = request.headers.get("content-length")

        if content_length and int(content_length) > max_size:
            return PlainTextResponse("Request too large", status_code=413)

        return await call_next(request)

    # -----------------------------
    # CORS – secure in production
    # -----------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins if settings.ENV == "production" else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------
    # GZIP Compression
    # -----------------------------
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # -----------------------------
    # Middleware ordering (critical)
    # -----------------------------
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TimingMiddleware)

    # -----------------------------
    # Routers
    # -----------------------------
    app.include_router(analyze.router)
    app.include_router(status.router)

    # -----------------------------
    # Error Handlers
    # -----------------------------
    init_error_handlers(app)

    return app


app = create_app()


@app.get("/health")
def health():
    return {"status": "ok"}
