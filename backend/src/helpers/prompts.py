"""
Module: prompts
Layer:  Helpers

Centralized prompt management.
Contains all LLM system and user instructions to avoid inlining in provider code.
Uses explicit JSON schemas to minimize hallucinations and parsing failures.

Author: Mariam Maysara
"""

# ── Base Vision Prompt ────────────────────────────────────────────────────────
# Consolidated prompt for Gemini Vision.
# Requests food identity and nutrition in a single multimodal pass to reduce latency.
GEMINI_PROMPT = """
Analyze this food image and return a JSON object with food identification AND nutrition data.

To reduce portion estimation errors, you MUST perform step-by-step chain-of-thought reasoning inside the JSON object's "reasoning" field BEFORE committing to a weight estimate. Follow these guidelines:
1. Identify all visible food items in the image.
2. Detect portion size cues and reference objects for scale (e.g., plate size, cup size, utensils, hands, packaging, or table texture). If no size reference object is visible, you MUST honestly lower your "confidence" score (e.g. to 0.40 - 0.60) and note the lack of reference in the reasoning field.
3. Internally estimate a plausible low and high range for the portion weight (in grams) based on the scale cues, then select a realistic single point estimate within that range.
4. Scale all total nutritional values (calories, protein, carbs, fat, fiber, sodium) precisely to the estimated weight, keeping base per_100g values accurate.

Ensure the "reasoning" field is the first field in the returned JSON object.

---

### FEW-SHOT EXAMPLES

#### Example 1: Single item with clear scale reference (Red Apple next to a fork)
- Context: A medium red apple is sitting on a white plate next to a standard metal dinner fork.
- Expected JSON Output:
{
  "reasoning": "1. Visible items: One whole red apple. 2. Scale references: A standard dining plate (approx. 25cm) and a standard metal fork (approx. 20cm) are visible next to the apple, providing clear scale. 3. Portions: The apple is average-sized relative to the fork. Plausible weight range: 150g - 200g. Point estimate: 175g. 4. Confidence: High (0.95) due to clear utensil and plate size references. 5. Nutrition: Base apple per_100g is 52 kcal. Total calories scaled to 175g is 91 kcal.",
  "food_name": "Red Apple",
  "confidence": 0.95,
  "ingredients": ["apple"],
  "estimated_weight_grams": 175,
  "meal_type": "snack",
  "cuisine": "fruit",
  "preparation_method": "raw",
  "nutrition": {
    "calories": 91.0,
    "protein": 0.45,
    "carbs": 24.5,
    "fat": 0.35,
    "fiber": 4.2,
    "sodium": 1.75,
    "per_100g": {
      "calories": 52.0,
      "protein": 0.26,
      "carbs": 14.0,
      "fat": 0.2,
      "fiber": 2.4,
      "sodium": 1.0
    }
  }
}

#### Example 2: Mixed dish with overlapping ingredients (Chicken Salad Bowl with a hand for scale)
- Context: A salad bowl containing lettuce, diced tomatoes, grilled chicken pieces, and olive oil dressing. A human hand is holding the bowl.
- Expected JSON Output:
{
  "reasoning": "1. Visible items: Lettuce greens, tomatoes, cubed grilled chicken breast, and olive oil dressing. 2. Scale references: A human hand holding the bowl provides a reliable size context. The bowl diameter is approx. 18cm. 3. Portions: Lettuce (approx. 90g), tomato (approx. 60g), chicken (approx. 100g), olive oil (approx. 10g). Plausible weight range: 240g - 280g. Point estimate: 260g. 4. Confidence: High (0.90) as the hand and bowl diameter provide good scale indicators. 5. Nutrition: Scaled using composite ingredient macros to 260g total weight.",
  "food_name": "Grilled Chicken Salad",
  "confidence": 0.90,
  "ingredients": ["lettuce", "tomato", "chicken breast", "olive oil"],
  "estimated_weight_grams": 260,
  "meal_type": "lunch",
  "cuisine": "American",
  "preparation_method": "mixed",
  "nutrition": {
    "calories": 302.0,
    "protein": 32.2,
    "carbs": 4.8,
    "fat": 17.2,
    "fiber": 1.8,
    "sodium": 195.0,
    "per_100g": {
      "calories": 116.15,
      "protein": 12.38,
      "carbs": 1.85,
      "fat": 6.62,
      "fiber": 0.69,
      "sodium": 75.0
    }
  }
}

#### Example 3: Single item with NO visible scale reference (Chocolate Chip Cookie close-up)
- Context: A close-up photograph of a chocolate chip cookie on a neutral table. No plates, utensils, hands, or other recognizable objects are visible in the shot.
- Expected JSON Output:
{
  "reasoning": "1. Visible items: One chocolate chip cookie. 2. Scale references: None. No plates, utensils, hands, or other standard items are visible to establish scale. Table texture is plain. 3. Portions: Lack of reference makes size estimation highly uncertain. A cookie can range from a small 25g snack to a large 80g bakery style cookie. Without cues, we estimate a moderate size. Plausible range: 30g - 60g. Point estimate: 45g. 4. Confidence: Low (0.50) due to complete absence of size/scale references. 5. Nutrition: Scaled standard cookie macros to 45g.",
  "food_name": "Chocolate Chip Cookie",
  "confidence": 0.50,
  "ingredients": ["flour", "sugar", "butter", "chocolate chips"],
  "estimated_weight_grams": 45,
  "meal_type": "snack",
  "cuisine": "American",
  "preparation_method": "baked",
  "nutrition": {
    "calories": 220.0,
    "protein": 2.2,
    "carbs": 29.2,
    "fat": 11.2,
    "fiber": 1.1,
    "sodium": 130.0,
    "per_100g": {
      "calories": 489.0,
      "protein": 4.9,
      "carbs": 64.9,
      "fat": 24.9,
      "fiber": 2.4,
      "sodium": 289.0
    }
  }
}

---

Return ONLY the following JSON structure (with "reasoning" as the first key), no markdown formatting outside the JSON, no plain text explanation:

{
  "reasoning": "<your step-by-step reasoning details>",
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
"""
