"use client";

import { useState } from "react";
import Link from "next/link";
import IntroScreen from "@/components/IntroScreen";
import Navbar from "@/components/navbar";

export default function Home() {
  const [showContent, setShowContent] = useState(false);

  if (!showContent) return <IntroScreen onComplete={() => setShowContent(true)} />;

  return (
    <div className="h-screen bg-[#020617] text-slate-100 flex flex-col overflow-hidden">

      {/* Floating background icons */}
      <div style={{
        position: "fixed", inset: 0,
        pointerEvents: "none", overflow: "hidden",
        zIndex: 0,
      }}>
        {[
          // [icon_path, top%, left%, size, delay, duration]
          { icon: "apple", top: "8%", left: "8%", size: 20, delay: 0, dur: 14 },
          { icon: "carrot", top: "15%", left: "88%", size: 18, delay: 2, dur: 12 },
          { icon: "dumbbell", top: "28%", left: "4%", size: 22, delay: 1, dur: 16 },
          { icon: "zap", top: "12%", left: "45%", size: 16, delay: 3, dur: 10 },
          { icon: "flame", top: "40%", left: "92%", size: 18, delay: 0.5, dur: 13 },
          { icon: "salad", top: "65%", left: "6%", size: 20, delay: 2.5, dur: 15 },
          { icon: "scale", top: "75%", left: "90%", size: 18, delay: 1.5, dur: 11 },
          { icon: "heart", top: "82%", left: "35%", size: 16, delay: 4, dur: 14 },
          { icon: "banana", top: "55%", left: "50%", size: 18, delay: 3.5, dur: 12 },
          { icon: "activity", top: "88%", left: "72%", size: 20, delay: 1, dur: 16 },
          { icon: "utensils", top: "30%", left: "70%", size: 18, delay: 2, dur: 13 },
          { icon: "droplets", top: "50%", left: "20%", size: 16, delay: 0, dur: 15 },
        ].map((item, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              top: item.top,
              left: item.left,
              opacity: 0.07,
              animation: `float ${item.dur}s ease-in-out infinite`,
              animationDelay: `${item.delay}s`,
            }}
          >
            <FloatingIcon name={item.icon} size={item.size} />
          </div>
        ))}
      </div>

      <Navbar />

      {/* Home content */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "80px 20px 28px", position: "relative", overflow: "hidden" }}>
        <div className="g1" /><div className="g2" />

        {/* Logo — float */}
        <div className="anim-fade-up anim-float" style={{ display: "flex", alignItems: "center", gap: "11px", marginBottom: "18px" }}>
          <svg width="clamp(32px, 5vw, 48px)" height="clamp(32px, 5vw, 48px)" viewBox="0 0 100 100" fill="none">
            <path d="M20 75L50 20L80 75" stroke="#10b981" strokeWidth="9" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="50" cy="55" r="7" fill="#10b981" />
          </svg>
          <span style={{ fontSize: "clamp(34px, 6vw, 48px)", fontWeight: 800, color: "#fff", letterSpacing: "-1.5px" }}>Veonix</span>
        </div>

        {/* Title */}
        <h1 className="anim-fade-up delay-1" style={{ fontSize: "clamp(25px, 4vw, 36px)", fontWeight: 700, textAlign: "center", lineHeight: 1.3, marginBottom: "6px", color: "#f1f5f9" }}>
          AI{" "}
          <em style={{ fontStyle: "normal", background: "linear-gradient(90deg,#34d399,#22d3ee)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            Nutrition
          </em>{" "}
          Analyzer
        </h1>
        <p className="anim-fade-up delay-2" style={{ fontSize: "clamp(13px, 1.5vw, 15px)", color: "#475569", textAlign: "center", marginBottom: "32px", letterSpacing: ".04em", maxWidth: "450px" }}>
          Snap your meal and get instant nutritional data.
        </p>

        {/* Buttons */}
        <div className="anim-fade-up delay-3" style={{ display: "flex", gap: "12px", flexWrap: "wrap", justifyContent: "center", marginBottom: "36px" }}>
          <Link href="/dashboard/upload" className="btn-glow" style={{
            padding: "clamp(10px, 1.5vh, 14px) clamp(26px, 3vw, 36px)", background: "#10b981", border: "none", borderRadius: "99px",
            color: "#020617", fontSize: "clamp(13px, 1.5vw, 15px)", fontWeight: 700, textDecoration: "none", transition: "all .15s",
            boxShadow: "0 4px 20px rgba(16, 185, 129, 0.2)"
          }}>Upload Your Meal</Link>
          <Link href="/dashboard/history" style={{
            padding: "clamp(10px, 1.5vh, 14px) clamp(26px, 3vw, 36px)", background: "transparent", border: "1px solid rgba(255,255,255,0.09)",
            borderRadius: "99px", color: "rgba(255,255,255,0.5)", fontSize: "clamp(13px, 1.5vw, 15px)", fontWeight: 500, textDecoration: "none"
          }}>View History</Link>
        </div>

        {/* Feature cards */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "10px",
          width: "100%",
          maxWidth: "min(480px, 100%)",
          marginTop: "8px",
        }}>

          {/* FAST */}
          <div className="card-hover anim-fade-up delay-4" style={{
            background: "rgba(15,23,42,0.6)",
            border: "1px solid rgba(255,255,255,0.05)",
            borderRadius: "16px",
            padding: "24px 14px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "8px",
            position: "relative",
            overflow: "hidden",
          }}>
            {/* Top accent line */}
            <div style={{ position: "absolute", top: 0, left: "20%", right: "20%", height: "1px", background: "linear-gradient(90deg, transparent, #34d399, transparent)" }} />
            {/* Icon */}
            <div style={{
              width: "36px", height: "36px", borderRadius: "10px",
              background: "rgba(52,211,153,0.08)",
              border: "1px solid rgba(52,211,153,0.15)",
              display: "flex", alignItems: "center", justifyContent: "center",
              position: "relative",
            }}>
              <div style={{ position: "absolute", inset: 0, borderRadius: "10px", background: "rgba(52,211,153,0.05)", filter: "blur(8px)" }} />
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: "relative", zIndex: 1 }}>
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
              </svg>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#94a3b8", letterSpacing: ".08em", textTransform: "uppercase" }}>Fast</div>
              <div style={{ fontSize: "10px", color: "#334155", marginTop: "2px" }}>Real-time AI</div>
            </div>
          </div>

          {/* SMART — center card, slightly elevated */}
          <div className="card-hover anim-fade-up delay-5" style={{
            background: "rgba(16,185,129,0.05)",
            border: "1px solid rgba(52,211,153,0.15)",
            borderRadius: "16px",
            padding: "24px 14px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "8px",
            position: "relative",
            overflow: "hidden",
          }}>
            {/* Top accent line — brighter */}
            <div style={{ position: "absolute", top: 0, left: "10%", right: "10%", height: "1px", background: "linear-gradient(90deg, transparent, #10b981, transparent)" }} />
            {/* Subtle bg glow */}
            <div style={{ position: "absolute", top: "-20px", left: "50%", transform: "translateX(-50%)", width: "80px", height: "80px", background: "rgba(16,185,129,0.08)", borderRadius: "50%", filter: "blur(20px)", pointerEvents: "none" }} />
            {/* Icon */}
            <div style={{
              width: "36px", height: "36px", borderRadius: "10px",
              background: "rgba(16,185,129,0.12)",
              border: "1px solid rgba(16,185,129,0.25)",
              display: "flex", alignItems: "center", justifyContent: "center",
              position: "relative",
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: "relative", zIndex: 1 }}>
                <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2z" />
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#34d399", letterSpacing: ".08em", textTransform: "uppercase" }}>Smart</div>
              <div style={{ fontSize: "11px", color: "#475569", marginTop: "3px" }}>
                Powered by{" "}
                <span style={{ color: "#10b981", fontWeight: 600 }}>Gemini Vision</span>
              </div>
            </div>
          </div>

          {/* SECURE */}
          <div className="card-hover anim-fade-up delay-6" style={{
            background: "rgba(15,23,42,0.6)",
            border: "1px solid rgba(255,255,255,0.05)",
            borderRadius: "16px",
            padding: "24px 14px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "8px",
            position: "relative",
            overflow: "hidden",
          }}>
            {/* Top accent line */}
            <div style={{ position: "absolute", top: 0, left: "20%", right: "20%", height: "1px", background: "linear-gradient(90deg, transparent, #38bdf8, transparent)" }} />
            {/* Icon */}
            <div style={{
              width: "36px", height: "36px", borderRadius: "10px",
              background: "rgba(56,189,248,0.08)",
              border: "1px solid rgba(56,189,248,0.15)",
              display: "flex", alignItems: "center", justifyContent: "center",
              position: "relative",
            }}>
              <div style={{ position: "absolute", inset: 0, borderRadius: "10px", background: "rgba(56,189,248,0.05)", filter: "blur(8px)" }} />
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ position: "relative", zIndex: 1 }}>
                <rect x="3" y="11" width="18" height="11" rx="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#94a3b8", letterSpacing: ".08em", textTransform: "uppercase" }}>Secure</div>
              <div style={{ fontSize: "10px", color: "#334155", marginTop: "2px" }}>Private & safe</div>
            </div>
          </div>

        </div>
      </div>

      <footer style={{
        borderTop: "1px solid rgba(255,255,255,0.04)",
        padding: "12px clamp(20px, 4vw, 48px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexShrink: 0,
        position: "relative",
      }}>
        {/* Left — empty spacer */}
        <div style={{ width: "80px" }} />

        {/* Center — © + logo + name */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <svg width="13" height="13" viewBox="0 0 100 100" fill="none">
            <path d="M20 75L50 20L80 75" stroke="#10b981" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="50" cy="55" r="7" fill="#10b981" />
          </svg>
          <span style={{ fontSize: "11px", color: "#334155" }}>
            Built by{" "}
            <a
              href="https://www.linkedin.com/in/mariam-maysara/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#34d399", fontWeight: 600, textDecoration: "none" }}
              className="hover:text-emerald-400 transition-colors"
            >
              Mariam Maysara
            </a>
          </span>
        </div>

        {/* Right — GitHub */}
        <a
          href="https://github.com/mariiammaysara/Veonix"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "flex", alignItems: "center", gap: "5px",
            padding: "4px 10px",
            background: "rgba(15,23,42,0.55)",
            border: "1px solid rgba(255,255,255,0.06)",
            borderRadius: "8px",
            color: "#475569", fontSize: "11px",
            fontWeight: 500, textDecoration: "none",
            width: "80px", justifyContent: "center",
          }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
          </svg>
          Source
        </a>
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
    heart: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
    ),
    banana: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 13c3.5-2 8-3 11-1s5 7 2 10M4 13c-1.5 3 0 7 3 8M4 13c2-3 5-5 8-4" />
      </svg>
    ),
    activity: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
    utensils: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7" />
      </svg>
    ),
    droplets: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z" />
        <path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97" />
      </svg>
    ),
  };

  return icons[name] || null;
}
