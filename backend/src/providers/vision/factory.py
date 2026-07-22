"""
Module: factory
Layer:  Providers (Factories)

Vision provider factory.
Decouples the Service layer from concrete AI provider implementations.
This is the single source of truth for injecting vision capabilities.

Author: Mariam Maysara
"""

import threading
from google import genai
from google.genai import types
from src.config import settings
from src.providers.vision.base import VisionProvider
from src.providers.vision.gemini_provider import GeminiProvider


_provider: VisionProvider | None = None
_provider_lock = threading.Lock()

_client: genai.Client | None = None
_client_lock = threading.Lock()


def get_gemini_client() -> genai.Client:
    """
    Retrieves the thread-safe shared Gemini API Client singleton.
    Configured with a client-wide 30-second request timeout.
    """
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = genai.Client(
                    api_key=settings.GEMINI_API_KEY,
                    http_options=types.HttpOptions(timeout=30_000)  # 30s timeout
                )
    return _client


def get_vision_provider() -> VisionProvider:
    """
    Retrieves the configured vision provider instance.
    Currently hardcoded to GeminiProvider; abstracting here enables future A/B testing or fallback switching.

    Returns:
        An object conforming to the VisionProvider protocol.
    """
    global _provider
    if _provider is None:
        with _provider_lock:
            if _provider is None:
                _provider = GeminiProvider()
    return _provider
