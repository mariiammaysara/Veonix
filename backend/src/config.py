"""
Module: config
Layer:  Infrastructure

Centralized configuration via Pydantic Settings.
Loads environment variables and provides typed access to app settings.

Author: Mariam Maysara
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application-wide settings managed through environment variables.
    """
    # ── Gemini Configuration ──────────────────────────────────
    GEMINI_API_KEY: str = ""
    # Strong multimodal model — used for vision/image analysis nodes
    GEMINI_MODEL: str = "gemini-2.5-flash"
    # Cheaper, faster text-only model — used for history and knowledge Q&A nodes
    GEMINI_MODEL_FAST: str = "gemini-2.0-flash"
    TAVILY_API_KEY: str = ""

    # ── Database Configuration ────────────────────────────────
    DATABASE_URL: str = "sqlite:///./veonix.db"

    # ── Application Metadata ──────────────────────────────────
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── Langfuse Tracing ──────────────────────────────────────
    # Generate public/secret keys from your self-hosted Langfuse instance's project settings after first login (http://localhost:3001).
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "http://localhost:3001"

    class Config:
        env_file = ".env"
        # Prevents startup crash if legacy keys remain in .env
        extra = "ignore"


settings = Settings()

# Sync Langfuse configurations to os.environ so the Langfuse SDK detects them
if settings.LANGFUSE_PUBLIC_KEY:
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
if settings.LANGFUSE_SECRET_KEY:
    os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
if settings.LANGFUSE_HOST:
    os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST

