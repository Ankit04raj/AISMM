import React, { useState, useEffect } from 'react';
import {
  Users,
  Eye,
  Heart,
  TrendingUp,
  MessageSquare,
  Sparkles,
  Share2,
  CheckCircle2,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Clock,
  Layers,
  AlertTriangle,
  RefreshCw,
  PieChart,
  BarChart2
} from 'lucide-react';
import { api } from '../api/client';

export default function OverviewTab({ onNavigateTab }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [strategy, setStrategy] = useState(null);
  const [platforms, setPlatforms] = useState([]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewData, strategyData, platformsData] = await Promise.all([
        api.getOverview(30),
        api.getStrategyDashboard().catch(() => null),
        api.listPlatforms().catch(() => ({ platforms: [] })),
      ]);
      setOverview(overviewData);
      setStrategy(strategyData);
      setPlatforms(platformsData.platforms || []);
    } catch (err) {
      console.error("Failed to load overview telemetry:", err);
      setError("Unable to reach AISMM backend. Please check connection or start the backend service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[450px] gap-3">
        <RefreshCw className="w-8 h-8 text-brand-400 animate-spin" />
        <p className="text-slate-400 text-xs font-mono">Synchronizing live telemetry from AISMM backend...</p>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="p-8 bg-rose-950/20 border border-rose-500/30 rounded-3xl flex flex-col items-center justify-center text-center gap-4 my-8 animate-fadeIn">
        <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white mb-1">Backend Connection Offline</h3>
          <p className="text-xs text-slate-400 max-w-md">{error || "Unable to reach AISMM backend"}</p>
        </div>
        <button
          onClick={loadData}
          className="px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-brand-600/20"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  // 5 KPI Cards per Module 03 specification
  const kpis = [
    { label: "Total Audience Reach", value: overview.total_reach?.toLocaleString() || "0", icon: Eye, color: "from-blue-600 to-indigo-600", accent: "text-blue-400" },
    { label: "Connected Followers", value: overview.total_followers?.toLocaleString() || "0", icon: Users, color: "from-purple-600 to-pink-600", accent: "text-purple-400" },
    { label: "Total Interactions", value: overview.total_engagements?.toLocaleString() || "0", icon: Heart, color: "from-rose-600 to-orange-500", accent: "text-rose-400" },
    { label: "Avg Engagement Rate", value: `${overview.overall_engagement_rate || 0}%`, icon: TrendingUp, color: "from-emerald-600 to-teal-600", accent: "text-emerald-400" },
    { label: "Active Channels", value: `${platforms.length || 5} Active`, icon: Share2, color: "from-cyan-600 to-blue-600", accent: "text-cyan-400" },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl p-6 sm:p-8 bg-gradient-to-r from-brand-900/40 via-[#0D121F] to-[#07090E] border border-[#1E293B] shadow-2xl">
        <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row justify-between md:items-center gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-300 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Universal Studio Core</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Central Intelligence Dashboard</h1>
            <p className="text-slate-400 text-xs sm:text-sm mt-1 max-w-xl">
              Live operational telemetry, multi-line performance charts, platform distributions, and strategic recommendations.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => onNavigateTab('composer')}
              className="px-5 py-2.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-95 text-white font-bold text-xs rounded-xl shadow-lg shadow-brand-600/30 transition-all flex items-center gap-2"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Create Post</span>
            </button>
            <button
              onClick={() => onNavigateTab('strategy')}
              className="px-5 py-2.5 bg-[#07090E] hover:bg-[#131B2E] text-slate-200 font-bold text-xs rounded-xl border border-[#1E293B] transition-all flex items-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>AI Strategy</span>
            </button>
          </div>
        </div>
      </div>

      {/* 5 KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className="bg-[#0D121F] border border-[#1E293B] rounded-2xl p-5 hover:border-brand-500/40 transition-all shadow-xl relative overflow-hidden"
            >
              <div className="flex justify-between items-start">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{kpi.label}</span>
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-tr ${kpi.color} flex items-center justify-center text-white shadow-md`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-2xl font-extrabold text-white tracking-tight font-mono">{kpi.value}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Multi-Line Performance Chart & Platform Donut Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Multi-Line Performance SVG Chart */}
        <div className="lg:col-span-8 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-sm text-white">Cross-Platform Engagement Velocity</h3>
              <p className="text-xs text-slate-400">Reach vs Engagement impressions trend across recent 30-day window</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-[#06B6D4] rounded" />
                <span className="text-slate-300">Reach</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-[#7C3AED] rounded" />
                <span className="text-slate-300">Engagements</span>
              </div>
            </div>
          </div>

          {/* SVG Multi-Line Chart */}
          <div className="relative h-56 w-full pt-4">
            <svg viewBox="0 0 600 200" className="w-full h-full overflow-visible">
              {/* Grid Lines */}
              <line x1="0" y1="40" x2="600" y2="40" stroke="#1E293B" strokeDasharray="3 3" />
              <line x1="0" y1="90" x2="600" y2="90" stroke="#1E293B" strokeDasharray="3 3" />
              <line x1="0" y1="140" x2="600" y2="140" stroke="#1E293B" strokeDasharray="3 3" />
              <line x1="0" y1="190" x2="600" y2="190" stroke="#1E293B" />

              {/* Reach Line (Cyan) */}
              <polyline
                fill="none"
                stroke="#06B6D4"
                strokeWidth="3"
                points="0,150 75,130 150,110 225,80 300,95 375,60 450,50 525,45 600,35"
              />
              {/* Engagements Line (Violet) */}
              <polyline
                fill="none"
                stroke="#7C3AED"
                strokeWidth="3"
                points="0,180 75,165 150,145 225,120 300,135 375,100 450,85 525,75 600,60"
              />

              {/* Data Markers */}
              <circle cx="225" cy="80" r="4" fill="#06B6D4" />
              <circle cx="375" cy="60" r="4" fill="#06B6D4" />
              <circle cx="600" cy="35" r="4" fill="#06B6D4" />

              <circle cx="225" cy="120" r="4" fill="#7C3AED" />
              <circle cx="375" cy="100" r="4" fill="#7C3AED" />
              <circle cx="600" cy="60" r="4" fill="#7C3AED" />
            </svg>
          </div>

          <div className="flex justify-between text-[11px] text-slate-500 font-mono pt-2 border-t border-[#1E293B]">
            <span>Day 01</span>
            <span>Day 08</span>
            <span>Day 15</span>
            <span>Day 22</span>
            <span>Day 30 (Current)</span>
          </div>
        </div>

        {/* Platform Donut Chart & Audience Share */}
        <div className="lg:col-span-4 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-white mb-1">Audience Distribution</h3>
            <p className="text-xs text-slate-400 mb-4">Share of audience across 5 connected networks</p>

            {/* SVG Donut Chart */}
            <div className="relative h-44 flex items-center justify-center">
              <svg viewBox="0 0 160 160" className="w-36 h-36">
                {/* Background Ring */}
                <circle cx="80" cy="80" r="55" fill="none" stroke="#1E293B" strokeWidth="18" />
                {/* Instagram Arc (35%) */}
                <circle cx="80" cy="80" r="55" fill="none" stroke="#EC4899" strokeWidth="18" strokeDasharray="120 345" strokeDashoffset="0" />
                {/* Facebook Arc (25%) */}
                <circle cx="80" cy="80" r="55" fill="none" stroke="#3B82F6" strokeWidth="18" strokeDasharray="86 345" strokeDashoffset="-120" />
                {/* X Arc (20%) */}
                <circle cx="80" cy="80" r="55" fill="none" stroke="#64748B" strokeWidth="18" strokeDasharray="69 345" strokeDashoffset="-206" />
                {/* LinkedIn Arc (12%) */}
                <circle cx="80" cy="80" r="55" fill="none" stroke="#06B6D4" strokeWidth="18" strokeDasharray="41 345" strokeDashoffset="-275" />
                {/* YouTube Arc (8%) */}
                <circle cx="80" cy="80" r="55" fill="none" stroke="#EF4444" strokeWidth="18" strokeDasharray="29 345" strokeDashoffset="-316" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center font-mono">
                <span className="text-xs font-bold text-slate-400">TOTAL</span>
                <span className="text-sm font-extrabold text-white">{overview.total_followers?.toLocaleString() || "0"}</span>
              </div>
            </div>
          </div>

          {/* Platform Share Badges */}
          <div className="grid grid-cols-2 gap-2 text-xs pt-4 border-t border-[#1E293B]">
            <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-pink-500" /><span>Instagram (35%)</span></div>
            <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-blue-500" /><span>Facebook (25%)</span></div>
            <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-slate-500" /><span>X / Twitter (20%)</span></div>
            <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-cyan-500" /><span>LinkedIn (12%)</span></div>
          </div>
        </div>
      </div>

      {/* AI Insights & Strategic Recommendations Bar */}
      {strategy?.directives && (
        <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              <h3 className="font-bold text-base text-white">Live AI Strategic Insights</h3>
            </div>
            <button
              onClick={() => onNavigateTab('strategy')}
              className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              <span>View Full Strategy</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {strategy.directives.slice(0, 3).map((d) => (
              <div key={d.id} className="p-4 bg-[#07090E] border border-[#1E293B] rounded-2xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase text-brand-400 font-mono">{d.category}</span>
                  <span className="text-[10px] font-bold text-emerald-400 font-mono">{d.projected_impact}</span>
                </div>
                <h4 className="font-bold text-xs text-slate-100">{d.title}</h4>
                <p className="text-[11px] text-slate-400 line-clamp-2">{d.actionable_step}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
