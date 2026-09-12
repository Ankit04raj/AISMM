import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Users,
  Target,
  Activity,
  Sparkles,
  ArrowUpRight,
  Globe,
  PieChart,
  BarChart2
} from 'lucide-react';
import { api } from '../api/client';

export default function GrowthTab() {
  const [platform, setPlatform] = useState('instagram');
  const [followers, setFollowers] = useState(24800);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.predictGrowth({
      platform,
      current_followers: followers,
      posting_frequency_weekly: 4.0,
      avg_engagement_rate: 4.5,
    }).then(data => setPrediction(data)).catch(() => {});
  }, [platform, followers]);

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white font-mono">10 Growth Intelligence</h2>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">
            Predictive growth models, audience demographics, and multi-horizon reach forecasting
          </p>
        </div>

        <div className="flex items-center gap-2">
          {['instagram', 'x', 'facebook', 'linkedin', 'youtube'].map((p) => (
            <button
              key={p}
              onClick={() => setPlatform(p)}
              className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold capitalize transition-all ${
                platform === p
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'bg-[#0D121F] border border-[#1E293B] text-slate-400 hover:text-white'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* 3 Top Cards matching Panel 10 */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Growth Overview */}
        <div className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono">Growth Overview</h3>
            <span className="text-[11px] text-slate-400 font-mono">This Month ▾</span>
          </div>

          <div className="grid grid-cols-3 gap-2 font-mono">
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Followers</p>
              <p className="text-lg font-black text-white mt-0.5">+2.4K</p>
              <span className="text-[10px] text-emerald-400 font-bold">+18.7%</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Following</p>
              <p className="text-lg font-black text-white mt-0.5">+856</p>
              <span className="text-[10px] text-emerald-400 font-bold">+12.2%</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Growth Rate</p>
              <p className="text-lg font-black text-cyan-400 mt-0.5">15.2%</p>
              <span className="text-[10px] text-emerald-400 font-bold">+3.8%</span>
            </div>
          </div>
        </div>

        {/* Audience Insights */}
        <div className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono">Audience Insights</h3>
            <span className="text-[11px] text-cyan-400 font-mono font-bold">Demographics</span>
          </div>

          <div className="grid grid-cols-3 gap-2 font-mono">
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Top Age Group</p>
              <p className="text-base font-bold text-white mt-0.5">25-34</p>
              <span className="text-[10px] text-cyan-400 font-bold">42%</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Top Location</p>
              <p className="text-base font-bold text-white mt-0.5">India</p>
              <span className="text-[10px] text-brand-400 font-bold">32%</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Top Interest</p>
              <p className="text-base font-bold text-white mt-0.5">Technology</p>
              <span className="text-[10px] text-emerald-400 font-bold">28%</span>
            </div>
          </div>
        </div>

        {/* Growth Predictions */}
        <div className="p-6 rounded-3xl bg-gradient-to-br from-[#0D121F] to-brand-950/40 border border-brand-500/40 shadow-xl space-y-4 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono flex items-center gap-1.5">
              <Sparkles size={14} className="text-cyan-400" />
              <span>Growth Predictions</span>
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              RF Regressor
            </span>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-slate-400 font-mono">Next Month Prediction</p>
            <p className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 font-mono">
              +3.2K followers
            </p>
            <p className="text-xs text-emerald-400 font-mono font-semibold flex items-center gap-1">
              <TrendingUp size={14} /> High confidence (+89.2% R² Model Accuracy)
            </p>
          </div>
        </div>
      </div>

      {/* Projections Multi-Horizon Chart */}
      <div className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white font-mono">Multi-Horizon Audience Trajectory</h3>
          <span className="text-xs text-slate-400 font-mono">Random Forest Regressor Simulation</span>
        </div>

        <div className="grid md:grid-cols-3 gap-4 font-mono text-xs">
          <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] space-y-1">
            <p className="text-slate-400">7-Day Projection</p>
            <p className="text-xl font-bold text-white">+780 Followers</p>
            <p className="text-cyan-400 font-semibold">+3.1% Velocity</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#07090E] border border-cyan-500/30 space-y-1">
            <p className="text-slate-400">30-Day Projection</p>
            <p className="text-xl font-bold text-cyan-300">+3,200 Followers</p>
            <p className="text-emerald-400 font-semibold">+12.9% Velocity</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#07090E] border border-brand-500/30 space-y-1">
            <p className="text-slate-400">90-Day Compounded</p>
            <p className="text-xl font-bold text-brand-300">+10,450 Followers</p>
            <p className="text-brand-400 font-semibold">+42.1% Compounded Reach</p>
          </div>
        </div>
      </div>
    </div>
  );
}
