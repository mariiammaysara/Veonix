import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Veonix – AI Calorie Analyzer",
  description: "Upload a food image and get instant nutrition facts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#020617] text-slate-100 min-h-screen flex flex-col`}
      >
        <main className="flex-1 flex flex-col">
          {children}
        </main>

        {/* FOOTER FIXED AT BOTTOM */}
        <footer className="w-full text-center py-6 text-sm text-gray-400">
          Developed by{" "}
          <span className="text-emerald-400 font-medium">
            Mariam Maysara
          </span>
        </footer>
      </body>
    </html>
  );
}
