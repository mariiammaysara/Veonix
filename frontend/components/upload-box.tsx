"use client";
import React, { useState, useCallback, useRef } from "react";
import { Image, Upload, RefreshCw, Zap } from "lucide-react";

type Props = {
  onFile: (file: File | null) => void;
  preview: string | null;
  onAnalyze: () => void;
};

export default function UploadBox({ onFile, preview, onAnalyze }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFile(e.dataTransfer.files[0]);
    }
  }, [onFile]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFile(e.target.files[0] ?? null);
    }
  };

  const handleContainerClick = () => {
    if (!preview && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const onChangeImage = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={handleContainerClick}
      className={`
        relative group w-full max-w-xl mx-auto
        bg-slate-800/40 backdrop-blur-xl rounded-[1.5rem] 
        border transition-all duration-500 ease-out overflow-hidden
        ${preview ? 'h-auto min-h-[400px] border-emerald-500/20' : 'h-64 md:h-80 cursor-pointer border-white/10 hover:border-emerald-400/30 hover:bg-emerald-500/5 hover:scale-[1.01] hover:shadow-[0_0_40px_rgba(16,185,129,0.1)]'}
        ${isDragging ? "border-emerald-500/50 bg-emerald-500/10 scale-[1.02] shadow-[0_0_50px_rgba(16,185,129,0.2)]" : ""}
      `}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
      />

      {/* Empty State */}
      {!preview && (
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
          {/* Icon Circle */}
          <div className={`
              mb-6 w-16 h-16 rounded-full bg-slate-900/60
              flex items-center justify-center
              border border-white/5
              transition-all duration-500
              group-hover:scale-110 group-hover:border-emerald-500/30 group-hover:bg-slate-900/80
            `}>
            <Image
              strokeWidth={1.5}
              className={`w-8 h-8 text-slate-400 group-hover:text-emerald-400 transition-colors duration-300 ${isDragging ? "text-emerald-400 animate-pulse" : ""}`}
            />
          </div>

          <div className="space-y-2">
            <h3 className="text-xl font-semibold text-slate-200 group-hover:text-emerald-100 transition-colors">
              Upload a meal image
            </h3>
            <p className="text-sm text-slate-500 group-hover:text-slate-400 transition-colors">
              Click or drag & drop to analyze
            </p>
          </div>

          <p className="absolute bottom-8 text-xs text-slate-600 font-medium tracking-wide uppercase opacity-70 group-hover:opacity-100 transition-opacity">
            PNG, JPG, WEBP • Max 5MB
          </p>
        </div>
      )}

      {/* Selected State (Preview) */}
      {preview && (
        <div className="absolute inset-0 flex flex-col animate-in fade-in zoom-in duration-500">
          {/* Image Layer */}
          <div className="relative flex-1 w-full bg-slate-950 overflow-hidden">
            <img
              src={preview}
              alt="Meal preview"
              className="w-full h-full object-cover opacity-90 transition-transform duration-700 hover:scale-105"
            />

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-80"></div>
          </div>

          {/* Action Bar */}
          <div className="absolute bottom-0 left-0 right-0 p-6 flex items-center justify-between gap-4 bg-gradient-to-t from-slate-900/90 to-transparent pt-20">
            <button
              onClick={onChangeImage}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 text-sm font-medium transition-all hover:scale-105 backdrop-blur-md border border-white/10"
            >
              <RefreshCw className="w-4 h-4" />
              Change
            </button>

            <button
              onClick={(e) => { e.stopPropagation(); onAnalyze(); }}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-semibold shadow-lg shadow-emerald-500/20 transition-all transform hover:scale-105 active:scale-95"
            >
              <Zap className="w-4 h-4 fill-current" />
              Analyze Meal
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
