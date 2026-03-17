"""
Module: exceptions
Layer:  Core

Domain-specific exception hierarchy for structured error handling.
Enables consistent error responses across all application layers.

Author: Mariam Maysara
"""

from src.enums.error_codes import ErrorCode


class VeonixException(Exception):
    """
    Base exception for all domain-specific errors.
    Attaches a machine-readable ErrorCode for consistent API responses.
    """
    def __init__(self, error_code: ErrorCode, detail: str = ""):
        self.error_code = error_code
        self.detail = detail
        super().__init__(error_code.user_message)


class VisionProviderError(VeonixException):
    """
    Raised when an external vision AI service fails or returns an invalid response.
    Typically raised by the Providers layer.
    """
    def __init__(self, detail: str = ""):
        super().__init__(ErrorCode.VISION_SERVICE_UNAVAILABLE, detail)


class LowConfidenceError(VeonixException):
    """
    Raised when the AI identifies food but with a confidence score below threshold.
    Typically raised by the Services layer.
    """
    def __init__(self, confidence: float):
        self.confidence = confidence
        super().__init__(ErrorCode.LOW_CONFIDENCE, f"confidence={confidence:.2f}")


class NoFoodDetectedError(VeonixException):
    """
    Raised when the vision AI explicitly indicates that no food is visible.
    """
    def __init__(self):
        super().__init__(ErrorCode.NO_FOOD_DETECTED)


class NutritionNotFoundError(VeonixException):
    """
    Raised when food is identified but no nutritional data can be retrieved.
    """
    def __init__(self, food_name: str):
        self.food_name = food_name
        super().__init__(ErrorCode.NUTRITION_NOT_FOUND, f"food={food_name}")


class NutritionServiceError(VeonixException):
    """
    Raised when upstream nutrition databases (USDA/Gemini) are unreachable.
    """
    def __init__(self, detail: str = ""):
        super().__init__(ErrorCode.NUTRITION_SERVICE_UNAVAILABLE, detail)


class ImageProcessingError(VeonixException):
    """
    Raised when an image fails preprocessing (compression, resizing, etc.).
    """
    def __init__(self, error_code: ErrorCode = ErrorCode.IMAGE_CORRUPTED, detail: str = ""):
        super().__init__(error_code, detail)
