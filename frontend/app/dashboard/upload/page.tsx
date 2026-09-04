"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import UploadBox from "@/components/upload-box";
import ResultsDisplay from "@/components/results-display";
import BatchResultsDisplay from "@/components/batch-results-display";
import LoadingScreen from "@/components/LoadingScreen";
import { analyzeImage, analyzeBatch, ApiError } from "@/lib/api";
import { getUserFriendlyError } from "@/lib/error-utils";
import type { MealResult, BatchResult } from "@/lib/types";

// ── Main page ────────────────────────────────────────────────────────────────

export default function UploadPage() {
  const router = useRouter();

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MealResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLowConfidence, setIsLowConfidence] = useState(false);

  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [batchPreviews, setBatchPreviews] = useState<string[]>([]);
  const [batchResult, setBatchResult] = useState<BatchResult | null>(null);
  const [batchLoading, setBatchLoading] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (result || batchResult) resetAll();
      else router.push("/");
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [result, batchResult, router]);

  const resetAll = useCallback(() => {
    setFile(null); setPreview(null); setResult(null);
    setError(null); setIsLowConfidence(false);
    setBatchFiles([]); setBatchPreviews([]); setBatchResult(null);
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
    setLoading(true); setError(null); setIsLowConfidence(false);

    try {
      const analysis = await analyzeImage(file);
      setResult(analysis);
    } catch (err: unknown) {
      if (err instanceof ApiError && err.code === "LOW_CONFIDENCE") {
        setIsLowConfidence(true); setFile(null); setPreview(null);
      } else {
        setError(getUserFriendlyError(err).message);
      }
    } finally {
      setLoading(false);
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

  if (loading) return <LoadingScreen />;
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

            {/* Tips */}
            {!preview && batchFiles.length === 0 && (
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

      <Footer />
    </div>
  );
}