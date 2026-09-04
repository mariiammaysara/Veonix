"""
Module: health
Layer:  Controllers

Infrastructure health endpoints for monitoring and diagnostics.
Provides uptime visibility and direct AI provider integration testing.

Author: Mariam Maysara
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from src.config import settings
from src.controllers.analyze import ALLOWED_TYPES, MAX_SIZE_BYTES

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

    Gated behind settings.DEBUG: this endpoint has no rate limiting and calls
    the paid Gemini API directly, so it must never be reachable in production.

    Args:
        file: Multipart image file to analyze.

    Returns:
        The raw response string from Gemini and diagnostic metadata.
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Debug endpoint is disabled.")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image type.")

    from google import genai
    from google.genai import types
    from PIL import Image
    import io
    from src.helpers.prompts import GEMINI_PROMPT

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the size limit.")

    image = Image.open(io.BytesIO(image_bytes))
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    try:
        # Runs the blocking SDK call in a worker thread so it doesn't stall the event loop.
        response = await asyncio.to_thread(
            client.models.generate_content,
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
