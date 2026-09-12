import React, { useState, useEffect } from 'react';
import {
  Search,
  Calendar,
  Sparkles,
  TrendingUp,
  Users,
  Eye,
  MousePointer,
  Award,
  RefreshCw,
  Plus,
  Clock,
  Zap,
  ArrowUpRight
} from 'lucide-react';
import { api } from '../api/client';

export default function OverviewTab({ onNavigateTab }) {
  const [data, setData] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overview, recent] = await Promise.all([
        api.getOverview(30),
        api.getPosts(1, 10),
      ]);
      setData(overview);
      setPosts(recent.posts || []);
    } catch (err) {
      console.error("Failed to load overview:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* 03 Header & Greeting */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white flex items-center gap-2">
            <span>Good morning, Ankit!</span>
            <span>✋ ✨</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Here's what's happening with your social media today.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-[#0D121F] border border-[#1E293B] text-xs text-slate-300 font-mono">
            <Calendar size={14} className="text-cyan-400" />
            <span>May 20 - May 26, 2024</span>
          </div>
          <div className="p-2 rounded-2xl bg-[#0D121F] border border-[#1E293B] text-slate-400 hover:text-white cursor-pointer">
            <Search size={16} />
          </div>
          <button
            onClick={() => onNavigateTab('composer')}
            className="px-4 py-2 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white rounded-2xl text-xs font-bold font-mono transition-all flex items-center gap-2 shadow-lg shadow-brand-600/25"
          >
            <Plus size={14} />
            <span>Create Post</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl text-xs text-rose-300 font-mono">
          {error}
        </div>
      )}

      {/* 5 Top KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {[
          { label: 'Total Reach', value: '2.4M', change: '+12.5%', icon: Eye, color: 'text-cyan-400' },
          { label: 'Engagement', value: '184.7K', change: '+8.3%', icon: Zap, color: 'text-brand-400' },
          { label: 'Profile Visits', value: '45.2K', change: '+15.7%', icon: Users, color: 'text-emerald-400' },
          { label: 'Clicks', value: '12.8K', change: '+9.2%', icon: MousePointer, color: 'text-blue-400' },
          { label: 'Conversions', value: '2.1K', change: '+11.3%', icon: Award, color: 'text-amber-400' },
        ].map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="p-5 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-slate-400">{kpi.label}</span>
                <Icon size={16} className={kpi.color} />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-black text-white font-mono">{kpi.value}</span>
                <span className="text-[11px] font-bold text-emerald-400 font-mono">{kpi.change}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Row: Performance Over Time & Platform Performance */}
      <div className="grid lg:grid-cols-12 gap-6">
        {/* Line Chart */}
        <div className="lg:col-span-8 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white font-mono">Performance Over Time</h3>
            <div className="flex items-center gap-2">
              {['7 Days', '30 Days', '90 Days'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTimeRange(t.toLowerCase())}
                  className={`px-3 py-1 rounded-xl text-xs font-mono font-bold transition-all ${
                    timeRange === t.toLowerCase()
                      ? 'bg-brand-600 text-white'
                      : 'bg-[#07090E] text-slate-400 hover:text-white border border-[#1E293B]'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* SVG Line Chart */}
          <div className="h-56 w-full relative">
            <svg viewBox="0 0 700 200" className="w-full h-full overflow-visible">
              <defs>
                <linearGradient id="cyanGlow" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#06B6D4" stopOpacity="0.0" />
                </linearGradient>
                <linearGradient id="violetGlow" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7C3AED" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#7C3AED" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line x1="0" y1="40" x2="700" y2="40" stroke="#1E293B" strokeDasharray="4 4" />
              <line x1="0" y1="90" x2="700" y2="90" stroke="#1E293B" strokeDasharray="4 4" />
              <line x1="0" y1="140" x2="700" y2="140" stroke="#1E293B" strokeDasharray="4 4" />

              {/* Area & Line 1: Reach (Cyan) */}
              <path
                d="M 0 140 Q 120 70 240 100 T 480 50 T 700 30"
                fill="none"
                stroke="#06B6D4"
                strokeWidth="3"
              />

              {/* Line 2: Engagement (Violet) */}
              <path
                d="M 0 160 Q 120 120 240 140 T 480 90 T 700 70"
                fill="none"
                stroke="#7C3AED"
                strokeWidth="3"
              />

              {/* Line 3: Clicks (Blue) */}
              <path
                d="M 0 180 Q 120 160 240 165 T 480 140 T 700 120"
                fill="none"
                stroke="#3B82F6"
                strokeWidth="2"
                strokeDasharray="4 2"
              />
            </svg>

            {/* X Axis Labels */}
            <div className="flex justify-between text-[11px] text-slate-500 font-mono pt-2">
              <span>May 20</span>
              <span>May 21</span>
              <span>May 22</span>
              <span>May 23</span>
              <span>May 24</span>
              <span>May 26</span>
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center gap-6 text-xs font-mono pt-2 border-t border-[#1E293B]">
            <span className="flex items-center gap-2 text-cyan-400">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
              Reach
            </span>
            <span className="flex items-center gap-2 text-brand-400">
              <span className="w-2.5 h-2.5 rounded-full bg-brand-400" />
              Engagement
            </span>
            <span className="flex items-center gap-2 text-blue-400">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-400" />
              Clicks
            </span>
          </div>
        </div>

        {/* Donut Chart: Platform Performance */}
        <div className="lg:col-span-4 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-6 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white font-mono">Platform Performance</h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">Audience reach distribution</p>
          </div>

          <div className="flex items-center justify-center relative my-2">
            {/* SVG Donut */}
            <svg viewBox="0 0 160 160" className="w-40 h-40 transform -rotate-90">
              <circle cx="80" cy="80" r="60" fill="transparent" stroke="#EC4899" strokeWidth="18" strokeDasharray="158 377" />
              <circle cx="80" cy="80" r="60" fill="transparent" stroke="#3B82F6" strokeWidth="18" strokeDasharray="105 377" strokeDashoffset="-158" />
              <circle cx="80" cy="80" r="60" fill="transparent" stroke="#2563EB" strokeWidth="18" strokeDasharray="56 377" strokeDashoffset="-263" />
              <circle cx="80" cy="80" r="60" fill="transparent" stroke="#06B6D4" strokeWidth="18" strokeDasharray="38 377" strokeDashoffset="-319" />
              <circle cx="80" cy="80" r="60" fill="transparent" stroke="#EF4444" strokeWidth="18" strokeDasharray="20 377" strokeDashoffset="-357" />
            </svg>
            <div className="absolute text-center">
              <p className="text-xl font-black text-white font-mono">2.4M</p>
              <p className="text-[10px] text-slate-400 font-mono">Total Reach</p>
            </div>
          </div>

          {/* Breakdown Rows */}
          <div className="space-y-2 text-xs font-mono">
            {[
              { name: 'Instagram', pct: '42%', val: '1.01M', color: 'bg-pink-500' },
              { name: 'X (Twitter)', pct: '28%', val: '672K', color: 'bg-blue-400' },
              { name: 'Facebook', pct: '15%', val: '360K', color: 'bg-blue-600' },
              { name: 'LinkedIn', pct: '10%', val: '240K', color: 'bg-cyan-500' },
              { name: 'YouTube', pct: '5%', val: '120K', color: 'bg-red-500' },
            ].map((p) => (
              <div key={p.name} className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-slate-300">
                  <span className={`w-2 h-2 rounded-full ${p.color}`} />
                  {p.name}
                </span>
                <span className="text-slate-400">{p.pct}</span>
                <span className="font-bold text-white">{p.val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Insights Banner Card */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0D121F] via-[#111827] to-[#0D121F] border border-brand-500/30 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
            <Sparkles size={16} className="text-brand-400" />
            <span>AI Insights & Growth Signals</span>
          </h3>
          <span className="text-[11px] font-mono text-cyan-400 font-bold">Real-Time Synthesis</span>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] space-y-1">
            <p className="text-[11px] text-slate-400 font-mono">Best performing content type</p>
            <p className="text-sm font-bold text-white font-mono">Carousel Posts</p>
            <p className="text-[11px] text-emerald-400 font-mono">+23% more engagement</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] space-y-1">
            <p className="text-[11px] text-slate-400 font-mono">Optimal posting time</p>
            <p className="text-sm font-bold text-white font-mono">Today, 7:00 PM</p>
            <p className="text-[11px] text-cyan-400 font-mono">+45% wider reach</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] space-y-1">
            <p className="text-[11px] text-slate-400 font-mono">Trending topic in your niche</p>
            <p className="text-sm font-bold text-white font-mono">AI Automation</p>
            <p className="text-[11px] text-brand-400 font-mono">High engagement potential</p>
          </div>
        </div>
      </div>
    </div>
  );
}
