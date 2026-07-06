/**
 * Veonix — TypeScript Interfaces
 * lib/types.ts
 *
 * Single source of truth for all data shapes.
 * Never use `any` — always import from here.
 */

export interface NutritionData {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
    sodium: number;
    per_100g: {
        calories: number;
        protein: number;
        carbs: number;
        fat: number;
        fiber: number;
        sodium: number;
    };
    source: string;
    is_estimated: boolean;
}

export interface MealResult {
    food_name: string;
    confidence: number;
    ingredients: string[];
    weight_grams: number;
    meal_type: string;
    cuisine: string;
    nutrition: NutritionData;
}

export interface MealHistoryItem {
    id: number;
    food_name: string;
    meal_type: string | null;
    weight_grams: number;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    created_at: string;
}

export interface MealHistoryResponse {
    total: number;
    meals: MealHistoryItem[];
}

export interface StatsResponse {
    total_meals: number;
    avg_calories: number;
    avg_protein: number;
    avg_carbs: number;
    avg_fat: number;
}

export interface ApiErrorResponse {
    status: "error";
    error: {
        code: string;
        message: string;
        detail: string;
    };
}

export interface UserProfile {
    user_id: string;
    dietary_goal: string;
    allergies: string[];
}

