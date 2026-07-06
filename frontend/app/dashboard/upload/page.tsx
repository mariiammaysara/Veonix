"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import UploadBox from "@/components/upload-box";
import ResultsDisplay from "@/components/results-display";
import LoadingScreen from "@/components/LoadingScreen";
import { analyzeImage, ApiError } from "@/lib/api";
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

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (result) {
        setResult(null);
        setFile(null);
        setPreview(null);
      } else {
        router.push("/");
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [result, router]);

  const handleFile = (f: File | null) => {
    setResult(null);
    setError(null);
    setIsLowConfidence(false);
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
      const data = await analyzeImage(file);
      setResult(data);
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

        {!result ? (
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
        ) : (
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
        )}
      </div>
    </div>
  );
}