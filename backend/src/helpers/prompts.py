"""
Module: prompts
Layer:  Helpers

Centralized prompt management.
Contains all LLM system and user instructions to avoid inlining in provider code.
Uses explicit JSON schemas to minimize hallucinations and parsing failures.

Author: Mariam Maysara
"""

# Consolidated prompt for Gemini Vision.
# Requests food identity and nutrition in a single multimodal pass to reduce latency.
GEMINI_PROMPT = """
Analyze this food image and return a JSON object with food identification AND nutrition data.

Return ONLY this JSON structure, no markdown, no explanation:

{
  "food_name": "<name of the food you see>",
  "confidence": <0.0 to 1.0>,
  "ingredients": ["<ingredient1>", "<ingredient2>"],
  "estimated_weight_grams": <total weight as integer>,
  "meal_type": "<breakfast or lunch or dinner or snack or drink or dessert>",
  "cuisine": "<cuisine type>",
  "preparation_method": "<raw or grilled or fried or baked or boiled or steamed or mixed or unknown>",
  "nutrition": {
    "calories": <total kcal for the estimated weight>,
    "protein": <grams>,
    "carbs": <grams>,
    "fat": <grams>,
    "fiber": <grams>,
    "sodium": <milligrams>,
    "per_100g": {
      "calories": <kcal per 100g>,
      "protein": <g per 100g>,
      "carbs": <g per 100g>,
      "fat": <g per 100g>,
      "fiber": <g per 100g>,
      "sodium": <mg per 100g>
    }
  }
}

IMPORTANT:
- Nutrition values must be accurate and realistic
- Scale total nutrition to the estimated_weight_grams
- per_100g values are the base values before scaling
- Return ONLY the JSON object
"""
