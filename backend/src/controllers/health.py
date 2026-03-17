"""
Module: health
Layer:  Controllers

Infrastructure health endpoints for monitoring and diagnostics.
Provides uptime visibility and direct AI provider integration testing.

Author: Mariam Maysara
"""

import logging
from fastapi import APIRouter, UploadFile, File
from src.config import settings

logger = logging.getLogger(__name__)
# Infrastructure router; excluded from user-facing stats/history logic
router = APIRouter(tags=["System"])


@router.get("/health")
async def health():
    """
    Application health check.
    Returns status 'ok' only if the basic app is running and API keys are configured.
    """
    return {
        "status": "ok",
        "vision": {
            "provider": "Gemini",
            "model": settings.GEMINI_MODEL,
            # Indicates if the provider is operationally ready based on presence of API key
            "status": "ok" if settings.GEMINI_API_KEY else "missing_api_key",
        },
        "nutrition": {
            "provider": "Gemini",
            "status": "ok" if settings.GEMINI_API_KEY else "missing_api_key",
        },
    }


@router.post("/debug/vision")
async def debug_vision(file: UploadFile = File(...)):
    """
    Sends an image directly to Gemini and returns the un-parsed raw text response.
    Bypasses the response_parser and DB layer to verify if the model 'sees' the image.

    Args:
        file: Multipart image file to analyze.

    Returns:
        The raw response string from Gemini and diagnostic metadata.
    """
    from google import genai
    from google.genai import types
    from PIL import Image
    import io
    from src.helpers.prompts import GEMINI_PROMPT

    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[GEMINI_PROMPT, image],
            config=types.GenerateContentConfig(
                # Deterministic setting tailored for food recognition
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )
        return {
            "status": "success",
            "model": settings.GEMINI_MODEL,
            "image_size_kb": round(len(image_bytes) / 1024, 1),
            "raw_response": response.text,
        }

    except Exception as e:
        logger.error(f"Debug vision failed: {str(e)}")
        return {"status": "error", "detail": str(e)}
