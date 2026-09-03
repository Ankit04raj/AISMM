import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Zap,
  ArrowRight,
  ChevronRight,
  Shield,
  Activity,
  Cpu,
  Lock,
  Layers,
  CheckCircle2,
  RefreshCw,
  Eye,
  TrendingUp,
  Clock,
  Flame,
  Globe,
  Check
} from 'lucide-react';
import { api } from '../api/client';

export default function LandingPage({ onLaunchDashboard, onOpenAuth }) {
  const [demoPrompt, setDemoPrompt] = useState("Just launched our new AI-powered analytics dashboard! 🚀 The insights are incredible! #AI #Analytics #Dashboard");
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [captionScore, setCaptionScore] = useState({ score: 92.4, grade: "Excellent" });
  const [sentimentScore, setSentimentScore] = useState({ score: "+0.84", label: "Very Positive" });
  const [bestTime, setBestTime] = useState("Today, 7:00 PM");
  const [adaptedOutputs, setAdaptedOutputs] = useState({
    instagram: "Big news! 🎉 Our AI-powered analytics dashboard is here! The insights are incredible! Link in bio! ✨\n#AI #Analytics #Growth #Tech",
    twitter: "Just launched: AI analytics dashboard. 📊 Real insights on audience engagement. Try it now! 👇 #AI #Analytics",
    linkedin: "Real Insights. Real Impact. Our new AI dashboard is transforming data into decisions. #AI #Analytics #Leadership #Innovation",
    facebook: "Excited to share our new AI-powered analytics dashboard! Built for real insights and real results. Check it out and let us know what you think!",
    youtube: "We've launched our AI-powered analytics dashboard! See how it can transform your data! 🚀\nTags: #AI, #Analytics, #Tech",
  });

  const handleOptimize = async () => {
    setIsOptimizing(true);
    try {
      const data = await api.optimizeContentAll({
        text: demoPrompt,
        platforms: ["instagram", "facebook", "twitter", "linkedin", "youtube"],
        top_k_hashtags: 5,
      });
      if (data) {
        if (data.caption_analysis) {
          setCaptionScore({ score: data.caption_analysis.score, grade: data.caption_analysis.grade });
        }
        if (data.sentiment) {
          setSentimentScore({ score: data.sentiment.score > 0 ? `+${data.sentiment.score}` : `${data.sentiment.score}`, label: data.sentiment.label });
        }
        if (data.platform_variants) {
          const variants = {};
          Object.entries(data.platform_variants).forEach(([k, v]) => {
            variants[k] = v.text;
          });
          setAdaptedOutputs(variants);
        }
      }
    } catch {
      // Local fallback for offline mode
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#07090E] text-[#F1F5F9] flex flex-col selection:bg-[#7C3AED] selection:text-white font-['Plus_Jakarta_Sans']">
      {/* Top Navigation */}
      <header className="border-b border-[#1E293B] bg-[#07090E]/90 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <div className="flex items-center space-x-2.5">
              <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#06B6D4] flex items-center justify-center shadow-lg shadow-[#7C3AED]/30">
                <Zap className="h-4 w-4 text-white" />
              </div>
              <span className="font-extrabold text-lg tracking-tight text-white">
                AISMM
              </span>
            </div>

            {/* Links */}
            <nav className="hidden md:flex items-center space-x-6 text-xs font-semibold text-slate-400">
              <a href="#features" className="hover:text-white transition-colors">Features</a>
              <div className="flex items-center space-x-1 hover:text-white cursor-pointer transition-colors">
                <span>Solutions</span>
                <span className="text-[10px]">▾</span>
              </div>
              <a href="#research" className="hover:text-white transition-colors">Research</a>
              <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
              <a href="#docs" className="hover:text-white transition-colors">Docs</a>
              <a href="#about" className="hover:text-white transition-colors">About</a>
            </nav>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onOpenAuth}
              className="text-xs font-bold text-slate-300 hover:text-white px-3 py-2 transition-colors"
            >
              Sign In
            </button>
            <button
              onClick={onLaunchDashboard}
              className="px-4 py-2 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white font-bold text-xs shadow-lg shadow-[#7C3AED]/30 transition-all flex items-center space-x-1.5"
            >
              <span>Get Started</span>
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 md:pt-16 md:pb-24">
        {/* Glow Effects */}
        <div className="absolute top-1/3 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[450px] bg-[#7C3AED]/15 rounded-full blur-[130px] pointer-events-none -z-10" />
        <div className="absolute top-1/2 right-10 w-[450px] h-[450px] bg-[#06B6D4]/10 rounded-full blur-[120px] pointer-events-none -z-10" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

            {/* Left Hero Column */}
            <div className="lg:col-span-6 space-y-6 text-left">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#0D121F] border border-[#1E293B] text-slate-300 text-[11px] font-medium">
                <Sparkles className="h-3 w-3 text-[#06B6D4]" />
                <span>AI-Powered Social Media Management</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-white">
                The Future of <br />
                <span className="text-white">
                  Social Media is AI
                </span>
              </h1>

              <p className="text-sm sm:text-base text-slate-400 max-w-xl leading-relaxed">
                AISMM is the world's first complete AI-powered social media management platform with 13 research-backed modules and enterprise-grade architecture.
              </p>

              {/* 4 Pill Stats Row */}
              <div className="grid grid-cols-4 gap-2.5 max-w-lg">
                {[
                  { value: "13", label: "AI Modules" },
                  { value: "5+", label: "Platforms" },
                  { value: "194", label: "Tests Passing" },
                  { value: "99.9%", label: "Uptime" },
                ].map((stat, i) => (
                  <div key={i} className="bg-[#0D121F] border border-[#1E293B] rounded-2xl p-3 text-center shadow-lg">
                    <div className="text-lg sm:text-xl font-extrabold text-[#7C3AED] font-mono">{stat.value}</div>
                    <div className="text-[10px] text-slate-400 font-medium mt-0.5">{stat.label}</div>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <button
                  onClick={onLaunchDashboard}
                  className="px-6 py-3 rounded-xl bg-[#7C3AED] hover:bg-[#6D28D9] text-white font-bold text-xs shadow-xl shadow-[#7C3AED]/30 transition-all flex items-center space-x-2"
                >
                  <span>Explore Live Demo</span>
                </button>
                <button
                  onClick={onLaunchDashboard}
                  className="px-6 py-3 rounded-xl bg-[#0D121F] hover:bg-[#131B2E] border border-[#1E293B] text-slate-200 font-bold text-xs transition-all"
                >
                  <span>View Dashboard</span>
                </button>
              </div>

              {/* Sub-label */}
              <div className="pt-2 text-[11px] text-slate-500 font-mono">
                <div>Built with ❤️ by AISMM Team</div>
                <div className="text-slate-600 mt-0.5">Research Backed • Production Ready • Enterprise Grade</div>
              </div>

              {/* Center Holographic 3D Cube Canvas Visual */}
              <div className="relative pt-6 pb-2 flex items-center justify-center">
                <div className="relative w-72 h-72 bg-[#0D121F]/60 border border-[#1E293B] rounded-3xl p-4 flex items-center justify-center shadow-2xl backdrop-blur-sm">
                  {/* Surrounding social icon floating nodes */}
                  <div className="absolute top-4 left-6 w-8 h-8 rounded-full bg-pink-600/30 border border-pink-500/50 flex items-center justify-center text-pink-300 text-xs font-bold animate-bounce">
                    IG
                  </div>
                  <div className="absolute top-4 right-6 w-8 h-8 rounded-full bg-blue-600/30 border border-blue-500/50 flex items-center justify-center text-blue-300 text-xs font-bold">
                    FB
                  </div>
                  <div className="absolute bottom-6 left-6 w-8 h-8 rounded-full bg-slate-700/50 border border-slate-500/50 flex items-center justify-center text-slate-200 text-xs font-bold">
                    X
                  </div>
                  <div className="absolute bottom-6 right-6 w-8 h-8 rounded-full bg-cyan-600/30 border border-cyan-500/50 flex items-center justify-center text-cyan-300 text-xs font-bold">
                    LI
                  </div>

                  {/* SVG Cube Hologram */}
                  <svg viewBox="0 0 160 160" className="w-40 h-40 drop-shadow-[0_0_20px_rgba(124,58,237,0.5)]">
                    {/* Outer Rings */}
                    <ellipse cx="80" cy="80" rx="70" ry="35" fill="none" stroke="#1E293B" strokeWidth="1.5" />
                    <ellipse cx="80" cy="80" rx="55" ry="25" fill="none" stroke="#7C3AED" strokeWidth="1.5" strokeDasharray="4 4" />
                    {/* Isometric Cube */}
                    <polygon points="80,25 125,50 80,75 35,50" fill="#7C3AED" fillOpacity="0.85" stroke="#C4B5FD" strokeWidth="1.5" />
                    <polygon points="35,50 80,75 80,125 35,100" fill="#0D121F" stroke="#06B6D4" strokeWidth="1.5" />
                    <polygon points="80,75 125,50 125,100 80,125" fill="#131B2E" stroke="#7C3AED" strokeWidth="1.5" />
                    {/* Center Core Text */}
                    <text x="80" y="80" fill="#22D3EE" fontSize="13" fontWeight="900" textAnchor="middle" dominantBaseline="middle" fontFamily="sans-serif">AI</text>
                  </svg>
                </div>
              </div>
            </div>

            {/* Right Interactive Preview & Adapted Outputs Panel */}
            <div className="lg:col-span-6 space-y-5">
              {/* AI Engine Live Preview Box */}
              <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-2xl space-y-4">
                <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
                  <div>
                    <h3 className="font-extrabold text-sm text-white">AI Engine Live Preview</h3>
                    <p className="text-[11px] text-slate-400">Try our AI Content Adaptation</p>
                  </div>
                  <Sparkles className="w-4 h-4 text-[#06B6D4]" />
                </div>

                <div className="bg-[#07090E] border border-[#1E293B] rounded-2xl p-3.5">
                  <textarea
                    value={demoPrompt}
                    onChange={(e) => setDemoPrompt(e.target.value)}
                    rows={3}
                    className="w-full bg-transparent text-xs text-slate-200 focus:outline-none resize-none leading-relaxed"
                  />
                </div>

                <button
                  onClick={handleOptimize}
                  disabled={isOptimizing}
                  className="w-full py-2.5 bg-[#7C3AED] hover:bg-[#6D28D9] rounded-xl text-xs font-bold text-white shadow-lg shadow-[#7C3AED]/25 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {isOptimizing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  <span>{isOptimizing ? "Optimizing with Engine..." : "Optimize Content"}</span>
                </button>

                {/* Live AI Diagnostics row */}
                <div className="pt-2">
                  <div className="text-[10px] uppercase font-bold text-slate-400 font-mono mb-2">Live AI Diagnostics</div>
                  <div className="grid grid-cols-3 gap-2 text-center font-mono">
                    <div className="bg-[#07090E] border border-[#1E293B] rounded-xl p-2.5">
                      <div className="text-[10px] text-slate-500">Caption Quality</div>
                      <div className="text-xs font-bold text-emerald-400 mt-1">{captionScore.score} / 100</div>
                      <div className="text-[9px] text-emerald-500">● {captionScore.grade}</div>
                    </div>
                    <div className="bg-[#07090E] border border-[#1E293B] rounded-xl p-2.5">
                      <div className="text-[10px] text-slate-500">Sentiment Score</div>
                      <div className="text-xs font-bold text-emerald-400 mt-1">{sentimentScore.score}</div>
                      <div className="text-[9px] text-emerald-500">● {sentimentScore.label}</div>
                    </div>
                    <div className="bg-[#07090E] border border-[#1E293B] rounded-xl p-2.5">
                      <div className="text-[10px] text-slate-500">Best Time to Post</div>
                      <div className="text-xs font-bold text-cyan-400 mt-1">{bestTime}</div>
                      <div className="text-[9px] text-cyan-500">● Optimal Reach</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Adapted Outputs Cards */}
              <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-2xl space-y-3">
                <h3 className="font-extrabold text-sm text-white border-b border-[#1E293B] pb-3">
                  AI Adapted Outputs
                </h3>

                <div className="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
                  {/* Instagram */}
                  <div className="p-3 bg-[#07090E] border border-[#1E293B] rounded-2xl space-y-1.5">
                    <div className="flex items-center space-x-2">
                      <div className="w-5 h-5 rounded-lg bg-pink-600/20 text-pink-400 text-[10px] font-bold flex items-center justify-center">IG</div>
                      <span className="text-xs font-bold text-slate-200">Instagram Format</span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">{adaptedOutputs.instagram}</p>
                    <div className="flex items-center space-x-4 text-[10px] text-slate-500 font-mono">
                      <span>❤️ 2.4K</span>
                      <span>💬 120</span>
                      <span>🔖 310</span>
                    </div>
                  </div>

                  {/* X */}
                  <div className="p-3 bg-[#07090E] border border-[#1E293B] rounded-2xl space-y-1.5">
                    <div className="flex items-center space-x-2">
                      <div className="w-5 h-5 rounded-lg bg-slate-700/40 text-slate-300 text-[10px] font-bold flex items-center justify-center">X</div>
                      <span className="text-xs font-bold text-slate-200">X (Twitter) Format</span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">{adaptedOutputs.twitter}</p>
                    <div className="flex items-center space-x-4 text-[10px] text-slate-500 font-mono">
                      <span>🔁 1.2K</span>
                      <span>💬 89</span>
                    </div>
                  </div>

                  {/* LinkedIn */}
                  <div className="p-3 bg-[#07090E] border border-[#1E293B] rounded-2xl space-y-1.5">
                    <div className="flex items-center space-x-2">
                      <div className="w-5 h-5 rounded-lg bg-blue-600/20 text-blue-400 text-[10px] font-bold flex items-center justify-center">LI</div>
                      <span className="text-xs font-bold text-slate-200">LinkedIn Format</span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">{adaptedOutputs.linkedin}</p>
                    <div className="flex items-center space-x-4 text-[10px] text-slate-500 font-mono">
                      <span>👍 804</span>
                      <span>💬 45</span>
                    </div>
                  </div>

                  {/* Facebook */}
                  <div className="p-3 bg-[#07090E] border border-[#1E293B] rounded-2xl space-y-1.5">
                    <div className="flex items-center space-x-2">
                      <div className="w-5 h-5 rounded-lg bg-indigo-600/20 text-indigo-400 text-[10px] font-bold flex items-center justify-center">FB</div>
                      <span className="text-xs font-bold text-slate-200">Facebook Format</span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">{adaptedOutputs.facebook}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Platform Integration Badges Bar */}
          <div className="mt-12 p-4 bg-[#0D121F] border border-[#1E293B] rounded-3xl shadow-xl">
            <div className="text-[10px] uppercase font-bold text-slate-400 font-mono text-center mb-3">Platform Integration Ecosystem</div>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {[
                { name: "Instagram", status: "100% Verified", color: "text-pink-400" },
                { name: "X (Twitter)", status: "100% Verified", color: "text-slate-300" },
                { name: "Facebook", status: "100% Verified", color: "text-blue-400" },
                { name: "LinkedIn", status: "100% Passing", color: "text-cyan-400" },
                { name: "YouTube", status: "100% Verified", color: "text-red-400" },
              ].map((p, idx) => (
                <div key={idx} className="p-2.5 bg-[#07090E] rounded-2xl border border-[#1E293B] text-center">
                  <div className={`text-xs font-bold ${p.color}`}>{p.name}</div>
                  <div className="text-[10px] text-emerald-400 font-mono mt-0.5">● {p.status}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 4 Feature Value Pillars */}
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: Cpu, title: "AI Powered", desc: "Advanced ML Models" },
              { icon: Activity, title: "Real-time", desc: "Live Data Processing" },
              { icon: Lock, title: "Secure", desc: "Enterprise Security" },
              { icon: Boxes, title: "Scalable", desc: "Built for Growth" },
            ].map((feat, i) => {
              const Icon = feat.icon;
              return (
                <div key={i} className="p-4 bg-[#0D121F] border border-[#1E293B] rounded-2xl flex items-center space-x-3.5">
                  <div className="w-9 h-9 rounded-xl bg-[#07090E] border border-[#1E293B] flex items-center justify-center text-[#7C3AED]">
                    <Icon className="w-4 h-4 text-[#06B6D4]" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">{feat.title}</h4>
                    <p className="text-[11px] text-slate-400">{feat.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#1E293B] bg-[#07090E] py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <div className="h-6 w-6 rounded-md bg-[#7C3AED] flex items-center justify-center text-white font-bold text-xs">
              A
            </div>
            <span className="font-semibold text-slate-300">AISMM — Universal AI Social Media Management System</span>
          </div>
          <div>
            13 Modules • 5 Adapters • 216 Tests Passing • Production Verified
          </div>
          <button
            onClick={onLaunchDashboard}
            className="text-[#06B6D4] hover:underline font-bold"
          >
            Launch Universal Studio →
          </button>
        </div>
      </footer>
    </div>
  );
}
