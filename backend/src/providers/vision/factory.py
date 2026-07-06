"""
Module: factory
Layer:  Providers (Factories)

Vision provider factory.
Decouples the Service layer from concrete AI provider implementations.
This is the single source of truth for injecting vision capabilities.

Author: Mariam Maysara
"""

from src.providers.vision.base import VisionProvider
from src.providers.vision.gemini_provider import GeminiProvider


_provider: VisionProvider | None = None

def get_vision_provider() -> VisionProvider:
    """
    Retrieves the configured vision provider instance.
    Currently hardcoded to GeminiProvider; abstracting here enables future A/B testing or fallback switching.

    Returns:
        An object conforming to the VisionProvider protocol.
    """
    global _provider
    if _provider is None:
        _provider = GeminiProvider()
    return _provider
