"use client";

import React from "react";
import type { BatchResult, BatchMealResult } from "@/lib/types";

interface Props {
  result: BatchResult;
  onReset: () => void;
}

const MACRO_COLOR = {
  calories: "#f59e0b",
  protein: "#10b981",
  carbs: "#3b82f6",
  fat: "#f43f5e",
};

function MacroChip({
  label,
  value,
  unit,
  color,
}: {
  label: string;
  value: number;
  unit: string;
  color: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "2px",
        padding: "10px 16px",
        borderRadius: "12px",
        background: `${color}10`,
        border: `1px solid ${color}25`,
        flex: 1,
        minWidth: "72px",
      }}
    >
      <span style={{ fontSize: "18px", fontWeight: 700, color }}>{value.toFixed(0)}</span>
      <span style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em" }}>
        {unit}
      </span>
      <span style={{ fontSize: "11px", color: "#475569", marginTop: "1px" }}>{label}</span>
    </div>
  );
}

function MealRow({ meal, index }: { meal: BatchMealResult | null; index: number }) {
  if (!meal) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "12px 16px",
          borderRadius: "12px",
          background: "rgba(239,68,68,0.04)",
          border: "1px solid rgba(239,68,68,0.1)",
        }}
      >
        <div
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            background: "rgba(239,68,68,0.08)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </div>
        <div>
          <p style={{ fontSize: "14px", color: "#ef4444", fontWeight: 500 }}>Image {index + 1} — Analysis failed</p>
          <p style={{ fontSize: "12px", color: "#64748b", marginTop: "2px" }}>Low confidence or unrecognized food</p>
        </div>
      </div>
    );
  }

  const mealTypeColor: Record<string, string> = {
    breakfast: "#f59e0b",
    lunch: "#10b981",
    dinner: "#6366f1",
    snack: "#f43f5e",
    drink: "#3b82f6",
    dessert: "#ec4899",
  };
  const badgeColor = mealTypeColor[meal.meal_type?.toLowerCase()] ?? "#64748b";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        padding: "12px 14px",
        borderRadius: "12px",
        background: "rgba(255,255,255,0.02)",
        border: "1px solid rgba(255,255,255,0.05)",
        transition: "background .15s",
      }}
    >
      {/* Index badge */}
      <div
        style={{
          width: "30px",
          height: "30px",
          borderRadius: "8px",
          background: "rgba(16,185,129,0.1)",
          border: "1px solid rgba(16,185,129,0.2)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "12px",
          fontWeight: 700,
          color: "#10b981",
          flexShrink: 0,
        }}
      >
        {index + 1}
      </div>

      {/* Name + type */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ fontSize: "14px", fontWeight: 600, color: "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {meal.food_name}
        </p>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "3px" }}>
          {meal.meal_type && (
            <span
              style={{
                fontSize: "10px",
                fontWeight: 600,
                color: badgeColor,
                background: `${badgeColor}12`,
                border: `1px solid ${badgeColor}25`,
                borderRadius: "5px",
                padding: "1px 6px",
                textTransform: "capitalize",
              }}
            >
              {meal.meal_type}
            </span>
          )}
          <span style={{ fontSize: "11px", color: "#475569" }}>
            {meal.confidence ? `${(meal.confidence * 100).toFixed(0)}% confidence` : ""}
          </span>
        </div>
        {meal.allergies_warning && (
          <p style={{ fontSize: "11px", color: "#fbbf24", marginTop: "3px" }}>{meal.allergies_warning}</p>
        )}
      </div>

      {/* Calorie badge */}
      <div style={{ textAlign: "right", flexShrink: 0 }}>
        <p style={{ fontSize: "16px", fontWeight: 700, color: "#f59e0b" }}>
          {meal.nutrition.calories.toFixed(0)}
        </p>
        <p style={{ fontSize: "10px", color: "#64748b" }}>kcal</p>
      </div>
    </div>
  );
}

export default function BatchResultsDisplay({ result, onReset }: Props) {
  const { meals, aggregate } = result;
  const successCount = meals.filter(Boolean).length;

  return (
    <div
      className="anim-scale-in"
      style={{
        width: "100%",
        maxWidth: "min(540px, 100%)",
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: 700, color: "#e2e8f0", margin: 0 }}>
            Batch Analysis
          </h2>
          <p style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            {successCount} of {meals.length} meals analyzed
          </p>
        </div>
        <button
          onClick={onReset}
          style={{
            padding: "8px 14px",
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: "10px",
            color: "#64748b",
            fontSize: "12px",
            fontWeight: 500,
            cursor: "pointer",
          }}
        >
          Analyze again
        </button>
      </div>

      {/* Aggregate totals strip */}
      <div
        style={{
          padding: "16px",
          borderRadius: "16px",
          background: "rgba(10,18,38,0.7)",
          border: "1px solid rgba(255,255,255,0.06)",
          backdropFilter: "blur(12px)",
        }}
      >
        <p style={{ fontSize: "11px", color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "12px" }}>
          Daily Totals
        </p>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          <MacroChip label="Calories" value={aggregate.total_calories} unit="kcal" color={MACRO_COLOR.calories} />
          <MacroChip label="Protein" value={aggregate.total_protein} unit="g" color={MACRO_COLOR.protein} />
          <MacroChip label="Carbs" value={aggregate.total_carbs} unit="g" color={MACRO_COLOR.carbs} />
          <MacroChip label="Fat" value={aggregate.total_fat} unit="g" color={MACRO_COLOR.fat} />
        </div>
      </div>

      {/* Per-meal list */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "8px",
          padding: "14px",
          borderRadius: "16px",
          background: "rgba(10,18,38,0.5)",
          border: "1px solid rgba(255,255,255,0.05)",
        }}
      >
        <p style={{ fontSize: "11px", color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "4px" }}>
          Meals Breakdown
        </p>
        {meals.map((meal, i) => (
          <MealRow key={i} meal={meal} index={i} />
        ))}
      </div>
    </div>
  );
}
