from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    # App environment
    ENV: str = "development"

    # Gemini API configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "models/gemini-2.5-flash"

    # Image limits
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024
    TEMP_DIR: str = "temp"

    # CORS settings
    CORS_ALLOWED_ORIGINS: Optional[str] = None
    # Example in .env:
    # CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None  # e.g. logs/app.log

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origins(self) -> List[str]:
        """Return parsed CORS origins as a list."""
        if not self.CORS_ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
