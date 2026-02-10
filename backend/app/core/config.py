from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "Veonix"
    debug: bool = False




    # Optional environment config (from .env)
    hf_token: str
    environment: str = "development"
    log_level: str = "INFO"

    # CORS
    allowed_origins: List[str] = ["*"]

    # ✅ Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
