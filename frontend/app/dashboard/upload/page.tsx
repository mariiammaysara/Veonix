"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import UploadBox from "@/components/upload-box";
import ResultsDisplay from "@/components/results-display";
import LoadingScreen from "@/components/LoadingScreen";
import { analyzeImage, confirmMeal, ApiError } from "@/lib/api";
import { getUserFriendlyError } from "@/lib/error-utils";
import type { MealResult } from "@/lib/types";

/**
 * Veonix — Upload & Analysis Page
 * 
 * Refined layout with a compact upload box, nutritional tips,
 * and improved spacing.
 */
export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MealResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLowConfidence, setIsLowConfidence] = useState(false);

  // HITL States
  const [isPending, setIsPending] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [pendingAnalysis, setPendingAnalysis] = useState<MealResult | null>(null);
  
  // Editable macro form fields
  const [editedFoodName, setEditedFoodName] = useState("");
  const [editedWeight, setEditedWeight] = useState(0);
  const [editedCalories, setEditedCalories] = useState(0);
  const [editedProtein, setEditedProtein] = useState(0);
  const [editedCarbs, setEditedCarbs] = useState(0);
  const [editedFat, setEditedFat] = useState(0);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (result || isPending) {
        setResult(null);
        setFile(null);
        setPreview(null);
        setIsPending(false);
        setPendingAnalysis(null);
      } else {
        router.push("/");
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [result, isPending, router]);

  const handleFile = (f: File | null) => {
    setResult(null);
    setError(null);
    setIsLowConfidence(false);
    setIsPending(false);
    setPendingAnalysis(null);
    setFile(f);
    if (f) {
      const url = URL.createObjectURL(f);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreview(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setIsLowConfidence(false);
    try {
      const response = await analyzeImage(file);
      if (response.status === "pending_confirmation") {
        setThreadId(response.thread_id || null);
        setPendingAnalysis(response.analysis);
        setIsPending(true);
        // Pre-fill fields for user review/edit
        setEditedFoodName(response.analysis.food_name);
        setEditedWeight(response.analysis.weight_grams);
        setEditedCalories(response.analysis.nutrition.calories);
        setEditedProtein(response.analysis.nutrition.protein);
        setEditedCarbs(response.analysis.nutrition.carbs);
        setEditedFat(response.analysis.nutrition.fat);
      } else {
        setResult(response.analysis);
      }
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "LOW_CONFIDENCE") {
        setIsLowConfidence(true);
        setFile(null);
        setPreview(null);
      } else {
        setError(getUserFriendlyError(err).message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (action: "approve" | "reject") => {
    if (!threadId || !pendingAnalysis) return;
    setLoading(true);
    setError(null);
    try {
      if (action === "reject") {
        await confirmMeal(threadId, "reject");
        setFile(null);
        setPreview(null);
        setResult(null);
        setIsPending(false);
        setPendingAnalysis(null);
      } else {
        const edits = {
          food_name: editedFoodName,
          weight_grams: Number(editedWeight),
          calories: Number(editedCalories),
          protein: Number(editedProtein),
          carbs: Number(editedCarbs),
          fat: Number(editedFat)
        };
        await confirmMeal(threadId, "approve", edits);

        const finalMeal: MealResult = {
          ...pendingAnalysis,
          food_name: editedFoodName,
          weight_grams: Number(editedWeight),
          nutrition: {
            ...pendingAnalysis.nutrition,
            calories: Number(editedCalories),
            protein: Number(editedProtein),
            carbs: Number(editedCarbs),
            fat: Number(editedFat)
          }
        };
        setResult(finalMeal);
        setIsPending(false);
        setPendingAnalysis(null);
      }
    } catch (err: unknown) {
      setError(getUserFriendlyError(err).message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingScreen />;

  return (
    <div style={{ minHeight: "100vh", background: "#020617", color: "#f1f5f9", display: "flex", flexDirection: "column", position: "relative", overflowX: "hidden" }}>
      <div className="g1" />

      {/* Shared Navbar */}
      <Navbar />

      {/* Main content */}
      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "80px 20px 40px", gap: "32px",
        position: "relative", zIndex: 1
      }}>

        {result ? (
          <>
            <div className="anim-scale-in" style={{ width: "100%", display: "flex", justifyContent: "center" }}>
              <ResultsDisplay data={result} preview={preview} />
            </div>
            <button
              onClick={() => { setFile(null); setPreview(null); setResult(null); setError(null); }}
              style={{
                padding: "10px 24px",
                background: "rgba(15,23,42,0.6)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "99px", color: "#94a3b8",
                fontSize: "13px", fontWeight: 600, cursor: "pointer",
                display: "flex", alignItems: "center", gap: "8px",
                transition: "all .2s",
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
              }}
              className="hover:scale-105 hover:border-emerald-500/30 hover:text-white"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Analyze another meal
            </button>
          </>
        ) : isPending ? (
          <div className="anim-scale-in" style={{
            width: "100%", maxWidth: "520px",
            background: "rgba(10,18,38,0.6)",
            border: "1px solid rgba(255,255,255,0.06)",
            borderRadius: "24px", padding: "28px 24px",
            display: "flex", flexDirection: "column", gap: "20px",
            backdropFilter: "blur(12px)",
            boxShadow: "0 20px 40px rgba(0,0,0,0.3)"
          }}>
            <div style={{ textAlign: "center", marginBottom: "4px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#f1f5f9" }}>
                Confirm Recommendation Details
              </h2>
              <p style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
                Review and customize the identified nutrition details before saving.
              </p>
            </div>

            {/* Allergies Warning Banner if present */}
            {pendingAnalysis?.allergies_warning && (
              <div style={{
                padding: "12px 16px", background: "rgba(245, 158, 11, 0.08)",
                border: "1px solid rgba(245, 158, 11, 0.2)", borderRadius: "12px",
                color: "#fbbf24", fontSize: "13px", display: "flex", alignItems: "center", gap: "10px",
                lineHeight: 1.5
              }}>
                <span style={{ fontSize: "16px" }}>⚠️</span>
                <span>{pendingAnalysis.allergies_warning}</span>
              </div>
            )}

            {/* Editable Fields Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div style={{ gridColumn: "span 2", display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>Food Name</label>
                <input
                  type="text"
                  value={editedFoodName}
                  onChange={(e) => setEditedFoodName(e.target.value)}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none"
                  }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>Weight (grams)</label>
                <input
                  type="number"
                  value={editedWeight}
                  onChange={(e) => setEditedWeight(Number(e.target.value))}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none"
                  }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>Calories (kcal)</label>
                <input
                  type="number"
                  value={editedCalories}
                  onChange={(e) => setEditedCalories(Number(e.target.value))}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none"
                  }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>Protein (g)</label>
                <input
                  type="number"
                  value={editedProtein}
                  onChange={(e) => setEditedProtein(Number(e.target.value))}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none"
                  }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>Carbs (g)</label>
                <input
                  type="number"
                  value={editedCarbs}
                  onChange={(e) => setEditedCarbs(Number(e.target.value))}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none"
                  }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>Fat (g)</label>
                <input
                  type="number"
                  value={editedFat}
                  onChange={(e) => setEditedFat(Number(e.target.value))}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none"
                  }}
                />
              </div>
            </div>

            {error && (
              <div style={{
                padding: "10px 14px", background: "rgba(239, 68, 68, 0.05)",
                border: "1px solid rgba(239, 68, 68, 0.15)", borderRadius: "12px",
                color: "#f87171", fontSize: "12px", textAlign: "center"
              }}>
                {error}
              </div>
            )}

            {/* Form actions */}
            <div style={{ display: "flex", gap: "12px", marginTop: "8px" }}>
              <button
                type="button"
                onClick={() => handleConfirm("reject")}
                style={{
                  flex: 1, padding: "12px", background: "rgba(239, 68, 68, 0.08)",
                  border: "1px solid rgba(239, 68, 68, 0.15)", borderRadius: "12px",
                  color: "#f87171", fontSize: "14px", fontWeight: 700, cursor: "pointer",
                  transition: "background .2s"
                }}
                className="hover:bg-red-500/10"
              >
                Discard
              </button>
              <button
                type="button"
                onClick={() => handleConfirm("approve")}
                style={{
                  flex: 2, padding: "12px", background: "#10b981",
                  border: "none", borderRadius: "12px",
                  color: "#020617", fontSize: "14px", fontWeight: 700, cursor: "pointer",
                  boxShadow: "0 4px 14px rgba(16, 185, 129, 0.2)",
                  transition: "opacity .2s"
                }}
                className="hover:opacity-90"
              >
                Approve & Save
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="anim-fade-up" style={{ textAlign: "center" }}>
              <h1 style={{ fontSize: "clamp(22px, 3vw, 28px)", fontWeight: 800, color: "#f1f5f9", marginBottom: "8px" }}>
                Analyze Your Meal
              </h1>
              <p style={{ fontSize: "14px", color: "#64748b", maxWidth: "340px", lineHeight: 1.6, margin: "0 auto" }}>
                Upload a clear photo to get instant, accurate nutritional insights.
              </p>
            </div>

            {/* Upload box container */}
            <div className="anim-scale-in delay-1" style={{ width: "100%", display: "flex", justifyContent: "center" }}>
              <UploadBox onFile={handleFile} preview={preview} onAnalyze={handleAnalyze} isLowConfidence={isLowConfidence} />
            </div>

            {/* Tips Section */}
            {!preview && (
              <div className="anim-fade-up delay-2" style={{
                display: "flex", flexWrap: "wrap", gap: "10px", width: "100%",
                maxWidth: "480px", justifyContent: "center"
              }}>
                {[
                  { icon: <path d="M12 2v2m0 16v2m10-10h-2M4 10H2m15.36-5.36l-1.42 1.42M6.05 17.95l-1.42 1.42m12.73 0l-1.42-1.42M6.05 6.05L4.63 4.63" />, text: "Use good lighting for accuracy" },
                  { icon: <path d="M3 6l9-4 9 4v11a2 2 0 01-2 2H5a2 2 0 01-2-2V6z" />, text: "Single dish per photo" },
                ].map(({ icon, text }, i) => (
                  <div key={i} style={{
                    flex: "1 1 200px", background: "rgba(15,23,42,0.3)",
                    border: "1px solid rgba(255,255,255,0.04)",
                    borderRadius: "12px", padding: "10px 14px",
                    display: "flex", alignItems: "center", gap: "10px",
                  }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                      <circle cx="12" cy="12" r="10" />
                      {icon}
                    </svg>
                    <span style={{ fontSize: "11px", color: "#64748b", fontWeight: 500 }}>{text}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="anim-scale-in" style={{
                width: "100%", maxWidth: "480px", padding: "14px",
                background: "rgba(239, 68, 68, 0.05)",
                border: "1px solid rgba(239, 68, 68, 0.15)",
                borderRadius: "12px", color: "#f87171",
                fontSize: "12px", textAlign: "center", fontWeight: 500
              }}>
                {error}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}