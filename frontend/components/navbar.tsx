"use client"

import Link from "next/link"
import VeonixLogo from "./veonix-logo"

export default function Navbar() {
  return (
    <nav className="w-full px-6 py-4 bg-[rgba(15,23,42,0.6)] backdrop-blur-lg border-b border-[#334155] flex justify-between items-center">
      <VeonixLogo size={28} />

      <div className="flex items-center gap-6 text-slate-300">
        <Link
          href="/dashboard/upload"
          className="hover:text-emerald-400 transition"
        >
          Upload
        </Link>

        <Link
          href="/dashboard/results"
          className="hover:text-emerald-400 transition"
        >
          Results
        </Link>

        <Link
          href="/"
          className="hover:text-emerald-400 transition"
        >
          Home
        </Link>
      </div>
    </nav>
  )
}
