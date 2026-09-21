import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Sparkles,
  AlertTriangle
} from 'lucide-react';
import { api } from '../api/client';

export default function GrowthTab() {
  const [platform, setPlatform] = useState('instagram');
  const [followers, setFollowers] = useState(10000);
  const [postingFrequency, setPostingFrequency] = useState(4.0);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    api.getAccounts().then(data => {
      if (!active) return;
      const accList = data.accounts || [];
      const acc = accList.find(a => a.platform === platform && a.is_active);
      if (acc?.account_metadata?.followers_count) {
        setFollowers(Number(acc.account_metadata.followers_count));
      }
    }).catch(() => {});
    return () => { active = false; };
  }, [platform]);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await api.predictGrowth({
          platform,
          current_followers: Math.max(0, Number(followers) || 0),
          posting_frequency_weekly: Number(postingFrequency) || 3.0,
          avg_engagement_rate: 4.5,
        });
        if (active) {
          setPrediction(data);
          setError(null);
        }
      } catch (err) {
        if (active) setError(`Growth prediction error: ${err.message}`);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [platform, followers, postingFrequency]);

  const proj7d = prediction?.projections?.['7d'];
  const proj30d = prediction?.projections?.['30d'];
  const proj90d = prediction?.projections?.['90d'];

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white font-mono">10 Growth Intelligence</h2>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">
            Platform-specific Random Forest Regressors, predictive growth modeling, and multi-horizon reach forecasting
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

      {error && (
        <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-xl text-xs text-red-300 font-mono flex items-center gap-2">
          <AlertTriangle size={14} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 3 Top Cards matching Panel 10 */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Growth Overview */}
        <div className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono">Account Baseline</h3>
            <span className="text-[11px] text-slate-400 font-mono capitalize">{platform}</span>
          </div>

          <div className="grid grid-cols-3 gap-2 font-mono">
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Current Base</p>
              <p className="text-base font-black text-white mt-0.5">{followers.toLocaleString()}</p>
              <span className="text-[10px] text-cyan-400 font-bold">Followers</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Frequency</p>
              <select
                value={postingFrequency}
                onChange={(e) => setPostingFrequency(Number(e.target.value))}
                className="bg-transparent text-sm font-black text-white mt-0.5 outline-none text-center cursor-pointer"
              >
                {[1, 2, 3, 4, 5, 7, 10, 14].map((f) => (
                  <option key={f} value={f} className="bg-[#07090E] text-white">
                    {f}/wk
                  </option>
                ))}
              </select>
              <span className="text-[10px] text-emerald-400 font-bold block">Cadence</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#07090E] border border-[#1E293B] text-center">
              <p className="text-[10px] text-slate-400">Model R²</p>
              <p className="text-base font-black text-cyan-400 mt-0.5">{prediction?.baseline_r2 != null ? `${(prediction.baseline_r2 * 100).toFixed(1)}%` : '—'}</p>
              <span className="text-[10px] text-emerald-400 font-bold">Confidence</span>
            </div>
          </div>
        </div>

        {/* Audience Insights / Feature Importances */}
        <div className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono">Key Growth Drivers</h3>
            <span className="text-[11px] text-cyan-400 font-mono font-bold">Feature Weights</span>
          </div>

          <div className="space-y-2 font-mono text-xs">
            {prediction?.feature_importances ? (
              Object.entries(prediction.feature_importances).slice(0, 3).map(([k, v]) => (
                <div key={k} className="flex justify-between items-center p-2 rounded-xl bg-[#07090E] border border-[#1E293B]">
                  <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}</span>
                  <span className="text-emerald-400 font-bold">{(v * 100).toFixed(1)}%</span>
                </div>
              ))
            ) : (
              <p className="text-slate-500 text-xs py-4 text-center">Loading feature importances…</p>
            )}
          </div>
        </div>

        {/* 30-Day Growth Predictions */}
        <div className="p-6 rounded-3xl bg-gradient-to-br from-[#0D121F] to-brand-950/40 border border-brand-500/40 shadow-xl space-y-4 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <h3 className="text-sm font-bold text-white font-mono flex items-center gap-1.5">
              <Sparkles size={14} className="text-cyan-400" />
              <span>30-Day Forecast</span>
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {prediction?.model_version || 'RF Regressor'}
            </span>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-slate-400 font-mono">Net Audience Addition</p>
            <p className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 font-mono">
              {proj30d ? `+${proj30d.net_growth_followers.toLocaleString()} followers` : loading ? 'Computing…' : '+0 followers'}
            </p>
            <p className="text-xs text-emerald-400 font-mono font-semibold flex items-center gap-1">
              <TrendingUp size={14} /> +{proj30d ? proj30d.growth_rate_percent.toFixed(1) : '0.0'}% Growth Rate ({proj30d?.predicted_reach?.toLocaleString() || '0'} est. reach)
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
            <p className="text-slate-400">7-Day Horizon</p>
            <p className="text-xl font-bold text-white">{proj7d ? `+${proj7d.net_growth_followers.toLocaleString()} Followers` : '0 Followers'}</p>
            <p className="text-cyan-400 font-semibold">+{proj7d ? proj7d.growth_rate_percent.toFixed(1) : '0.0'}% Velocity</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#07090E] border border-cyan-500/30 space-y-1">
            <p className="text-slate-400">30-Day Horizon</p>
            <p className="text-xl font-bold text-cyan-300">{proj30d ? `+${proj30d.net_growth_followers.toLocaleString()} Followers` : '0 Followers'}</p>
            <p className="text-emerald-400 font-semibold">+{proj30d ? proj30d.growth_rate_percent.toFixed(1) : '0.0'}% Velocity</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#07090E] border border-brand-500/30 space-y-1">
            <p className="text-slate-400">90-Day Compounded</p>
            <p className="text-xl font-bold text-brand-300">{proj90d ? `+${proj90d.net_growth_followers.toLocaleString()} Followers` : '0 Followers'}</p>
            <p className="text-brand-400 font-semibold">+{proj90d ? proj90d.growth_rate_percent.toFixed(1) : '0.0'}% Compounded Growth</p>
          </div>
        </div>
      </div>
    </div>
  );
}
