"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, useReducedMotion } from "framer-motion";

export default function IntroPage() {
    const router = useRouter();
    const shouldReduceMotion = useReducedMotion();
    const [redirect, setRedirect] = useState(false);

    useEffect(() => {
        // If reduced motion is preferred, redirect almost immediately
        if (shouldReduceMotion) {
            router.push("/");
            return;
        }

        // Redirect after animation completes (2.5s)
        const timer = setTimeout(() => {
            setRedirect(true);
            setTimeout(() => router.push("/"), 500); // Wait for exit animation
        }, 2500);

        return () => clearTimeout(timer);
    }, [router, shouldReduceMotion]);

    return (
        <div className="fixed inset-0 bg-[#020617] flex items-center justify-center overflow-hidden z-50">

            {/* Background Gradient Spotlights */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 1 }}
                className="absolute inset-0 pointer-events-none"
            >
                <div className="absolute top-[20%] left-[20%] w-[300px] h-[300px] bg-emerald-500/20 rounded-full blur-[100px]" />
                <div className="absolute bottom-[20%] right-[20%] w-[350px] h-[350px] bg-blue-500/10 rounded-full blur-[120px]" />
            </motion.div>

            {/* Main Content Container */}
            <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 1.1, filter: "blur(10px)" }}
                transition={{
                    duration: 1.2,
                    ease: [0.22, 1, 0.36, 1], // Custom heavy ease-out
                    delay: 0.2
                }}
                className={`flex flex-col items-center justify-center relative ${redirect ? "opacity-0 transition-opacity duration-500" : ""}`}
            >

                {/* Glow Effect Behind Logo */}
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 0.6, 0.3]
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-emerald-500/30 rounded-full blur-3xl -z-10"
                />

                {/* 3D-Style Logo Icon */}
                <div className="relative mb-8 perspective-1000">
                    <svg width="80" height="80" viewBox="0 0 100 100" fill="none" className="drop-shadow-[0_10px_20px_rgba(16,185,129,0.4)]">
                        <motion.path
                            d="M20 75 L50 20 L80 75"
                            stroke="#10b981"
                            strokeWidth="6"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            initial={{ pathLength: 0, opacity: 0 }}
                            animate={{ pathLength: 1, opacity: 1 }}
                            transition={{ duration: 1.5, ease: "easeInOut" }}
                        />
                        <motion.circle
                            cx="50" cy="55" r="5"
                            fill="#10b981"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 1, type: "spring", stiffness: 200 }}
                        />
                    </svg>
                </div>

                {/* Text with Gradient and Depth */}
                <h1 className="text-5xl font-bold tracking-[0.2em] text-transparent bg-clip-text bg-gradient-to-br from-white via-slate-200 to-emerald-400 drop-shadow-2xl relative">
                    VEONIX
                    {/* Reflection / Shine effect */}
                    <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent bg-[length:200%_100%] animate-shine opacity-30 blur-sm pointer-events-none"></span>
                </h1>

                {/* Subtitle */}
                <motion.p
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.2, duration: 0.8 }}
                    className="text-emerald-500/80 text-sm font-medium tracking-widest mt-4 uppercase"
                >
                    Visual Intelligence
                </motion.p>
            </motion.div>

        </div>
    );
}
