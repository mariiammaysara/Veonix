"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Utensils, Flame, Trash2 } from "lucide-react";

// History Key for LocalStorage (must match UploadPage)
const HISTORY_KEY = "veonix_meal_history";

export default function HistoryPage() {
  const router = useRouter();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        router.push("/");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [router]);

  useEffect(() => {
    // Load from LocalStorage
    try {
      const existing = localStorage.getItem(HISTORY_KEY);
      if (existing) {
        setHistory(JSON.parse(existing));
      }
    } catch (e) {
      console.error("Failed to load history", e);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDelete = (id: number | string) => { // ID might be string or number depending on backend response vs generated
    if (!id) {
      // Fallback for items without ID (generated purely on frontend?)
      // If no ID, we might need a different way to identify, but let's assume analyze returns an ID or we should generate one.
      // Actually, the backend still returns an ID. If we use that, good.
      // If we decide to support fully offline later, we'd need frontend IDs.
      // For now, let's filter by index if needed, but standard is ID.
      return;
    }

    try {
      const updated = history.filter((meal) => meal.id !== id);
      setHistory(updated);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    } catch (err) {
      console.error("Delete failed locally:", err);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#020617] text-slate-100 p-4 md:p-6 relative overflow-hidden flex flex-col items-center">

      {/* Background Aurora Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] animate-pulse pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] animate-pulse pointer-events-none"></div>

      <div className="w-full max-w-[1100px] relative z-10 flex-1 flex flex-col">

        {/* Header */}
        <div className="flex flex-col items-center justify-center mb-12 relative">
          <Link
            href="/"
            className="absolute left-0 top-1/2 -translate-y-1/2 flex items-center gap-2 text-slate-400 hover:text-emerald-400 transition-colors group px-3 py-2 rounded-full hover:bg-slate-800/50"
          >
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span className="hidden sm:inline text-sm font-medium">Home</span>
          </Link>

          <div className="flex flex-col items-center">
            <h1 className="text-3xl font-bold tracking-tight text-white mb-2">
              Your Meal History
            </h1>
            {/* Gradient Underline */}
            <div className="h-1 w-24 bg-gradient-to-r from-emerald-500/0 via-emerald-500/50 to-emerald-500/0 rounded-full"></div>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-slate-800/40 rounded-2xl h-64 border border-white/5"></div>
            ))}
          </div>
        ) : history.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center py-20">
            <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mb-6">
              <Utensils className="w-8 h-8 text-emerald-500/60" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">No meals yet</h2>
            <p className="text-slate-400 mb-8 max-w-xs mx-auto">
              Analyze your first meal to see it here
            </p>
            <Link
              href="/dashboard/upload"
              className="px-8 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/20 transition-transform hover:scale-105"
            >
              Analyze Meal
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-20">
            {history.map((meal, index) => (
              <div
                key={meal.id || index}
                className="bg-slate-900/40 border border-slate-800 backdrop-blur-sm rounded-2xl p-5 hover:border-emerald-500/20 transition-all group relative"
              >
                {/* Delete Action */}
                <button
                  onClick={() => handleDelete(meal.id)}
                  className="absolute top-4 right-4 text-slate-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100 p-2 hover:bg-slate-800 rounded-full"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <div className="flex items-start gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                    <Utensils className="w-6 h-6 text-emerald-500" />
                  </div>
                  <div className="pr-6">
                    <h3 className="text-lg font-semibold text-slate-200 line-clamp-1 min-h-[1.75rem]" title={meal.food_name}>
                      {meal.food_name || "Unknown Meal"}
                    </h3>
                    <div className="flex items-center gap-1.5 mt-1">
                      <Flame className="w-3.5 h-3.5 text-orange-400" />
                      <span className="text-sm font-medium text-slate-300">
                        {meal.calories} <span className="text-slate-500 font-normal">kcal</span>
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 mt-auto">
                  {/* Protein */}
                  <div className="bg-slate-950/50 rounded-lg p-2 text-center border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Prot</p>
                    <p className="text-sm font-semibold text-slate-300">{meal.macros?.protein || 0}g</p>
                  </div>
                  {/* Carbs */}
                  <div className="bg-slate-950/50 rounded-lg p-2 text-center border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Carb</p>
                    <p className="text-sm font-semibold text-slate-300">{meal.macros?.carbs || 0}g</p>
                  </div>
                  {/* Fat */}
                  <div className="bg-slate-950/50 rounded-lg p-2 text-center border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Fat</p>
                    <p className="text-sm font-semibold text-slate-300">{meal.macros?.fat || 0}g</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}