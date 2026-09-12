import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Compass,
  CheckCircle2,
  TrendingUp,
  Award,
  Layers,
  Zap,
  Target,
  BarChart3
} from 'lucide-react';
import { api } from '../api/client';

export default function StrategyTab() {
  const [loading, setLoading] = useState(false);

  const pillars = [
    { num: 1, title: "AI & Automation Tips", impact: "High Virality", color: "text-cyan-400" },
    { num: 2, title: "Behind the Scenes", impact: "High Trust", color: "text-brand-400" },
    { num: 3, title: "Industry Insights", impact: "High Engagement", color: "text-emerald-400" },
    { num: 4, title: "User Success Stories", impact: "High Conversion", color: "text-blue-400" },
  ];

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white font-mono">11 AI Strategy Engine</h2>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">
            Multi-model strategic synthesis, content pillar optimization, and radar capability mapping
          </p>
        </div>
        <span className="text-xs font-mono font-bold px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 flex items-center gap-2">
          <Compass size={14} />
          <span>Strategic Synthesis</span>
        </span>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left: Content Strategy Pillars */}
        <div className="lg:col-span-7 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono">Content Strategy</h3>
            <span className="text-xs text-brand-400 font-mono font-bold">AI Recommendation</span>
          </div>

          {/* Recommended Strategy Box */}
          <div className="p-4 rounded-2xl bg-gradient-to-r from-brand-950/40 via-[#0D121F] to-cyan-950/40 border border-brand-500/40 space-y-1">
            <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Recommended Strategy</span>
            <p className="text-base font-bold text-white font-mono">Educational Content</p>
            <p className="text-xs text-emerald-400 font-mono font-semibold">High performance predicted (+34% audience retention)</p>
          </div>

          {/* Strategy Pillars List */}
          <div className="space-y-2.5">
            <p className="text-xs font-bold text-white font-mono">Strategy Pillars:</p>
            {pillars.map((pil) => (
              <div
                key={pil.num}
                className="p-3.5 rounded-2xl bg-[#07090E] border border-[#1E293B] flex items-center justify-between font-mono text-xs"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-lg bg-[#0D121F] border border-[#1E293B] flex items-center justify-center font-bold text-slate-300 text-[11px]">
                    {pil.num}
                  </span>
                  <span className="font-semibold text-slate-200">{pil.title}</span>
                </div>
                <span className={`text-[11px] font-bold ${pil.color}`}>{pil.impact}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Strategy Radar Chart */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-5 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono">Pillar Balance Matrix</h3>
            <span className="text-xs text-slate-400 font-mono">Performance Radar</span>
          </div>

          {/* SVG Radar Chart */}
          <div className="h-56 w-full flex items-center justify-center relative my-2">
            <svg viewBox="0 0 240 240" className="w-48 h-48">
              {/* Web Rings */}
              <polygon points="120,20 215,89 179,200 61,200 25,89" fill="none" stroke="#1E293B" strokeWidth="1" />
              <polygon points="120,50 184,96 159,174 81,174 56,96" fill="none" stroke="#1E293B" strokeWidth="1" />
              <polygon points="120,80 152,104 140,147 100,147 88,104" fill="none" stroke="#1E293B" strokeWidth="1" />

              {/* Axes Lines */}
              <line x1="120" y1="120" x2="120" y2="20" stroke="#1E293B" strokeWidth="1" />
              <line x1="120" y1="120" x2="215" y2="89" stroke="#1E293B" strokeWidth="1" />
              <line x1="120" y1="120" x2="179" y2="200" stroke="#1E293B" strokeWidth="1" />
              <line x1="120" y1="120" x2="61" y2="200" stroke="#1E293B" strokeWidth="1" />
              <line x1="120" y1="120" x2="25" y2="89" stroke="#1E293B" strokeWidth="1" />

              {/* Data Polygon */}
              <polygon
                points="120,35 190,95 160,185 70,180 40,95"
                fill="rgba(124, 58, 237, 0.25)"
                stroke="#7C3AED"
                strokeWidth="2"
              />
              {/* Data Dots */}
              <circle cx="120" cy="35" r="4" fill="#06B6D4" />
              <circle cx="190" cy="95" r="4" fill="#06B6D4" />
              <circle cx="160" cy="185" r="4" fill="#06B6D4" />
              <circle cx="70" cy="180" r="4" fill="#06B6D4" />
              <circle cx="40" cy="95" r="4" fill="#06B6D4" />
            </svg>
          </div>

          <div className="flex flex-wrap justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-[#1E293B]">
            <span>Engagement</span>
            <span>Virality</span>
            <span>Reach</span>
            <span>Consistency</span>
            <span>Growth</span>
          </div>
        </div>
      </div>
    </div>
  );
}
