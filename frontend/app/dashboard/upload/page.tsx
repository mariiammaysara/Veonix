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

/**
 * Veonix — Upload & Analysis Page (Phase 9)
 *
 * Adds:
 *   - SSE streaming progress log for single-image analysis
 *   - Multi-file selection + batch analysis flow
 *   - BatchResultsDisplay for aggregate nutrition summary
 */

// ── Stream event icon ────────────────────────────────────────────────────────

const EVENT_ICONS: Record<string, string> = {
  start: "🗜️",
  profile: "👤",
  vision_start: "🔭",
  vision_done: "✅",
  allergy_check: "⚠️",
  saving: "💾",
  pending_confirmation: "🔔",
  done: "🎉",
  error: "❌",
  low_confidence: "📷",
};

// ── Stream progress log ──────────────────────────────────────────────────────

function StreamProgressLog({ events }: { events: StreamEvent[] }) {
  if (events.length === 0) return null;

  return (
    <div
      className="anim-scale-in"
      style={{
        width: "100%",
        maxWidth: "480px",
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
        gap: "6px",
        padding: "16px",
        borderRadius: "16px",
        background: "rgba(10,18,38,0.6)",
        border: "1px solid rgba(255,255,255,0.05)",
        backdropFilter: "blur(8px)",
      }}
    >
      <p style={{ fontSize: "11px", color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "6px" }}>
        Analysis Progress
      </p>
      {events.map((ev, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            padding: "8px 10px",
            borderRadius: "10px",
            background: ev.event === "error" ? "rgba(239,68,68,0.06)" : "rgba(255,255,255,0.02)",
            border: `1px solid ${ev.event === "error" ? "rgba(239,68,68,0.12)" : "rgba(255,255,255,0.04)"}`,
            opacity: i < events.length - 1 ? 0.65 : 1,
            transition: "opacity .2s",
          }}
        >
          <span style={{ fontSize: "14px", flexShrink: 0 }}>{EVENT_ICONS[ev.event] ?? "•"}</span>
          <span
            style={{
              fontSize: "13px",
              color: ev.event === "error" ? "#f87171" : ev.event === "done" || ev.event === "vision_done" ? "#34d399" : "#94a3b8",
              fontWeight: i === events.length - 1 ? 600 : 400,
            }}
          >
            {ev.message}
            {ev.food_name && ev.confidence !== undefined && (
              <span style={{ color: "#64748b", fontWeight: 400, marginLeft: "6px" }}>
                ({(ev.confidence * 100).toFixed(0)}% confidence)
              </span>
            )}
          </span>
        </div>
      ))}
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────

export default function UploadPage() {
  const router = useRouter();

  // Single-file state
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MealResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLowConfidence, setIsLowConfidence] = useState(false);

  // SSE streaming state
  const [streamEvents, setStreamEvents] = useState<StreamEvent[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  // Batch state
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [batchPreviews, setBatchPreviews] = useState<string[]>([]);
  const [batchResult, setBatchResult] = useState<BatchResult | null>(null);
  const [batchLoading, setBatchLoading] = useState(false);

  // HITL states
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
      if (result || isPending || batchResult) {
        resetAll();
      } else {
        router.push("/");
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [result, isPending, batchResult, router]);

  const resetAll = useCallback(() => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setIsLowConfidence(false);
    setStreamEvents([]);
    setIsStreaming(false);
    setBatchFiles([]);
    setBatchPreviews([]);
    setBatchResult(null);
    setIsPending(false);
    setPendingAnalysis(null);
    setThreadId(null);
  }, []);

  // ── Single file handler ────────────────────────────────────────────────────

  const handleFile = (f: File | null) => {
    resetAll();
    setFile(f);
    if (f) {
      const url = URL.createObjectURL(f);
      setPreview(url);
    }
  };

  // ── Multi-file handler (batch mode) ───────────────────────────────────────

  const handleFiles = useCallback((files: File[]) => {
    resetAll();
    setBatchFiles(files);
    const urls = files.map((f) => URL.createObjectURL(f));
    setBatchPreviews(urls);
  }, [resetAll]);

  // ── Single SSE streaming analysis ────────────────────────────────────────

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setIsLowConfidence(false);
    setStreamEvents([]);
    setIsStreaming(true);

    try {
      let finalResult: MealResult | null = null;
      let pendingThreadId: string | null = null;
      let pendingMeal: MealResult | null = null;

      await analyzeImageStream(file, (ev: StreamEvent) => {
        setStreamEvents((prev) => [...prev, ev]);

        if (ev.event === "done" && ev.result) {
          finalResult = ev.result as unknown as MealResult;
        }
        if (ev.event === "pending_confirmation" && ev.result) {
          pendingThreadId = ev.thread_id ?? null;
          pendingMeal = ev.result as unknown as MealResult;
        }
        if (ev.event === "low_confidence") {
          setIsLowConfidence(true);
        }
      });

      if (pendingThreadId && pendingMeal) {
        setThreadId(pendingThreadId);
        setPendingAnalysis(pendingMeal);
        setIsPending(true);
        setEditedFoodName(pendingMeal.food_name);
        setEditedWeight(pendingMeal.weight_grams);
        setEditedCalories(pendingMeal.nutrition.calories);
        setEditedProtein(pendingMeal.nutrition.protein);
        setEditedCarbs(pendingMeal.nutrition.carbs);
        setEditedFat(pendingMeal.nutrition.fat);
      } else if (finalResult) {
        setResult(finalResult);
      } else if (!isLowConfidence) {
        setError("No result received. Please try again.");
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
      setIsStreaming(false);
    }
  };

  // ── Batch analysis ────────────────────────────────────────────────────────

  const handleBatchAnalyze = async () => {
    if (batchFiles.length === 0) return;
    setBatchLoading(true);
    setError(null);
    try {
      const data = await analyzeBatch(batchFiles);
      setBatchResult(data);
    } catch (err: unknown) {
      setError(getUserFriendlyError(err).message);
    } finally {
      setBatchLoading(false);
    }
  };

  // ── HITL confirm ──────────────────────────────────────────────────────────

  const handleConfirm = async (action: "approve" | "reject") => {
    if (!threadId || !pendingAnalysis) return;
    setLoading(true);
    setError(null);
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
        const finalMeal: MealResult = {
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

  // ── Render ────────────────────────────────────────────────────────────────

  if (loading && !isStreaming) return <LoadingScreen />;
  if (batchLoading) return <LoadingScreen />;

  return (
    <div style={{ minHeight: "100vh", background: "#020617", color: "#f1f5f9", display: "flex", flexDirection: "column", position: "relative", overflowX: "hidden" }}>
      <div className="g1" />
      <Navbar />

      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "80px 20px 40px", gap: "28px",
        position: "relative", zIndex: 1,
      }}>

        {/* ── Batch result ── */}
        {batchResult ? (
          <>
            <BatchResultsDisplay result={batchResult} onReset={resetAll} />
          </>
        ) : result ? (
          /* ── Single result ── */
          <>
            <div className="anim-scale-in" style={{ width: "100%", display: "flex", justifyContent: "center" }}>
              <ResultsDisplay data={result} preview={preview} />
            </div>
            <button
              onClick={resetAll}
              style={{
                padding: "10px 24px", background: "rgba(15,23,42,0.6)",
                border: "1px solid rgba(255,255,255,0.1)", borderRadius: "99px",
                color: "#94a3b8", fontSize: "13px", fontWeight: 600, cursor: "pointer",
                display: "flex", alignItems: "center", gap: "8px",
                transition: "all .2s", boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Analyze another meal
            </button>
          </>
        ) : isPending ? (
          /* ── HITL confirmation form ── */
          <div className="anim-scale-in" style={{
            width: "100%", maxWidth: "520px",
            background: "rgba(10,18,38,0.6)", border: "1px solid rgba(255,255,255,0.06)",
            borderRadius: "24px", padding: "28px 24px",
            display: "flex", flexDirection: "column", gap: "20px",
            backdropFilter: "blur(12px)", boxShadow: "0 20px 40px rgba(0,0,0,0.3)",
          }}>
            <div style={{ textAlign: "center", marginBottom: "4px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#f1f5f9" }}>Confirm Recommendation Details</h2>
              <p style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>Review and customize before saving.</p>
            </div>

            {pendingAnalysis?.allergies_warning && (
              <div style={{ padding: "12px 16px", background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)", borderRadius: "12px", color: "#fbbf24", fontSize: "13px", display: "flex", alignItems: "center", gap: "10px", lineHeight: 1.5 }}>
                <span style={{ fontSize: "16px" }}>⚠️</span>
                <span>{pendingAnalysis.allergies_warning}</span>
              </div>
            )}

            {/* SSE progress recap */}
            {streamEvents.length > 0 && <StreamProgressLog events={streamEvents} />}

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div style={{ gridColumn: "span 2", display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>Food Name</label>
                <input type="text" value={editedFoodName} onChange={(e) => setEditedFoodName(e.target.value)} style={{ width: "100%", padding: "10px 12px", background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none" }} />
              </div>
              {[
                { label: "Weight (g)", val: editedWeight, set: setEditedWeight },
                { label: "Calories (kcal)", val: editedCalories, set: setEditedCalories },
                { label: "Protein (g)", val: editedProtein, set: setEditedProtein },
                { label: "Carbs (g)", val: editedCarbs, set: setEditedCarbs },
                { label: "Fat (g)", val: editedFat, set: setEditedFat },
              ].map(({ label, val, set }) => (
                <div key={label} style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  <label style={{ fontSize: "11px", fontWeight: 600, color: "#64748b", textTransform: "uppercase" }}>{label}</label>
                  <input type="number" value={val} onChange={(e) => set(Number(e.target.value))} style={{ width: "100%", padding: "10px 12px", background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "10px", color: "#f1f5f9", fontSize: "14px", outline: "none" }} />
                </div>
              ))}
            </div>

            {error && <div style={{ padding: "10px 14px", background: "rgba(239,68,68,0.05)", border: "1px solid rgba(239,68,68,0.15)", borderRadius: "12px", color: "#f87171", fontSize: "12px", textAlign: "center" }}>{error}</div>}

            <div style={{ display: "flex", gap: "12px", marginTop: "8px" }}>
              <button onClick={() => handleConfirm("reject")} style={{ flex: 1, padding: "12px", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.15)", borderRadius: "12px", color: "#f87171", fontSize: "14px", fontWeight: 700, cursor: "pointer" }}>
                Discard
              </button>
              <button onClick={() => handleConfirm("approve")} style={{ flex: 2, padding: "12px", background: "#10b981", border: "none", borderRadius: "12px", color: "#020617", fontSize: "14px", fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 14px rgba(16,185,129,0.2)" }}>
                Approve & Save
              </button>
            </div>
          </div>
        ) : (
          /* ── Upload / progress view ── */
          <>
            <div className="anim-fade-up" style={{ textAlign: "center" }}>
              <h1 style={{ fontSize: "clamp(22px, 3vw, 28px)", fontWeight: 800, color: "#f1f5f9", marginBottom: "8px" }}>
                Analyze Your Meal
              </h1>
              <p style={{ fontSize: "14px", color: "#64748b", maxWidth: "360px", lineHeight: 1.6, margin: "0 auto" }}>
                Upload one photo for instant analysis — or select multiple for a full-day batch.
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

            {/* SSE streaming progress log (during single analysis) */}
            {isStreaming && streamEvents.length > 0 && (
              <StreamProgressLog events={streamEvents} />
            )}

            {/* After-stream progress — show until result appears */}
            {!isStreaming && streamEvents.length > 0 && !result && !isPending && (
              <StreamProgressLog events={streamEvents} />
            )}

            {/* Tips (hidden while streaming) */}
            {!preview && !isStreaming && batchFiles.length === 0 && (
              <div className="anim-fade-up delay-2" style={{ display: "flex", flexWrap: "wrap", gap: "10px", width: "100%", maxWidth: "480px", justifyContent: "center" }}>
                {[
                  { icon: <path d="M12 2v2m0 16v2m10-10h-2M4 10H2m15.36-5.36l-1.42 1.42M6.05 17.95l-1.42 1.42m12.73 0l-1.42-1.42M6.05 6.05L4.63 4.63" />, text: "Use good lighting for accuracy" },
                  { icon: <path d="M3 6l9-4 9 4v11a2 2 0 01-2 2H5a2 2 0 01-2-2V6z" />, text: "Select multiple photos for batch" },
                ].map(({ icon, text }, i) => (
                  <div key={i} style={{ flex: "1 1 200px", background: "rgba(15,23,42,0.3)", border: "1px solid rgba(255,255,255,0.04)", borderRadius: "12px", padding: "10px 14px", display: "flex", alignItems: "center", gap: "10px" }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                      <circle cx="12" cy="12" r="10" />
                      {icon}
                    </svg>
                    <span style={{ fontSize: "11px", color: "#64748b", fontWeight: 500 }}>{text}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="anim-scale-in" style={{ width: "100%", maxWidth: "480px", padding: "14px", background: "rgba(239,68,68,0.05)", border: "1px solid rgba(239,68,68,0.15)", borderRadius: "12px", color: "#f87171", fontSize: "12px", textAlign: "center", fontWeight: 500 }}>
                {error}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}