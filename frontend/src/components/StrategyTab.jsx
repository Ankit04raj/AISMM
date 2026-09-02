import React, { useState } from 'react';
import {
  Lightbulb,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Clock,
  Layers,
  TrendingUp,
  ShieldAlert,
  Share2
} from 'lucide-react';

export default function StrategyTab() {
  const recommendations = [
    {
      id: "rec_1",
      category: "TIMING",
      priority: "HIGH",
      title: "Align Primary Posting with Peak Window (Wednesday at 19:00 UTC)",
      action: "Schedule top-tier product and educational content on Wednesdays at 19:00 UTC for maximum discovery.",
      reasoning: "ML scheduling ensemble predicts a 38.4% engagement index lift during this hour across connected channels.",
      confidence: "91%",
      impact: "+38.4% Lift",
      platform: "Instagram & Facebook",
    },
    {
      id: "rec_2",
      category: "CONTENT_FORMAT",
      priority: "HIGH",
      title: "Prioritize Multi-Slide Carousel & Video Assets",
      action: "Increase carousel and short-form video ratio to at least 60% of weekly content mix.",
      reasoning: "Performance data indicates multi-frame media drives 42% longer dwell time and 1.8x more saves/shares compared to single static images.",
      confidence: "88%",
      impact: "+24.5% Reach",
      platform: "Instagram & LinkedIn",
    },
    {
      id: "rec_3",
      category: "GROWTH_VELOCITY",
      priority: "MEDIUM",
      title: "Increase Weekly Cadence from 3.0 to 4.5+ Posts",
      action: "Scale active posting schedule to 4-5 strategic posts per week across active networks.",
      reasoning: "Growth regression models project a +18.4% monthly follower velocity acceleration when cadence meets platform algorithm discovery thresholds.",
      confidence: "86%",
      impact: "+18.4% Followers",
      platform: "All Channels",
    },
    {
      id: "rec_4",
      category: "CROSS_PLATFORM_SYNERGY",
      priority: "LOW",
      title: "Cross-Pollinate Top Performing Posts Across Networks",
      action: "Adapt high-engagement Instagram posts into LinkedIn native formats 24h after publication.",
      reasoning: "Repurposing proven high-sentiment content yields 70% of original reach with 90% less content production overhead.",
      confidence: "84%",
      impact: "+12.0% Reach",
      platform: "Cross-Platform",
    },
  ];

  const platformProfiles = [
    { platform: "Instagram", frequency: "5.0 posts/wk", time: "18:00 - 21:00 UTC", format: "Carousel / Reels", hashtags: "4-6 tags", growth: "+4,200/mo" },
    { platform: "Facebook", frequency: "4.0 posts/wk", time: "19:00 - 22:00 UTC", format: "Community Videos", hashtags: "0-2 tags", growth: "+3,100/mo" },
    { platform: "X (Twitter)", frequency: "12.0 tweets/wk", time: "12:00 - 15:00 UTC", format: "Threads & Media", hashtags: "1-2 tags", growth: "+5,500/mo" },
    { platform: "LinkedIn", frequency: "3.5 posts/wk", time: "08:00 - 11:00 UTC", format: "Document Shares", hashtags: "3-5 tags", growth: "+2,800/mo" },
    { platform: "YouTube", frequency: "2.0 videos/wk", time: "15:00 - 18:00 UTC", format: "Videos & Shorts", hashtags: "3-5 tags", growth: "+1,400/mo" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">AI Strategy Engine & Strategic Recommendations</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Multi-model intelligence synthesis orchestrator combining scheduling, sentiment, growth, and format signals (CLAUDE.md Section 33)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 flex items-center space-x-1.5">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Strategy Health Score: 88 / 100</span>
          </span>
        </div>
      </div>

      {/* Ranked Strategic Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl hover:border-gray-700 transition-all space-y-3"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-2">
                <span className={`text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider ${
                  rec.priority === "HIGH"
                    ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                    : rec.priority === "MEDIUM"
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                    : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                }`}>
                  {rec.priority} Priority
                </span>
                <span className="text-xs font-bold text-gray-400">{rec.category.replace("_", " ")}</span>
                <span className="text-xs text-gray-500">• {rec.platform}</span>
              </div>

              <span className="text-xs font-bold text-emerald-400 font-mono px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 self-start sm:self-auto">
                {rec.impact}
              </span>
            </div>

            <h3 className="text-sm sm:text-base font-extrabold text-gray-100">{rec.title}</h3>
            <p className="text-xs text-gray-300 leading-relaxed bg-gray-950/70 p-3 rounded-xl border border-gray-800/60">
              {rec.action}
            </p>

            <div className="text-[11px] text-gray-400 flex flex-col sm:flex-row sm:items-center justify-between gap-1 pt-1 border-t border-gray-800/60">
              <span><strong>Reasoning:</strong> {rec.reasoning}</span>
              <span className="text-brand-400 font-semibold font-mono">Confidence: {rec.confidence}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Platform Strategy Profiles */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-gray-200 mb-1">Tailored Platform Strategy Profiles</h3>
        <p className="text-xs text-gray-400 mb-4">Recommended publishing cadences and optimal format mixes per network</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {platformProfiles.map((prof) => (
            <div key={prof.platform} className="p-4 rounded-xl bg-gray-950 border border-gray-800/80 space-y-2 text-xs">
              <div className="font-extrabold text-sm text-brand-300 flex items-center justify-between">
                <span>{prof.platform}</span>
                <span className="text-emerald-400 text-xs font-mono">{prof.growth}</span>
              </div>
              <div className="text-gray-300"><strong>Cadence:</strong> {prof.frequency}</div>
              <div className="text-gray-300"><strong>Peak Window:</strong> {prof.time}</div>
              <div className="text-gray-300"><strong>Top Format:</strong> {prof.format}</div>
              <div className="text-gray-300"><strong>Hashtags:</strong> {prof.hashtags}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
