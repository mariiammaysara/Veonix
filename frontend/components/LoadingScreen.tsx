"use client";

import { useState, useEffect } from "react";

const STEPS = [
  "Identifying food items",
  "Fetching nutrition data",
  "Calculating macros",
  "Finalizing results",
];

export default function LoadingScreen() {
  const [activeStep, setActiveStep] = useState(0);
  const [doneSteps, setDoneSteps] = useState<number[]>([]);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    STEPS.forEach((_, i) => {
      if (i === 0) return;
      timers.push(setTimeout(() => {
        setDoneSteps(prev => [...prev, i - 1]);
        setActiveStep(i);
      }, i * 900));
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div style={{
      minHeight: "100vh",
      background: "#020617",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: "32px",
      position: "relative",
      overflow: "hidden",
    }}>
      <div className="g1" />

      {/* Pulse rings */}
      <div style={{ position: "relative", width: "64px", height: "64px" }}>
        <div className="pulse-ring-1" />
        <div className="pulse-ring-2" />
        {/* Spinner */}
        <div style={{
          position: "absolute", inset: "16px",
          borderRadius: "50%",
          border: "2px solid rgba(52,211,153,0.1)",
          borderTopColor: "#34d399",
          animation: "rs .75s linear infinite",
        }} />
      </div>

      {/* Label */}
      <div style={{ textAlign: "center" }}>
        <p style={{ fontSize: "15px", fontWeight: 600, color: "#e2e8f0", marginBottom: "4px" }}>
          Analyzing your meal...
        </p>
        <p style={{ fontSize: "12px", color: "#334155" }}>This may take a few seconds</p>
      </div>

      {/* Steps */}
      <div style={{ display: "flex", flexDirection: "column", gap: "10px", width: "220px" }}>
        {STEPS.map((step, i) => {
          const isDone = doneSteps.includes(i);
          const isActive = activeStep === i;
          const isIdle = !isDone && !isActive;

          return (
            <div
              key={step}
              style={{
                display: "flex", alignItems: "center", gap: "10px",
                fontSize: "12px",
                color: isDone ? "#34d399" : isActive ? "#e2e8f0" : "#1e293b",
                transition: "color .35s",
              }}
            >
              {/* Step indicator */}
              <div style={{ width: "18px", height: "18px", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                {isDone ? (
                  /* Checkmark */
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="7" fill="rgba(16,185,129,0.1)" stroke="#10b981" strokeWidth="1" />
                    <path d="M5 8l2 2 4-4" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : isActive ? (
                  /* Spinner */
                  <div style={{ width: "11px", height: "11px", borderRadius: "50%", border: "1.5px solid rgba(148,163,184,0.12)", borderTopColor: "#475569", animation: "rs .7s linear infinite" }} />
                ) : (
                  /* Dot */
                  <div style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#1e293b", margin: "auto" }} />
                )}
              </div>
              {step}
            </div>
          );
        })}
      </div>
    </div>
  );
}
