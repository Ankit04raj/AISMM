import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart,
  Layers,
  ArrowUpRight,
  Sparkles,
  Activity,
  CheckCircle2
} from 'lucide-react';

export default function AnalyticsTab() {
  const platformBenchmarks = [
    { platform: "Instagram", reach: "48.2k", impressions: "62.4k", engagements: "3,370", rate: "5.4%", strongest: true },
    { platform: "Facebook", reach: "32.1k", impressions: "41.2k", engagements: "1,560", rate: "3.8%", strongest: false },
    { platform: "LinkedIn", reach: "22.4k", impressions: "28.9k", engagements: "1,300", rate: "4.5%", strongest: false },
    { platform: "X (Twitter)", reach: "38.6k", impressions: "51.2k", engagements: "1,480", rate: "2.9%", strongest: false },
    { platform: "YouTube", reach: "14.5k", impressions: "18.8k", engagements: "1,520", rate: "8.1%", strongest: true },
  ];

  const contentFormatROI = [
    { format: "Multi-Slide Carousels", avg_impressions: "4,850", avg_engagement: "6.8%", share: "35%", performance: "Highest Retention" },
    { format: "Short-Form Videos / Reels", avg_impressions: "6,200", avg_engagement: "5.9%", share: "40%", performance: "Highest Discovery" },
    { format: "Single Static Images", avg_impressions: "2,400", avg_engagement: "3.4%", share: "15%", performance: "Baseline" },
    { format: "Text & Link Posts", avg_impressions: "1,850", avg_engagement: "2.8%", share: "10%", performance: "Direct Conversion" },
  ];

  const driftPoints = [
    { date: "Aug 01", actual: 10000, pred: 10000, mape: "0.0%" },
    { date: "Aug 08", actual: 10320, pred: 10290, mape: "0.29%" },
    { date: "Aug 15", actual: 10710, pred: 10680, mape: "0.28%" },
    { date: "Aug 22", actual: 11050, pred: 11110, mape: "0.54%" },
    { date: "Aug 29", actual: 11420, pred: 11390, mape: "0.26%" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">Universal Analytics & Comparative Benchmarking</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Normalized cross-platform performance without incompatible metric collisions (CLAUDE.md Section 30 & 31)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            Model Drift Status: Calibrated (MAPE 0.31%)
          </span>
        </div>
      </div>

      {/* Platform Comparative Benchmarking Table */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-gray-200 mb-4">Cross-Platform Normalized Benchmarking</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400">
                <th className="pb-3 font-bold">Platform</th>
                <th className="pb-3 font-bold">Total Reach</th>
                <th className="pb-3 font-bold">Impressions</th>
                <th className="pb-3 font-bold">Interactions</th>
                <th className="pb-3 font-bold">Engagement Rate</th>
                <th className="pb-3 font-bold text-right">Channel Role</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {platformBenchmarks.map((p) => (
                <tr key={p.platform} className="hover:bg-gray-950/50 transition-colors">
                  <td className="py-3 font-bold text-gray-100 flex items-center space-x-2">
                    <span>{p.platform}</span>
                    {p.strongest && (
                      <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                        Top ROI
                      </span>
                    )}
                  </td>
                  <td className="py-3 text-gray-300 font-mono">{p.reach}</td>
                  <td className="py-3 text-gray-300 font-mono">{p.impressions}</td>
                  <td className="py-3 text-gray-300 font-mono">{p.engagements}</td>
                  <td className="py-3 text-emerald-400 font-bold font-mono">{p.rate}</td>
                  <td className="py-3 text-right text-gray-400">{p.platform === "YouTube" ? "Deep Video Watch" : "Community Discovery"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Content Format ROI Breakdown & Growth Drift Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Content Format ROI */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h3 className="font-bold text-sm text-gray-200 mb-1">Content Format Engagement ROI</h3>
          <p className="text-xs text-gray-400 mb-4">Performance breakdown across visual and text formats</p>
          <div className="space-y-3">
            {contentFormatROI.map((fmt, i) => (
              <div key={i} className="p-3.5 rounded-xl bg-gray-950 border border-gray-800/80 flex items-center justify-between">
                <div>
                  <div className="font-bold text-xs text-gray-200">{fmt.format}</div>
                  <div className="text-[11px] text-gray-400">{fmt.performance} • {fmt.share} of total posts</div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-bold text-emerald-400">{fmt.avg_engagement}</div>
                  <div className="text-[11px] text-gray-400">{fmt.avg_impressions} avg imp</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Growth Model Drift Calibration */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h3 className="font-bold text-sm text-gray-200 mb-1">Actual vs Predicted Growth Drift</h3>
          <p className="text-xs text-gray-400 mb-4">Evaluating Random Forest regressor error percentage over time</p>
          <div className="space-y-2.5 text-xs">
            {driftPoints.map((dp, i) => (
              <div key={i} className="p-2.5 rounded-lg bg-gray-950 border border-gray-800/60 flex items-center justify-between font-mono">
                <span className="text-gray-400">{dp.date}</span>
                <span className="text-gray-300">Actual: {dp.actual.toLocaleString()}</span>
                <span className="text-indigo-400">Pred: {dp.pred.toLocaleString()}</span>
                <span className="text-emerald-400 font-bold">Error: {dp.mape}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
