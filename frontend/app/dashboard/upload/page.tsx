"use client";

import React, { useState, useEffect } from "react";
import UploadBox from "@/components/upload-box";

import ResultsDisplay from "@/components/results-display";
import LoadingScreen from "@/components/LoadingScreen";
import { analyzeImage } from "@/lib/api";
import { X, Apple, Salad, Banana, Drumstick, Dumbbell, Droplet, Utensils, Zap, Flame, Leaf, Fish, Candy, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ApiError } from "@/lib/api";
import { getUserFriendlyError } from "@/lib/error-utils";
import ErrorCard from "@/components/error-card";

// History Key for LocalStorage
const HISTORY_KEY = "veonix_meal_history";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<{ title: string; message: string } | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (result) {
          setFile(null);
          setPreview(null);
          setResult(null);
        } else {
          router.push("/");
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [result, router]);

  const onFile = (f: File | null) => {
    setResult(null);
    setError(null);
    if (!f) {
      setFile(null);
      setPreview(null);
    } else {
      setFile(f);
      const url = URL.createObjectURL(f);
      setPreview(url);
    }
  };

  const saveToHistory = (mealData: any) => {
    try {
      const existing = localStorage.getItem(HISTORY_KEY);
      const history = existing ? JSON.parse(existing) : [];
      // Add new meal to the beginning
      // Ensure we have a timestamp if not provided by backend properly (though it usually is)
      const newEntry = {
        ...mealData,
        created_at: mealData.created_at || new Date().toISOString()
      };
      const updated = [newEntry, ...history];
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error("Failed to save history locally", e);
    }
  };

  const onAnalyze = async () => {
    if (!file) {
      setError({ title: "No image selected", message: "Please select an image first." });
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await analyzeImage(file);
      setResult(res);
      saveToHistory(res);
    } catch (err: any) {
      // Use the global error handler
      const userFriendly = getUserFriendlyError(err);
      setError(userFriendly);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617] text-slate-100 p-4 relative overflow-hidden">

      {/* Background Aurora Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-emerald-500/20 rounded-full blur-[100px] animate-float-slow pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-teal-500/20 rounded-full blur-[100px] animate-float pointer-events-none"></div>
      <div className="absolute top-[40%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none"></div>

      {/* Background Floating Icons - Organized Layout */}
      <div className="hidden md:block absolute inset-0 overflow-hidden pointer-events-none z-0">
        {[
          { Icon: Apple, top: '8%', left: '15%' },
          { Icon: Banana, top: '12%', left: '80%' },

          { Icon: Salad, top: '30%', left: '8%' },
          { Icon: Dumbbell, top: '32%', left: '90%' },

          { Icon: Flame, top: '55%', left: '10%' },
          { Icon: Zap, top: '60%', left: '88%' },

          { Icon: Utensils, top: '80%', left: '20%' },
          { Icon: Leaf, top: '85%', left: '75%' },
        ].map((item, i) => (
          <div
            key={i}
            className="animate-float"
            style={{
              position: 'absolute',
              top: item.top,
              left: item.left,
              opacity: 0.08,
              transform: 'scale(0.9)',
              animationDuration: '14s',
              animationDelay: `${i * 1.5}s`
            }}
          >
            <item.Icon size={32} strokeWidth={1.5} />
          </div>
        ))}
      </div>

      {!result && (
        <Link
          href="/"
          className="absolute top-6 right-6 p-2 rounded-full bg-slate-800/60 hover:bg-slate-700/60 backdrop-blur-md transition shadow-lg z-50"
        >
          <X className="w-5 h-5 text-emerald-400" />
        </Link>
      )}

      <div className={`w-full max-w-4xl transition-all duration-300 relative z-10`}>
        {/* Subtle Glow Behind Card */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[110%] h-[110%] bg-emerald-500/5 rounded-full blur-3xl -z-10 pointer-events-none"></div>

        {!result && (
          <div className="animate-fade-up flex flex-col items-center">
            <h1 className="text-3xl md:text-4xl font-bold mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300 tracking-tight">
              Analyze Your Meal
            </h1>

            <div className="w-full max-w-xl relative">
              <UploadBox
                onFile={onFile}
                preview={preview}
                onAnalyze={onAnalyze}
              />

              {error && (
                <ErrorCard
                  title={error.title}
                  message={error.message}
                  onRetry={onAnalyze}
                />
              )}
            </div>
          </div>
        )}

        {result && (
          <div className="animate-fade-up">
            <ResultsDisplay data={result} preview={preview} />

            <div className="mt-10 flex justify-center">
              <button
                onClick={() => {
                  setFile(null);
                  setPreview(null);
                  setResult(null);
                }}
                className="group flex items-center gap-2 px-8 py-3 bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 font-medium rounded-full border border-slate-700/50 hover:border-emerald-500/30 transition-all hover:shadow-[0_0_20px_rgba(16,185,129,0.1)]"
              >
                <div className="p-1.5 bg-slate-700/50 rounded-full group-hover:bg-emerald-500/20 group-hover:text-emerald-400 transition-colors">
                  <Utensils className="w-4 h-4" />
                </div>
                Analyze Another Meal
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}