"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function LoadingPage() {
    const router = useRouter();

    useEffect(() => {
        const timer = setTimeout(() => {
            // Redirect to home page after 2 seconds
            router.push("/");
        }, 2000);

        return () => clearTimeout(timer);
    }, [router]);

    return (
        <div className="fixed inset-0 w-full h-full bg-slate-950 flex flex-col items-center justify-center z-50 overflow-hidden">
            <div className="relative z-10 flex flex-col items-center animate-in fade-in zoom-in duration-700">
                {/* Logo */}
                <div className="mb-6">
                    <svg width="48" height="48" viewBox="0 0 100 100" fill="none">
                        <path d="M20 75 L50 20 L80 75" stroke="#10b981" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
                        <circle cx="50" cy="55" r="5" fill="#10b981" />
                    </svg>
                </div>

                {/* App Name */}
                <h1 className="text-xl font-medium tracking-[0.2em] text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-600 mb-8">
                    VEONIX
                </h1>

                {/* Loading Text */}
                <p className="text-slate-500 text-sm font-medium tracking-wide mb-6">
                    Preparing your nutrition insights...
                </p>

                {/* Minimal Spinner */}
                <div>
                    <Loader2 className="w-5 h-5 text-emerald-500/80 animate-spin duration-[2000ms]" />
                </div>
            </div>
        </div>
    );
}
