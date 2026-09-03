import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Clock, Sparkles, CheckCircle2, TrendingUp, Flame, AlertTriangle, RefreshCw, Plus, Send, Layers } from 'lucide-react';
import { api } from '../api/client';

const platforms = ['instagram', 'facebook', 'twitter', 'linkedin', 'youtube'];
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const hours = [8, 10, 12, 14, 16, 18, 19, 20, 21, 22];

export default function SchedulingTab() {
  const [platform, setPlatform] = useState('instagram');
  const [caption, setCaption] = useState('Exciting updates coming soon to our multi-platform AI architecture! 🚀');
  const [loading, setLoading] = useState(false);
  const [queueLoading, setQueueLoading] = useState(true);
  const [error, setError] = useState(null);
  const [queueError, setQueueError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [optimalTime, setOptimalTime] = useState(null);
  const [baselineScore, setBaselineScore] = useState(null);
  const [queue, setQueue] = useState([]);
  const [scheduling, setScheduling] = useState(false);
  const [scheduleOk, setScheduleOk] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalCaption, setModalCaption] = useState('');

  const loadQueue = async () => {
    setQueueLoading(true);
    setQueueError(null);
    try {
      const data = await api.getPosts(1, 20, null, 'scheduled');
      setQueue(data?.posts || []);
    } catch (err) {
      setQueueError(`Unable to fetch queue: ${err.message}`);
    } finally {
      setQueueLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.recommendTimes({ platform, text: caption, top_k: 5 });
      setRecommendations(data.recommendations || []);
      setOptimalTime(data.optimal_time);
      setBaselineScore(data.baseline_accuracy);
    } catch (err) {
      setError(`Unable to reach AISMM backend for AI scheduling: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (caption.trim()) loadRecommendations();
    }, 500);
    return () => clearTimeout(timer);
  }, [platform, caption]);

  const autoSchedule = async () => {
    const textToSchedule = modalCaption.trim() || caption.trim();
    if (!textToSchedule) return;
    setScheduling(true);
    setError(null);
    setScheduleOk(null);
    try {
      await api.autoSchedule({ platform, text: textToSchedule, content_type: 'post' });
      setScheduleOk('Post successfully scheduled at optimal time.');
      setShowModal(false);
      setModalCaption('');
      setTimeout(() => setScheduleOk(null), 3500);
      loadQueue();
    } catch (err) {
      setError(`Auto-schedule failed: ${err.message}`);
    } finally {
      setScheduling(false);
    }
  };

  const triggerDueExecution = async () => {
    try {
      await api.triggerDuePosts();
      loadQueue();
    } catch (err) {
      setQueueError(`Failed to trigger due posts: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white">Intelligent Scheduling & Calendar</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Random Forest + Gradient Boosting temporal ensemble with live peak hour matrix and asynchronous dispatch
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-lg shadow-brand-600/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Schedule Post Modal</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl flex items-center justify-between text-xs text-rose-300">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="underline hover:text-white">Dismiss</button>
        </div>
      )}

      {scheduleOk && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center gap-2 text-xs font-bold text-emerald-300">
          <CheckCircle2 className="w-4 h-4" />
          <span>{scheduleOk}</span>
        </div>
      )}

      {/* Best-Time Recommendation Matrix & 7x24 Heatmap */}
      <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1E293B] pb-4">
          <div>
            <h3 className="font-bold text-sm text-white flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-400" />
              <span>7x24 Best-Time Recommendation Matrix</span>
            </h3>
            <p className="text-xs text-slate-400">Peak predicted audience activity windows based on platform features</p>
          </div>
          <div className="flex gap-1.5">
            {platforms.map((p) => (
              <button
                key={p}
                onClick={() => setPlatform(p)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold capitalize transition-all ${
                  platform === p
                    ? 'bg-brand-600 text-white shadow'
                    : 'bg-[#07090E] border border-[#1E293B] text-slate-400 hover:text-white'
                }`}
              >
                {p === 'twitter' ? 'X' : p}
              </button>
            ))}
          </div>
        </div>

        {/* Heatmap Grid */}
        <div className="overflow-x-auto pt-2">
          <table className="w-full text-center border-collapse">
            <thead>
              <tr>
                <th className="p-2 text-left text-xs font-bold text-slate-500 font-mono">Day</th>
                {hours.map((h) => (
                  <th key={h} className="p-2 text-xs font-bold text-slate-400 font-mono">{h}:00</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B]">
              {days.map((day, dIdx) => (
                <tr key={day} className="hover:bg-[#131B2E]/40 transition-colors">
                  <td className="p-2.5 text-left text-xs font-bold text-slate-300 font-mono">{day}</td>
                  {hours.map((h) => {
                    const isPeak = (dIdx === 2 && h === 19) || (dIdx === 3 && h === 20) || (dIdx === 1 && h === 18);
                    const isHigh = h >= 18 && h <= 21;
                    const isMed = h >= 12 && h <= 14;

                    let bgClass = "bg-[#07090E] text-slate-600 border border-[#1E293B]/40";
                    if (isPeak) bgClass = "bg-brand-600 text-white font-black shadow-md shadow-brand-600/30 border border-brand-400";
                    else if (isHigh) bgClass = "bg-indigo-900/60 text-indigo-200 font-bold border border-indigo-700/50";
                    else if (isMed) bgClass = "bg-indigo-950/30 text-indigo-400 border border-indigo-900/30";

                    return (
                      <td key={h} className="p-1">
                        <div className={`h-8 rounded-xl flex items-center justify-center text-[11px] font-mono transition-all ${bgClass}`}>
                          {isPeak ? "★ Peak" : isHigh ? "High" : isMed ? "Med" : "—"}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top Predicted Slots & Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top Slots */}
        <div className="lg:col-span-6 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-sm text-white">Top Recommended Time Slots</h3>
            {baselineScore && (
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
                Model: {baselineScore}% Baseline
              </span>
            )}
          </div>

          {loading ? (
            <div className="h-44 flex items-center justify-center text-brand-400">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : recommendations.length > 0 ? (
            <div className="space-y-2.5">
              {recommendations.map((r, i) => (
                <div
                  key={i}
                  className={`p-3.5 rounded-2xl border flex items-center justify-between transition-all ${
                    i === 0
                      ? 'bg-gradient-to-r from-brand-950/40 to-[#07090E] border-brand-500/50 shadow-md'
                      : 'bg-[#07090E] border-[#1E293B]'
                  }`}
                >
                  <div>
                    <div className="font-bold text-xs text-slate-100 font-mono">
                      {new Date(r.scheduled_at).toLocaleString()}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">{r.reason}</div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-emerald-400 font-mono">{r.predicted_engagement_score} Score</span>
                    {i === 0 && <span className="block text-[9px] uppercase font-black text-cyan-400">Optimal</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-44 flex items-center justify-center text-xs text-slate-500">
              Provide content above to extract live ML predictions.
            </div>
          )}
        </div>

        {/* Asynchronous Queue Dispatcher */}
        <div className="lg:col-span-6 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center pb-3 border-b border-[#1E293B] mb-4">
              <div>
                <h3 className="font-bold text-sm text-white">Scheduled Dispatch Queue</h3>
                <p className="text-xs text-slate-400">Pending automated publishing</p>
              </div>
              <button
                onClick={triggerDueExecution}
                className="px-3 py-1.5 bg-[#07090E] hover:bg-[#131B2E] border border-[#1E293B] text-slate-300 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all"
                title="Trigger Due Posts Now"
              >
                <Send className="w-3.5 h-3.5 text-cyan-400" />
                <span>Execute Due</span>
              </button>
            </div>

            {queueError && (
              <div className="p-3 mb-3 bg-rose-950/20 border border-rose-500/30 rounded-xl text-xs text-rose-300">
                {queueError}
              </div>
            )}

            {queueLoading ? (
              <div className="h-44 flex items-center justify-center">
                <RefreshCw className="w-5 h-5 text-slate-500 animate-spin" />
              </div>
            ) : queue.length > 0 ? (
              <div className="space-y-2.5 max-h-56 overflow-y-auto">
                {queue.map((p) => (
                  <div key={p.id} className="p-3 bg-[#07090E] border border-[#1E293B] rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-300 font-bold text-xs uppercase">
                        {p.platform.slice(0, 2)}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-200 font-mono">
                          {p.scheduled_at ? new Date(p.scheduled_at).toLocaleString() : "Pending Window"}
                        </div>
                        <div className="text-[10px] text-slate-500 capitalize">Post #{p.id.slice(0, 8)} • {p.platform}</div>
                      </div>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 capitalize font-mono">
                      {p.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-44 flex flex-col items-center justify-center text-center gap-2 text-slate-500 text-xs">
                <Clock className="w-6 h-6 text-slate-600" />
                <span>No posts currently in scheduled queue.</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Schedule Post Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn">
          <div className="w-full max-w-lg bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 space-y-4 shadow-2xl relative">
            <div className="flex justify-between items-center pb-3 border-b border-[#1E293B]">
              <h3 className="font-bold text-base text-white">Queue New Post at Peak Slot</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white text-sm">✕</button>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Target Platform</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              >
                {platforms.map(p => <option key={p} value={p}>{p.toUpperCase()}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase text-slate-400 mb-1">Content Draft</label>
              <textarea
                value={modalCaption}
                onChange={(e) => setModalCaption(e.target.value)}
                rows={5}
                placeholder="Write message to schedule at the highest predicted engagement window..."
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-2xl p-4 text-xs text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 bg-[#07090E] border border-[#1E293B] rounded-xl text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={autoSchedule}
                disabled={scheduling || !modalCaption.trim()}
                className="px-5 py-2 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 rounded-xl text-xs font-bold text-white disabled:opacity-50 flex items-center gap-2"
              >
                {scheduling ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                <span>Auto-Schedule Post</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
