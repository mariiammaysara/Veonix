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
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ── Database Configuration ────────────────────────────────
    DATABASE_URL: str = "sqlite:///./veonix.db"

    # ── Application Metadata ──────────────────────────────────
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        # Prevents startup crash if legacy keys remain in .env
        extra = "ignore"


settings = Settings()
