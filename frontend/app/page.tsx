"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import IntroScreen from "@/components/IntroScreen";
import Navbar from "@/components/navbar";

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
    <div className="min-h-screen bg-[#020617] text-slate-100 flex flex-col relative overflow-x-hidden">
      
      {/* ── 1. Hero Section ── */}
      <section style={{ position: "relative", width: "100%", overflow: "hidden" }}>
        
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
          padding: "120px 24px 80px",
          display: "grid",
          gridTemplateColumns: "1fr",
          gap: "48px",
          position: "relative",
          zIndex: 1,
        }} className="lg:grid-cols-2 items-center">
          
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
              width: "100%", maxWidth: "370px",
              background: "rgba(15,23,42,0.65)", border: "1px solid rgba(255,255,255,0.05)",
              borderRadius: "20px", padding: "18px", display: "flex", flexDirection: "column", gap: "12px",
              boxShadow: "0 20px 40px rgba(0,0,0,0.3)"
            }}>
              {/* Mock photo with sweep scan line */}
              <div style={{
                position: "relative", width: "100%", height: "130px", borderRadius: "12px",
                background: "linear-gradient(135deg, rgba(16,185,129,0.06), rgba(56,189,248,0.08))",
                display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden",
                border: "1px solid rgba(255,255,255,0.04)"
              }}>
                <div className="scan-line" />
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.7 }}>
                  <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7" />
                </svg>
              </div>

              {/* Title & Calories */}
              <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "15px", fontWeight: 700, color: "#f1f5f9", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>Grilled Salmon Plate</div>
                  <div style={{ fontSize: "11px", color: "#475569", marginTop: "2px" }}>Mediterranean · Dinner · ~350g</div>
                </div>
                <div style={{
                  display: "inline-flex", alignItems: "center", gap: "4px", padding: "4px 8px",
                  background: "rgba(249,115,22,0.06)", border: "1px solid rgba(249,115,22,0.14)", borderRadius: "8px", flexShrink: 0
                }}>
                  <span className="num-reveal delay-3" style={{ fontSize: "16px", fontWeight: 700, color: "#fb923c" }}>520</span>
                  <span style={{ fontSize: "10px", color: "rgba(251,146,60,0.45)" }}>kcal</span>
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
                    background: "rgba(15,23,42,0.45)", border: "1px solid rgba(255,255,255,0.03)",
                    borderRadius: "12px", padding: "10px 8px"
                  }}>
                    <span style={{ fontSize: "14px", fontWeight: 700, color: mac.color }}>{mac.val}</span>
                    <div style={{ fontSize: "9px", color: "#475569", textTransform: "uppercase", letterSpacing: ".05em", marginTop: "1px" }}>{mac.label}</div>
                    <div style={{ height: "2px", background: "rgba(255,255,255,0.03)", borderRadius: "1px", marginTop: "4px", overflow: "hidden" }}>
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
      <section style={{ width: "100%", borderTop: "1px solid rgba(255,255,255,0.03)" }}>
        <div style={{ width: "100%", maxWidth: "1100px", margin: "0 auto", padding: "80px 24px" }}>
          
          <div style={{ textAlign: "center", marginBottom: "48px" }}>
            <h2 style={{ fontSize: "28px", fontWeight: 700, color: "#f1f5f9" }}>How It Works</h2>
            <p style={{ fontSize: "14px", color: "#64748b", marginTop: "6px" }}>A clean, three-step automated tracking loop</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "24px" }} className="md:grid-cols-3">
            {[
              {
                step: "01",
                title: "Snap a photo",
                desc: "Take or upload a picture of a meal from any device.",
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                )
              }
            ].map((st, i) => (
              <div key={st.step} className="card-hover" style={{
                background: "rgba(15,23,42,0.55)", border: "1px solid rgba(255,255,255,0.04)",
                borderRadius: "16px", padding: "28px 24px"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                  <div style={{
                    width: "36px", height: "36px", borderRadius: "10px",
                    background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.18)",
                    display: "flex", alignItems: "center", justifyContent: "center"
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
      <section style={{ width: "100%", borderTop: "1px solid rgba(255,255,255,0.03)" }}>
        <div style={{ width: "100%", maxWidth: "1100px", margin: "0 auto", padding: "80px 24px" }}>
          
          <div style={{ textAlign: "center", marginBottom: "48px" }}>
            <h2 style={{ fontSize: "28px", fontWeight: 700, color: "#f1f5f9" }}>Key Features</h2>
            <p style={{ fontSize: "14px", color: "#64748b", marginTop: "6px" }}>Tailored tools for seamless daily nutrition tracking</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "20px" }} className="sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                title: "Fast",
                sub: "Real-time AI processing",
                color: "#34d399",
                bg: "rgba(52,211,153,0.08)",
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                  </svg>
                )
              },
              {
                title: "Smart",
                sub: "Powered by Gemini Vision",
                color: "#10b981",
                bg: "rgba(16,185,129,0.12)",
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 2v20M2 12h20" />
                  </svg>
                )
              },
              {
                title: "History",
                sub: "Saved and aggregated",
                color: "#38bdf8",
                bg: "rgba(56,189,248,0.08)",
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 8v4l3 3" />
                    <circle cx="12" cy="12" r="10" />
                  </svg>
                )
              },
              {
                title: "Private",
                sub: "Secure database protection",
                color: "#f472b6",
                bg: "rgba(244,114,182,0.08)",
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f472b6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                )
              }
            ].map((ft) => (
              <div key={ft.title} className="card-hover" style={{
                background: "rgba(15,23,42,0.55)", border: "1px solid rgba(255,255,255,0.04)",
                borderRadius: "16px", padding: "24px 18px", display: "flex", flexDirection: "column",
                alignItems: "center", gap: "8px", position: "relative", overflow: "hidden"
              }}>
                <div style={{ position: "absolute", top: 0, left: "25%", right: "25%", height: "1px", background: `linear-gradient(90deg, transparent, ${ft.color}, transparent)` }} />
                <div style={{
                  width: "36px", height: "36px", borderRadius: "10px",
                  background: ft.bg, border: `1px solid ${ft.color}25`,
                  display: "flex", alignItems: "center", justifyContent: "center"
                }}>
                  {ft.icon}
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "12px", fontWeight: 700, color: ft.color, letterSpacing: ".08em", textTransform: "uppercase" }}>{ft.title}</div>
                  <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>{ft.sub}</div>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ── 4. Built With ── */}
      <section style={{ width: "100%", borderTop: "1px solid rgba(255,255,255,0.03)" }}>
        <div style={{ width: "100%", maxWidth: "1100px", margin: "0 auto", padding: "40px 24px" }}>
          
          <div style={{ textAlign: "center", marginBottom: "16px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: "0.15em" }}>Built with</span>
          </div>

          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", justifyContent: "center" }}>
            {["FastAPI", "Next.js 15", "TypeScript", "Gemini Vision", "Docker", "Tailwind CSS"].map((tech) => (
              <span key={tech} style={{
                padding: "6px 16px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "99px", color: "#64748b", fontSize: "12px", fontWeight: 500
              }}>{tech}</span>
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
            
            <h2 style={{ fontSize: "24px", fontWeight: 700, color: "#f1f5f9", marginBottom: "8px" }}>Ready to see what is on your plate?</h2>
            <p style={{ fontSize: "14px", color: "#64748b", maxWidth: "440px", margin: "0 auto 28px", lineHeight: 1.5 }}>
              Snap your meal to receive instantly calculated macro ratios and logs.
            </p>
            <Link href="/dashboard/upload" className="btn-glow" style={{
              display: "inline-block", padding: "14px 36px", background: "#10b981", border: "none", borderRadius: "99px",
              color: "#020617", fontSize: "14px", fontWeight: 700, textDecoration: "none", transition: "all .15s",
              boxShadow: "0 4px 20px rgba(16, 185, 129, 0.2)"
            }}>Get Started</Link>
          </div>

        </div>
      </section>

      {/* ── 6. Footer ── */}
      <footer style={{
        borderTop: "1px solid rgba(255,255,255,0.04)",
        padding: "16px clamp(20px, 4vw, 48px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        width: "100%",
        marginTop: "40px",
        background: "rgba(2,6,23,0.4)",
        position: "relative",
        zIndex: 1,
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
    banana: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 13c3.5-2 8-3 11-1s5 7 2 10M4 13c-1.5 3 0 7 3 8M4 13c2-3 5-5 8-4" />
      </svg>
    ),
  };

  return icons[name] || null;
}
