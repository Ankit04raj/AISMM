import React, { useState, useEffect, useMemo } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  ChevronLeft,
  ChevronRight,
  AlertCircle
} from 'lucide-react';
import { api } from '../api/client';

export default function SchedulingTab() {
  const [platform, setPlatform] = useState('instagram');
  const [caption, setCaption] = useState('Exciting updates coming soon to our multi-platform AI architecture! 🚀');
  const [loading, setLoading] = useState(false);
  const [scheduledOk, setScheduledOk] = useState(false);
  const [scheduleError, setScheduleError] = useState(null);
  const [monthOffset, setMonthOffset] = useState(0);

  const [bestTimes, setBestTimes] = useState([
    { day: "Today", time: "7:00 PM", quality: "Optimal", tag: "Great", impact: "+45% reach", optimal: true },
    { day: "Tomorrow", time: "6:30 PM", quality: "Good", tag: "Good", impact: "+30% reach", optimal: false },
  ]);

  const viewDate = useMemo(() => {
    const target = new Date();
    target.setMonth(target.getMonth() + monthOffset);
    return target;
  }, [monthOffset]);

  const calendarDays = useMemo(() => {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDay = new Date(year, month, 1).getDay();
    const today = new Date();
    const isCurrentMonth = today.getFullYear() === year && today.getMonth() === month;

    const days = [];
    for (let i = 0; i < firstDay; i++) days.push({ d: null, empty: true });
    for (let d = 1; d <= daysInMonth; d++) {
      days.push({
        d,
        active: true,
        scheduled: d % 7 === 0 || (isCurrentMonth && d === today.getDate())
      });
    }
    return days;
  }, [viewDate]);

  useEffect(() => {
    let active = true;
    api.recommendTimes({ platform })
      .then(res => {
        if (active && res?.recommendations?.length) {
          setBestTimes(res.recommendations);
        }
      })
      .catch((err) => {
        console.warn("Temporal recommendations notice:", err.message);
      });
    return () => { active = false; };
  }, [platform]);

  const handleSchedulePost = async () => {
    if (!caption.trim()) {
      setScheduleError("Please enter post content to schedule.");
      return;
    }
    setLoading(true);
    setScheduleError(null);
    setScheduledOk(false);
    try {
      await api.autoSchedule({ platform, text: caption, content_type: 'post' });
      window.dispatchEvent(new CustomEvent('aismm:content-published'));
      setScheduledOk(true);
      setTimeout(() => setScheduledOk(false), 4000);
    } catch (err) {
      setScheduleError(err.message || "Failed to schedule post. Please check platform connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white font-mono">07 Smart Scheduling</h2>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">
            AI-driven temporal heat matching and automatic queue dispatch
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

      {scheduleError && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl text-xs text-rose-300 font-mono flex items-center gap-2">
          <AlertCircle size={16} className="shrink-0 text-rose-400" />
          <span>{scheduleError}</span>
        </div>
      )}

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left: Best Time to Post */}
        <div className="lg:col-span-7 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white font-mono">Best Time to Post</h3>
            <span className="text-xs text-slate-400 font-mono">Based on your audience activity</span>
          </div>

          <div className="space-y-3">
            {bestTimes.map((bt, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-2xl border transition-all flex items-center justify-between font-mono ${
                  bt.optimal
                    ? 'bg-gradient-to-r from-[#0D121F] to-brand-950/40 border-brand-500/50 shadow-lg'
                    : 'bg-[#07090E] border-[#1E293B]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${bt.optimal ? 'bg-brand-600/30 text-brand-300' : 'bg-slate-800 text-slate-400'}`}>
                    <Clock size={18} />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">{bt.day}</p>
                    <p className="text-xs text-cyan-400 font-semibold">{bt.time}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${
                    bt.optimal ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {bt.quality}
                  </span>
                  <span className="text-xs font-bold text-emerald-400">{bt.impact}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Caption Preview */}
          <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] space-y-2">
            <label className="block text-xs font-bold text-slate-300 font-mono">
              Schedule Draft
            </label>
            <textarea
              rows={3}
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              className="w-full bg-transparent border-0 text-xs text-slate-200 focus:outline-none font-mono resize-none"
            />
          </div>

          <button
            onClick={handleSchedulePost}
            disabled={loading}
            className="w-full py-3.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-95 text-white font-bold rounded-2xl text-xs font-mono transition-all shadow-xl shadow-brand-600/25 flex items-center justify-center gap-2"
          >
            <CalendarIcon size={16} />
            <span>{loading ? "Scheduling with AI..." : scheduledOk ? "✓ Post Added to Schedule" : "Schedule Post"}</span>
          </button>
        </div>

        {/* Right: Calendar View */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-5 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-4">
            <h3 className="text-sm font-bold text-white font-mono">{viewDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setMonthOffset((o) => o - 1)}
                aria-label="Previous Month"
                className="p-1.5 rounded-lg bg-[#07090E] text-slate-400 hover:text-white border border-[#1E293B] transition-colors"
              >
                <ChevronLeft size={14} />
              </button>
              <button
                onClick={() => setMonthOffset(0)}
                aria-label="Current Month"
                className="px-2 py-1 rounded-lg bg-[#07090E] text-slate-400 hover:text-white border border-[#1E293B] text-[10px] font-mono transition-colors"
              >
                Today
              </button>
              <button
                onClick={() => setMonthOffset((o) => o + 1)}
                aria-label="Next Month"
                className="p-1.5 rounded-lg bg-[#07090E] text-slate-400 hover:text-white border border-[#1E293B] transition-colors"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>

          {/* Calendar Header */}
          <div className="grid grid-cols-7 text-center text-[10px] font-bold text-slate-500 font-mono">
            <span>Su</span>
            <span>Mo</span>
            <span>Tu</span>
            <span>We</span>
            <span>Th</span>
            <span>Fr</span>
            <span>Sa</span>
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1.5 text-center text-xs font-mono">
            {calendarDays.map((cell, idx) => (
              <div
                key={idx}
                className={`h-9 rounded-xl flex flex-col items-center justify-center relative transition-all ${
                  cell.empty
                    ? 'opacity-0 pointer-events-none'
                    : cell.scheduled
                    ? 'bg-[#07090E] border border-cyan-500/40 text-slate-200'
                    : 'bg-[#07090E]/60 text-slate-400'
                }`}
              >
                <span>{cell.d}</span>
                {cell.scheduled && (
                  <span className="w-1 h-1 rounded-full bg-cyan-400 mt-0.5" />
                )}
              </div>
            ))}
          </div>

          <div className="p-3.5 rounded-2xl bg-[#07090E] border border-[#1E293B] flex items-center justify-between text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              Optimal Peak
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-brand-500" />
              Scheduled
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
