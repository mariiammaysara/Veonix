"use client";

import Link from "next/link";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import { useMealHistory } from "@/hooks/use-meal-history";
import type { MealHistoryItem } from "@/lib/types";

/**
 * Veonix — Meal History Page
 * 
 * Displays a grid of previously analyzed meals with nutritional summaries.
 * Optimized for vertical spacing to prevent navbar overlap.
 */
export default function HistoryPage() {
  const { meals, total, loading, error, handleDelete } = useMealHistory();

  return (
    <div style={{ minHeight: "100vh", background: "#020617", color: "#f1f5f9", display: "flex", flexDirection: "column", position: "relative", overflowX: "hidden" }}>
      <div className="g1" />

      {/* Shared Floating Navbar */}
      <Navbar />

      {/* Page content — properly below navbar with 80px offset */}
      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        alignItems: "center", padding: "100px 20px 40px",
        position: "relative", gap: "32px", zIndex: 1
      }}>

        {/* Header */}
        <div className="anim-fade-up" style={{ textAlign: "center" }}>
          <h2 style={{ fontSize: "24px", fontWeight: 800, color: "#f1f5f9", marginBottom: "6px" }}>
            Your meal history
          </h2>
          <p style={{ fontSize: "14px", color: "#64748b" }}>
            {total} meal{total !== 1 ? "s" : ""} tracked so far
          </p>
        </div>

        {error && (
          <div style={{
            padding: "10px 16px", background: "rgba(239,68,68,0.06)",
            border: "1px solid rgba(239,68,68,0.15)", borderRadius: "10px",
            color: "#f87171", fontSize: "13px", fontWeight: 500,
          }}>
            {error}
          </div>
        )}

        {/* Grid Wrapper */}
        {loading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "12px", width: "100%", maxWidth: "900px" }}>
            {[...Array(4)].map((_, i) => (
              <div key={i} style={{
                height: "160px", borderRadius: "16px",
                background: "rgba(15,23,42,0.4)",
                border: "1px solid rgba(255,255,255,0.04)",
                animation: "pulse 2s infinite ease-in-out"
              }} />
            ))}
          </div>
        ) : meals.length === 0 ? (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "16px", paddingTop: "60px" }} className="anim-fade-up">
            <div style={{
              width: "60px", height: "60px", borderRadius: "20px",
              background: "rgba(15,23,42,0.6)", border: "1px solid rgba(255,255,255,0.05)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#334155" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 2h18M3 7h18M3 12h18M3 17h18M3 22h18" />
              </svg>
            </div>
            <p style={{ fontSize: "15px", color: "#64748b", fontWeight: 500 }}>No meals tracked yet</p>
            <Link href="/dashboard/upload" style={{
              padding: "10px 24px", background: "#10b981", borderRadius: "99px",
              color: "#020617", fontSize: "13px", fontWeight: 700, textDecoration: "none"
            }} className="btn-glow">
              Analyze your first meal
            </Link>
          </div>
        ) : (
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            gap: "16px",
            width: "100%",
            maxWidth: "1000px"
          }}>
            {meals.map((meal, i) => (
              <MealCard key={meal.id} meal={meal} onDelete={handleDelete} index={i} />
            ))}

            {/* Add meal card */}
            <Link href="/dashboard/upload" className="card-hover anim-fade-up delay-4" style={{
              background: "rgba(15,23,42,0.4)",
              border: "1px dashed rgba(255,255,255,0.08)",
              borderRadius: "20px", padding: "24px",
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              gap: "12px", textDecoration: "none", minHeight: "160px",
              transition: "all .3s"
            }}>
              <div style={{
                width: "44px", height: "44px", borderRadius: "14px",
                background: "rgba(16,185,129,0.05)", border: "1px solid rgba(16,185,129,0.12)",
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 5v14M5 12h14" />
                </svg>
              </div>
              <span style={{ fontSize: "13px", color: "#34d399", fontWeight: 600 }}>Analyze New Meal</span>
            </Link>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 0.8; }
        }
      `}</style>

      <Footer />
    </div>
  );
}

function MealCard({ meal, onDelete, index }: { meal: MealHistoryItem; onDelete: (id: number) => void; index: number }) {
  const date = new Date(meal.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" });

  return (
    <div
      className={`card-hover anim-fade-up delay-${Math.min(index + 1, 6)}`}
      style={{
        background: "rgba(15,23,42,0.55)",
        border: "1px solid rgba(255,255,255,0.05)",
        borderRadius: "20px", padding: "20px",
        position: "relative",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
      }}
    >
      {/* Delete button */}
      <button
        onClick={() => onDelete(meal.id)}
        style={{
          position: "absolute", top: "14px", right: "14px",
          width: "28px", height: "28px",
          background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.03)",
          cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "#475569", borderRadius: "8px",
          transition: "all .2s",
          zIndex: 2
        }}
        onMouseEnter={e => {
          (e.currentTarget as HTMLButtonElement).style.color = "#f87171";
          (e.currentTarget as HTMLButtonElement).style.background = "rgba(239,68,68,0.08)";
          (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(239,68,68,0.15)";
        }}
        onMouseLeave={e => {
          (e.currentTarget as HTMLButtonElement).style.color = "#475569";
          (e.currentTarget as HTMLButtonElement).style.background = "rgba(255,255,255,0.02)";
          (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(255,255,255,0.03)";
        }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>

      {/* Food info */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px", marginBottom: "16px", paddingRight: "30px" }}>
        <div style={{
          width: "48px", height: "48px", borderRadius: "12px",
          background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.15)",
          display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0
        }}>
          <span style={{ fontSize: "20px" }}>🍽️</span>
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: "15px", fontWeight: 700, color: "#f8fafc", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {meal.food_name}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "4px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "4px", background: "rgba(251,146,60,0.1)", padding: "2px 6px", borderRadius: "6px", border: "1px solid rgba(251,146,60,0.15)" }}>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fb923c" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2c0 0-5 5.5-5 10a5 5 0 0 0 10 0C17 7.5 12 2 12 2z" />
              </svg>
              <span style={{ fontSize: "11px", color: "#fb923c", fontWeight: 700 }}>{meal.calories} kcal</span>
            </div>
            <span style={{ fontSize: "11px", color: "#475569", fontWeight: 500 }}>{date}</span>
          </div>
        </div>
      </div>

      {/* Macros */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "8px" }}>
        {[
          { label: "PROT", value: meal.protein, color: "#38bdf8" },
          { label: "CARB", value: meal.carbs, color: "#fbbf24" },
          { label: "FAT", value: meal.fat, color: "#fb7185" },
        ].map(({ label, value, color }) => (
          <div key={label} style={{
            background: "rgba(2,6,23,0.45)", borderRadius: "10px",
            padding: "8px 4px", textAlign: "center",
            border: "1px solid rgba(255,255,255,0.03)",
            position: "relative",
            overflow: "hidden"
          }}>
            <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: "2px", background: color, opacity: 0.3 }} />
            <div style={{ fontSize: "9px", color: "#475569", textTransform: "uppercase", fontWeight: 700, letterSpacing: ".05em" }}>{label}</div>
            <div style={{ fontSize: "13px", fontWeight: 700, color: "#cbd5e1", marginTop: "2px" }}>{value}g</div>
          </div>
        ))}
      </div>
    </div>
  );
}