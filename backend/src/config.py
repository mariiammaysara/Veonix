"""
Module: config
Layer:  Infrastructure

Centralized configuration via Pydantic Settings.
Loads environment variables and provides typed access to app settings.

Author: Mariam Maysara
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application-wide settings managed through environment variables.
    """
    # ── Gemini Configuration ──────────────────────────────────
    GEMINI_API_KEY: str = ""
    # Multimodal model used for vision/image analysis
    # "gemini-flash-latest" is a Google-maintained alias that always points to
    # the current stable Flash model, so it doesn't need bumping when a
    # pinned version (like gemini-2.5-flash) gets deprecated or overloaded.
    GEMINI_MODEL: str = "gemini-flash-latest"

    # ── Database Configuration ────────────────────────────────
    DATABASE_URL: str = "sqlite:///./veonix.db"

    # ── Application Metadata ──────────────────────────────────
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://veonix.mariammaysara.com",
    ]

    class Config:
        env_file = ".env"
        # Prevents startup crash if legacy keys remain in .env
        extra = "ignore"


settings = Settings()

