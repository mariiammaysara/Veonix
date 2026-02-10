"use client";

import { Loader2 } from "lucide-react";
import React from "react";

export default function LoadingScreen() {
  return (
    <div className="fixed inset-0 w-full h-full bg-gradient-to-b from-[#0f172a] to-[#020617] flex flex-col items-center justify-center z-50">
      <div className="flex flex-col items-center animate-fade-up">
        {/* Veonix Logo (Simplified for Loading) */}
        <div className="mb-8 relative flex items-center justify-center">
          <div className="absolute -inset-4 bg-emerald-600/20 rounded-full blur-xl pointer-events-none animate-pulse"></div>
          <svg width="64" height="64" viewBox="0 0 100 100" fill="none" className="relative z-10">
            <path d="M20 75 L50 20 L80 75" stroke="#10b981" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="50" cy="55" r="6" fill="#10b981" />
          </svg>
        </div>

        <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Analyzing your meal...</h2>
        <p className="text-slate-400 text-sm mb-8 font-medium">This may take a few seconds</p>

        <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
      </div>
    </div>
  );
}
