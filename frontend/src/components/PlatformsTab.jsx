import React, { useState } from 'react';
import {
  Share2,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  RefreshCw,
  ExternalLink,
  Layers,
  Zap,
  Info
} from 'lucide-react';

export default function PlatformsTab() {
  const [platforms, setPlatforms] = useState([
    {
      id: "instagram",
      name: "Instagram",
      account: "@AISMM_Official",
      status: "connected",
      category: "Business Creator Page",
      api_standard: "Instagram Graph API v19.0",
      token_status: "Valid (AES-256 Vault)",
      last_synced: "2 mins ago",
      capabilities: ["post_image", "post_video", "post_carousel", "post_story", "post_reel", "schedule_post", "get_insights", "reply_comment"],
    },
    {
      id: "facebook",
      name: "Facebook",
      account: "AISMM Business Page",
      status: "connected",
      category: "Verified Page",
      api_standard: "Facebook Graph API v19.0",
      token_status: "Valid (Page Token)",
      last_synced: "5 mins ago",
      capabilities: ["post_text", "post_image", "post_video", "schedule_post", "get_insights", "reply_comment", "manage_webhooks"],
    },
    {
      id: "x",
      name: "X (Twitter)",
      account: "@AISMM_Tech",
      status: "connected",
      category: "Developer Verified",
      api_standard: "X API v2 (OAuth 2.0 PKCE S256)",
      token_status: "Valid (Refresh Token Active)",
      last_synced: "1 min ago",
      capabilities: ["post_text", "post_image", "post_video", "get_post", "get_insights", "reply_comment", "manage_webhooks"],
    },
    {
      id: "linkedin",
      name: "LinkedIn",
      account: "AISMM Technology Corp.",
      status: "connected",
      category: "Organization Page",
      api_standard: "LinkedIn REST & UGC API",
      token_status: "Valid (3-Legged OAuth)",
      last_synced: "12 mins ago",
      capabilities: ["post_text", "post_image", "post_video", "post_carousel", "get_insights", "reply_comment", "update_profile"],
    },
    {
      id: "youtube",
      name: "YouTube",
      account: "AISMM AI Engineering Channel",
      status: "connected",
      category: "Brand Channel",
      api_standard: "YouTube Data API v3 & Analytics",
      token_status: "Valid (Google OAuth)",
      last_synced: "8 mins ago",
      capabilities: ["post_video", "delete_post", "get_post", "get_analytics", "get_insights", "reply_comment", "delete_comment"],
    },
  ]);

  const toggleConnection = (id) => {
    setPlatforms(platforms.map(p => {
      if (p.id === id) {
        return { ...p, status: p.status === "connected" ? "disconnected" : "connected" };
      }
      return p;
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">Platform Connection Hub</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Manage authenticated platform adapters and inspect dynamic capability declarations (CLAUDE.md Section 44)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            5/5 Connected
          </span>
        </div>
      </div>

      {/* Platform Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {platforms.map((p) => {
          const isConnected = p.status === "connected";
          return (
            <div
              key={p.id}
              className={`bg-gray-900/80 border rounded-2xl p-5 shadow-xl flex flex-col justify-between transition-all ${
                isConnected ? "border-gray-800" : "border-gray-800/40 opacity-70"
              }`}
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="h-9 w-9 rounded-xl bg-gray-800 border border-gray-700 flex items-center justify-center font-black text-sm text-brand-400">
                      {p.name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-extrabold text-sm text-gray-100">{p.name}</div>
                      <div className="text-[11px] text-gray-400">{p.category}</div>
                    </div>
                  </div>
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full flex items-center space-x-1 ${
                    isConnected ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-gray-800 text-gray-400"
                  }`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${isConnected ? "bg-emerald-400 animate-pulse" : "bg-gray-500"}`}></span>
                    <span>{isConnected ? "Connected" : "Disconnected"}</span>
                  </span>
                </div>

                {/* Account Details */}
                <div className="mt-4 p-3 rounded-xl bg-gray-950/70 border border-gray-800/60 text-xs space-y-1.5">
                  <div className="flex items-center justify-between text-gray-300">
                    <span className="text-gray-400">Account:</span>
                    <span className="font-bold">{p.account}</span>
                  </div>
                  <div className="flex items-center justify-between text-gray-300">
                    <span className="text-gray-400">Token Status:</span>
                    <span className="text-brand-300 font-mono text-[10px]">{p.token_status}</span>
                  </div>
                  <div className="flex items-center justify-between text-gray-300">
                    <span className="text-gray-400">Standard:</span>
                    <span className="text-gray-400 text-[10px]">{p.api_standard}</span>
                  </div>
                </div>

                {/* Capabilities */}
                <div className="mt-4">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">
                    Supported Capabilities ({p.capabilities.length})
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {p.capabilities.map((cap) => (
                      <span
                        key={cap}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-800/60 text-gray-300 border border-gray-700/50"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-5 pt-3 border-t border-gray-800 flex items-center justify-between">
                <span className="text-[10px] text-gray-400">Synced: {p.last_synced}</span>
                <button
                  onClick={() => toggleConnection(p.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    isConnected
                      ? "bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20"
                      : "bg-brand-600 hover:bg-brand-500 text-white"
                  }`}
                >
                  {isConnected ? "Disconnect" : "Connect Account"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
