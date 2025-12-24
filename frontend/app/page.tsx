"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-[#0f172a] to-[#020617] text-slate-100 flex flex-col items-center justify-center px-6 py-20 overflow-hidden relative">
      
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-emerald-500/5 rounded-full blur-[120px] pointer-events-none"></div>

      <style jsx>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
          100% { transform: translateY(0px); }
        }
        .animate-fade-up { animation: fadeInUp 0.8s ease-out forwards; }
        .animate-float { animation: float 4s ease-in-out infinite; }
      `}</style>

      <div className="max-w-3xl mx-auto text-center relative z-10">
        
        <div className="flex justify-center mb-10 animate-fade-up animate-float">
          <div className="flex items-center gap-2">
            <svg width="42" height="42" viewBox="0 0 100 100" fill="none">
              <path d="M20 75 L50 20 L80 75" stroke="#34d399" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="50" cy="55" r="6" fill="#10b981" />
            </svg>
            <span className="text-3xl font-bold tracking-wide">Veonix</span>
          </div>
        </div>

        <h1 
          className="text-4xl md:text-5xl font-extrabold mb-6 text-slate-50 animate-fade-up"
          style={{ animationDelay: '0.2s' }}
        >
          AI Nutrition Analyzer
        </h1>

        <p 
          className="text-slate-300 max-w-2xl mx-auto text-2xl md:text-3xl font-medium tracking-tight mb-10 animate-fade-up"
          style={{ animationDelay: '0.4s', opacity: 0 }} 
        >
          Eat. Snap. Know.
        </p>

        <div 
          className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-up"
          style={{ animationDelay: '0.6s', opacity: 0 }}
        >
          <Link
            href="/dashboard/upload"
            className="px-10 py-3 bg-emerald-500 hover:bg-emerald-600 text-black font-semibold rounded-full shadow-lg shadow-emerald-500/30 transition-all hover:scale-110 active:scale-95 text-center"
          >
            Upload Your Meal
          </Link>

          <Link
            href="/dashboard/history"
            className="px-10 py-3 bg-slate-800 hover:bg-slate-700 text-emerald-400 font-semibold rounded-full border border-emerald-500/20 shadow-lg transition-all hover:scale-110 active:scale-95 text-center"
          >
            View History
          </Link>
        </div>

        <div 
          className="mt-20 flex justify-center gap-12 animate-fade-up opacity-0 border-t border-slate-800/30 pt-8"
          style={{ animationDelay: '0.8s', opacity: 0 }}
        >
          <div className="flex flex-col items-center">
            <span className="text-white font-bold text-sm tracking-widest">FAST</span>
            <span className="text-[10px] text-slate-500 uppercase mt-1">Real-time</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-white font-bold text-sm tracking-widest">SMART</span>
            <span className="text-[10px] text-slate-500 uppercase mt-1">AI Logic</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-white font-bold text-sm tracking-widest">SECURE</span>
            <span className="text-[10px] text-slate-500 uppercase mt-1">Private</span>
          </div>
        </div>

      </div>
    </div>
  );
}