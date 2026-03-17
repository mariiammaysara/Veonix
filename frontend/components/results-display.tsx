"use client";

import { useState, useEffect } from "react";
import type { MealResult } from "@/lib/types";

interface Props { data: MealResult; preview: string | null; }

const MACROS = [
  {
    key: "protein" as const, label: "Protein", color: "#38bdf8", bg: "rgba(56,189,248,0.09)", bar: 52,
    icon: <path d="M18 8h1a4 4 0 0 1 0 8h-1M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8zM6 1v3M10 1v3M14 1v3" />
  },
  {
    key: "carbs" as const, label: "Carbs", color: "#fbbf24", bg: "rgba(251,191,36,0.09)", bar: 28,
    icon: <><path d="M12 2a10 10 0 0 1 10 10H2A10 10 0 0 1 12 2z" /><path d="M2 12h20M12 22v-4" /></>
  },
  {
    key: "fat" as const, label: "Fat", color: "#fb7185", bg: "rgba(251,113,133,0.09)", bar: 60,
    icon: <path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z" />
  },
];

export default function ResultsDisplay({ data, preview }: Props) {
  const { nutrition } = data;
  const total = nutrition.protein + nutrition.carbs + nutrition.fat;
  const pPct = total ? Math.round(nutrition.protein / total * 100) : 0;
  const cPct = total ? Math.round(nutrition.carbs / total * 100) : 0;
  const fPct = total ? 100 - pPct - cPct : 0;

  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setLoaded(true), 150);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="anim-scale-in" style={{ width: "100%", maxWidth: "min(560px, 100%)", display: "flex", flexDirection: "column", gap: "10px", margin: "0 auto" }}>

      {/* Header card */}
      <div className="anim-fade-up" style={{ background: "rgba(15,23,42,0.65)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "18px", padding: "16px", display: "flex", gap: "14px" }}>
        {preview ? (
          <img src={preview} alt={data.food_name} style={{ width: "64px", height: "64px", borderRadius: "12px", objectFit: "cover", border: "1px solid rgba(255,255,255,0.04)", flexShrink: 0 }} />
        ) : (
          <div style={{ width: "64px", height: "64px", borderRadius: "12px", background: "linear-gradient(135deg,#0c2644,#091a14)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "28px", flexShrink: 0, border: "1px solid rgba(255,255,255,0.04)" }}>🍽️</div>
        )}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "16px", fontWeight: 700, color: "#f1f5f9" }}>{data.food_name}</div>
          <div style={{ fontSize: "11px", color: "#475569", marginTop: "3px" }}>{data.cuisine} · {data.meal_type} · ~{data.weight_grams}g</div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", marginTop: "8px", padding: "5px 11px", background: "rgba(249,115,22,0.06)", border: "1px solid rgba(249,115,22,0.14)", borderRadius: "8px" }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fb923c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2c0 0-5 5.5-5 10a5 5 0 0 0 10 0C17 7.5 12 2 12 2z" />
            </svg>
            <span className="num-reveal delay-2" style={{ fontSize: "20px", fontWeight: 700, color: "#fb923c" }}>{nutrition.calories}</span>
            <span style={{ fontSize: "11px", color: "rgba(251,146,60,0.45)" }}>kcal</span>
          </div>
        </div>
      </div>

      {/* Macro cards — 3 cols */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
        {MACROS.map(({ key, label, color, bg, bar, icon }, i) => (
          <div key={key} className={`card-hover anim-fade-up delay-${i + 2}`} style={{ background: "rgba(15,23,42,0.65)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "14px", padding: "12px" }}>
            <div style={{ width: "28px", height: "28px", borderRadius: "9px", background: bg, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "6px" }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">{icon}</svg>
            </div>
            <div className="num-reveal" style={{ fontSize: "20px", fontWeight: 700, lineHeight: 1, color, animationDelay: `${(i + 2) * 0.1}s` }}>
              {nutrition[key]}<span style={{ fontSize: "10px", fontWeight: 400, opacity: .4 }}>g</span>
            </div>
            <div style={{ fontSize: "10px", color: "#475569", textTransform: "uppercase", letterSpacing: ".05em", marginTop: "3px" }}>{label}</div>
            <div style={{ height: "3px", background: "rgba(255,255,255,0.04)", borderRadius: "2px", marginTop: "6px", overflow: "hidden" }}>
              <div
                className={`bar-fill ${loaded ? 'loaded' : ''}`}
                style={{ "--bar-width": `${bar}%`, background: color } as React.CSSProperties}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Fiber + Sodium — 2 cols */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
        {[
          { label: "Fiber", value: nutrition.fiber, unit: "g", color: "#34d399", bg: "rgba(52,211,153,0.09)", icon: <path d="M12 22V12M12 12C12 6 6 2 6 2s0 6 6 10zM12 12c0-6 6-10 6-10s0 6-6 10z" /> },
          { label: "Sodium", value: nutrition.sodium, unit: "mg", color: "#f472b6", bg: "rgba(244,114,182,0.09)", icon: <><circle cx="12" cy="12" r="5" /><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12" /></> },
        ].map(({ label, value, unit, color, bg, icon }, i) => (
          <div key={label} className={`card-hover anim-fade-up delay-${i + 5}`} style={{ background: "rgba(15,23,42,0.65)", border: "1px solid rgba(255,255,255,0.04)", borderRadius: "14px", padding: "12px" }}>
            <div style={{ width: "28px", height: "28px", borderRadius: "9px", background: bg, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "6px" }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">{icon}</svg>
            </div>
            <div className="num-reveal" style={{ fontSize: "20px", fontWeight: 700, lineHeight: 1, color, animationDelay: `${(i + 5) * 0.1}s` }}>
              {value}<span style={{ fontSize: "10px", fontWeight: 400, opacity: .4 }}>{unit}</span>
            </div>
            <div style={{ fontSize: "10px", color: "#475569", textTransform: "uppercase", letterSpacing: ".05em", marginTop: "3px" }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Macro ratio bar */}
      <div className="anim-fade-up delay-6" style={{ background: "rgba(15,23,42,0.65)", border: "1px solid rgba(255,255,255,0.04)", borderRadius: "14px", padding: "12px 14px" }}>
        <div style={{ fontSize: "10px", color: "#475569", textTransform: "uppercase", letterSpacing: ".05em", marginBottom: "8px" }}>Macro ratio</div>
        <div style={{ display: "flex", gap: "2px", height: "5px", borderRadius: "3px", overflow: "hidden" }}>
          <div className={`ratio-seg ${loaded ? 'loaded' : ''}`} style={{ "--seg-width": `${pPct}%`, background: "#38bdf8" } as React.CSSProperties} />
          <div className={`ratio-seg ${loaded ? 'loaded' : ''}`} style={{ "--seg-width": `${cPct}%`, background: "#fbbf24", transitionDelay: "0.1s" } as React.CSSProperties} />
          <div className={`ratio-seg ${loaded ? 'loaded' : ''}`} style={{ "--seg-width": `${fPct}%`, background: "#fb7185", transitionDelay: "0.2s" } as React.CSSProperties} />
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "12px", marginTop: "8px" }}>
          {[["#38bdf8", `Protein ${pPct}%`], ["#fbbf24", `Carbs ${cPct}%`], ["#fb7185", `Fat ${fPct}%`]].map(([color, label]) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "11px", color: "#475569" }}>
              <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: color }} />
              {label}
            </div>
          ))}
        </div>
      </div>

      {/* Source */}
      {nutrition.is_estimated && (
        <div className="anim-fade-in delay-6" style={{ fontSize: "11px", color: "#fbbf24", textAlign: "center", padding: "6px", background: "rgba(251,191,36,0.05)", borderRadius: "10px", border: "1px solid rgba(251,191,36,0.1)" }}>
          ⚠️ Estimated values — not from a verified database
        </div>
      )}
    </div>
  );
}
