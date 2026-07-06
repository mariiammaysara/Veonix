"""
Module: main
Layer:  Entry Point

FastAPI application factory and lifecycle management.
Coordinates middleware, routers, and database initialization.

Author: Mariam Maysara
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.controllers.analyze import router as analyze_router
from src.controllers.coach import router as coach_router
from src.controllers.health import router as health_router
from src.controllers.profile import router as profile_router
from src.middleware.request_id import RequestIdMiddleware
from src.middleware.request_logger import RequestLoggerMiddleware
from src.middleware.timing import TimingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown lifecycle events.
    Preferred over deprecated on_event handlers for robust resource management.
    """
    yield
    # Resources are automatically cleaned up after yield


app = FastAPI(
    title="Veonix API",
    description="AI Nutrition Analysis — Food Vision + Gemini Single Model",
    version="2.1.0",
    lifespan=lifespan,
)

# CORS configuration
# Must be defined early to intercept preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://veonix.mariammaysara.com",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware stack
# Order matters: last added is the first to intercept the request
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(RequestIdMiddleware)

# API Routers
# analyze_router handles core business logic; health_router for infrastructure checks
app.include_router(analyze_router)
app.include_router(coach_router)
app.include_router(profile_router)
app.include_router(health_router)
