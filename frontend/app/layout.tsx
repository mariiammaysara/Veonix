import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import KeyboardNav from "@/components/keyboard-nav";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Veonix",
  description: "Upload a food image and get instant nutrition facts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#020617] text-slate-100 min-h-screen`}>
        <KeyboardNav />
        {children}
      </body>
    </html>
  );
}
