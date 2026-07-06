"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import LoadingScreen from "@/components/LoadingScreen";
import { getProfile, updateProfile } from "@/lib/api";
import { getUserFriendlyError } from "@/lib/error-utils";

/**
 * Veonix — Settings / User Profile Page
 * 
 * Provides a premium interface for managing nutritional goals and allergies.
 * Persists the values in the database and updates LangGraph Store memory context.
 */
export default function SettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [goal, setGoal] = useState("");
  const [allergyInput, setAllergyInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const profile = await getProfile();
        setGoal(profile.dietary_goal || "");
        setAllergyInput((profile.allergies || []).join(", "));
      } catch (err: unknown) {
        setError(getUserFriendlyError(err).message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    // Split allergies by commas and clean whitespaces
    const allergiesList = allergyInput
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    try {
      await updateProfile(goal, allergiesList);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: unknown) {
      setError(getUserFriendlyError(err).message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingScreen />;

  return (
    <div style={{ minHeight: "100vh", background: "#020617", color: "#f1f5f9", display: "flex", flexDirection: "column", position: "relative", overflowX: "hidden" }}>
      <div className="g1" />

      {/* Shared Navbar */}
      <Navbar />

      {/* Settings Form Container */}
      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        padding: "80px 20px 40px", gap: "24px",
        position: "relative", zIndex: 1
      }}>

        <div className="anim-fade-up" style={{ textAlign: "center", marginBottom: "8px" }}>
          <h1 style={{ fontSize: "clamp(22px, 3vw, 28px)", fontWeight: 800, color: "#f1f5f9", marginBottom: "8px" }}>
            Profile & Memory Settings
          </h1>
          <p style={{ fontSize: "14px", color: "#64748b", maxWidth: "400px", lineHeight: 1.6, margin: "0 auto" }}>
            Customize your coach's memory with your dietary goal and allergies.
          </p>
        </div>

        <form onSubmit={handleSave} className="anim-scale-in delay-1" style={{
          width: "100%", maxWidth: "480px",
          background: "rgba(10,18,38,0.6)",
          border: "1px solid rgba(255,255,255,0.06)",
          borderRadius: "24px", padding: "28px 24px",
          display: "flex", flexDirection: "column", gap: "20px",
          backdropFilter: "blur(12px)",
          boxShadow: "0 20px 40px rgba(0,0,0,0.3)"
        }}>
          {/* Dietary Goal */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <label style={{ fontSize: "12px", fontWeight: 600, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Dietary Goal
            </label>
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g. Build muscle, high protein diet, 500 calorie deficit daily"
              style={{
                width: "100%", height: "90px", padding: "12px",
                background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "12px", color: "#f1f5f9", fontSize: "14px", outline: "none",
                resize: "none", transition: "border .2s"
              }}
              className="focus:border-emerald-500/50"
            />
          </div>

          {/* Allergies */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <label style={{ fontSize: "12px", fontWeight: 600, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Allergies & Intolerances
            </label>
            <input
              type="text"
              value={allergyInput}
              onChange={(e) => setAllergyInput(e.target.value)}
              placeholder="e.g. peanuts, dairy, gluten, shellfish"
              style={{
                width: "100%", padding: "12px",
                background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "12px", color: "#f1f5f9", fontSize: "14px", outline: "none",
                transition: "border .2s"
              }}
              className="focus:border-emerald-500/50"
            />
            <span style={{ fontSize: "11px", color: "#475569" }}>
              Separate multiple allergies with commas. The coach will warn you if any ingredient matches.
            </span>
          </div>

          {/* Status Indicators */}
          {error && (
            <div style={{
              padding: "10px 14px", background: "rgba(239, 68, 68, 0.05)",
              border: "1px solid rgba(239, 68, 68, 0.15)", borderRadius: "12px",
              color: "#f87171", fontSize: "12px", textAlign: "center"
            }}>
              {error}
            </div>
          )}

          {success && (
            <div className="anim-scale-in" style={{
              padding: "10px 14px", background: "rgba(16, 185, 129, 0.05)",
              border: "1px solid rgba(16, 185, 129, 0.15)", borderRadius: "12px",
              color: "#34d399", fontSize: "12px", textAlign: "center", fontWeight: 600
            }}>
              ✓ Memory updated successfully!
            </div>
          )}

          {/* Save Button */}
          <button
            type="submit"
            disabled={saving}
            className="btn-glow"
            style={{
              padding: "12px", background: "#10b981", border: "none", borderRadius: "12px",
              color: "#020617", fontSize: "15px", fontWeight: 700, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
              opacity: saving ? 0.7 : 1, transition: "opacity .2s"
            }}
          >
            {saving ? "Updating memory..." : "Save Settings"}
          </button>
        </form>

        <button
          onClick={() => router.push("/")}
          style={{
            padding: "8px 20px", background: "transparent", border: "none",
            color: "#64748b", fontSize: "13px", fontWeight: 500, cursor: "pointer",
            display: "flex", alignItems: "center", gap: "6px"
          }}
          className="hover:text-slate-300"
        >
          ← Go back to dashboard
        </button>
      </div>
    </div>
  );
}
