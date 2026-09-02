import React, { useState, useEffect } from 'react';
import {
  Users,
  Eye,
  Heart,
  TrendingUp,
  MessageSquare,
  Sparkles,
  Share2,
  CheckCircle2,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Clock,
  Layers
} from 'lucide-react';
import { api } from '../api/client';

export default function OverviewTab({ onNavigateTab }) {
  const [loading, setLoading] = useState(false);
  const [overview, setOverview] = useState({
    total_connected_platforms: 5,
    total_followers: 58400,
    total_impressions: 142000,
    total_reach: 110760,
    total_engagements: 6840,
    overall_engagement_rate: 4.82,
    total_posts_published: 28,
    total_comments_received: 492,
    average_sentiment_score: 0.68,
    time_period_days: 30,
  });

  useEffect(() => {
    async function loadData() {
      const data = await api.getOverview(30);
      if (data) {
        setOverview(data);
      }
    }
    loadData();
  }, []);

  const kpis = [
    { label: "Total Audience Reach", value: overview.total_reach?.toLocaleString() || "110,760", icon: Eye, change: "+14.2%", color: "from-blue-500 to-indigo-600" },
    { label: "Total Connected Followers", value: overview.total_followers?.toLocaleString() || "58,400", icon: Users, change: "+8.6%", color: "from-purple-500 to-pink-600" },
    { label: "Total Interactions", value: overview.total_engagements?.toLocaleString() || "6,840", icon: Heart, change: "+22.4%", color: "from-rose-500 to-orange-500" },
    { label: "Avg Engagement Rate", value: `${overview.overall_engagement_rate || 4.82}%`, icon: TrendingUp, change: "+1.2%", color: "from-emerald-500 to-teal-600" },
  ];

  const connectedPlatforms = [
    { name: "Instagram", followers: "18.4k", rate: "5.4%", status: "Active", format: "Carousels / Reels" },
    { name: "Facebook", followers: "14.2k", rate: "3.8%", status: "Active", format: "Page Videos" },
    { name: "X (Twitter)", followers: "12.8k", rate: "2.9%", status: "Active", format: "Threads & Media" },
    { name: "LinkedIn", followers: "8.6k", rate: "4.5%", status: "Active", format: "Document Shares" },
    { name: "YouTube", followers: "4.4k", rate: "8.1%", status: "Active", format: "Videos & Shorts" },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-brand-900/60 via-indigo-950/40 to-gray-900 border border-brand-500/20 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-md bg-brand-500/20 text-brand-300 text-xs font-semibold mb-2">
            <Sparkles className="h-3.5 w-3.5 text-brand-400" />
            <span>AI Strategy Active</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-white">Universal Management Hub</h2>
          <p className="text-xs sm:text-sm text-gray-400 mt-1">
            5 Social Networks dynamically connected. AI engines optimizing timing, sentiment, and auto-reply.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigateTab("composer")}
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold shadow-lg shadow-brand-600/30 transition-all flex items-center space-x-2"
          >
            <Zap className="h-4 w-4" />
            <span>New Post with AI</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((k, i) => {
          const Icon = k.icon;
          return (
            <div key={i} className="bg-gray-900/80 border border-gray-800/80 rounded-2xl p-5 shadow-lg relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-400">{k.label}</span>
                <div className={`h-8 w-8 rounded-lg bg-gradient-to-tr ${k.color} flex items-center justify-center text-white shadow-sm`}>
                  <Icon className="h-4 w-4" />
                </div>
              </div>
              <div className="text-2xl font-black text-white mt-3 tracking-tight">{k.value}</div>
              <div className="flex items-center space-x-1.5 text-xs text-emerald-400 font-semibold mt-2">
                <ArrowUpRight className="h-3.5 w-3.5" />
                <span>{k.change} vs prior 30d</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Two Column Layout: Connected Platforms & AI Health Index */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Active Platforms Status */}
        <div className="lg:col-span-8 bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-gray-200">Connected Social Networks (5/5)</h3>
              <p className="text-xs text-gray-400">All network adapters operating via BasePlatformAdapter contracts</p>
            </div>
            <button
              onClick={() => onNavigateTab("platforms")}
              className="text-xs font-semibold text-brand-400 hover:text-brand-300"
            >
              Manage Platforms →
            </button>
          </div>

          <div className="space-y-2.5">
            {connectedPlatforms.map((p, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3.5 rounded-xl bg-gray-950/70 border border-gray-800/60 hover:border-gray-700 transition-all"
              >
                <div className="flex items-center space-x-3">
                  <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></div>
                  <div>
                    <div className="font-bold text-sm text-gray-200">{p.name}</div>
                    <div className="text-[11px] text-gray-400">Top format: {p.format}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-bold text-gray-200">{p.followers} followers</div>
                  <div className="text-[11px] text-emerald-400 font-medium">{p.rate} engagement</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Audience Sentiment & Model Health */}
        <div className="lg:col-span-4 bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-gray-200">Audience Sentiment & Health</h3>
            <p className="text-xs text-gray-400 mt-0.5">Dual-phase VADER + comment trajectory</p>

            <div className="mt-6 text-center">
              <div className="inline-flex items-center justify-center p-6 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <span className="text-3xl font-extrabold">+0.68</span>
              </div>
              <div className="font-bold text-sm text-gray-200 mt-3">Very Positive Audience Mood</div>
              <div className="text-xs text-gray-400 mt-1">78.4% positive / 4.2% negative comments</div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-800 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Peak Window</span>
              <span className="text-indigo-400 font-bold">Wednesdays 19:00 UTC</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Auto-Reply Routing</span>
              <span className="text-emerald-400 font-bold">88.5% confidence (Active)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
