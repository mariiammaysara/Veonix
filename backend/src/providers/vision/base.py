"""
Module: base
Layer:  Providers (Interfaces)

Abstract interface for vision providers.
Enables transparent provider swapping without modifying core business logic.

Author: Mariam Maysara
"""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class VisionResult:
    """
    Standardized data carrier for all vision analysis results.
    Consolidates food identity and nutritional estimation into a single object.
    """
    # ── Food Identity ─────────────────────────────────────────
    food_name: str
    confidence: float
    ingredients: list[str]
    estimated_weight_grams: int
    meal_type: str
    cuisine: str
    preparation_method: str

    # ── Nutrition Metrics (Direct from AI) ──────────────────
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    fiber: float = 0.0
    sodium: float = 0.0
    per_100g: dict = field(default_factory=dict)


class VisionProvider(Protocol):
    """
    Interface definition for Vision AI integrations.
    Uses structural subtyping (Protocol) to allow flexible provider implementations
    without strict inheritance requirements.
    """
    async def analyze(self, image_bytes: bytes) -> VisionResult:
        """
        Analyzes an image and returns a consolidated identification and nutrition result.

        Args:
            image_bytes: Optimized binary image data.

        Returns:
            VisionResult object containing the AI's findings.
        """
        ...
