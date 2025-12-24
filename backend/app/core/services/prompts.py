FOOD_ANALYSIS_PROMPT = """
Identify the food and calculate calories for the TOTAL visible portion.

STRICT CALCULATION RULES:
1. First, estimate the total weight in grams based on standard sizes (e.g., a typical whole roasted chicken is 1000g-1200g).
2. Use standard nutritional values (e.g., ~160-200 kcal per 100g for roasted chicken).
3. DO NOT inflate numbers based on visual textures. Keep the estimate realistic for a single meal/dish.
4. Total calories should be a realistic sum of the identified items.

Return JSON:
{
  "food_name": "Accurate name",
  "calories": total_integer,
  "macros": {"protein": int, "carbs": int, "fat": int}
}
"""