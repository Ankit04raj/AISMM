import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, Target, Activity, RefreshCw, AlertTriangle, PieChart, BarChart2, Sparkles } from 'lucide-react';
import { api } from '../api/client';

const platformMultipliers = { instagram: 1.0, facebook: 0.85, twitter: 1.25, linkedin: 0.75, youtube: 0.60 };

export default function GrowthTab() {
  const [platform, setPlatform] = useState('instagram');
  const [followers, setFollowers] = useState(10000);
  const [frequency, setFrequency] = useState(4.0);
  const [modelsStatus, setModelsStatus] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStatus = async () => {
    try {
      const status = await api.getGrowthModelsStatus();
      setModelsStatus(status || []);
    } catch {
      // Fallback
    }
  };

  const getPrediction = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.predictGrowth({
        platform,
        current_followers: followers,
        posting_frequency_weekly: frequency,
        avg_engagement_rate: 4.5,
      });
      setPrediction(data);
    } catch (err) {
      setError(`Unable to reach AISMM backend: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  useEffect(() => {
    const timer = setTimeout(getPrediction, 500);
    return () => clearTimeout(timer);
  }, [platform, followers, frequency]);

  const activeStatus = modelsStatus.find(m => m.platform === platform) || { stage: 'production', current_r2: 0.892, rmse: 22.4 };

  return (
    <div className="space-y-6 animate-fadeIn"><div className="notice">Experimental decision support. Current ML models use synthetic training/evaluation data; scores are not validated predictions of your real audience. Review recommendations before acting.</div>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white">Predictive Growth Modeling & Forecasts</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Platform-specific Random Forest Regressors forecasting 7, 30, and 90-day audience velocity & demographics
          </p>
        </div>
        <div className="text-xs font-bold px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-2 font-mono">
          <Target className="w-3.5 h-3.5" />
          <span>Experimental simulator</span>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl flex items-center justify-between text-xs text-rose-300">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={getPrediction} className="underline hover:text-white">Retry Forecast</button>
        </div>
      )}

      {/* Simulator Inputs & Platform Toggles */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl space-y-6">
          <div>
            <label className="block text-[11px] font-bold uppercase text-slate-400 mb-2.5 font-mono">
              Target Social Network
            </label>
            <div className="flex flex-wrap gap-2">
              {Object.keys(platformMultipliers).map((p) => (
                <button
                  key={p}
                  onClick={() => setPlatform(p)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-bold capitalize transition-all ${
                    platform === p
                      ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
                      : 'bg-[#07090E] border border-[#1E293B] text-slate-400 hover:text-white'
                  }`}
                >
                  {p === 'x' ? 'X' : p}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-[11px] font-bold uppercase text-slate-400 font-mono">
                Simulation follower baseline
              </label>
              <span className="text-sm font-extrabold text-brand-400 font-mono">
                {followers.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min="1000"
              max="200000"
              step="1000"
              value={followers}
              onChange={(e) => setFollowers(Number(e.target.value))}
              className="w-full accent-brand-500 h-2 bg-[#07090E] rounded-lg cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-[11px] font-bold uppercase text-slate-400 font-mono">
                Posting Frequency
              </label>
              <span className="text-sm font-extrabold text-cyan-400 font-mono">
                {frequency.toFixed(1)} posts / week
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="14"
              step="0.5"
              value={frequency}
              onChange={(e) => setFrequency(Number(e.target.value))}
              className="w-full accent-cyan-500 h-2 bg-[#07090E] rounded-lg cursor-pointer"
            />
          </div>
        </div>

        {/* Forecast Multi-Horizon Trend Curve & Cards */}
        <div className="lg:col-span-7 space-y-4">
          {loading && !prediction ? (
            <div className="h-64 bg-[#0D121F] border border-[#1E293B] rounded-3xl flex flex-col items-center justify-center gap-3">
              <RefreshCw className="w-6 h-6 text-brand-400 animate-spin" />
              <p className="text-xs text-slate-400 font-mono">Running Random Forest regression projections...</p>
            </div>
          ) : prediction ? (
            <>
              {/* 3 Multi-Horizon KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-[#0D121F] border border-[#1E293B] rounded-2xl p-5 shadow-xl">
                  <div className="flex justify-between text-[11px] font-bold uppercase text-slate-400 font-mono">
                    <span>7-Day Short</span>
                    <span className="text-emerald-400">+{prediction.projections["7d"].growth_rate_percent}%</span>
                  </div>
                  <div className="mt-3 text-2xl font-black text-white font-mono">
                    {prediction.projections["7d"].predicted_followers.toLocaleString()}
                  </div>
                  <div className="mt-1 text-[11px] text-emerald-400 font-semibold font-mono">
                    +{prediction.projections["7d"].net_growth_followers.toLocaleString()} net gain
                  </div>
                </div>

                <div className="bg-gradient-to-br from-[#0D121F] via-brand-950/30 to-[#0D121F] border border-brand-500/40 rounded-2xl p-5 shadow-2xl relative overflow-hidden">
                  <div className="flex justify-between text-[11px] font-bold uppercase text-brand-300 font-mono">
                    <span>30-Day Target</span>
                    <span className="text-emerald-400">+{prediction.projections["30d"].growth_rate_percent}%</span>
                  </div>
                  <div className="mt-3 text-2xl font-black text-white font-mono">
                    {prediction.projections["30d"].predicted_followers.toLocaleString()}
                  </div>
                  <div className="mt-1 text-[11px] text-brand-400 font-semibold font-mono">
                    +{prediction.projections["30d"].net_growth_followers.toLocaleString()} net gain
                  </div>
                </div>

                <div className="bg-[#0D121F] border border-[#1E293B] rounded-2xl p-5 shadow-xl">
                  <div className="flex justify-between text-[11px] font-bold uppercase text-slate-400 font-mono">
                    <span>90-Day Quarter</span>
                    <span className="text-emerald-400">+{prediction.projections["90d"].growth_rate_percent}%</span>
                  </div>
                  <div className="mt-3 text-2xl font-black text-white font-mono">
                    {prediction.projections["90d"].predicted_followers.toLocaleString()}
                  </div>
                  <div className="mt-1 text-[11px] text-emerald-400 font-semibold font-mono">
                    +{prediction.projections["90d"].net_growth_followers.toLocaleString()} net gain
                  </div>
                </div>
              </div>

              <div className="notice">These are simulated model outputs for the assumptions you entered, not your account's measured growth. No validated growth-accuracy history is available.</div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
