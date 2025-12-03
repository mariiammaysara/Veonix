from typing import List, Dict, Any, Optional


class NutritionNormalizer:
    """
    Normalize nutrition items based on:
    - type: packaged vs fresh
    - category-based rules (fresh)
    - safe numeric conversion
    - clamping to realistic ranges
    """

    # Fresh Food Category Rules
    CATEGORY_RULES = {
        "salad": {
            "calories": (80, 250),
            "fat_grams": (3, 20),
        },
        "chicken": {
            "calories": (120, 240),
            "protein_grams": (20, 35),
        },
        "fish": {
            "calories": (150, 280),
            "protein_grams": (20, 30),
        },
        "salmon": {
            "calories": (180, 280),
            "protein_grams": (20, 30),
        },
        "pasta": {
            "calories": (150, 350),
            "carb_grams": (25, 55),
        },
        "rice": {
            "calories": (150, 350),
            "carb_grams": (25, 55),
        },
        "brownie": {
            "calories": (280, 500),
            "fat_grams": (10, 35),
        },
        "cake": {
            "calories": (250, 500),
            "fat_grams": (10, 35),
        },
        "chocolate": {
            "calories": (250, 550),
            "fat_grams": (12, 40),
        },
    }

    # For fresh foods if no category matched
    GENERIC_RANGE = (50, 700)

    # Packaged foods
    PACKAGED_RANGES = {
        "calories": (60, 200),
        "protein_grams": (0, 5),
        "carb_grams": (8, 30),
        "fat_grams": (1, 12),
    }

    # Public API
    @classmethod
    def normalize_items(cls, items: List[Dict[str, Any]], food_type: str = "fresh") -> List[Dict[str, Any]]:
        """
        food_type comes from Gemini prompt:
        - packaged
        - fresh
        """
        if food_type not in ("packaged", "fresh"):
            food_type = "fresh"

        return [cls._normalize_item(item, food_type) for item in items]

    # Normalize Single Item
    @classmethod
    def _normalize_item(cls, item: Dict[str, Any], food_type: str) -> Dict[str, Any]:
        name = str(item.get("food_name", "")).lower()

        # If missing calories → invalid item
        if item.get("calories") is None:
            item["confidence_level"] = "Low"
            return item

        # Decide normalization method
        if food_type == "packaged":
            rule = cls.PACKAGED_RANGES
        else:
            rule = cls._match_category(name)

        for key in list(item.keys()):
            if cls._is_nutrition_key(key):
                item[key] = cls._normalize_value(key, item[key], rule, food_type)

        return item

    # Category Detection (Fresh Foods Only)
    @classmethod
    def _match_category(cls, name: str) -> Dict[str, tuple]:
        for category, rules in cls.CATEGORY_RULES.items():
            if category in name:
                return rules
        return {"calories": cls.GENERIC_RANGE}

    # Nutrition Logic
    @staticmethod
    def _is_nutrition_key(key: str) -> bool:
        return key in {"calories", "protein_grams", "carb_grams", "fat_grams"}

    @classmethod
    def _normalize_value(cls, key: str, value: Any, rule: Dict[str, tuple], food_type: str) -> Optional[float]:
        num = cls._to_float(value)
        if num is None:
            return None

        # Packaged → always clamp to packaged limits
        if food_type == "packaged":
            min_val, max_val = cls.PACKAGED_RANGES.get(key, (0, 500))
            return cls._clamp(num, min_val, max_val)

        # Fresh → category rules
        if key in rule:
            min_val, max_val = rule[key]
            return cls._clamp(num, min_val, max_val)

        # Fresh fallback for calories
        if key == "calories":
            min_val, max_val = cls.GENERIC_RANGE
            return cls._clamp(num, min_val, max_val)

        return num

    # Safe Numeric Handling
    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            v = value.strip().replace(",", "")
            if not v:
                return None
            try:
                return float(v)
            except ValueError:
                return None

        return None

    # Clamp Helper
    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        return max(min(value, max_val), min_val)
