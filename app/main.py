from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging_config import logger
from app.core.error_handler import init_error_handlers

from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_logger import RequestLoggingMiddleware
from app.middleware.timing import TimingMiddleware

from app.routers import analyze, status


def create_app() -> FastAPI:
    app = FastAPI()

    # -----------------------------
    # CORS
    # -----------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------
    # MIDDLEWARE ORDER (VERY IMPORTANT)
    # -----------------------------
    # 1) Generate request_id
    app.add_middleware(RequestIDMiddleware)

    # 2) Log request start/end with request_id
    app.add_middleware(RequestLoggingMiddleware)

    # 3) Measure execution time
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
