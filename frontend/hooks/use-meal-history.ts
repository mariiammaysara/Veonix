/**
 * Veonix — Meal History Hook
 * hooks/use-meal-history.ts
 *
 * Fetches meal history from the backend DB.
 * Handles loading, error, and delete states.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { getMealHistory, deleteMeal } from "@/lib/api";
import type { MealHistoryItem } from "@/lib/types";

export function useMealHistory() {
    const [meals, setMeals] = useState<MealHistoryItem[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchHistory = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getMealHistory();
            setMeals(data.meals);
            setTotal(data.total);
        } catch (err) {
            setError("Failed to load meal history.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    const handleDelete = useCallback(async (id: number) => {
        try {
            await deleteMeal(id);
            setMeals((prev) => prev.filter((m) => m.id !== id));
            setTotal((prev) => prev - 1);
        } catch {
            setError("Failed to delete meal. Please try again.");
        }
    }, []);

    return { meals, total, loading, error, refetch: fetchHistory, handleDelete };
}
