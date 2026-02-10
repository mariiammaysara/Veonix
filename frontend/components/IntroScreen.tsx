"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface IntroScreenProps {
    onComplete: () => void;
}

export default function IntroScreen({ onComplete }: IntroScreenProps) {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        // Check session storage
        const hasSeenIntro = sessionStorage.getItem("veonix_intro_seen");

        if (hasSeenIntro) {
            setIsVisible(false);
            onComplete();
            return;
        }

        // Set flag and timer
        const timer = setTimeout(() => {
            sessionStorage.setItem("veonix_intro_seen", "true");
            setIsVisible(false);
            setTimeout(onComplete, 1000); // Allow exit animation to finish
        }, 2500);

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
                    exit={{ opacity: 0, transition: { duration: 0.8, ease: "easeInOut" } }}
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-gradient-to-b from-[#020617] to-[#03122f] overflow-hidden"
                >
                    {/* Ambient Glow */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 0.4, scale: 1.2 }}
                            transition={{ duration: 2, ease: "easeOut" }}
                            className="w-[500px] h-[500px] bg-emerald-500/20 rounded-full blur-[120px]"
                        />
                    </div>

                    {/* 3D Text Container */}
                    <div className="relative perspective-1000">
                        <motion.h1
                            initial={{
                                opacity: 0,
                                scale: 0.8,
                                filter: "blur(12px)",
                                rotateX: 20,
                                y: 50
                            }}
                            animate={{
                                opacity: 1,
                                scale: 1,
                                filter: "blur(0px)",
                                rotateX: 0,
                                y: 0
                            }}
                            transition={{
                                duration: 1.8,
                                ease: [0.22, 1, 0.36, 1]
                            }}
                            className="text-6xl md:text-8xl font-black tracking-widest text-transparent bg-clip-text bg-gradient-to-b from-[#10b981] to-[#34d399] relative z-10"
                            style={{
                                textShadow: "0 20px 50px rgba(16, 185, 129, 0.3), 0 0 20px rgba(16, 185, 129, 0.1)"
                            }}
                        >
                            VEONIX
                        </motion.h1>

                        {/* Reflection / Floor Shadow */}
                        <motion.div
                            initial={{ opacity: 0, scaleX: 0.5 }}
                            animate={{ opacity: 0.3, scaleX: 1 }}
                            transition={{ duration: 2, delay: 0.5 }}
                            className="absolute -bottom-8 left-0 right-0 h-4 bg-emerald-500/30 blur-xl rounded-[100%]"
                        />
                    </div>

                    {/* Subtle details */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1, duration: 1 }}
                        className="absolute bottom-10 text-emerald-500/40 text-xs tracking-[0.5em] font-light uppercase"
                    >
                        Visual Intelligence
                    </motion.div>

                </motion.div>
            )}
        </AnimatePresence>
    );
}
