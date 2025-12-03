from io import BytesIO
from typing import Any
from PIL import Image


def load_image_bytes(file) -> bytes:
    """
    Read raw bytes from an uploaded file.
    The caller handles HTTP errors.
    """
    content = file.file.read()
    if not content:
        raise ValueError("Uploaded file is empty.")
    return content


def pil_from_bytes(data: bytes) -> Image.Image:
    """
    Convert raw bytes to a PIL Image.
    """
    try:
        return Image.open(BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode image bytes: {exc}")


def to_jpeg_bytes(image: Image.Image, quality: int = 90) -> bytes:
    """
    Encode a PIL Image into JPEG bytes.
    """
    try:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        return buffer.getvalue()
    except Exception as exc:
        raise ValueError(f"Failed to encode image as JPEG: {exc}")
