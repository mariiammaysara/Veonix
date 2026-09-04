"""
Module: gemini_provider
Layer:  Providers (Implementation)

Google Gemini Vision integration via the google-genai SDK.
Executes a multimodal analysis that returns both food identity and nutrition in one round-trip.

Author: Mariam Maysara
"""

import logging
from typing import Optional
from PIL import Image
import io
from google import genai
from google.genai import types

from src.providers.vision.base import VisionResult
from src.helpers.prompts import GEMINI_PROMPT
from src.helpers.response_parser import parse_gemini_response
from src.config import settings
from src.exceptions import VisionProviderError

logger = logging.getLogger(__name__)


class GeminiProvider:
    """
    Gemini-based implementation of the VisionProvider interface.

    Responsibilities:
        - Interfacing with the Gemini 2.5 Pro/Flash Vision API.
        - Enforcing structured JSON output from the model.
        - Mapping raw API responses to domain-specific dataclasses.

    Dependencies:
        - google-genai SDK
        - response_parser helpers
    """

    @property
    def client(self) -> genai.Client:
        """Resolves the shared Gemini client lazily, on first real use."""
        from src.providers.vision.factory import get_gemini_client
        return get_gemini_client()

    async def analyze(self, image_bytes: bytes, prompt: Optional[str] = None) -> VisionResult:
        """
        Sends an image to Gemini and performs multimodal extraction.

        Args:
            image_bytes: Optimized binary image data.
            prompt: Optional custom prompt. Falls back to GEMINI_PROMPT if None,
                    allowing goal-aware prompt injection from the agent layer.

        Returns:
            Verified VisionResult object.

        Raises:
            VisionProviderError: If the API call fails or the response is malformed.
        """
        # Use injected prompt if provided, otherwise fall back to the static base prompt.
        effective_prompt = prompt if prompt is not None else GEMINI_PROMPT

        try:
            image = Image.open(io.BytesIO(image_bytes))

            logger.info(f"GeminiProvider.analyze() using model={settings.GEMINI_MODEL}")

            # Trigger content generation with explicit JSON forcing
            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[effective_prompt, image],
                config=types.GenerateContentConfig(
                    # Temperature 0.1 ensures higher determinism for factual nutrition data
                    temperature=0.1,
                    # Eliminates markdown formatting around JSON for reliable parsing
                    response_mime_type="application/json",
                ),
            )

            raw_response = response.text
            logger.info(f"Gemini raw response: {raw_response[:200]}...")

            return parse_gemini_response(raw_response)

        except Exception as e:
            logger.error(f"Gemini API handshake failed: {str(e)}")
            raise VisionProviderError(f"Upstream AI error: {str(e)}")


