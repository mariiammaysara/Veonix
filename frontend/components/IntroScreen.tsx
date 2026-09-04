"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface IntroScreenProps {
    onComplete: () => void;
}

export default function IntroScreen({ onComplete }: IntroScreenProps) {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        // Check session storage to avoid repeating the intro on every visit
        const hasSeenIntro = sessionStorage.getItem("veonix_intro_seen");

        if (hasSeenIntro) {
            setIsVisible(false);
            onComplete();
            return;
        }

        // Timer for the intro presentation
        const timer = setTimeout(() => {
            sessionStorage.setItem("veonix_intro_seen", "true");
            setIsVisible(false);
            setTimeout(onComplete, 800); // Allow exit animation to complete smoothly
        }, 2200);

        return () => clearTimeout(timer);
    }, [onComplete]);

    if (!isVisible && sessionStorage.getItem("veonix_intro_seen")) {
        return null;
    }

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    key="intro-overlay"
                    initial={{ opacity: 1 }}
                    exit={{ opacity: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } }}
                    className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#020617] overflow-hidden"
                >
                    {/* Ambient Glow - Soft, elegant, and minimal */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 0.15, scale: 1.1 }}
                            transition={{ duration: 1.8, ease: "easeOut" }}
                            className="w-[450px] h-[450px] bg-gradient-to-tr from-emerald-500/20 to-teal-500/20 rounded-full blur-[100px]"
                        />
                    </div>

                    {/* Logo & Brand Name Container */}
                    <div className="flex flex-col items-center gap-6 z-10">
                        {/* Elegant Line-Art Logo */}
                        <motion.div
                            initial={{ opacity: 0, y: 15, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            transition={{
                                duration: 1.2,
                                ease: [0.16, 1, 0.3, 1]
                            }}
                            className="relative"
                        >
                            <svg width="60" height="60" viewBox="0 0 100 100" fill="none" className="drop-shadow-[0_0_15px_rgba(16,185,129,0.15)]">
                                <motion.path
                                    d="M25 70L50 25L75 70"
                                    stroke="#10b981"
                                    strokeWidth="4.5"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    initial={{ pathLength: 0 }}
                                    animate={{ pathLength: 1 }}
                                    transition={{ duration: 1.4, ease: "easeInOut" }}
                                />
                                <motion.circle
                                    cx="50"
                                    cy="53"
                                    r="5.5"
                                    fill="#10b981"
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 0.8, duration: 0.5, ease: "easeOut" }}
                                />
                            </svg>
                        </motion.div>

                        {/* Modern Sentence Case with Premium Gradient */}
                        <motion.h1
                            initial={{
                                opacity: 0,
                                scale: 0.96,
                                filter: "blur(4px)",
                                y: 8
                            }}
                            animate={{
                                opacity: 1,
                                scale: 1,
                                filter: "blur(0px)",
                                y: 0
                            }}
                            transition={{
                                duration: 1.2,
                                ease: [0.16, 1, 0.3, 1],
                                delay: 0.2
                            }}
                            className="text-4xl md:text-5xl font-bold tracking-[-0.02em] text-transparent bg-clip-text bg-gradient-to-r from-[#ffffff] via-[#34d399] to-[#22d3ee] text-center select-none"
                        >
                            Veonix
                        </motion.h1>
                    </div>

                    {/* Minimalist Subtitle */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.35 }}
                        transition={{ delay: 0.7, duration: 1.2 }}
                        className="absolute bottom-12 text-slate-400 text-[10px] tracking-[0.6em] font-medium uppercase select-none"
                    >
                        Visual Intelligence
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
