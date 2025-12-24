"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-[#0f172a] to-[#020617] text-slate-100 flex flex-col items-center justify-center px-6 py-20">
      <div className="max-w-3xl mx-auto text-center">
        <div className="flex justify-center mb-10">
          <div className="flex items-center gap-2">
            <svg width="42" height="42" viewBox="0 0 100 100" fill="none">
              <path
                d="M20 75 L50 20 L80 75"
                stroke="#34d399"
                strokeWidth="8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="50" cy="55" r="6" fill="#10b981" />
            </svg>
            <span className="text-3xl font-bold tracking-wide">Veonix</span>
          </div>
        </div>

        {/* Emerald Gradient Applied to H1 */}
        <h1 className="text-4xl md:text-5xl font-extrabold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-emerald-200 to-emerald-500 pb-2">
          AI Nutrition Analyzer
        </h1>

        {/* Softer Emerald for the Paragraph */}
        <p className="text-emerald-400/80 max-w-2xl mx-auto text-lg leading-relaxed font-medium">
          Upload any meal photo → Veonix analyzes it using advanced AI →
          Instantly get calories, macros, and full nutrition facts.
        </p>

        <div className="mt-10">
          <Link
            href="/dashboard/upload"
            className="relative z-20 px-10 py-3 bg-emerald-500 hover:bg-emerald-600 text-black font-semibold rounded-full shadow-lg shadow-emerald-500/30 transition pointer-events-auto inline-block"
            onClick={() => console.log("Upload button clicked")}
          >
            Upload Your Meal
          </Link>
        </div>
      </div>
    </div>
  );
}