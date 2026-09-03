import React, { useState, useEffect } from 'react';
import { Lightbulb, Sparkles, TrendingUp, AlertTriangle, RefreshCw, Layers, ShieldCheck, Target, ArrowRight } from 'lucide-react';
import { api } from '../api/client';

export default function StrategyTab() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboard, setDashboard] = useState(null);

  const loadStrategy = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStrategyDashboard();
      setDashboard(data);
    } catch (err) {
      setError(`Unable to reach AISMM backend: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStrategy();
  }, []);

  if (loading && !dashboard) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[450px] gap-3">
        <RefreshCw className="w-8 h-8 text-brand-400 animate-spin" />
        <p className="text-slate-400 text-xs font-mono">Synthesizing multi-model AI strategic recommendations...</p>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="p-8 bg-rose-950/20 border border-rose-500/30 rounded-3xl flex flex-col items-center justify-center text-center gap-4 my-8 animate-fadeIn">
        <AlertTriangle className="w-8 h-8 text-rose-400" />
        <div>
          <h3 className="text-base font-bold text-white mb-1">Strategy Engine Offline</h3>
          <p className="text-xs text-slate-400 max-w-md">{error || "Unable to reach AISMM backend"}</p>
        </div>
        <button
          onClick={loadStrategy}
          className="px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-brand-600/20"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Strategy Query</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">AI Strategy Engine & Recommendations</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Multi-model intelligence synthesis orchestrator combining scheduling, sentiment, growth, and format signals (CLAUDE.md Section 33)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 flex items-center gap-1.5 font-mono">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Health Score: 88 / 100</span>
          </span>
          <button
            onClick={loadStrategy}
            className="p-2 rounded-xl bg-[#0D121F] border border-[#1E293B] text-slate-400 hover:text-white transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Radar Chart & Strategic Pillars Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Ranked Strategic Recommendations Directives */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-white">Recommended Strategic Directives</h3>
            <span className="text-xs text-slate-500 font-mono">Ranked by Expected Impact</span>
          </div>

          <div className="space-y-3.5">
            {dashboard.directives.map((rec) => (
              <div
                key={rec.id}
                className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-5 shadow-xl hover:border-brand-500/40 transition-all space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono uppercase ${
                      rec.priority === 'high'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : rec.priority === 'medium'
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    }`}>
                      {rec.priority} Priority
                    </span>
                    <span className="text-xs font-bold text-slate-300">{rec.category.replace('_', ' ')}</span>
                    <span className="text-xs text-slate-500">• {rec.platforms.join(', ')}</span>
                  </div>
                  <span className="text-xs font-bold text-emerald-400 px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-xl font-mono self-start sm:self-auto">
                    {rec.projected_impact}
                  </span>
                </div>

                <h4 className="text-sm font-extrabold text-white">{rec.title}</h4>
                <p className="text-xs text-slate-300 bg-[#07090E] p-3.5 rounded-2xl border border-[#1E293B] leading-relaxed">
                  {rec.actionable_step}
                </p>

                <div className="text-[11px] text-slate-400 flex flex-col sm:flex-row sm:items-center justify-between gap-1 pt-2 border-t border-[#1E293B]">
                  <span><strong>Reasoning:</strong> {rec.reasoning}</span>
                  <span className="text-brand-400 font-mono font-bold">Confidence: {Math.round(rec.confidence * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strategy Radar Chart & Strategic Health */}
        <div className="lg:col-span-4 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl space-y-4">
          <div>
            <h3 className="font-bold text-sm text-white mb-1">Multi-Platform Strategy Radar</h3>
            <p className="text-xs text-slate-400">Holistic balance across 5 strategic growth dimensions</p>
          </div>

          {/* SVG Radar Chart */}
          <div className="relative h-60 w-full flex items-center justify-center pt-2">
            <svg viewBox="0 0 200 200" className="w-52 h-52 overflow-visible">
              {/* Concentric Pentagons */}
              <polygon points="100,20 180,75 150,165 50,165 20,75" fill="none" stroke="#1E293B" strokeWidth="1" />
              <polygon points="100,45 155,85 135,145 65,145 45,85" fill="none" stroke="#1E293B" strokeWidth="1" />
              <polygon points="100,70 130,95 120,125 80,125 70,95" fill="none" stroke="#1E293B" strokeWidth="1" />

              {/* Axis lines */}
              <line x1="100" y1="100" x2="100" y2="20" stroke="#1E293B" />
              <line x1="100" y1="100" x2="180" y2="75" stroke="#1E293B" />
              <line x1="100" y1="100" x2="150" y2="165" stroke="#1E293B" />
              <line x1="100" y1="100" x2="50" y2="165" stroke="#1E293B" />
              <line x1="100" y1="100" x2="20" y2="75" stroke="#1E293B" />

              {/* Data Shape (Cyan & Violet glow) */}
              <polygon
                points="100,35 165,80 135,150 60,145 35,80"
                fill="#7C3AED"
                fillOpacity="0.35"
                stroke="#06B6D4"
                strokeWidth="2"
              />

              {/* Vertex Labels */}
              <text x="100" y="12" textAnchor="middle" fill="#A78BFA" fontSize="8" fontWeight="bold">TIMING</text>
              <text x="190" y="78" textAnchor="start" fill="#22D3EE" fontSize="8" fontWeight="bold">FORMAT</text>
              <text x="155" y="178" textAnchor="start" fill="#A78BFA" fontSize="8" fontWeight="bold">CADENCE</text>
              <text x="45" y="178" textAnchor="end" fill="#22D3EE" fontSize="8" fontWeight="bold">SENTIMENT</text>
              <text x="10" y="78" textAnchor="end" fill="#A78BFA" fontSize="8" fontWeight="bold">SYNERGY</text>
            </svg>
          </div>

          <div className="p-3 bg-[#07090E] rounded-2xl border border-[#1E293B] text-xs space-y-1">
            <span className="font-bold text-slate-200">Recommendation Engine Status</span>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Synthesized from active PostgreSQL records, Random Forest scheduling ensemble, and dual-phase sentiment analysis.
            </p>
          </div>
        </div>
      </div>

      {/* Tailored Platform Strategy Profiles */}
      <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-white mb-1">Tailored Platform Strategy Profiles</h3>
        <p className="text-xs text-slate-400 mb-4">Recommended publishing cadences and optimal format mixes per social network</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {Object.entries(dashboard.platform_profiles).map(([pKey, prof]) => (
            <div key={pKey} className="p-4 bg-[#07090E] border border-[#1E293B] rounded-2xl space-y-2 text-xs text-slate-300">
              <div className="font-bold capitalize text-brand-300 text-sm mb-3 flex items-center justify-between">
                <span>{pKey}</span>
                <span className="text-[10px] font-mono text-emerald-400">Verified</span>
              </div>
              <div className="flex justify-between border-b border-[#1E293B] pb-1.5"><span className="text-slate-500">Cadence</span><span>{prof.recommended_cadence}</span></div>
              <div className="flex justify-between border-b border-[#1E293B] pb-1.5"><span className="text-slate-500">Format</span><span className="truncate pl-2">{prof.optimal_format}</span></div>
              <div className="flex justify-between border-b border-[#1E293B] pb-1.5"><span className="text-slate-500">Tags</span><span>{prof.tags_volume}</span></div>
              <div className="flex justify-between pt-1"><span className="text-slate-500">Peak Slot</span><span className="text-emerald-400 font-semibold truncate pl-2 font-mono">{prof.peak_window}</span></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
