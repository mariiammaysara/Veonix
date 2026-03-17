"""
Module: error_codes
Layer:  Enums

Single source of truth for all API error codes, HTTP statuses, and user-facing messages.
Provides a unified contract between backend errors and frontend displays.

Author: Mariam Maysara
"""

from enum import Enum


class ErrorCode(Enum):
    """
    Structured error definitions.
    Tuple structure: (internal_code, http_status, user_message)
    """
    # ── Image errors ──────────────────────────────────────────
    INVALID_IMAGE_FORMAT = (
        "INVALID_IMAGE_FORMAT",
        415,
        "Please upload a valid image (JPEG, PNG, or WEBP).",
    )
    IMAGE_TOO_LARGE = (
        "IMAGE_TOO_LARGE",
        413,
        "Image is too large. Please upload an image under 10MB.",
    )
    IMAGE_CORRUPTED = (
        "IMAGE_CORRUPTED",
        422,
        "The image appears to be corrupted. Please try a different photo.",
    )

    # ── Vision / AI errors ────────────────────────────────────
    VISION_SERVICE_UNAVAILABLE = (
        "VISION_SERVICE_UNAVAILABLE",
        503,
        "The AI analysis service is currently unavailable. Please try again in a moment.",
    )
    LOW_CONFIDENCE = (
        "LOW_CONFIDENCE",
        422,
        "Couldn't identify the food clearly. Try a clearer photo with better lighting.",
    )
    NO_FOOD_DETECTED = (
        "NO_FOOD_DETECTED",
        422,
        "No food was detected in this image. Please upload a photo of a meal.",
    )

    # ── Nutrition errors ──────────────────────────────────────
    NUTRITION_NOT_FOUND = (
        "NUTRITION_NOT_FOUND",
        404,
        "Nutrition data wasn't found for this food. Try a more common dish.",
    )
    NUTRITION_SERVICE_UNAVAILABLE = (
        "NUTRITION_SERVICE_UNAVAILABLE",
        503,
        "Nutrition database is temporarily unavailable. Please try again shortly.",
    )

    # ── General errors ────────────────────────────────────────
    INTERNAL_ERROR = (
        "INTERNAL_ERROR",
        500,
        "Something went wrong on our end. Please try again.",
    )
    RATE_LIMIT_EXCEEDED = (
        "RATE_LIMIT_EXCEEDED",
        429,
        "Too many requests. Please wait a moment before trying again.",
    )

    # Properties used for clean access to tuple members without indexing
    @property
    def code(self) -> str:
        return self.value[0]

    @property
    def http_status(self) -> int:
        return self.value[1]

    @property
    def user_message(self) -> str:
        return self.value[2]
