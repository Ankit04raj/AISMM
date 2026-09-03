import React, { useState, useEffect } from 'react';
import {
  Share2,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  RefreshCw,
  ExternalLink,
  Layers,
  Zap,
  AlertTriangle,
  Plus,
  Key,
  Lock
} from 'lucide-react';
import { api } from '../api/client';

export default function PlatformsTab() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [platformList, setPlatformList] = useState([]);
  const [userAccounts, setUserAccounts] = useState([]);
  const [connectingPlatform, setConnectingPlatform] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [platformsData, accountsData] = await Promise.all([
        api.listPlatforms(),
        api.getAccounts().catch(() => ({ accounts: [], total: 0 })),
      ]);
      setPlatformList(platformsData.platforms || ["instagram", "facebook", "x", "linkedin", "youtube"]);
      setUserAccounts(accountsData.accounts || []);
    } catch (err) {
      console.error("Failed loading platforms data:", err);
      setError("Unable to reach AISMM backend. Please verify your connection.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
        <RefreshCw className="w-8 h-8 text-brand-400 animate-spin" />
        <p className="text-slate-400 text-xs font-mono">Querying platform adapters & capability registries...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-rose-950/20 border border-rose-500/30 rounded-3xl flex flex-col items-center justify-center text-center gap-4 my-8 animate-fadeIn">
        <AlertTriangle className="w-8 h-8 text-rose-400" />
        <div>
          <h3 className="text-base font-bold text-white mb-1">Platform Hub Offline</h3>
          <p className="text-xs text-slate-400 max-w-md">{error}</p>
        </div>
        <button
          onClick={loadData}
          className="px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-brand-600/20"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry</span>
        </button>
      </div>
    );
  }

  const platformsMeta = {
    instagram: { name: "Instagram", standard: "Instagram Graph API v19.0", caps: ["post_image", "post_video", "post_carousel", "post_reel", "schedule_post", "get_insights", "reply_comment"] },
    facebook: { name: "Facebook", standard: "Facebook Graph API v19.0", caps: ["post_text", "post_image", "post_video", "schedule_post", "get_insights", "reply_comment", "manage_webhooks"] },
    x: { name: "X (Twitter)", standard: "X API v2 (OAuth 2.0 PKCE)", caps: ["post_text", "post_image", "post_video", "get_post", "get_insights", "reply_comment"] },
    linkedin: { name: "LinkedIn", standard: "LinkedIn REST & UGC API", caps: ["post_text", "post_image", "post_video", "post_carousel", "get_insights", "reply_comment"] },
    youtube: { name: "YouTube", standard: "YouTube Data API v3 & Analytics", caps: ["post_video", "delete_post", "get_analytics", "get_insights", "reply_comment"] },
  };

  const handleConnect = async (pKey) => {
    setConnectingPlatform(pKey);
    try {
      const oauth = await api.fetchApi("/auth/oauth/init", {
        method: "POST",
        body: JSON.stringify({ platform: pKey, redirect_uri: window.location.origin }),
      });
      if (oauth && oauth.authorization_url) {
        window.open(oauth.authorization_url, "_blank");
      }
    } catch (err) {
      alert(`OAuth initialization failed: ${err.message}`);
    } finally {
      setConnectingPlatform(null);
    }
  };

  const handleDisconnect = async (accountId) => {
    if (!confirm("Are you sure you want to disconnect this platform account?")) return;
    try {
      await api.disconnectAccount(accountId);
      loadData();
    } catch (err) {
      alert(`Disconnection failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Platform Connection Hub</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Manage authenticated platform adapters, OAuth tokens, and dynamic capability contracts (CLAUDE.md Section 44)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono">
            {platformList.length} Adapters Registered
          </span>
          <button
            onClick={loadData}
            className="p-2 rounded-xl bg-[#0D121F] border border-[#1E293B] text-slate-400 hover:text-white transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Platform Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {platformList.map((pKey) => {
          const meta = platformsMeta[pKey] || { name: pKey.toUpperCase(), standard: "REST API", caps: ["post_text", "get_insights"] };
          const linkedAccount = userAccounts.find(a => a.platform.toLowerCase() === pKey.toLowerCase());
          const isConnected = !!linkedAccount;

          return (
            <div
              key={pKey}
              className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl flex flex-col justify-between hover:border-brand-500/40 transition-all space-y-4"
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-600 flex items-center justify-center font-extrabold text-sm text-white shadow-md">
                      {meta.name.charAt(0)}
                    </div>
                    <div>
                      <h4 className="font-bold text-sm text-white">{meta.name}</h4>
                      <p className="text-[11px] text-slate-400 font-mono">{meta.standard}</p>
                    </div>
                  </div>
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1.5 font-mono ${
                    isConnected
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "bg-[#07090E] text-slate-400 border border-[#1E293B]"
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
                    <span>{isConnected ? "Connected" : "Standby"}</span>
                  </span>
                </div>

                {/* Account Details */}
                <div className="mt-4 p-3.5 rounded-2xl bg-[#07090E] border border-[#1E293B] text-xs space-y-2 font-mono">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Account:</span>
                    <span className="font-bold text-slate-200">
                      {linkedAccount ? `@${linkedAccount.username || linkedAccount.display_name}` : "Not Connected"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Security Vault:</span>
                    <span className="text-brand-400 font-semibold">
                      {isConnected ? "AES-256 Encrypted" : "Awaiting Token"}
                    </span>
                  </div>
                </div>

                {/* Capabilities */}
                <div className="mt-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2 font-mono">
                    Dynamic Capabilities ({meta.caps.length})
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {meta.caps.map((cap) => (
                      <span
                        key={cap}
                        className="text-[10px] font-mono px-2.5 py-0.5 rounded-lg bg-[#07090E] text-slate-300 border border-[#1E293B]"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="pt-4 border-t border-[#1E293B] flex items-center justify-between">
                <span className="text-[10px] text-slate-500 font-mono">
                  {isConnected ? "Sync Active" : "OAuth Ready"}
                </span>
                <button
                  onClick={() => isConnected ? handleDisconnect(linkedAccount.id) : handleConnect(pKey)}
                  disabled={connectingPlatform === pKey}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    isConnected
                      ? "bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20"
                      : "bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white shadow-md shadow-brand-600/20"
                  }`}
                >
                  {connectingPlatform === pKey ? "Connecting..." : isConnected ? "Disconnect" : "Connect OAuth"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
