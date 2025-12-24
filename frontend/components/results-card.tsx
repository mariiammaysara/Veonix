// components/results-card.tsx
import React from "react";

type Props = {
  title: string;
  serving?: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
};

export default function ResultsCard({ title, serving, calories, protein, carbs, fat }: Props) {
  return (
    <div className="bg-gradient-to-br from-slate-800/60 to-slate-800/40 p-4 rounded-xl shadow-lg border border-slate-700">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
          {serving && <p className="text-sm text-slate-400">{serving}</p>}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-emerald-300">{calories ?? "-" } kcal</div>
          <div className="text-xs text-slate-400">Calories</div>
        </div>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-sm text-slate-400">Protein</div>
          <div className="text-lg text-slate-100">{protein ?? "-" } g</div>
        </div>
        <div>
          <div className="text-sm text-slate-400">Carbs</div>
          <div className="text-lg text-slate-100">{carbs ?? "-" } g</div>
        </div>
        <div>
          <div className="text-sm text-slate-400">Fat</div>
          <div className="text-lg text-slate-100">{fat ?? "-" } g</div>
        </div>
      </div>
    </div>
  );
}
