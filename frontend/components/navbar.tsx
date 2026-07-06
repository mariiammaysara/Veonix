"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Upload, Clock, Settings } from "lucide-react";

/**
 * Veonix — Shared Navbar Component
 * 
 * Implements a floating, pill-style navigation with a glassmorphic background.
 * Optimized for perfect centering using a 3-column grid layout.
 */
export default function Navbar() {
  const pathname = usePathname();

  const NAV_LINKS = [
    { label: "Home", href: "/", icon: Home },
    { label: "Upload", href: "/dashboard/upload", icon: Upload },
    { label: "History", href: "/dashboard/history", icon: Clock },
    { label: "Settings", href: "/dashboard/settings", icon: Settings },
  ];

  return (
    <nav className="anim-fade-in" style={{
      display: "grid",
      gridTemplateColumns: "1fr auto 1fr",
      alignItems: "center",
      padding: "0 clamp(20px, 4vw, 48px)",
      height: "80px",
      background: "transparent",
      position: "absolute",
      top: 0,
      left: 0,
      right: 0,
      zIndex: 50,
      width: "100%",
    }}>
      {/* 1. Brand Logo (Left Column) */}
      <div style={{ display: "flex", justifyContent: "flex-start" }}>
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none" }}>
          <svg width="24" height="24" viewBox="0 0 100 100" fill="none">
            <path d="M20 75L50 20L80 75" stroke="#10b981" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="50" cy="55" r="7" fill="#10b981" />
          </svg>
          <span style={{ fontSize: "18px", fontWeight: 800, color: "#fff", letterSpacing: "-.5px" }}>Veonix</span>
        </Link>
      </div>

      {/* 2. Navigation Pill (Center Column - Guaranteed Center) */}
      <div style={{
        display: "flex", alignItems: "center", gap: "4px",
        padding: "5px",
        background: "rgba(15, 23, 42, 0.35)",
        border: "1px solid rgba(255, 255, 255, 0.06)",
        borderRadius: "99px",
        backdropFilter: "blur(16px)",
        boxShadow: "0 10px 30px -10px rgba(0,0,0,0.5)"
      }}>
        {NAV_LINKS.map(({ label, href, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link key={label} href={href} style={{
              display: "flex", alignItems: "center", gap: "8px",
              padding: "7px 16px",
              fontSize: "13px", fontWeight: 500,
              borderRadius: "99px",
              textDecoration: "none",
              transition: "all 0.4s cubic-bezier(0.2, 1, 0.2, 1)",
              color: isActive ? "#fff" : "rgba(148, 163, 184, 0.6)",
              background: isActive ? "#0f172a" : "transparent",
              boxShadow: isActive ? "0 0 20px rgba(16, 185, 129, 0.1), inset 0 0 0 1px rgba(16, 185, 129, 0.15)" : "none",
              border: isActive ? "1px solid rgba(16, 185, 129, 0.08)" : "1px solid transparent",
              transform: isActive ? "scale(1.02)" : "scale(1)"
            }}>
              <Icon size={14} strokeWidth={isActive ? 2.5 : 2} style={{
                color: isActive ? "#34d399" : "inherit",
                transition: "color 0.4s ease"
              }} />
              <span className="hidden sm:inline">{label}</span>
            </Link>
          );
        })}
      </div>

      {/* 3. Empty Spacer (Right Column - Balances the Logo) */}
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        {/* Empty for centering balance */}
      </div>
    </nav>
  );
}
