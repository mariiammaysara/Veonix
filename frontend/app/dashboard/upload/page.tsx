"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import UploadBox from "@/components/upload-box";
import ResultsDisplay from "@/components/results-display";
import BatchResultsDisplay from "@/components/batch-results-display";
import LoadingScreen from "@/components/LoadingScreen";
import { analyzeImageStream, analyzeBatch, confirmMeal, ApiError } from "@/lib/api";
import { getUserFriendlyError } from "@/lib/error-utils";
import type { MealResult, StreamEvent, BatchResult } from "@/lib/types";

// ── Step config for cleaner progress UI ─────────────────────────────────────

const STEP_ORDER = [
  "start",
  "profile",
  "vision_start",
  "vision_done",
  "allergy_check",
  "saving",
  "pending_confirmation",
  "done",
];

const STEP_LABELS: Record<string, string> = {
  start: "Compressing image",
  profile: "Loading your profile",
  vision_start: "Identifying food",
  vision_done: "Food identified",
  allergy_check: "Checking allergens",
  saving: "Preparing result",
  pending_confirmation: "Ready for review",
  done: "Analysis complete",
  error: "Something went wrong",
  low_confidence: "Low confidence — retake photo",
};

// ── Clean progress stepper ───────────────────────────────────────────────────

function ProgressStepper({ events }: { events: StreamEvent[] }) {
  if (events.length === 0) return null;

  const seenEvents = events.map((e) => e.event as string);
  const hasError = seenEvents.includes("error");
  const lastEvent = events[events.length - 1];

  if (hasError) {
    return (
      <div className="anim-scale-in" style={{
        width: "100%", maxWidth: "440px", margin: "0 auto",
        padding: "14px 18px",
        borderRadius: "14px",
        background: "rgba(239,68,68,0.06)",
        border: "1px solid rgba(239,68,68,0.14)",
        display: "flex", alignItems: "center", gap: "10px",
      }}>
        <span style={{
          width: "8px", height: "8px", borderRadius: "50%",
          background: "#f87171", flexShrink: 0,
          boxShadow: "0 0 6px rgba(248,113,113,0.5)",
        }} />
        <span style={{ fontSize: "13px", color: "#f87171", fontWeight: 500 }}>
          {lastEvent.message}
        </span>
      </div>
    );
  }

  const isDone = seenEvents.includes("done") || seenEvents.includes("pending_confirmation");
  const steps = STEP_ORDER.filter((s) => !["pending_confirmation", "done"].includes(s));
  const activeIdx = (() => {
    for (let i = steps.length - 1; i >= 0; i--) {
      if (seenEvents.includes(steps[i])) return i;
    }
    return -1;
  })();

  return (
    <div className="anim-scale-in" style={{
      width: "100%", maxWidth: "440px", margin: "0 auto",
      padding: "20px 24px",
      borderRadius: "16px",
      background: "rgba(10,18,38,0.5)",
      border: "1px solid rgba(255,255,255,0.05)",
      backdropFilter: "blur(10px)",
    }}>
      {/* Progress bar */}
      <div style={{
        height: "2px",
        borderRadius: "2px",
        background: "rgba(255,255,255,0.05)",
        marginBottom: "16px",
        overflow: "hidden",
      }}>
        <div style={{
          height: "100%",
          borderRadius: "2px",
          background: isDone
            ? "linear-gradient(90deg,#10b981,#34d399)"
            : "linear-gradient(90deg,#10b981,#34d399)",
          width: isDone ? "100%" : `${Math.round(((activeIdx + 1) / steps.length) * 100)}%`,
          transition: "width 0.5s cubic-bezier(.16,1,.3,1)",
          boxShadow: "0 0 8px rgba(16,185,129,0.4)",
        }} />
      </div>

      {/* Current step label */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        {!isDone ? (
          <span className="step-dot-active" style={{
            width: "8px", height: "8px", borderRadius: "50%",
            background: "#10b981", flexShrink: 0,
            display: "inline-block",
          }} />
        ) : (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        )}
        <span style={{
          fontSize: "13px",
          color: isDone ? "#34d399" : "#94a3b8",
          fontWeight: isDone ? 600 : 400,
        }}>
          {isDone
            ? (seenEvents.includes("pending_confirmation") ? "Ready for review" : "Analysis complete")
            : (STEP_LABELS[events[events.length - 1]?.event] ?? "Processing…")}
        </span>
      </div>

      {/* Vision result preview */}
      {lastEvent?.food_name && lastEvent?.confidence !== undefined && (
        <div style={{
          marginTop: "10px",
          paddingTop: "10px",
          borderTop: "1px solid rgba(255,255,255,0.04)",
          display: "flex", alignItems: "center", gap: "8px",
        }}>
          <span style={{ fontSize: "12px", color: "#64748b" }}>Detected:</span>
          <span style={{ fontSize: "13px", color: "#f1f5f9", fontWeight: 600 }}>
            {lastEvent.food_name}
          </span>
          <span style={{
            marginLeft: "auto",
            fontSize: "11px", fontWeight: 700,
            color: lastEvent.confidence >= 0.8 ? "#34d399" : lastEvent.confidence >= 0.6 ? "#fbbf24" : "#f87171",
            background: lastEvent.confidence >= 0.8 ? "rgba(52,211,153,0.08)" : "rgba(251,191,36,0.08)",
            padding: "2px 8px", borderRadius: "99px",
            border: `1px solid ${lastEvent.confidence >= 0.8 ? "rgba(52,211,153,0.15)" : "rgba(251,191,36,0.15)"}`,
          }}>
            {Math.round(lastEvent.confidence * 100)}%
          </span>
        </div>
      )}
    </div>
  );
}

// ── Editable field component ─────────────────────────────────────────────────

function EditField({
  label, value, onChange, type = "text"
}: {
  label: string;
  value: string | number;
  onChange: (v: string) => void;
  type?: string;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
      <label style={{
        fontSize: "10px", fontWeight: 700,
        color: "#475569", textTransform: "uppercase", letterSpacing: "0.08em",
      }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          padding: "10px 12px",
          background: "rgba(15,23,42,0.6)",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: "10px",
          color: "#f1f5f9",
          fontSize: "14px",
          outline: "none",
          transition: "border-color 0.2s",
          width: "100%",
        }}
        onFocus={(e) => (e.target.style.borderColor = "rgba(16,185,129,0.35)")}
        onBlur={(e) => (e.target.style.borderColor = "rgba(255,255,255,0.07)")}
      />
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────

export default function UploadPage() {
  const router = useRouter();

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MealResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLowConfidence, setIsLowConfidence] = useState(false);

  const [streamEvents, setStreamEvents] = useState<StreamEvent[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [batchPreviews, setBatchPreviews] = useState<string[]>([]);
  const [batchResult, setBatchResult] = useState<BatchResult | null>(null);
  const [batchLoading, setBatchLoading] = useState(false);

  const [isPending, setIsPending] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [pendingAnalysis, setPendingAnalysis] = useState<MealResult | null>(null);

  const [editedFoodName, setEditedFoodName] = useState("");
  const [editedWeight, setEditedWeight] = useState(0);
  const [editedCalories, setEditedCalories] = useState(0);
  const [editedProtein, setEditedProtein] = useState(0);
  const [editedCarbs, setEditedCarbs] = useState(0);
  const [editedFat, setEditedFat] = useState(0);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (result || isPending || batchResult) resetAll();
      else router.push("/");
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [result, isPending, batchResult, router]);

  const resetAll = useCallback(() => {
    setFile(null); setPreview(null); setResult(null);
    setError(null); setIsLowConfidence(false);
    setStreamEvents([]); setIsStreaming(false);
    setBatchFiles([]); setBatchPreviews([]); setBatchResult(null);
    setIsPending(false); setPendingAnalysis(null); setThreadId(null);
  }, []);

  const handleFile = (f: File | null) => {
    resetAll(); setFile(f);
    if (f) setPreview(URL.createObjectURL(f));
  };

  const handleFiles = useCallback((files: File[]) => {
    resetAll();
    setBatchFiles(files);
    setBatchPreviews(files.map((f) => URL.createObjectURL(f)));
  }, [resetAll]);

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true); setError(null);
    setIsLowConfidence(false); setStreamEvents([]); setIsStreaming(true);

    try {
      let finalResult: MealResult | null = null;
      let pendingThreadId: string | null = null;
      let pendingMeal: MealResult | null = null;

      await analyzeImageStream(file, (ev: StreamEvent) => {
        setStreamEvents((prev) => [...prev, ev]);
        if (ev.event === "done" && ev.result) finalResult = ev.result as unknown as MealResult;
        if (ev.event === "pending_confirmation" && ev.result) {
          pendingThreadId = ev.thread_id ?? null;
          pendingMeal = ev.result as unknown as MealResult;
        }
        if (ev.event === "low_confidence") setIsLowConfidence(true);
      });

      if (pendingThreadId && pendingMeal) {
        const meal = pendingMeal as MealResult;
        setThreadId(pendingThreadId); setPendingAnalysis(meal); setIsPending(true);
        setEditedFoodName(meal.food_name); setEditedWeight(meal.weight_grams);
        setEditedCalories(meal.nutrition.calories); setEditedProtein(meal.nutrition.protein);
        setEditedCarbs(meal.nutrition.carbs); setEditedFat(meal.nutrition.fat);
      } else if (finalResult) {
        setResult(finalResult);
      } else if (!isLowConfidence) {
        setError("No result received. Please try again.");
      }
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "LOW_CONFIDENCE") {
        setIsLowConfidence(true); setFile(null); setPreview(null);
      } else {
        setError(getUserFriendlyError(err).message);
      }
    } finally {
      setLoading(false); setIsStreaming(false);
    }
  };

  const handleBatchAnalyze = async () => {
    if (batchFiles.length === 0) return;
    setBatchLoading(true); setError(null);
    try {
      setBatchResult(await analyzeBatch(batchFiles));
    } catch (err: unknown) {
      setError(getUserFriendlyError(err).message);
    } finally {
      setBatchLoading(false);
    }
  };

  const handleConfirm = async (action: "approve" | "reject") => {
    if (!threadId || !pendingAnalysis) return;
    setLoading(true); setError(null);
    try {
      if (action === "reject") {
        await confirmMeal(threadId, "reject");
        resetAll();
      } else {
        const edits = {
          food_name: editedFoodName,
          weight_grams: Number(editedWeight),
          calories: Number(editedCalories),
          protein: Number(editedProtein),
          carbs: Number(editedCarbs),
          fat: Number(editedFat),
        };
        await confirmMeal(threadId, "approve", edits);
        setResult({
          ...pendingAnalysis,
          food_name: editedFoodName,
          weight_grams: Number(editedWeight),
          nutrition: {
            ...pendingAnalysis.nutrition,
            calories: Number(editedCalories),
            protein: Number(editedProtein),
            carbs: Number(editedCarbs),
            fat: Number(editedFat),
          },
        });
        setIsPending(false); setPendingAnalysis(null);
      }
    } catch (err: unknown) {
      setError(getUserFriendlyError(err).message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !isStreaming) return <LoadingScreen />;
  if (batchLoading) return <LoadingScreen />;

  return (
    <div style={{
      minHeight: "100vh",
      background: "#020617",
      color: "#f1f5f9",
      display: "flex",
      flexDirection: "column",
      position: "relative",
      overflowX: "hidden",
    }}>
      <div className="g1" />
      <Navbar />

      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "100px 24px 60px",
        gap: "32px",
        position: "relative",
        zIndex: 1,
      }}>

        {/* ── Batch result ── */}
        {batchResult ? (
          <BatchResultsDisplay result={batchResult} onReset={resetAll} />
        ) : result ? (
          /* ── Single result ── */
          <>
            <div className="anim-scale-in" style={{ width: "100%", display: "flex", justifyContent: "center" }}>
              <ResultsDisplay data={result} preview={preview} />
            </div>
            <button
              onClick={resetAll}
              style={{
                padding: "10px 22px",
                background: "rgba(15,23,42,0.5)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "99px",
                color: "#64748b",
                fontSize: "13px",
                fontWeight: 500,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "7px",
                transition: "all .2s",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.color = "#94a3b8";
                (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(255,255,255,0.14)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.color = "#64748b";
                (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(255,255,255,0.08)";
              }}
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Analyze another meal
            </button>
          </>
        ) : isPending ? (
          /* ── HITL confirmation ── */
          <div className="anim-scale-in" style={{
            width: "100%",
            maxWidth: "480px",
            background: "rgba(10,18,38,0.65)",
            border: "1px solid rgba(255,255,255,0.06)",
            borderRadius: "20px",
            padding: "32px 28px",
            display: "flex",
            flexDirection: "column",
            gap: "24px",
            backdropFilter: "blur(16px)",
            boxShadow: "0 24px 48px rgba(0,0,0,0.4)",
          }}>
            {/* Header */}
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: 700, color: "#f1f5f9", marginBottom: "4px" }}>
                Review before saving
              </h2>
              <p style={{ fontSize: "12px", color: "#475569", lineHeight: 1.6 }}>
                AI estimates can vary — adjust any values before confirming.
              </p>
            </div>

            {/* Allergy warning */}
            {pendingAnalysis?.allergies_warning && (
              <div style={{
                padding: "12px 14px",
                background: "rgba(245,158,11,0.07)",
                border: "1px solid rgba(245,158,11,0.18)",
                borderRadius: "12px",
                color: "#fbbf24",
                fontSize: "12px",
                display: "flex",
                alignItems: "flex-start",
                gap: "10px",
                lineHeight: 1.6,
              }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: "1px" }}>
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                <span>{pendingAnalysis.allergies_warning}</span>
              </div>
            )}

            {/* Fields */}
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <EditField label="Food name" value={editedFoodName} onChange={setEditedFoodName} />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <EditField label="Weight (g)" value={editedWeight} onChange={(v) => setEditedWeight(Number(v))} type="number" />
                <EditField label="Calories (kcal)" value={editedCalories} onChange={(v) => setEditedCalories(Number(v))} type="number" />
                <EditField label="Protein (g)" value={editedProtein} onChange={(v) => setEditedProtein(Number(v))} type="number" />
                <EditField label="Carbs (g)" value={editedCarbs} onChange={(v) => setEditedCarbs(Number(v))} type="number" />
                <EditField label="Fat (g)" value={editedFat} onChange={(v) => setEditedFat(Number(v))} type="number" />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div style={{
                padding: "10px 14px",
                background: "rgba(239,68,68,0.05)",
                border: "1px solid rgba(239,68,68,0.12)",
                borderRadius: "10px",
                color: "#f87171",
                fontSize: "12px",
              }}>
                {error}
              </div>
            )}

            {/* Actions */}
            <div style={{ display: "flex", gap: "10px" }}>
              <button
                onClick={() => handleConfirm("reject")}
                style={{
                  padding: "11px 18px",
                  background: "transparent",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "12px",
                  color: "#64748b",
                  fontSize: "13px",
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "all .2s",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(239,68,68,0.25)";
                  (e.currentTarget as HTMLButtonElement).style.color = "#f87171";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(255,255,255,0.08)";
                  (e.currentTarget as HTMLButtonElement).style.color = "#64748b";
                }}
              >
                Discard
              </button>
              <button
                onClick={() => handleConfirm("approve")}
                className="btn-glow"
                style={{
                  flex: 1,
                  padding: "11px",
                  background: "linear-gradient(135deg,#10b981,#059669)",
                  border: "none",
                  borderRadius: "12px",
                  color: "#020617",
                  fontSize: "14px",
                  fontWeight: 700,
                  cursor: "pointer",
                  boxShadow: "0 4px 16px rgba(16,185,129,0.22)",
                }}
              >
                Save meal
              </button>
            </div>
          </div>
        ) : (
          /* ── Upload view ── */
          <>
            {/* Title */}
            <div className="anim-fade-up" style={{ textAlign: "center" }}>
              <h1 style={{
                fontSize: "clamp(20px, 3vw, 26px)",
                fontWeight: 700,
                color: "#f1f5f9",
                letterSpacing: "-0.01em",
                marginBottom: "6px",
              }}>
                Analyze your meal
              </h1>
              <p style={{
                fontSize: "13px",
                color: "#475569",
                lineHeight: 1.7,
                maxWidth: "320px",
                margin: "0 auto",
              }}>
                Drop a photo for instant AI nutrition analysis,<br />
                or select multiple for a full-day batch.
              </p>
            </div>

            {/* Upload box */}
            <div className="anim-scale-in delay-1" style={{ width: "100%", display: "flex", justifyContent: "center" }}>
              <UploadBox
                onFile={handleFile}
                onFiles={handleFiles}
                preview={batchFiles.length > 1 ? null : preview}
                previews={batchFiles.length > 1 ? batchPreviews : []}
                onAnalyze={batchFiles.length > 1 ? handleBatchAnalyze : handleAnalyze}
                isLowConfidence={isLowConfidence}
              />
            </div>

            {/* Progress stepper */}
            {streamEvents.length > 0 && (
              <ProgressStepper events={streamEvents} />
            )}

            {/* Tips */}
            {!preview && !isStreaming && batchFiles.length === 0 && (
              <div className="anim-fade-up delay-2" style={{
                display: "flex",
                gap: "8px",
                width: "100%",
                maxWidth: "440px",
                justifyContent: "center",
                flexWrap: "wrap",
              }}>
                {[
                  "Good lighting improves accuracy",
                  "Select multiple photos for a batch",
                ].map((tip, i) => (
                  <div key={i} style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "7px",
                    padding: "7px 13px",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid rgba(255,255,255,0.04)",
                    borderRadius: "99px",
                  }}>
                    <span style={{
                      width: "4px", height: "4px", borderRadius: "50%",
                      background: "#334155", flexShrink: 0,
                    }} />
                    <span style={{ fontSize: "11px", color: "#475569" }}>{tip}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="anim-scale-in" style={{
                width: "100%",
                maxWidth: "440px",
                padding: "12px 16px",
                background: "rgba(239,68,68,0.05)",
                border: "1px solid rgba(239,68,68,0.12)",
                borderRadius: "12px",
                color: "#f87171",
                fontSize: "12px",
                fontWeight: 500,
                textAlign: "center",
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