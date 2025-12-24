"use client";

import React, { useState } from "react";
import UploadBox from "@/components/upload-box";
import ImagePreview from "@/components/image-preview";
import ResultsDisplay from "@/components/results-display";
import { analyzeImage } from "@/lib/api";
import { X } from "lucide-react";
import Link from "next/link";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onFile = (f: File | null) => {
    setResult(null);
    setError(null);

    if (!f) {
      setFile(null);
      setPreview(null);
      return;
    }

    setFile(f);
    const url = URL.createObjectURL(f);
    setPreview(url);
  };

  const onAnalyze = async () => {
    if (!file) return setError("Please upload an image first");
    setLoading(true);
    setError(null);

    try {
      const res = await analyzeImage(file);
      setResult(res);
    } catch (e: any) {
      setError(e?.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617] text-slate-100 p-4 relative">
      
      <Link
        href="/"
        className="absolute top-6 right-6 p-2 rounded-full bg-slate-800/60 hover:bg-slate-700/60 backdrop-blur-md transition shadow-lg"
      >
        <X className="w-5 h-5 text-emerald-400" />
      </Link>

      <div className="w-full max-w-md bg-slate-800/60 backdrop-blur-xl rounded-2xl shadow-lg p-6">
        {!result && (
          <h1 className="text-2xl font-semibold mb-4 text-center text-[#34d399]">
            Analyze Your Meal
          </h1>
        )}

        {!result && (
          <>
            <UploadBox onFile={onFile} />
            {preview && <ImagePreview src={preview} alt="preview" />}
            {error && <div className="text-red-400 mt-3">{error}</div>}
            {preview && (
              <button
                onClick={onAnalyze}
                disabled={loading}
                className="w-full mt-4 px-4 py-2 bg-[#10b981] hover:bg-[#059669] rounded-lg font-medium disabled:opacity-50 transition-all"
              >
                {loading ? "Analyzing…" : "Analyze"}
              </button>
            )}
          </>
        )}

        {result && (
          <ResultsDisplay
            preview={preview}
            data={result} 
          />
        )}
      </div>
    </div>
  );
}