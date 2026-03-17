"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Veonix — Global Keyboard Navigation
 * components/keyboard-nav.tsx
 *
 * Listens for global keydown events.
 * Currently handles:
 * - Escape: Navigate to home (/)
 */
export default function KeyboardNav() {
    const router = useRouter();

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Don't navigate if user is typing in an input or textarea
            const isInput = e.target instanceof HTMLInputElement ||
                e.target instanceof HTMLTextAreaElement ||
                (e.target as HTMLElement).isContentEditable;

            if (e.key === "Escape" && !isInput) {
                router.push("/");
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [router]);

    // This component doesn't render anything
    return null;
}
