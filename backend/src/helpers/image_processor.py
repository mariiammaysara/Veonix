"""
Module: image_processor
Layer:  Helpers

Image preprocessing pipeline.
Normalizes and compresses images before they are transmitted to AI providers.
Ensures compatibility with Gemini Vision API requirements.

Author: Mariam Maysara
"""

import io
import logging
from PIL import Image
from src.exceptions import ImageProcessingError

logger = logging.getLogger(__name__)

# Max dimension (width or height) — 800px is sufficient for Gemini food analysis
# and reduces visual token count vs the previous 1200px limit.
MAX_DIMENSION = 800
# 85 is the sweet spot: high visual quality for AI with ~40% smaller file size
JPEG_QUALITY = 85


def compress_image(image_bytes: bytes) -> bytes:
    """
    Normalizes image format, resizes proportionately, and applies JPEG compression.

    Args:
        image_bytes: Raw input image data.

    Returns:
        Compressed JPEG binary data.

    Raises:
        ImageProcessingError: If the image is corrupted or cannot be processed.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Gemini Vision requires RGB — RGBA or palette modes cause a 400 error.
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # Downscale only if the longest side exceeds the limit.
            width, height = img.size
            if max(width, height) > MAX_DIMENSION:
                scale = MAX_DIMENSION / max(width, height)
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.LANCZOS)
                logger.debug(f"Resized image from {width}x{height} to {new_size[0]}x{new_size[1]}")

            output = io.BytesIO()
            img.save(output, format="JPEG", quality=JPEG_QUALITY)
            return output.getvalue()

    except Exception as e:
        logger.error(f"Image compression failed: {e}")
        raise ImageProcessingError(detail=f"Could not process image: {e}")
