import React, { useState } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  Sparkles,
  CheckCircle2,
  TrendingUp,
  Flame,
  ArrowRight
} from 'lucide-react';

export default function SchedulingTab() {
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const hours = [8, 10, 12, 14, 16, 18, 19, 20, 21, 22];

  const scheduledQueue = [
    { id: "q1", title: "AI Strategy Deep Dive & Benchmarks", platform: "LinkedIn", scheduled_for: "Tomorrow at 09:00 UTC", lift: "+24.2%", status: "Queued" },
    { id: "q2", title: "Autonomous Social Media Framework Video", platform: "YouTube", scheduled_for: "Wednesday at 15:00 UTC", lift: "+31.5%", status: "Queued" },
    { id: "q3", title: "Interactive Feature Carousel & Tutorial", platform: "Instagram", scheduled_for: "Wednesday at 19:00 UTC", lift: "+38.4%", status: "Optimal" },
    { id: "q4", title: "Community Q&A & Product Updates", platform: "Facebook", scheduled_for: "Thursday at 20:00 UTC", lift: "+18.0%", status: "Queued" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">Intelligent Scheduling & 7x24 Heatmap</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Random Forest + Gradient Boosting temporal ensemble (88.42% accuracy) matching peak engagement slots
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 flex items-center space-x-1.5">
            <Flame className="h-3.5 w-3.5 text-orange-400" />
            <span>Optimal Window: Wed 19:00 UTC (+38.4% Lift)</span>
          </span>
        </div>
      </div>

      {/* 7x24 Peak Engagement Time Heatmap Grid */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-sm text-gray-200">Temporal Engagement Heatmap (Hour-by-Day)</h3>
            <p className="text-xs text-gray-400">Darker indigo blocks signify peak predicted audience engagement</p>
          </div>
          <div className="flex items-center space-x-2 text-[11px] text-gray-400">
            <span>Low</span>
            <div className="flex space-x-1">
              <span className="h-3 w-3 rounded bg-gray-950 border border-gray-800"></span>
              <span className="h-3 w-3 rounded bg-indigo-950/60"></span>
              <span className="h-3 w-3 rounded bg-indigo-700"></span>
              <span className="h-3 w-3 rounded bg-brand-500"></span>
            </div>
            <span>Peak</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-center border-collapse">
            <thead>
              <tr>
                <th className="p-2 text-left text-xs font-bold text-gray-400">Day</th>
                {hours.map((h) => (
                  <th key={h} className="p-2 text-xs font-bold text-gray-400">{h}:00</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {days.map((day, dIdx) => (
                <tr key={day} className="border-t border-gray-800/60">
                  <td className="p-2.5 text-left text-xs font-semibold text-gray-300">{day}</td>
                  {hours.map((h) => {
                    const isPeak = (dIdx === 2 && h === 19) || (dIdx === 3 && h === 20) || (dIdx === 1 && h === 18);
                    const isHigh = h >= 18 && h <= 21;
                    const isMed = h >= 12 && h <= 14;

                    let bgClass = "bg-gray-950 text-gray-500";
                    if (isPeak) bgClass = "bg-brand-500 text-white font-black shadow-lg shadow-brand-500/30";
                    else if (isHigh) bgClass = "bg-indigo-700/80 text-white font-bold";
                    else if (isMed) bgClass = "bg-indigo-950/60 text-indigo-300";

                    return (
                      <td key={h} className="p-1">
                        <div className={`h-8 rounded-lg flex items-center justify-center text-xs transition-all ${bgClass}`}>
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

      {/* Scheduled Posts Queue */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-gray-200 mb-4">Autonomous Due Post Dispatcher Queue</h3>
        <div className="space-y-3">
          {scheduledQueue.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-4 rounded-xl bg-gray-950 border border-gray-800/80 hover:border-gray-700 transition-all"
            >
              <div className="flex items-center space-x-3.5">
                <div className="h-10 w-10 rounded-xl bg-gray-900 border border-gray-800 flex items-center justify-center text-brand-400 font-bold text-xs">
                  {item.platform.slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <div className="font-bold text-sm text-gray-100">{item.title}</div>
                  <div className="text-xs text-gray-400 flex items-center space-x-2 mt-0.5">
                    <span>{item.platform}</span>
                    <span>•</span>
                    <span className="text-indigo-400">{item.scheduled_for}</span>
                  </div>
                </div>
              </div>

              <div className="text-right flex items-center space-x-4">
                <span className="text-xs font-bold text-emerald-400 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20">
                  {item.lift} Expected Lift
                </span>
                <span className="text-xs text-gray-400 font-semibold">{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
