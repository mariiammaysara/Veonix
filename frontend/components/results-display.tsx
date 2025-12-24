"use client";

import React from "react";
import Image from "next/image";

interface NutritionResultProps {
  preview?: string | null;
  data: {
    food_name: string;
    calories: number;
    macros: {
      protein: number;
      carbs: number;
      fat: number;
    };
  } | null;
}

export default function ResultsDisplay({ preview, data }: NutritionResultProps) {
  if (!data) return null;

  return (
    <div className="w-full bg-slate-800/60 backdrop-blur-xl p-6 rounded-2xl shadow-xl border border-slate-700/50 mt-6 animate-in fade-in zoom-in duration-300">
      
      {/* Image Preview */}
      {preview && (
        <div className="w-full flex justify-center mb-4">
          <Image
            src={preview}
            alt="meal preview"
            width={300}
            height={200}
            className="rounded-xl shadow-lg object-cover"
          />
        </div>
      )}

      <h2 className="text-2xl font-bold text-emerald-400 mb-4 text-center">
        {data.food_name}
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Calories Card */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-emerald-500/20 flex flex-col items-center justify-center text-center">
          <p className="text-2xl font-bold text-emerald-400">{data.calories}</p>
          <p className="text-slate-400 text-xs uppercase tracking-wider">Calories</p>
        </div>

        {/* Protein Card */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700 flex flex-col items-center justify-center text-center">
          <p className="text-xl font-bold text-blue-400">{data.macros?.protein}g</p>
          <p className="text-slate-400 text-xs uppercase">Protein</p>
        </div>

        {/* Carbs Card */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700 flex flex-col items-center justify-center text-center">
          <p className="text-xl font-bold text-yellow-400">{data.macros?.carbs}g</p>
          <p className="text-slate-400 text-xs uppercase">Carbs</p>
        </div>

        {/* Fat Card */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700 flex flex-col items-center justify-center text-center">
          <p className="text-xl font-bold text-red-400">{data.macros?.fat}g</p>
          <p className="text-slate-400 text-xs uppercase">Fat</p>
        </div>
      </div>
    </div>
  );
}