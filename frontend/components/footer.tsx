import Link from "next/link";

/**
 * Veonix — Shared Footer
 *
 * Minimal, consistent footer used across dashboard pages (upload, history,
 * settings). The marketing homepage keeps its own richer multi-column footer.
 */
export default function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid rgba(255,255,255,0.04)",
        padding: "28px clamp(20px, 4vw, 48px)",
        position: "relative",
        zIndex: 1,
        marginTop: "auto",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "16px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <svg width="18" height="18" viewBox="0 0 100 100" fill="none">
            <path
              d="M20 75L50 20L80 75"
              stroke="#34d399"
              strokeWidth="10"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="50" cy="55" r="7" fill="#10b981" />
          </svg>
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

        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <Link
            href="/"
            style={{ fontSize: "13px", color: "#94a3b8", textDecoration: "none" }}
            className="hover:text-emerald-400 transition-colors"
          >
            Home
          </Link>
          <a
            href="https://github.com/mariiammaysara/Veonix"
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: "13px", color: "#94a3b8", textDecoration: "none" }}
            className="hover:text-emerald-400 transition-colors"
          >
            GitHub
          </a>
          <a
            href="https://www.linkedin.com/in/mariam-maysara/"
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: "13px", color: "#94a3b8", textDecoration: "none" }}
            className="hover:text-emerald-400 transition-colors"
          >
            LinkedIn
          </a>
        </div>
      </div>
    </footer>
  );
}
