"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import LoadingPage from "@/app/loading/page";
import {
  Zap, Brain, Lock,
  Apple, Banana, GlassWater, Dumbbell, Utensils, Carrot,
  Leaf, Activity, Flame, Salad, ShoppingCart, Scale
} from "lucide-react";

import IntroScreen from "@/components/IntroScreen";
// ... (imports)

export default function Home() {
  const [showContent, setShowContent] = useState(false);

  // If intro has been seen, content shows immediately.
  // IntroScreen handles checking sessionStorage and hiding itself if needed.

  if (!showContent) {
    return (
      <IntroScreen onComplete={() => setShowContent(true)} />
    );
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-[#0f172a] to-[#020617] text-slate-100 flex flex-col items-center justify-center px-4 py-12 md:px-6 md:py-20 overflow-hidden relative">

      {/* Background Floating Icons - Fixed Layout (Hidden on mobile for performance) */}
      <div className="hidden md:block absolute inset-0 overflow-hidden pointer-events-none">
        {[
          { icon: Apple, top: "8%", left: "10%" },
          { icon: ShoppingCart, top: "15%", left: "85%" },
          { icon: Banana, top: "30%", left: "5%" },
          { icon: Dumbbell, top: "40%", left: "92%" },
          { icon: Utensils, top: "65%", left: "12%" },
          { icon: Scale, top: "75%", left: "88%" },
          { icon: Salad, top: "85%", left: "30%" },
          { icon: Zap, top: "10%", left: "40%" },
        ].map((item, i) => (
          <div
            key={i}
            className="animate-float"
            style={{
              position: "absolute",
              top: item.top,
              left: item.left,
              opacity: 0.1,
              animationDuration: '12s',
              animationDelay: `${i * 1.5}s`
            }}
          >
            <item.icon size={24} strokeWidth={1.5} />
          </div>
        ))}
      </div>



      <div className="max-w-4xl mx-auto text-center relative z-10 flex flex-col items-center">

        {/* Logo Section */}
        <div className="flex justify-center mb-6 animate-fade-up">
          <div className="flex items-center gap-4 animate-float">
            <div className="relative flex items-center justify-center">
              {/* Focused Glow on Logo */}
              <div className="absolute -inset-4 bg-emerald-600/20 rounded-full blur-xl pointer-events-none"></div>
              <svg width="48" height="48" viewBox="0 0 100 100" fill="none" className="relative z-10">
                <path d="M20 75 L50 20 L80 75" stroke="#10b981" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="50" cy="55" r="6" fill="#10b981" />
              </svg>
            </div>
            <span className="text-4xl font-bold tracking-tight text-white drop-shadow-md">Veonix</span>
          </div>
        </div>

        {/* Main Heading */}
        <h1
          className="text-4xl md:text-5xl font-bold mb-4 pb-2 text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-200 to-emerald-400 animate-fade-up"
          style={{ animationDelay: '0.1s' }}
        >
          AI Nutrition Analyzer
        </h1>

        {/* Subheading */}
        <p
          className="text-slate-400 max-w-xl mx-auto text-xl font-medium tracking-tight mb-8 animate-fade-up leading-relaxed"
          style={{ animationDelay: '0.2s' }}
        >
          Eat. Snap. Know.
        </p>

        {/* Action Buttons */}
        <div
          className="flex flex-col sm:flex-row gap-5 justify-center w-full max-w-md animate-fade-up"
          style={{ animationDelay: '0.3s' }}
        >
          <Link
            href="/dashboard/upload"
            className="group relative px-8 py-3.5 bg-gradient-to-r from-emerald-500 to-emerald-600 text-slate-950 font-bold text-base rounded-full shadow-[0_0_20px_rgba(16,185,129,0.15)] transition-all duration-200 ease-out hover:scale-105 hover:shadow-[0_0_25px_rgba(16,185,129,0.25)] flex items-center justify-center gap-2 overflow-hidden"
          >
            <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
            <span className="relative">Upload Your Meal</span>
            <svg className="w-4 h-4 relative group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path></svg>
          </Link>

          <Link
            href="/dashboard/history"
            className="px-8 py-3.5 bg-transparent border border-white/20 text-white/80 font-semibold text-base rounded-full backdrop-blur-sm transition-all duration-200 ease-out hover:bg-emerald-500/10 hover:border-emerald-400/40 flex items-center justify-center"
          >
            View History
          </Link>
        </div>

        {/* Features Cards */}
        <div
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-5 w-full max-w-2xl animate-fade-up"
          style={{ animationDelay: '0.5s' }}
        >
          {[
            { title: "FAST", subtitle: "Real-time Analysis", icon: Zap },
            { title: "SMART", subtitle: "Advanced AI Logic", icon: Brain },
            { title: "SECURE", subtitle: "Private & Safe", icon: Lock }
          ].map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={item.title}
                className="group p-4 rounded-xl bg-slate-900/40 border border-white/10 hover:border-emerald-500/30 transition-all duration-300 hover:-translate-y-[2px] hover:bg-slate-800/60 backdrop-blur-md flex flex-col items-center"
              >
                <div className="mb-2.5 p-2 bg-white/5 rounded-full group-hover:bg-emerald-500/10 transition-colors duration-300">
                  <Icon className="w-5 h-5 text-slate-300 group-hover:text-emerald-500 transition-colors duration-300" strokeWidth={2} />
                </div>
                <div className="text-slate-100 font-bold text-sm tracking-wider mb-0.5 group-hover:text-emerald-400 transition-colors">{item.title}</div>
                <div className="text-slate-500 text-[11px] font-medium uppercase tracking-wide group-hover:text-slate-400">{item.subtitle}</div>
              </div>
            )
          })}
        </div>

      </div>

    </div>
  );
}
