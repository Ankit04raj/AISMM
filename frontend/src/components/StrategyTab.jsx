import React, { useState, useEffect } from 'react';
import {
  Compass,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { api } from '../api/client';

export default function StrategyTab() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [strategyData, setStrategyData] = useState(null);

  const loadStrategy = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStrategyDashboard();
      setStrategyData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await api.getStrategyDashboard();
        if (active) {
          setStrategyData(data);
          setError(null);
        }
      } catch (err) {
        if (active) setError(err.message);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const defaultPillars = [
    { num: 1, title: "AI & Automation Tips", impact: "High Virality", color: "text-cyan-400" },
    { num: 2, title: "Behind the Scenes", impact: "High Trust", color: "text-brand-400" },
    { num: 3, title: "Industry Insights", impact: "High Engagement", color: "text-emerald-400" },
    { num: 4, title: "User Success Stories", impact: "High Conversion", color: "text-blue-400" },
  ];

  const pillars = strategyData?.pillars?.map((p, i) => ({ ...p, num: i + 1, color: "text-cyan-400" })) || defaultPillars;

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
        <div className="flex items-center gap-3">
          <button
            onClick={loadStrategy}
            disabled={loading}
            className="p-2 rounded-xl bg-[#0D121F] border border-[#1E293B] text-slate-400 hover:text-white transition-colors"
            title="Refresh Strategy"
          >
            <RefreshCw size={14} className={loading ? "animate-spin text-cyan-400" : ""} />
          </button>
          <span className="text-xs font-mono font-bold px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 flex items-center gap-2">
            <Compass size={14} />
            <span>Strategic Synthesis</span>
          </span>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl text-xs text-rose-300 font-mono flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} className="text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={loadStrategy} className="underline text-rose-200 font-bold ml-3">Retry</button>
        </div>
      )}

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
            <p className="text-base font-bold text-white font-mono">{strategyData?.recommendation || "Educational & Product Insights"}</p>
            <p className="text-xs text-emerald-400 font-mono font-semibold">
              {strategyData?.recommendation_confidence ? `+${strategyData.recommendation_confidence}% retention predicted` : "Optimal engagement cadence recommended"}
            </p>
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

        {/* Right: Strategy Radar Chart - Dynamic */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-5 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono">Pillar Balance Matrix</h3>
            <span className="text-xs text-slate-400 font-mono">{loading ? 'Synthesizing…' : 'Performance Radar'}</span>
          </div>

          {/* Helper to compute radar coordinates */}
          {(() => {
            const scores = strategyData?.pillar_scores || [85, 45, 70, 60, 55];
            const maxVal = Math.max(...scores, 100);
            const center = { x: 120, y: 120 };
            const radius = 80;
            const angles = [Math.PI/2, Math.PI/2 - 2*Math.PI/5, Math.PI/2 - 4*Math.PI/5, Math.PI/2 - 6*Math.PI/5, Math.PI/2 - 8*Math.PI/5];

            const computePoint = (val, angle) => ({
              x: center.x + radius * (val / maxVal) * Math.cos(angle),
              y: center.y + radius * (val / maxVal) * Math.sin(angle)
            });

            const polygon = scores.map((score, i) => computePoint(score, angles[i]));
            const pointsStr = polygon.map(p => `${p.x},${p.y}`).join(' ');

            const cycles = [0, 1, 2, 3, 4];
            const computeCircle = (factor = 1) => {
              return cycles.map((_, i) => computePoint(factor * maxVal, angles[i])).map(p => `${p.x},${p.y}`).join(' ');
            };

            return (
              <div className="h-56 w-full flex items-center justify-center relative my-2">
                <svg viewBox="0 0 240 240" className="w-48 h-48">
                  <g stroke="#1E293B" strokeWidth="1">
                    {[0.25, 0.5, 0.75, 1].map(factor => (
                      <polygon key={factor} points={computeCircle(factor)} fill="none" opacity="0.3" />
                    ))}
                  </g>
                  <g stroke="#1E293B" strokeWidth="1">
                    {angles.map((_, i) => {
                      const end = computePoint(maxVal, angles[i]);
                      return <line key={i} x1={center.x} y1={center.y} x2={end.x} y2={end.y} />;
                    })}
                  </g>
                  <polygon points={pointsStr} fill="rgba(124, 58, 237, 0.25)" stroke="#7C3AED" strokeWidth="2" />
                  <g fill="#06B6D4">
                    {polygon.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r="4" />)}
                  </g>
                </svg>
                <div className="absolute text-center">
                  <p className="text-xs font-mono text-cyan-400">{strategyData?.recommendation || 'Strategy Score'}</p>
                </div>
              </div>
            );
          })()}

          <div className="flex flex-wrap justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-[#1E293B]">
            {strategyData?.pillar_labels?.map((l, i) => (<span key={i}>{l}</span>)) || ['Engagement', 'Virality', 'Reach', 'Consistency', 'Growth'].map((l, i) => (<span key={i}>{l}</span>))}
          </div>
        </div>
      </div>
    </div>
  );
}
