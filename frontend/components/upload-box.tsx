"use client";

import React, { useState, useCallback, useRef } from "react";

interface Props {
  onFile: (file: File | null) => void;
  preview: string | null;
  onAnalyze: () => void;
}

export default function UploadBox({ onFile, preview, onAnalyze }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files[0]) onFile(e.dataTransfer.files[0]);
  }, [onFile]);

  if (preview) {
    return (
      <div className="anim-scale-in" style={{ width: "100%", maxWidth: "min(480px, 100%)", borderRadius: "20px", border: "1px solid rgba(255,255,255,0.05)", overflow: "hidden", position: "relative", margin: "0 auto" }}>
        <img src={preview} alt="Preview" style={{ width: "100%", height: "clamp(200px, 30vh, 320px)", objectFit: "cover", display: "block" }} />
        <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: "110px", background: "linear-gradient(to top,rgba(2,6,23,0.97),transparent)", pointerEvents: "none" }} />
        <div style={{ position: "absolute", bottom: "16px", left: "16px", right: "16px", display: "flex", gap: "10px" }}>
          <button onClick={() => fileInputRef.current?.click()} style={{
            padding: "10px 16px", background: "rgba(2,6,23,0.85)", border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: "12px", color: "#475569", fontSize: "14px", fontWeight: 500, cursor: "pointer",
            display: "flex", alignItems: "center", gap: "6px", backdropFilter: "blur(8px)"
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 4v6h6M23 20v-6h-6" /><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10M23 14l-4.64 4.36A9 9 0 0 1 3.51 15" />
            </svg>
            Change
          </button>
          <button onClick={onAnalyze} className="btn-glow" style={{
            flex: 1, padding: "10px", background: "#10b981", border: "none", borderRadius: "12px",
            color: "#020617", fontSize: "15px", fontWeight: 700, cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center", gap: "8px"
          }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#020617" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
            </svg>
            Analyze meal
          </button>
        </div>
        <input ref={fileInputRef} type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} className="hidden" />
      </div>
    );
  }

  return (
    <div
      onDragOver={handleDrag} onDragLeave={handleDrag} onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className="anim-scale-in"
      style={{
        width: "100%", maxWidth: "min(480px, 100%)", borderRadius: "20px",
        background: isDragging ? "rgba(16,185,129,0.025)" : "rgba(10,18,38,0.6)",
        border: `1.5px dashed ${isDragging ? "rgba(52,211,153,0.28)" : "rgba(255,255,255,0.06)"}`,
        cursor: "pointer", transition: "all .2s ease",
        margin: "0 auto",
        transform: isDragging ? "scale(1.02)" : "scale(1)"
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "28px 20px 24px", gap: "14px" }}>
        {/* Icon ring — float when empty */}
        <div className="anim-float" style={{ width: "54px", height: "54px", borderRadius: "16px", background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.12)", display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
          <div style={{ position: "absolute", inset: "-6px", borderRadius: "24px", border: "1px dashed rgba(16,185,129,0.1)" }} />
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="16 16 12 12 8 16" /><line x1="12" y1="12" x2="12" y2="21" />
            <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
          </svg>
        </div>
        <div>
          <p style={{ fontSize: "16px", fontWeight: 600, color: "#cbd5e1", textAlign: "center" }}>Drop your meal photo here</p>
          <p style={{ fontSize: "12px", color: "#475569", textAlign: "center", lineHeight: 1.5, marginTop: "6px" }}>Works best with clear, well-lit photos<br />JPG · PNG · WEBP · up to 10 MB</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", width: "180px" }}>
          <div style={{ flex: 1, height: "1px", background: "rgba(255,255,255,0.04)" }} />
          <span style={{ fontSize: "11px", color: "#334155", textTransform: "uppercase", letterSpacing: ".08em" }}>or</span>
          <div style={{ flex: 1, height: "1px", background: "rgba(255,255,255,0.04)" }} />
        </div>
        <button style={{ padding: "8px 24px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "99px", color: "#475569", fontSize: "13px", fontWeight: 500, cursor: "pointer" }}>
          Browse files
        </button>
      </div>
      <input ref={fileInputRef} type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} className="hidden" />
    </div>
  );
}
