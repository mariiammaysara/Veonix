"use client";

import { useState } from "react";
import Link from "next/link";
import { askCoach } from "@/lib/api";

interface Message {
  sender: "user" | "coach";
  text: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "coach",
      text: "Hi! I am your AI Nutrition Coach. Ask me anything about your meal history! (e.g., 'What is my average calories this week?' or 'How many meals did I log this month?')",
    },
  ]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || isLoading) return;

    // Append user message
    setMessages((prev) => [...prev, { sender: "user", text: trimmedQuestion }]);
    setQuestion("");
    setIsLoading(true);

    try {
      const res = await askCoach(trimmedQuestion);
      setMessages((prev) => [...prev, { sender: "coach", text: res.answer }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "coach",
          text: err?.message || "Sorry, I encountered an error processing your query. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-[#0f172a] to-[#020617] text-slate-100 flex flex-col items-center justify-start px-6 py-24">
      <div className="max-w-3xl w-full mx-auto text-center mb-10">
        <div className="flex justify-center mb-6">
          <div className="flex items-center gap-2">
            <svg width="36" height="36" viewBox="0 0 100 100" fill="none">
              <path
                d="M20 75 L50 20 L80 75"
                stroke="#34d399"
                strokeWidth="8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="50" cy="55" r="6" fill="#10b981" />
            </svg>
            <span className="text-2xl font-bold tracking-wide">Veonix</span>
          </div>
        </div>

        <h1 className="text-3xl md:text-4xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white via-emerald-200 to-emerald-500 pb-2">
          AI Nutrition Analyzer
        </h1>

        <p className="text-emerald-400/80 max-w-xl mx-auto text-base leading-relaxed font-medium mb-6">
          Upload any meal photo → Veonix analyzes it using advanced AI →
          Instantly get calories, macros, and full nutrition facts.
        </p>

        <div>
          <Link
            href="/dashboard/upload"
            className="px-8 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-black font-semibold rounded-full shadow-lg shadow-emerald-500/30 transition inline-block text-sm"
          >
            Upload Your Meal
          </Link>
        </div>
      </div>

      {/* Glassmorphic Chat Interface */}
      <div className="max-w-3xl w-full mx-auto bg-slate-900/60 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur-md overflow-hidden flex flex-col h-[480px]">
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-semibold text-emerald-400 text-sm">Ask your AI Coach</span>
          </div>
          <span className="text-xs text-slate-500">Connected to meal history</span>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 flex flex-col">
          {messages.map((msg, index) => {
            const isCoach = msg.sender === "coach";
            return (
              <div
                key={index}
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  isCoach
                    ? "bg-slate-800/80 text-slate-200 self-start rounded-tl-none border border-slate-700/50"
                    : "bg-emerald-500 text-black self-end rounded-tr-none font-medium shadow-md shadow-emerald-500/10"
                }`}
              >
                {msg.text}
              </div>
            );
          })}
          {isLoading && (
            <div className="bg-slate-800/50 text-slate-400 self-start rounded-2xl rounded-tl-none px-4 py-3 text-sm border border-slate-700/30 animate-pulse flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "300ms" }} />
              <span>Analyzing meal database...</span>
            </div>
          )}
        </div>

        {/* Chat Input Footer */}
        <form onSubmit={handleSend} className="p-4 border-t border-slate-800 bg-slate-950/40 flex items-center gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What is my average protein this week?"
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30 transition"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !question.trim()}
            className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 disabled:hover:bg-emerald-500 text-black font-semibold rounded-xl text-sm transition flex items-center gap-1.5"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}