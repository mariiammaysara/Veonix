"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import IntroScreen from "@/components/IntroScreen";
import Navbar from "@/components/navbar";

// TODO: replace with real values once tracked (see analytics/usage data)
const STATS = [
  { value: "—", label: "Meals Logged", color: "#34d399" },
  { value: "—", label: "Accuracy Rate", color: "#38bdf8" },
  { value: "—", label: "Average Analysis", color: "#34d399" },
  { value: "—", label: "Privacy Protection", color: "#fb7185" }
];

export default function Home() {
  const [showContent, setShowContent] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (showContent) {
      const t = setTimeout(() => setLoaded(true), 250);
      return () => clearTimeout(t);
    }
  }, [showContent]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        // Allow resetting/escaping intro screen state if needed
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  if (!showContent) return <IntroScreen onComplete={() => setShowContent(true)} />;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 flex flex-col relative overflow-x-hidden" style={{
      backgroundImage: `
        radial-gradient(circle at 15% 15%, rgba(16, 185, 129, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(56, 189, 248, 0.02) 0%, transparent 45%),
        linear-gradient(rgba(255, 255, 255, 0.003) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.003) 1px, transparent 1px)
      `,
      backgroundSize: "100% 100%, 100% 100%, 80px 80px, 80px 80px"
    }}>

      {/* Global Floating background particles */}
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none", overflow: "hidden", zIndex: 0 }}>
        {[
          { top: "15%", left: "10%", size: "4px", delay: "0s", dur: "14s" },
          { top: "35%", left: "80%", size: "6px", delay: "3s", dur: "18s" },
          { top: "60%", left: "22%", size: "3px", delay: "1.5s", dur: "16s" },
          { top: "78%", left: "75%", size: "5px", delay: "4s", dur: "15s" },
          { top: "92%", left: "12%", size: "4px", delay: "2s", dur: "17s" },
        ].map((pt, idx) => (
          <div
            key={idx}
            style={{
              position: "absolute",
              top: pt.top,
              left: pt.left,
              width: pt.size,
              height: pt.size,
              borderRadius: "50%",
              background: "rgba(52, 211, 153, 0.2)",
              boxShadow: "0 0 8px rgba(52, 211, 153, 0.4)",
              pointerEvents: "none",
              animation: `float ${pt.dur} ease-in-out infinite`,
              animationDelay: pt.delay,
            }}
          />
        ))}
      </div>
      
      {/* ── 1. Hero Section ── */}
      <section style={{ position: "relative", width: "100%", overflow: "hidden", minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        
        {/* Floating background food icons limited to Hero */}
        <div style={{ position: "absolute", inset: 0, pointerEvents: "none", overflow: "hidden", zIndex: 0 }}>
          {[
            { icon: "apple", top: "12%", left: "6%", size: 20, delay: 0, dur: 14 },
            { icon: "carrot", top: "18%", left: "90%", size: 18, delay: 2, dur: 12 },
            { icon: "dumbbell", top: "45%", left: "4%", size: 22, delay: 1, dur: 16 },
            { icon: "zap", top: "14%", left: "48%", size: 16, delay: 3, dur: 10 },
            { icon: "flame", top: "50%", left: "92%", size: 18, delay: 0.5, dur: 13 },
            { icon: "salad", top: "72%", left: "8%", size: 20, delay: 2.5, dur: 15 },
            { icon: "scale", top: "80%", left: "88%", size: 18, delay: 1.5, dur: 11 },
            { icon: "banana", top: "60%", left: "52%", size: 18, delay: 3.5, dur: 12 },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                top: item.top,
                left: item.left,
                opacity: 0.06,
                animation: `float ${item.dur}s ease-in-out infinite`,
                animationDelay: `${item.delay}s`,
              }}
            >
              <FloatingIcon name={item.icon} size={item.size} />
            </div>
          ))}
        </div>

        <Navbar />

        {/* Hero grid */}
        <div style={{
          width: "100%",
          maxWidth: "1100px",
          margin: "0 auto",
          padding: "40px 24px",
          position: "relative",
          zIndex: 1,
          flex: 1,
          display: "grid",
          alignContent: "center"
        }} className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          
          {/* Left Column: Headline copy */}
          <div style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <div className="g1" /><div className="g2" />
            
            {/* Logo */}
            <div className="anim-fade-up" style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
              <svg width="34" height="34" viewBox="0 0 100 100" fill="none">
                <path d="M20 75L50 20L80 75" stroke="#10b981" strokeWidth="9" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="50" cy="55" r="7" fill="#10b981" />
              </svg>
              <span style={{ fontSize: "28px", fontWeight: 800, color: "#fff", letterSpacing: "-1px" }}>Veonix</span>
            </div>

            {/* Title */}
            <h1 className="anim-fade-up delay-1" style={{ fontSize: "clamp(32px, 5vw, 48px)", fontWeight: 800, lineHeight: 1.15, letterSpacing: "-1.5px", color: "#f1f5f9", marginBottom: "16px" }}>
              AI{" "}
              <span style={{ background: "linear-gradient(90deg,#34d399,#22d3ee)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                Nutrition
              </span>{" "}
              Analyzer
            </h1>

            {/* Subtitle */}
            <p className="anim-fade-up delay-2" style={{ fontSize: "16px", color: "#64748b", lineHeight: 1.6, marginBottom: "32px", maxWidth: "480px" }}>
              Snap your meal and get instant nutritional data. Built on advanced multimodal AI to track your diet with absolute precision.
            </p>

            {/* Buttons */}
            <div className="anim-fade-up delay-3" style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
              <Link href="/dashboard/upload" className="btn-glow" style={{
                padding: "14px 32px", background: "#10b981", border: "none", borderRadius: "99px",
                color: "#020617", fontSize: "14px", fontWeight: 700, textDecoration: "none", transition: "all .15s",
                boxShadow: "0 4px 20px rgba(16, 185, 129, 0.2)"
              }}>Upload Your Meal</Link>
              <Link href="/dashboard/history" style={{
                padding: "14px 32px", background: "transparent", border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "99px", color: "rgba(255,255,255,0.65)", fontSize: "14px", fontWeight: 500, textDecoration: "none",
                transition: "all .15s"
              }} className="hover:border-slate-700 hover:text-slate-100">View History</Link>
            </div>
          </div>

          {/* Right Column: Signature visual preview card */}
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
            <div className="anim-fade-up anim-float delay-2" style={{
              width: "100%", maxWidth: "460px",
              background: "rgba(20,32,58,0.65)", border: "1px solid rgba(16,185,129,0.12)",
              borderRadius: "20px", padding: "22px", display: "flex", flexDirection: "column", gap: "16px",
              boxShadow: "0 20px 40px rgba(0,0,0,0.3)", backdropFilter: "blur(12px)"
            }}>
              {/* Mock photo with sweep scan line */}
              <div style={{
                position: "relative", width: "100%", height: "160px", borderRadius: "12px",
                background: "linear-gradient(135deg, rgba(16,185,129,0.06), rgba(56,189,248,0.08))",
                display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden",
                border: "1px solid rgba(255,255,255,0.04)"
              }}>
                <div className="scan-line" />
                <svg width="100%" height="100%" viewBox="0 0 200 160" fill="none" style={{ position: "absolute", inset: 0 }}>
                  {/* Plate */}
                  <ellipse cx="100" cy="80" rx="94" ry="68" fill="rgba(255,255,255,0.035)" stroke="rgba(255,255,255,0.1)" strokeWidth="1.5" />
                  <ellipse cx="100" cy="80" rx="74" ry="52" fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.07)" strokeWidth="1" />

                  {/* Asparagus spears (behind the fillet) */}
                  <g strokeLinecap="round">
                    <path d="M120 108l18-40" stroke="#34d399" strokeWidth="5" />
                    <path d="M130 112l16-42" stroke="#34d399" strokeWidth="5" />
                    <path d="M140 116l14-40" stroke="#34d399" strokeWidth="5" />
                    <path d="M138 68l4 8-8 2z" fill="#34d399" stroke="none" />
                    <path d="M148 66l4 8-8 2z" fill="#34d399" stroke="none" />
                    <path d="M156 68l4 8-8 2z" fill="#34d399" stroke="none" />
                  </g>

                  {/* Salmon fillet */}
                  <path
                    d="M52 78c-2-18 16-34 40-34 22 0 42 12 46 30 4 17-10 34-34 38-24 4-50-14-52-34z"
                    fill="#fb7654" fillOpacity="0.85" stroke="#fdba8c" strokeWidth="1.5" strokeLinejoin="round"
                  />
                  <path
                    d="M60 70c8 4 14 12 16 22M74 60c10 4 18 14 20 26M90 56c10 5 18 16 19 28M106 58c8 6 14 15 14 24"
                    stroke="#fff7ed" strokeOpacity="0.35" strokeWidth="1.5" strokeLinecap="round"
                  />

                  {/* Lemon wedge */}
                  <path d="M44 118a18 18 0 0 1 26-26z" fill="#fde047" fillOpacity="0.9" stroke="#fef08a" strokeWidth="1.5" strokeLinejoin="round" />
                  <path d="M49 113a11 11 0 0 1 14-14" stroke="#fef9c3" strokeOpacity="0.8" strokeWidth="1" />
                  <path d="M46 116l3-3M50 120l3-3M54 124l3-3" stroke="#fef08a" strokeOpacity="0.6" strokeWidth="1" />

                  {/* Herb garnish */}
                  <circle cx="90" cy="48" r="2.2" fill="#4ade80" />
                  <circle cx="100" cy="44" r="1.8" fill="#4ade80" fillOpacity="0.85" />
                  <circle cx="80" cy="46" r="1.6" fill="#4ade80" fillOpacity="0.8" />
                </svg>
              </div>

              {/* Title & Calories */}
              <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "17px", fontWeight: 700, color: "#f1f5f9", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>Grilled Salmon Plate</div>
                  <div style={{ fontSize: "12px", color: "#475569", marginTop: "2px" }}>Mediterranean · Dinner · ~350g</div>
                </div>
                <div style={{
                  display: "inline-flex", alignItems: "center", gap: "4px", padding: "6px 12px",
                  background: "rgba(249,115,22,0.06)", border: "1px solid rgba(249,115,22,0.14)", borderRadius: "8px", flexShrink: 0
                }}>
                  <span className="num-reveal delay-3" style={{ fontSize: "20px", fontWeight: 700, color: "#fb923c" }}>520</span>
                  <span style={{ fontSize: "11px", color: "rgba(251,146,60,0.45)" }}>kcal</span>
                </div>
              </div>

              {/* Macro bars */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
                {[
                  { label: "Protein", val: "42g", pct: 70, color: "#38bdf8" },
                  { label: "Carbs", val: "12g", pct: 20, color: "#fbbf24" },
                  { label: "Fat", val: "32g", pct: 53, color: "#fb7185" },
                ].map((mac, i) => (
                  <div key={mac.label} style={{
                    background: "rgba(20,32,58,0.4)", border: "1px solid rgba(255,255,255,0.04)",
                    borderRadius: "12px", padding: "12px 10px"
                  }}>
                    <span style={{ fontSize: "16px", fontWeight: 700, color: mac.color }}>{mac.val}</span>
                    <div style={{ fontSize: "9px", color: "#475569", textTransform: "uppercase", letterSpacing: ".05em", marginTop: "2px" }}>{mac.label}</div>
                    <div style={{ height: "3px", background: "rgba(255,255,255,0.03)", borderRadius: "1px", marginTop: "4px", overflow: "hidden" }}>
                      <div
                        className={`bar-fill ${loaded ? 'loaded' : ''}`}
                        style={{ "--bar-width": `${mac.pct}%`, background: mac.color } as React.CSSProperties}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. How It Works ── */}
      <section style={{ width: "100%", borderTop: "1px solid rgba(255,255,255,0.03)", position: "relative", overflow: "hidden" }}>
        
        {/* Subtle background radial glow */}
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "700px",
          height: "450px",
          background: "radial-gradient(circle, rgba(16,185,129,0.03) 0%, rgba(56,189,248,0.01) 50%, transparent 70%)",
          filter: "blur(60px)",
          pointerEvents: "none",
          zIndex: 0
        }} />

        <div style={{ width: "100%", maxWidth: "980px", margin: "0 auto", padding: "40px 24px", position: "relative", zIndex: 1 }}>
          
          <div style={{ textAlign: "center", marginBottom: "40px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#34d399", textTransform: "uppercase", letterSpacing: "0.15em", display: "block", marginBottom: "8px" }}>How It Works</span>
            <h2 style={{ fontSize: "28px", fontWeight: 700, color: "#f1f5f9" }}>From plate to macros in three steps</h2>
          </div>

          <div style={{ gap: "24px", position: "relative" }} className="grid grid-cols-1 md:grid-cols-3">
            
            {/* Connecting line */}
            <div style={{
              position: "absolute",
              top: "50px",
              left: "15%",
              right: "15%",
              height: "2px",
              background: "linear-gradient(90deg, transparent, rgba(52,211,153,0.15) 20%, rgba(52,211,153,0.15) 80%, transparent)",
              zIndex: 0
            }} className="hidden md:block" />

            {[
              {
                step: "01",
                title: "Snap a photo",
                desc: "Take or upload a picture of a meal from any device.",
                icon: (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                    <circle cx="12" cy="13" r="4" />
                  </svg>
                )
              },
              {
                step: "02",
                title: "Gemini Vision analyzes it",
                desc: "Identifies the food and estimates calories, protein, carbs, and fat.",
                icon: (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2z" />
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                )
              },
              {
                step: "03",
                title: "Track it over time",
                desc: "Every analyzed meal is automatically logged to your dashboard database.",
                icon: (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                )
              }
            ].map((st, i) => (
              <div key={st.step} className="card-hover" style={{
                background: "rgba(20,32,58,0.6)", border: "1px solid rgba(16,185,129,0.1)",
                borderRadius: "16px", padding: "28px 24px", backdropFilter: "blur(8px)",
                position: "relative", zIndex: 1
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                  <div style={{
                    width: "52px", height: "52px", borderRadius: "14px",
                    background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.18)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    position: "relative", zIndex: 2
                  }}>
                    {st.icon}
                  </div>
                  <span style={{ fontSize: "13px", fontWeight: 700, color: "#475569" }}>{st.step}</span>
                </div>
                <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#f1f5f9", marginBottom: "8px" }}>{st.title}</h3>
                <p style={{ fontSize: "13px", color: "#64748b", lineHeight: 1.5 }}>{st.desc}</p>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ── 3. Features ── */}
      <section style={{ width: "100%", borderTop: "1px solid rgba(255,255,255,0.03)", position: "relative", overflow: "hidden" }}>
        
        {/* Subtle background radial glow */}
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "800px",
          height: "450px",
          background: "radial-gradient(circle, rgba(56,189,248,0.02) 0%, rgba(16,185,129,0.005) 50%, transparent 70%)",
          filter: "blur(70px)",
          pointerEvents: "none",
          zIndex: 0
        }} />

        <div style={{ width: "100%", maxWidth: "1100px", margin: "0 auto", padding: "40px 24px", position: "relative", zIndex: 1 }}>
          
          <div style={{ textAlign: "center", marginBottom: "40px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#34d399", textTransform: "uppercase", letterSpacing: "0.15em", display: "block", marginBottom: "8px" }}>Why Veonix</span>
            <h2 style={{ fontSize: "28px", fontWeight: 700, color: "#f1f5f9" }}>Built to be quick, accurate, and yours</h2>
          </div>

          <div style={{ gap: "24px" }} className="grid grid-cols-1 md:grid-cols-3">
            {[
              {
                title: "Fast Analysis",
                sub: "Analyze meals in less than 2 seconds.",
                color: "#34d399",
                bg: "rgba(52,211,153,0.08)",
                icon: (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                  </svg>
                )
              },
              {
                title: "AI Powered",
                sub: "Powered by Gemini Vision.",
                color: "#38bdf8",
                bg: "rgba(56,189,248,0.08)",
                icon: (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="4" y="4" width="16" height="16" rx="2" />
                    <path d="M9 9h6v6H9zM9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 15h3M1 9h3M1 15h3" />
                  </svg>
                )
              },
              {
                title: "Privacy First",
                sub: "Images are processed securely.",
                color: "#34d399",
                bg: "rgba(52,211,153,0.08)",
                icon: (
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                )
              }
            ].map((ft) => (
              <div key={ft.title} className="card-hover" style={{
                background: "rgba(20,32,58,0.6)", border: "1px solid rgba(16,185,129,0.1)",
                borderRadius: "16px", padding: "32px 24px", display: "flex", flexDirection: "column",
                alignItems: "center", gap: "12px", position: "relative", overflow: "hidden", backdropFilter: "blur(8px)"
              }}>
                <div style={{ position: "absolute", top: 0, left: "25%", right: "25%", height: "1px", background: `linear-gradient(90deg, transparent, ${ft.color}, transparent)` }} />
                <div style={{
                  width: "52px", height: "52px", borderRadius: "14px",
                  background: ft.bg, border: `1px solid ${ft.color}25`,
                  display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "4px"
                }}>
                  {ft.icon}
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "16px", fontWeight: 700, color: ft.color, letterSpacing: ".02em" }}>{ft.title}</div>
                  <div style={{ fontSize: "13px", color: "#64748b", marginTop: "6px", lineHeight: 1.5 }}>{ft.sub}</div>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ── 9. Statistics Section ── */}
      <section style={{ width: "100%", borderTop: "1px solid rgba(255,255,255,0.03)", position: "relative", overflow: "hidden" }}>
        
        {/* Subtle background radial glow */}
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "700px",
          height: "400px",
          background: "radial-gradient(circle, rgba(16,185,129,0.02) 0%, rgba(56,189,248,0.005) 50%, transparent 70%)",
          filter: "blur(60px)",
          pointerEvents: "none",
          zIndex: 0
        }} />

        <div style={{ width: "100%", maxWidth: "1100px", margin: "0 auto", padding: "60px 24px", position: "relative", zIndex: 1 }}>
          <div style={{ textAlign: "center", marginBottom: "40px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#34d399", textTransform: "uppercase", letterSpacing: "0.15em", display: "block", marginBottom: "8px" }}>Veonix by the numbers</span>
            <h2 style={{ fontSize: "28px", fontWeight: 700, color: "#f1f5f9" }}>Proven performance, complete security</h2>
          </div>

          <div style={{ gap: "24px" }} className="grid grid-cols-2 lg:grid-cols-4">
            {STATS.map((stat, i) => (
              <div key={stat.label} className="card-hover" style={{
                background: "rgba(20,32,58,0.6)", border: "1px solid rgba(255,255,255,0.04)",
                borderRadius: "16px", padding: "32px 20px", display: "flex", flexDirection: "column",
                alignItems: "center", justifyContent: "center", gap: "8px", backdropFilter: "blur(8px)"
              }}>
                <span style={{ fontSize: "clamp(24px, 4vw, 36px)", fontWeight: 800, color: stat.color, letterSpacing: "-1px" }}>{stat.value}</span>
                <span style={{ fontSize: "12px", color: "#64748b", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em", textAlign: "center" }}>{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 5. Final CTA ── */}
      <section style={{ width: "100%", borderTop: "1px solid rgba(255,255,255,0.03)" }}>
        <div style={{ width: "100%", maxWidth: "1100px", margin: "0 auto", padding: "60px 24px" }}>
          
          <div className="anim-scale-in" style={{
            width: "100%", maxWidth: "800px", margin: "0 auto",
            background: "linear-gradient(135deg, rgba(16,185,129,0.04), rgba(56,189,248,0.04))",
            border: "1px solid rgba(52,211,153,0.12)", borderRadius: "24px", padding: "48px 32px",
            textAlign: "center", position: "relative", overflow: "hidden", boxShadow: "0 12px 32px rgba(0,0,0,0.2)"
          }}>
            {/* Soft internal gradient background glow */}
            <div style={{ position: "absolute", top: "-50px", left: "-50px", width: "100px", height: "100px", background: "rgba(16,185,129,0.06)", borderRadius: "50%", filter: "blur(40px)" }} />
            
            <h2 style={{ fontSize: "24px", fontWeight: 700, color: "#f1f5f9", marginBottom: "8px" }}>Start tracking your nutrition with AI.</h2>
            <p style={{ fontSize: "14px", color: "#64748b", maxWidth: "440px", margin: "0 auto 28px", lineHeight: 1.5 }}>
              Upload your first meal in seconds.
            </p>
            <Link href="/dashboard/upload" className="btn-glow" style={{
              display: "inline-block", padding: "14px 36px", background: "#10b981", border: "none", borderRadius: "99px",
              color: "#020617", fontSize: "14px", fontWeight: 700, textDecoration: "none", transition: "all .15s",
              boxShadow: "0 4px 20px rgba(16, 185, 129, 0.2)"
            }}>Analyze My Meal →</Link>
          </div>

        </div>
      </section>

      {/* ── 6. Footer ── */}
      <footer style={{
        borderTop: "1px solid rgba(255,255,255,0.04)",
        padding: "48px clamp(24px, 5vw, 64px) 32px",
        background: "rgba(2,6,23,0.7)",
        backdropFilter: "blur(12px)",
        position: "relative",
        zIndex: 1,
        marginTop: "80px"
      }}>
        <div style={{
          maxWidth: "1100px",
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "1fr",
          gap: "32px"
        }} className="md:grid-cols-3 items-start">
          
          {/* Column 1: Brand */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <svg width="24" height="24" viewBox="0 0 100 100" fill="none">
                <path d="M20 75L50 20L80 75" stroke="#10b981" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="50" cy="55" r="7" fill="#10b981" />
              </svg>
              <span style={{ fontSize: "18px", fontWeight: 800, color: "#fff", letterSpacing: "-0.5px" }}>Veonix</span>
            </div>
            <p style={{ fontSize: "13px", color: "#64748b", lineHeight: 1.5, maxWidth: "240px" }}>
              AI-powered nutrition analysis and tracking.
            </p>
          </div>

          {/* Column 2: Product */}
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>Product</span>
            <Link href="/dashboard/upload" style={{ fontSize: "13px", color: "#94a3b8", textDecoration: "none" }} className="hover:text-emerald-400 transition-colors">Upload</Link>
            <Link href="/dashboard/history" style={{ fontSize: "13px", color: "#94a3b8", textDecoration: "none" }} className="hover:text-emerald-400 transition-colors">History</Link>
          </div>

          {/* Column 3: Connect */}
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: "0.1em" }}>Connect</span>
            <a href="https://github.com/mariiammaysara/Veonix" target="_blank" rel="noopener noreferrer" style={{ fontSize: "13px", color: "#94a3b8", textDecoration: "none" }} className="hover:text-emerald-400 transition-colors">GitHub</a>
            <a href="https://www.linkedin.com/in/mariam-maysara/" target="_blank" rel="noopener noreferrer" style={{ fontSize: "13px", color: "#94a3b8", textDecoration: "none" }} className="hover:text-emerald-400 transition-colors">LinkedIn</a>
          </div>

        </div>

        {/* Thin top border & copyright */}
        <div style={{
          maxWidth: "1100px",
          margin: "32px auto 0",
          paddingTop: "24px",
          borderTop: "1px solid rgba(255, 255, 255, 0.04)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px"
        }}>
          <span style={{ fontSize: "13px", color: "#64748b" }}>
            &copy; 2026 Veonix. Built by{" "}
            <a
              href="https://www.linkedin.com/in/mariam-maysara/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#34d399", fontWeight: 600, textDecoration: "none" }}
              className="hover:text-emerald-400 transition-colors"
            >
              Mariam Maysara
            </a>
            .
          </span>
        </div>
      </footer>

    </div>
  );
}

function FloatingIcon({ name, size }: { name: string; size: number }) {
  const icons: Record<string, React.ReactNode> = {
    apple: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20.94c1.5 0 4-1.5 4-8.94a4 4 0 0 0-8 0c0 7.44 2.5 8.94 4 8.94z" />
        <path d="M12 7a2 2 0 0 1 2-2c0 1.5-1 2-2 2z" />
      </svg>
    ),
    carrot: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2.27 21.73L13 11M8.5 8.5c2-2 5-2 7 0s2 5 0 7l-7-7z" />
        <path d="M8.5 8.5L5 5M15.5 8.5l3-3M12 5.5l1-3" />
      </svg>
    ),
    dumbbell: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M6 5v14M18 5v14M6 8H2v8h4M18 8h4v8h-4M6 12h12" />
      </svg>
    ),
    zap: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
      </svg>
    ),
    flame: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M8.5 14.5A2.5 2.5 0 0 0 11 17c1.38 0 2.5-1.12 2.5-2.5 0-1.5-1-2.5-2-4-.5 1.5-2 2.5-2 4zM12 2c0 0-4 4-4 8a4 4 0 0 0 8 0c0-3-2-6-4-8z" />
      </svg>
    ),
    salad: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M7 20h10M12 20v-8M5 12c0-4 3-7 7-7s7 3 7 7" />
        <path d="M5 12h14" />
      </svg>
    ),
    scale: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3v17M5 20h14M5 7l7-4 7 4M5 12l7-4 7 4" />
      </svg>
    ),
    banana: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 13c3.5-2 8-3 11-1s5 7 2 10M4 13c-1.5 3 0 7 3 8M4 13c2-3 5-5 8-4" />
      </svg>
    ),
  };

  return icons[name] || null;
}
