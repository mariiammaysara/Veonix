"use client";
import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorCardProps {
    title: string;
    message: string;
    onRetry?: () => void;
}

export default function ErrorCard({ title, message, onRetry }: ErrorCardProps) {
    return (
        <div className="w-full max-w-lg mx-auto mt-6 p-6 rounded-2xl bg-red-500/5 border border-red-500/10 flex flex-col items-center text-center animate-in fade-in slide-in-from-top-4 backdrop-blur-sm">
            <div className="p-3 bg-red-500/10 rounded-full mb-3 ring-1 ring-red-500/20">
                <AlertCircle className="w-6 h-6 text-red-400" />
            </div>
            <h3 className="text-red-200 font-semibold text-lg mb-2">{title}</h3>
            <p className="text-slate-400 text-sm mb-6 leading-relaxed max-w-xs">{message}</p>

            {onRetry && (
                <button
                    onClick={onRetry}
                    className="flex items-center gap-2 px-6 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-300 hover:text-red-200 text-sm font-medium rounded-full transition-all duration-300 border border-red-500/10 hover:border-red-500/30"
                >
                    <RefreshCw className="w-4 h-4" />
                    Try Again
                </button>
            )}
        </div>
    );
}
