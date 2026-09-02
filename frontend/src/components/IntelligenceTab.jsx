import React, { useState } from 'react';
import {
  MessageSquare,
  Activity,
  AlertTriangle,
  TrendingUp,
  Flame,
  CheckCircle2,
  Clock,
  Sparkles
} from 'lucide-react';

export default function IntelligenceTab() {
  const trajectoryData = [
    { period: "0-1h (Immediate)", sentiment: "+0.78", label: "Very Positive", comments: 42, tone: "High enthusiasm & praise" },
    { period: "1-6h (Early Viral)", sentiment: "+0.69", label: "Positive", comments: 128, tone: "Feature questions & inquiries" },
    { period: "6-24h (Sustained)", sentiment: "+0.64", label: "Positive", comments: 194, tone: "Community sharing & discussion" },
    { period: "24-72h (Long-tail)", sentiment: "+0.58", label: "Positive", comments: 85, tone: "Support & detailed requests" },
    { period: ">72h (Evergreen)", sentiment: "+0.52", label: "Stable", comments: 43, tone: "Organic explore discovery" },
  ];

  const recentComments = [
    { id: "c1", platform: "Instagram", author: "alex_creator", text: "How much does the annual pro plan cost? Need multi-channel publishing!", sentiment: "+0.45", intent: "Pricing Inquiry", time: "10m ago" },
    { id: "c2", platform: "LinkedIn", author: "Sarah Jenkins, CTO", text: "Impressive multi-platform architecture. We are looking for something that supports custom webhooks.", sentiment: "+0.88", intent: "Compliment / General", time: "25m ago" },
    { id: "c3", platform: "X (Twitter)", author: "@dev_sam", text: "Does the API support custom rate limit thresholds for enterprise?", sentiment: "+0.32", intent: "Technical Inquiry", time: "42m ago" },
    { id: "c4", platform: "YouTube", author: "TechTutorialsHQ", text: "Best breakdown of autonomous social scheduling I've seen all year. Subscribed!", sentiment: "+0.95", intent: "Praise", time: "1h ago" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">Post-Posting Intelligence & Temporal Trajectory</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Real-time comment synchronization, audience emotion drift, and automated viral/negative alerts (CLAUDE.md Section 17 & Phase 9)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center space-x-1.5">
            <Activity className="h-3.5 w-3.5" />
            <span>Audience Mood: Stable (+0.68)</span>
          </span>
        </div>
      </div>

      {/* Temporal Sentiment Trajectory Breakdown */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-gray-200 mb-1">Temporal Sentiment Trajectory Analysis</h3>
        <p className="text-xs text-gray-400 mb-5">Tracking how audience sentiment evolves across 5 standardized post-publishing horizons</p>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {trajectoryData.map((t, idx) => (
            <div key={idx} className="bg-gray-950 border border-gray-800/80 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="text-[11px] font-bold text-gray-400">{t.period}</div>
                <div className="text-2xl font-black text-emerald-400 mt-2">{t.sentiment}</div>
                <div className="text-xs font-semibold text-gray-200 mt-0.5">{t.label}</div>
              </div>
              <div className="mt-4 pt-3 border-t border-gray-800/60 text-[11px] text-gray-400">
                <div className="font-semibold text-gray-300">{t.comments} comments</div>
                <div className="text-gray-500 truncate mt-0.5">{t.tone}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Unified Multi-Platform Comment Stream */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-sm text-gray-200">Unified Real-Time Comment Stream</h3>
            <p className="text-xs text-gray-400">Aggregated comments synchronized from Instagram, Facebook, X, LinkedIn, and YouTube</p>
          </div>
          <span className="text-xs text-gray-400 font-mono">492 Total Comments Processed</span>
        </div>

        <div className="space-y-3">
          {recentComments.map((c) => (
            <div
              key={c.id}
              className="p-4 rounded-xl bg-gray-950 border border-gray-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-gray-700 transition-all"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-brand-400">{c.author}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-gray-900 text-gray-400 border border-gray-800">
                    {c.platform}
                  </span>
                  <span className="text-[10px] text-gray-500">• {c.time}</span>
                </div>
                <p className="text-xs text-gray-200">{c.text}</p>
              </div>

              <div className="flex items-center space-x-3 flex-shrink-0">
                <span className="text-xs font-semibold text-gray-300 px-2.5 py-1 rounded-md bg-gray-900 border border-gray-800">
                  {c.intent}
                </span>
                <span className="text-xs font-bold text-emerald-400 font-mono px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                  {c.sentiment}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
