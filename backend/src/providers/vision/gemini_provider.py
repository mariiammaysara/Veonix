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

    def __init__(self):
        from src.providers.vision.factory import get_gemini_client
        self.client = get_gemini_client()

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
        # Use injected prompt if provided (e.g. goal-aware build_vision_prompt result),
        # otherwise fall back to the static base prompt for full backward compatibility.
        effective_prompt = prompt if prompt is not None else GEMINI_PROMPT

        try:
            image = Image.open(io.BytesIO(image_bytes))

            logger.info(f"GeminiProvider.analyze() using model={settings.GEMINI_MODEL}")

            # Import here to avoid circular import at module load time
            from langfuse._client.get_client import get_client as _get_langfuse_client
            langfuse = _get_langfuse_client()

            # Wrap the actual Gemini call as a Langfuse "generation" so that
            # real latency and token counts appear in the trace (not just the
            # graph shell latency which is always ~0ms).
            with langfuse.start_as_current_observation(
                name="gemini-vision-generate",
                as_type="generation",
                model=settings.GEMINI_MODEL,
                input={"prompt_summary": effective_prompt[:300], "image_present": True},
            ) as generation:
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

                # Extract token usage from Gemini response metadata if available
                usage_details = None
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    um = response.usage_metadata
                    usage_details = {}
                    if hasattr(um, "prompt_token_count") and um.prompt_token_count:
                        usage_details["input"] = um.prompt_token_count
                    if hasattr(um, "candidates_token_count") and um.candidates_token_count:
                        usage_details["output"] = um.candidates_token_count
                    if hasattr(um, "total_token_count") and um.total_token_count:
                        usage_details["total"] = um.total_token_count

                # Update the generation span with output and token usage
                generation.update(
                    output=raw_response[:500],  # truncate long JSON for readability
                    usage_details=usage_details or {},
                )

            return parse_gemini_response(raw_response)

        except Exception as e:
            logger.error(f"Gemini API handshake failed: {str(e)}")
            raise VisionProviderError(f"Upstream AI error: {str(e)}")


