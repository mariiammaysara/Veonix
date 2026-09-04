"use client";

import React, { useState, useCallback, useRef } from "react";

interface Props {
  onFile: (file: File | null) => void;
  onFiles?: (files: File[]) => void;
  preview: string | null;
  onAnalyze: () => void;
  isLowConfidence?: boolean;
  previews?: string[];
}

export default function UploadBox({
  onFile,
  onFiles,
  preview,
  onAnalyze,
  isLowConfidence = false,
  previews = [],
}: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(e.type === "dragover");
  }, []);

  const handleFileChange = useCallback(
    (fileList: FileList | null) => {
      if (!fileList || fileList.length === 0) return;
      if (fileList.length > 1 && onFiles) {
        onFiles(Array.from(fileList));
      } else {
        onFile(fileList[0]);
      }
    },
    [onFile, onFiles]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleFileChange(e.dataTransfer.files);
    },
    [handleFileChange]
  );

  // ── Multi-file batch preview ──────────────────────────────────────────────
  if (previews.length > 1) {
    return (
      <div className="anim-scale-in" style={{ width: "100%", maxWidth: "480px", margin: "0 auto" }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: `repeat(${Math.min(previews.length, 3)}, 1fr)`,
          gap: "8px",
          marginBottom: "14px",
        }}>
          {previews.map((src, i) => (
            <div key={i} style={{
              position: "relative",
              borderRadius: "12px",
              overflow: "hidden",
              aspectRatio: "1",
              border: "1px solid rgba(255,255,255,0.06)",
            }}>
              <img src={src} alt={`Image ${i + 1}`} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              <div style={{
                position: "absolute", top: "8px", left: "8px",
                background: "rgba(16,185,129,0.9)",
                borderRadius: "6px", padding: "2px 7px",
                fontSize: "10px", fontWeight: 700, color: "#020617",
              }}>
                {i + 1}
              </div>
            </div>
          ))}
          {previews.length > 3 && (
            <div style={{
              borderRadius: "12px",
              background: "rgba(255,255,255,0.02)",
              border: "1px dashed rgba(255,255,255,0.07)",
              display: "flex", alignItems: "center", justifyContent: "center", aspectRatio: "1",
            }}>
              <span style={{ fontSize: "13px", color: "#64748b" }}>+{previews.length - 3} more</span>
            </div>
          )}
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={() => fileInputRef.current?.click()}
            style={{
              padding: "11px 16px",
              background: "rgba(15,23,42,0.6)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: "12px",
              color: "#64748b",
              fontSize: "13px",
              fontWeight: 500,
              cursor: "pointer",
              display: "flex", alignItems: "center", gap: "6px",
              transition: "all .2s",
            }}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 4v6h6M23 20v-6h-6" />
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10M23 14l-4.64 4.36A9 9 0 0 1 3.51 15" />
            </svg>
            Change
          </button>
          <button
            onClick={onAnalyze}
            className="btn-glow"
            style={{
              flex: 1, padding: "11px",
              background: "linear-gradient(135deg,#10b981,#059669)",
              border: "none", borderRadius: "12px",
              color: "#020617", fontSize: "14px", fontWeight: 700,
              cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
              boxShadow: "0 4px 16px rgba(16,185,129,0.22)",
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#020617" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
            </svg>
            Analyze {previews.length} meals
          </button>
        </div>

        <input ref={fileInputRef} type="file" accept="image/*" multiple
          onChange={(e) => handleFileChange(e.target.files)} className="hidden" />
      </div>
    );
  }

  // ── Single-image preview ──────────────────────────────────────────────────
  if (preview) {
    return (
      <div className="anim-scale-in" style={{
        width: "100%",
        maxWidth: "440px",
        borderRadius: "20px",
        border: "1px solid rgba(255,255,255,0.07)",
        overflow: "hidden",
        position: "relative",
        margin: "0 auto",
        boxShadow: "0 16px 40px rgba(0,0,0,0.3)",
      }}>
        <img
          src={preview}
          alt="Preview"
          style={{
            width: "100%",
            height: "clamp(200px, 32vh, 300px)",
            objectFit: "cover",
            display: "block",
          }}
        />
        {/* Gradient overlay */}
        <div style={{
          position: "absolute", bottom: 0, left: 0, right: 0, height: "120px",
          background: "linear-gradient(to top,rgba(2,6,23,0.98) 0%,rgba(2,6,23,0.6) 60%,transparent 100%)",
          pointerEvents: "none",
        }} />
        {/* Action buttons */}
        <div style={{
          position: "absolute", bottom: "16px", left: "16px", right: "16px",
          display: "flex", gap: "10px",
        }}>
          <button
            onClick={() => fileInputRef.current?.click()}
            style={{
              padding: "10px 14px",
              background: "rgba(2,6,23,0.7)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "12px",
              color: "#64748b",
              fontSize: "13px",
              fontWeight: 500,
              cursor: "pointer",
              display: "flex", alignItems: "center", gap: "6px",
              backdropFilter: "blur(12px)",
              transition: "all .2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#94a3b8")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#64748b")}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 4v6h6M23 20v-6h-6" />
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10M23 14l-4.64 4.36A9 9 0 0 1 3.51 15" />
            </svg>
            Change
          </button>
          <button
            onClick={onAnalyze}
            className="btn-glow"
            style={{
              flex: 1, padding: "10px",
              background: "linear-gradient(135deg,#10b981,#059669)",
              border: "none", borderRadius: "12px",
              color: "#020617", fontSize: "14px", fontWeight: 700,
              cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
              boxShadow: "0 4px 16px rgba(16,185,129,0.25)",
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#020617" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
            </svg>
            Analyze meal
          </button>
        </div>
        <input ref={fileInputRef} type="file" accept="image/*" multiple
          onChange={(e) => handleFileChange(e.target.files)} className="hidden" />
      </div>
    );
  }

  // ── Empty drop zone ───────────────────────────────────────────────────────
  const accentColor = isLowConfidence ? "#fbbf24" : "#10b981";
  const accentAlpha = isLowConfidence ? "rgba(245,158,11," : "rgba(16,185,129,";

  return (
    <div
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className="anim-scale-in"
      style={{
        width: "100%",
        maxWidth: "440px",
        margin: "0 auto",
        borderRadius: "20px",
        background: isDragging
          ? `${accentAlpha}0.04)`
          : "rgba(10,18,38,0.5)",
        border: `1.5px dashed ${isDragging ? `${accentAlpha}0.35)` : isLowConfidence ? `${accentAlpha}0.22)` : "rgba(255,255,255,0.08)"}`,
        cursor: "pointer",
        transition: "all .25s ease",
        transform: isDragging ? "scale(1.015)" : "scale(1)",
      }}
    >
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "52px 28px 44px",
        gap: "16px",
      }}>
        {/* Icon */}
        <div className="anim-float" style={{
          width: "56px", height: "56px",
          borderRadius: "16px",
          background: `${accentAlpha}0.07)`,
          border: `1px solid ${accentAlpha}0.14)`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          {isLowConfidence ? (
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke={accentColor} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
          ) : (
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke={accentColor} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="16 16 12 12 8 16" />
              <line x1="12" y1="12" x2="12" y2="21" />
              <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
            </svg>
          )}
        </div>

        {/* Text */}
        <div style={{ textAlign: "center" }}>
          {isLowConfidence ? (
            <>
              <p style={{ fontSize: "15px", fontWeight: 600, color: "#fbbf24", marginBottom: "6px" }}>
                Low confidence — retake photo
              </p>
              <p style={{ fontSize: "12px", color: "#78716c", lineHeight: 1.7 }}>
                Make sure the food is clearly visible,<br />well-lit, and centered.
              </p>
            </>
          ) : (
            <>
              <p style={{ fontSize: "15px", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
                Drop your meal photo here
              </p>
              <p style={{ fontSize: "12px", color: "#475569", lineHeight: 1.7 }}>
                JPEG · PNG · WEBP · up to 10 MB<br />
                Select multiple for batch analysis
              </p>
            </>
          )}
        </div>

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", width: "160px" }}>
          <div style={{ flex: 1, height: "1px", background: "rgba(255,255,255,0.05)" }} />
          <span style={{ fontSize: "10px", color: "#334155", textTransform: "uppercase", letterSpacing: ".1em" }}>or</span>
          <div style={{ flex: 1, height: "1px", background: "rgba(255,255,255,0.05)" }} />
        </div>

        {/* Browse button */}
        <button style={{
          padding: "9px 22px",
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: "99px",
          color: "#64748b",
          fontSize: "12px",
          fontWeight: 500,
          cursor: "pointer",
          transition: "all .2s",
        }}>
          Browse files
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={(e) => handleFileChange(e.target.files)}
        className="hidden"
      />
    </div>
  );
}
