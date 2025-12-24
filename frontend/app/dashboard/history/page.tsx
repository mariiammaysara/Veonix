"use client";

import { useEffect, useState } from "react";
import { getMealHistory, deleteMeal } from "@/lib/api";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMealHistory()
      .then((data) => setHistory(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: number) => {
    if (!id) return;
    try {
      await deleteMeal(id);
      setHistory((prev) => prev.filter((meal) => meal.id !== id));
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#020617] text-slate-100 p-6 md:p-8 relative overflow-hidden">
      
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/5 rounded-full blur-[120px] animate-pulse"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/5 rounded-full blur-[120px] animate-pulse"></div>

      <div className="max-w-6xl mx-auto relative z-10 mb-10">
        <div className="flex justify-between items-center mb-6">
          <Link 
            href="/" 
            className="flex items-center gap-2 text-slate-400 hover:text-emerald-400 transition-colors group"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span className="text-sm font-medium">Back</span>
          </Link>

          <div className="flex items-center gap-2 group">
            <svg className="group-hover:rotate-12 transition-transform duration-300" width="24" height="24" viewBox="0 0 100 100" fill="none">
              <path d="M20 75 L50 20 L80 75" stroke="#34d399" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="50" cy="55" r="6" fill="#10b981" />
            </svg>
            <span className="text-lg font-bold tracking-[0.2em] uppercase text-slate-100">Veonix</span>
          </div>
          
          <div className="w-12 hidden md:block"></div>
        </div>

        <div className="text-center animate-in fade-in slide-in-from-top duration-700">
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200">
            Your Meal History
          </h1>
          <div className="h-1 w-24 bg-gradient-to-r from-emerald-500/40 to-transparent mx-auto mt-4 rounded-full"></div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-40">
           <div className="w-8 h-8 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-20 animate-in fade-in duration-1000 relative z-10">
          <p className="text-slate-500 text-lg mb-4">No meals found in your history.</p>
          <Link 
            href="/dashboard/upload" 
            className="text-emerald-400 hover:text-emerald-300 underline underline-offset-4 font-medium transition-colors"
          >
            Analyze your first meal
          </Link>
        </div>
      ) : (
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
          {history.map((meal: any, index: number) => (
            <div 
              key={meal.id || index} 
              style={{ animationDelay: `${index * 100}ms` }}
              className="bg-[#0f172a]/40 border border-slate-800 rounded-[2rem] p-6 backdrop-blur-xl relative group 
                         hover:border-emerald-500/40 hover:bg-[#0f172a]/60 hover:scale-[1.02] 
                         hover:shadow-[0_0_30px_rgba(16,185,129,0.1)] transition-all duration-500 
                         animate-in fade-in zoom-in duration-700"
            >
              
              <div className="flex justify-between items-center mb-4">
                <span className="px-3 py-0.5 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold rounded-full border border-emerald-500/20 uppercase tracking-widest group-hover:bg-emerald-500 group-hover:text-black transition-colors duration-500">
                  Meal
                </span>
                <button 
                  onClick={() => handleDelete(meal.id)}
                  className="text-slate-600 hover:text-red-400 transition-colors text-sm transform hover:rotate-90 duration-300"
                >
                  ✕
                </button>
              </div>

              <h3 className="text-xl font-bold text-center text-slate-100 mb-6 tracking-tight uppercase group-hover:text-emerald-400 transition-colors">
                {meal.food_name}
              </h3>

              <div className="space-y-4">
                <div className="text-center relative">
                  <span className="text-4xl font-black text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.3)] group-hover:drop-shadow-[0_0_15px_rgba(52,211,153,0.6)] transition-all">
                    {meal.calories}
                  </span>
                  <span className="text-slate-500 text-xs ml-1 font-black uppercase tracking-tighter">kcal</span>
                </div>

                <div className="grid grid-cols-3 gap-2 border-t border-slate-800/60 pt-6">
                  {[
                    { label: 'Protein', val: meal.macros?.protein },
                    { label: 'Carbs', val: meal.macros?.carbs },
                    { label: 'Fat', val: meal.macros?.fat }
                  ].map((macro) => (
                    <div key={macro.label} className="text-center">
                      <p className="text-emerald-400 font-black text-base group-hover:scale-110 transition-transform">{macro.val || 0}g</p>
                      <p className="text-[9px] text-slate-500 font-black uppercase tracking-widest mt-0.5">{macro.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-6 text-center pt-3 border-t border-slate-800/30">
                <span className="text-[9px] text-slate-600 font-black uppercase tracking-[0.2em] group-hover:text-slate-400 transition-colors">
                   {meal.created_at 
                     ? new Date(meal.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) 
                     : "Recent Meal"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}