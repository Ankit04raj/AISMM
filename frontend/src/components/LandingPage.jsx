import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Layers,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Zap,
  Lock,
  TrendingUp,
  Share2,
  CheckCircle2,
  Clock,
  Heart,
  MessageCircle,
  Repeat2,
  Eye,
  Activity
} from 'lucide-react';

export default function LandingPage({ onLaunchDashboard, onOpenAuth }) {
  const [activePlatform, setActivePlatform] = useState('instagram');
  const [inputText, setInputText] = useState('Just launched our new AI-powered analytics dashboard! 🚀 The insights are incredible! #AI #Analytics #Dashboard');

  const adaptedOutputs = {
    instagram: {
      text: "Big news! 🚀 Our AI-powered analytics dashboard is here! The insights are incredible! Link in bio! 💖",
      likes: "2.5K",
      comments: "120",
      color: "from-pink-500 to-purple-600",
      badge: "Instagram"
    },
    x: {
      text: "Just launched: AI analytics dashboard. Real insights on interactive engagement. #AI #Analytics",
      likes: "1.2K",
      comments: "89",
      color: "from-blue-400 to-slate-700",
      badge: "X (Twitter)"
    },
    linkedin: {
      text: "Real Insights, Real Impact. Our new AI dashboard is transforming data into decisions. #AI #Analytics",
      likes: "806",
      comments: "45",
      color: "from-blue-600 to-cyan-700",
      badge: "LinkedIn"
    },
    facebook: {
      text: "Excited to share our new AI-powered analytics dashboard! Built for real insights and real results.",
      likes: "2.1K",
      comments: "102",
      color: "from-blue-600 to-indigo-600",
      badge: "Facebook"
    },
    youtube: {
      text: "We've launched our AI-powered analytics dashboard! See how it can transform your data! 🚀📺",
      likes: "3.7K",
      comments: "211",
      color: "from-red-600 to-rose-700",
      badge: "YouTube"
    }
  };

  return (
    <div className="min-h-screen bg-[#07090E] text-slate-100 selection:bg-brand-500 selection:text-white font-sans overflow-x-hidden">
      {/* 01 Navigation Bar */}
      <header className="border-b border-[#1E293B]/70 bg-[#07090E]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-5 sm:px-8 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 font-extrabold text-xl tracking-tight">
            <span className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
              <Layers size={22} />
            </span>
            <span className="text-white font-mono font-bold text-xl">AISMM</span>
          </Link>

          <nav className="hidden lg:flex items-center gap-8 text-xs font-semibold text-slate-400 font-mono">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#solutions" className="hover:text-white transition-colors">Solutions</a>
            <a href="#research" className="hover:text-white transition-colors">Research</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <a href="#docs" className="hover:text-white transition-colors">Docs</a>
            <a href="#about" className="hover:text-white transition-colors">About</a>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={onOpenAuth}
              className="px-4 py-2 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-900 transition-all font-mono"
            >
              Sign In
            </button>
            <button
              onClick={onLaunchDashboard}
              className="px-5 py-2.5 bg-gradient-to-r from-brand-600 to-cyan-500 hover:opacity-90 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-brand-600/25 font-mono flex items-center gap-1.5"
            >
              <span>Get Started</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-5 sm:px-8 pt-12 sm:pt-20 pb-20">
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Hero Text */}
          <div className="lg:col-span-6 space-y-8">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/25 text-xs font-mono text-brand-300">
              <Sparkles size={14} className="text-cyan-400" />
              <span>AI-Powered Social Media Management</span>
            </div>

            <h1 className="text-5xl sm:text-6xl font-black tracking-tight text-white leading-[1.08]">
              The Future of <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 via-cyan-400 to-blue-500">
                Social Media is AI
              </span>
            </h1>

            <p className="text-sm sm:text-base text-slate-400 leading-relaxed max-w-xl font-normal">
              AISMM is the world's first complete AI-powered social media management platform with 13 research-backed modules and enterprise-grade architecture.
            </p>

            {/* Stat Counters */}
            <div className="grid grid-cols-4 gap-4 p-5 rounded-2xl bg-[#0D121F] border border-[#1E293B] shadow-xl">
              <div>
                <p className="text-2xl sm:text-3xl font-black text-white font-mono">13</p>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">AI Modules</p>
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-black text-cyan-400 font-mono">5+</p>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">Platforms</p>
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-black text-brand-400 font-mono">194</p>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">Tests Passing</p>
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-black text-emerald-400 font-mono">99.9%</p>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">Uptime</p>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={onLaunchDashboard}
                className="px-7 py-3.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-95 text-white rounded-2xl text-xs font-bold transition-all shadow-xl shadow-brand-600/30 font-mono flex items-center gap-2"
              >
                <span>Explore Live Demo</span>
                <ArrowRight size={16} />
              </button>
              <button
                onClick={onLaunchDashboard}
                className="px-6 py-3.5 bg-[#0D121F] hover:bg-slate-900 border border-[#1E293B] text-slate-200 rounded-2xl text-xs font-bold transition-all font-mono"
              >
                View Dashboard
              </button>
            </div>

            <div className="flex items-center gap-4 text-[11px] text-slate-500 font-mono">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Research Backed
              </span>
              <span>•</span>
              <span>Production Ready</span>
              <span>•</span>
              <span>Enterprise Grade</span>
            </div>
          </div>

          {/* Right Column: AI Live Preview Panel */}
          <div className="lg:col-span-6 space-y-6">
            <div className="relative p-6 sm:p-7 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-2xl space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-[#1E293B] pb-4">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  <span className="text-xs font-mono font-bold text-slate-300 ml-2">01 AI Engine Live Preview</span>
                </div>
                <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20">
                  Try our AI Content Adaptation
                </span>
              </div>

              {/* Draft Box */}
              <div className="space-y-3">
                <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B]">
                  <p className="text-xs text-slate-300 font-mono leading-relaxed">{inputText}</p>
                </div>
                <button
                  onClick={() => {}}
                  className="w-full py-2.5 bg-gradient-to-r from-brand-600 to-cyan-600 text-white font-bold rounded-xl text-xs shadow-lg shadow-brand-600/20 flex items-center justify-center gap-2 font-mono"
                >
                  <Sparkles size={14} />
                  <span>Optimize Content</span>
                </button>
              </div>

              {/* AI Adapted Outputs */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white font-mono">AI Adapted Outputs</span>
                  <div className="flex gap-1.5">
                    {['instagram', 'x', 'linkedin', 'facebook', 'youtube'].map((p) => (
                      <button
                        key={p}
                        onClick={() => setActivePlatform(p)}
                        className={`text-[10px] font-mono uppercase px-2 py-1 rounded-lg font-bold transition-all ${
                          activePlatform === p
                            ? 'bg-brand-600 text-white'
                            : 'bg-[#07090E] text-slate-400 border border-[#1E293B] hover:text-slate-200'
                        }`}
                      >
                        {p.charAt(0)}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-300 font-mono">
                      {adaptedOutputs[activePlatform]?.badge}
                    </span>
                    <span className="text-[10px] text-emerald-400 font-mono font-bold flex items-center gap-1">
                      <CheckCircle2 size={12} /> Adapted for Algorithm
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">
                    {adaptedOutputs[activePlatform]?.text}
                  </p>
                  <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono pt-1">
                    <span className="flex items-center gap-1 text-rose-400">
                      <Heart size={12} /> {adaptedOutputs[activePlatform]?.likes}
                    </span>
                    <span className="flex items-center gap-1 text-cyan-400">
                      <MessageCircle size={12} /> {adaptedOutputs[activePlatform]?.comments}
                    </span>
                  </div>
                </div>
              </div>

              {/* Live AI Diagnostics Row */}
              <div className="grid grid-cols-3 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-[#07090E] border border-[#1E293B] text-center">
                  <p className="text-[10px] text-slate-400 font-mono">Caption Quality</p>
                  <p className="text-base font-bold text-cyan-300 font-mono mt-0.5">92.4 <span className="text-[10px] text-slate-500">/100</span></p>
                  <span className="text-[9px] text-emerald-400 font-mono font-bold">● Excellent</span>
                </div>
                <div className="p-3 rounded-xl bg-[#07090E] border border-[#1E293B] text-center">
                  <p className="text-[10px] text-slate-400 font-mono">Sentiment Score</p>
                  <p className="text-base font-bold text-emerald-400 font-mono mt-0.5">+0.84</p>
                  <span className="text-[9px] text-emerald-400 font-mono font-bold">● Very Positive</span>
                </div>
                <div className="p-3 rounded-xl bg-[#07090E] border border-[#1E293B] text-center">
                  <p className="text-[10px] text-slate-400 font-mono">Best Time to Post</p>
                  <p className="text-xs font-bold text-white font-mono mt-1">Today, 7:00 PM</p>
                  <span className="text-[9px] text-cyan-400 font-mono font-bold">● Optimal Reach</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Platform Integration Row */}
        <div className="mt-16 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B]">
          <p className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 text-center mb-6">
            Platform Integration & Capability Matrix
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            {[
              { name: 'Instagram', status: '100% Verified', color: 'text-pink-400' },
              { name: 'X (Twitter)', status: '100% Verified', color: 'text-blue-400' },
              { name: 'Facebook', status: '100% Verified', color: 'text-indigo-400' },
              { name: 'LinkedIn', status: '100% Passing', color: 'text-cyan-400' },
              { name: 'YouTube', status: '100% Verified', color: 'text-red-400' },
            ].map((plat) => (
              <div key={plat.name} className="p-3.5 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center space-y-1">
                <p className={`text-xs font-bold font-mono ${plat.color}`}>{plat.name}</p>
                <p className="text-[10px] text-emerald-400 font-mono font-semibold flex items-center justify-center gap-1">
                  <CheckCircle2 size={10} /> {plat.status}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 4 Feature Pillars */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mt-8">
          {[
            { icon: Cpu, title: 'AI Powered', desc: 'Advanced ML & NLP Models', color: 'text-brand-400' },
            { icon: Activity, title: 'Real-time', desc: 'Live Data & Comment Stream', color: 'text-cyan-400' },
            { icon: Lock, title: 'Secure', desc: 'AES-256 Vault Encryption', color: 'text-emerald-400' },
            { icon: TrendingUp, title: 'Scalable', desc: 'Built for High-Growth Brands', color: 'text-amber-400' },
          ].map((feat) => {
            const Icon = feat.icon;
            return (
              <div key={feat.title} className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] flex items-center gap-4">
                <div className={`p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] ${feat.color}`}>
                  <Icon size={22} />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white font-mono">{feat.title}</h4>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{feat.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#1E293B] bg-[#07090E] py-8">
        <div className="max-w-7xl mx-auto px-5 sm:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-500">
          <p>© 2026 AISMM — AI-Powered Social Media Management Ecosystem.</p>
          <div className="flex gap-6">
            <Link to="/terms" className="hover:text-slate-300">Terms of Service</Link>
            <Link to="/privacy" className="hover:text-slate-300">Privacy Policy</Link>
            <button onClick={onOpenAuth} className="hover:text-slate-300">Sign In</button>
          </div>
        </div>
      </footer>
    </div>
  );
}
