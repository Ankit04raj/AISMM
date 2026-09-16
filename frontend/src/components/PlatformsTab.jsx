import React, { useState, useEffect } from 'react';
import {
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Zap,
  Plus,
  Link as LinkIcon,
  Key,
  X,
  User,
  Globe
} from 'lucide-react';
import { api } from '../api/client';

export default function PlatformsTab() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [platformList, setPlatformList] = useState([]);
  const [oauthStatus, setOauthStatus] = useState({});
  const [userAccounts, setUserAccounts] = useState([]);
  const [connectingPlatform, setConnectingPlatform] = useState(null);
  const [syncingAccountId, setSyncingAccountId] = useState(null);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('instagram');
  const [modalSubmitting, setModalSubmitting] = useState(false);
  const [modalError, setModalError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [platformsData, accountsData] = await Promise.all([
        api.listPlatforms(),
        api.getAccounts(),
      ]);
      setPlatformList((platformsData.platforms || []).filter(p => p !== 'twitter'));
      setOauthStatus(platformsData.oauth_status || {});
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

  const platformsMeta = {
    instagram: {
      name: "Instagram",
      standard: "Instagram Graph API v20.0",
      caps: ["post_image", "post_video", "post_carousel", "post_reel", "schedule_post", "get_insights", "reply_comment"],
      placeholder: "@username or https://instagram.com/username",
      portalUrl: "https://developers.facebook.com/apps",
      portalName: "Meta for Developers (Facebook Login for Business)",
      envVars: "INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET",
    },
    facebook: {
      name: "Facebook",
      standard: "Facebook Graph API v20.0",
      caps: ["post_text", "post_image", "post_video", "schedule_post", "get_insights", "reply_comment", "manage_webhooks"],
      placeholder: "Page Name or https://facebook.com/pagename",
      portalUrl: "https://developers.facebook.com/apps",
      portalName: "Meta for Developers",
      envVars: "FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET",
    },
    x: {
      name: "X (Twitter)",
      standard: "X API v2 (OAuth 2.0 PKCE)",
      caps: ["post_text", "post_image", "post_video", "get_post", "get_insights", "reply_comment"],
      placeholder: "@handle or https://x.com/handle",
      portalUrl: "https://developer.twitter.com/en/portal/dashboard",
      portalName: "X Developer Portal (Web App with PKCE)",
      envVars: "X_CLIENT_ID, X_CLIENT_SECRET",
    },
    linkedin: {
      name: "LinkedIn",
      standard: "LinkedIn REST & UGC API",
      caps: ["post_text", "post_image", "post_video", "post_carousel", "get_insights", "reply_comment"],
      placeholder: "username or https://linkedin.com/in/username",
      portalUrl: "https://www.linkedin.com/developers/apps",
      portalName: "LinkedIn Developer Portal",
      envVars: "LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET",
    },
    youtube: {
      name: "YouTube",
      standard: "YouTube Data API v3 & Analytics",
      caps: ["post_video", "delete_post", "get_analytics", "get_insights", "reply_comment"],
      placeholder: "Channel ID or https://youtube.com/@channel",
      portalUrl: "https://console.cloud.google.com/apis/credentials",
      portalName: "Google Cloud Console (OAuth Client ID, Web app)",
      envVars: "YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET",
    },
  };

  const openConnectModal = (pKey = 'instagram') => {
    setSelectedPlatform(pKey);
    setModalError(null);
    setShowModal(true);
  };

  const handleOAuthConnect = async (pKey) => {
    setConnectingPlatform(pKey);
    setError(null);
    setModalSubmitting(true);
    setModalError(null);
    try {
      const oauth = await api.initOAuth(pKey);
      sessionStorage.setItem('aismm_oauth_platform', pKey);
      if (oauth?.authorization_url) {
        window.location.assign(oauth.authorization_url);
      }
    } catch (err) {
      setModalError(`Connection unavailable: ${err.message}`);
      setError(`Connection unavailable: ${err.message}`);
    } finally {
      setConnectingPlatform(null);
      setModalSubmitting(false);
    }
  };

  const handleDisconnect = async (accountId) => {
    if (!confirm("Are you sure you want to disconnect this platform account?")) return;
    try {
      await api.disconnectAccount(accountId);
      setNotice("Account disconnected successfully.");
      setTimeout(() => setNotice(null), 4000);
      window.dispatchEvent(new CustomEvent('aismm:accounts-updated'));
      loadData();
    } catch (err) {
      alert(`Disconnection failed: ${err.message}`);
    }
  };

  const handleSync = async (accountId) => {
    setSyncingAccountId(accountId);
    try {
      const res = await api.syncAccount(accountId);
      setNotice(`Profile synced! Follower metrics & public data refreshed.`);
      setTimeout(() => setNotice(null), 4000);
      window.dispatchEvent(new CustomEvent('aismm:accounts-updated'));
      loadData();
    } catch (err) {
      alert(`Sync failed: ${err.message}`);
    } finally {
      setSyncingAccountId(null);
    }
  };

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
          <h3 className="text-base font-bold text-white mb-1">Platform Hub Notice</h3>
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

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Platform Connection Hub</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Connect real social accounts via OAuth 2.0, Handle (@username), or Profile URL with AES-256 vault encryption
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => openConnectModal('instagram')}
            className="px-4 py-2 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-brand-600/20"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Link Social Profile</span>
          </button>
          <button
            onClick={loadData}
            className="p-2 rounded-xl bg-[#0D121F] border border-[#1E293B] text-slate-400 hover:text-white transition-colors"
            title="Refresh Account Data"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {notice && (
        <div className="p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-2xl flex items-center gap-3 text-xs text-emerald-300 font-mono animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{notice}</span>
        </div>
      )}

      {/* Platform Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {platformList.map((pKey) => {
          const meta = platformsMeta[pKey] || { name: pKey.toUpperCase(), standard: "REST API", caps: ["post_text", "get_insights"] };
          const linkedAccount = userAccounts.find(a => a.platform.toLowerCase() === pKey.toLowerCase());
          const isConnected = !!linkedAccount;
          const isLiveOAuth = isConnected && (
            linkedAccount?.metadata?.connected_via === 'oauth' ||
            (linkedAccount?.access_token && !linkedAccount.access_token.includes('direct_'))
          );
          const isDirectDemo = isConnected && !isLiveOAuth;

          return (
            <div
              key={pKey}
              className={`bg-[#0D121F] border rounded-3xl p-6 shadow-xl flex flex-col justify-between transition-all space-y-4 ${
                isLiveOAuth
                  ? "border-emerald-500/40 hover:border-emerald-400"
                  : isDirectDemo
                  ? "border-amber-500/30 hover:border-amber-400/50"
                  : "border-[#1E293B] hover:border-brand-500/40"
              }`}
            >
              <div>
                {/* Card Top */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {linkedAccount?.profile_image_url ? (
                      <img
                        src={linkedAccount.profile_image_url}
                        alt={meta.name}
                        className="w-10 h-10 rounded-2xl object-cover border border-[#1E293B] shadow-md bg-[#07090E]"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-600 flex items-center justify-center font-extrabold text-sm text-white shadow-md">
                        {meta.name.charAt(0)}
                      </div>
                    )}
                    <div>
                      <h4 className="font-bold text-sm text-white flex items-center gap-1.5">
                        {meta.name}
                        {linkedAccount?.metadata?.is_verified && (
                          <span className="text-[10px] text-cyan-400 font-bold" title="Verified Profile">✓</span>
                        )}
                      </h4>
                      <p className="text-[11px] text-slate-400 font-mono">{meta.standard}</p>
                    </div>
                  </div>
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1.5 font-mono ${
                    isLiveOAuth
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : isDirectDemo
                      ? "bg-amber-500/10 text-amber-300 border border-amber-500/20"
                      : "bg-[#07090E] text-slate-400 border border-[#1E293B]"
                  }`}>
                    {isLiveOAuth && <ShieldCheck className="w-3 h-3 text-emerald-400" />}
                    {isDirectDemo && <User className="w-3 h-3 text-amber-400" />}
                    <span>{isLiveOAuth ? "OAuth 2.0 Live ✓" : isDirectDemo ? "Manual / Demo Mode" : "Available"}</span>
                  </span>
                </div>

                {/* Account Details */}
                <div className="mt-4 p-3.5 rounded-2xl bg-[#07090E] border border-[#1E293B] text-xs space-y-2.5 font-mono">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Handle / ID:</span>
                    <div className="flex items-center gap-1.5 truncate max-w-[180px]">
                      <span className="font-bold text-slate-200">
                        {linkedAccount ? `@${linkedAccount.username || linkedAccount.display_name}` : "Not Connected"}
                      </span>
                      {linkedAccount?.metadata?.profile_url && (
                        <a
                          href={linkedAccount.metadata.profile_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-cyan-400 hover:text-cyan-300 inline-flex items-center"
                          title="Open Real Profile Page"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
                  {linkedAccount?.display_name && linkedAccount.display_name !== linkedAccount.username && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Name:</span>
                      <span className="font-medium text-slate-300 truncate max-w-[170px]">
                        {linkedAccount.display_name}
                      </span>
                    </div>
                  )}
                  {linkedAccount?.metadata?.followers_count !== undefined && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Audience:</span>
                      <span className="font-bold text-cyan-400">
                        {Number(linkedAccount.metadata.followers_count).toLocaleString()} Followers
                      </span>
                    </div>
                  )}
                  {linkedAccount?.metadata?.following_count !== undefined && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Following:</span>
                      <span className="font-medium text-slate-300">
                        {Number(linkedAccount.metadata.following_count).toLocaleString()}
                      </span>
                    </div>
                  )}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Vault Privacy:</span>
                    <span className="text-brand-400 font-semibold">
                      {isConnected ? "AES-256 Vault Token" : "Encrypted Storage"}
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
              <div className="pt-4 border-t border-[#1E293B] flex items-center justify-between gap-2">
                <span className="text-[10px] text-slate-500 font-mono">
                  {isConnected ? "OAuth 2.0 Live Active" : "OAuth Handshake Required"}
                </span>
                <div className="flex items-center gap-2">
                  {isConnected ? (
                    <>
                      <button
                        onClick={() => handleSync(linkedAccount.id)}
                        disabled={syncingAccountId === linkedAccount.id}
                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#07090E] hover:bg-slate-800 text-slate-300 border border-[#1E293B] transition-all flex items-center gap-1.5"
                        title="Sync live public profile & metrics via API"
                      >
                        <RefreshCw className={`w-3 h-3 ${syncingAccountId === linkedAccount.id ? "animate-spin text-cyan-400" : ""}`} />
                        <span>{syncingAccountId === linkedAccount.id ? "Syncing..." : "Sync"}</span>
                      </button>
                      <button
                        onClick={() => handleDisconnect(linkedAccount.id)}
                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-all"
                      >
                        Disconnect
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleOAuthConnect(pKey)}
                      disabled={connectingPlatform === pKey}
                      className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white shadow-md shadow-brand-600/20 transition-all flex items-center gap-1.5"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>{connectingPlatform === pKey ? "Redirecting..." : "Connect via OAuth"}</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Connect Social Account Modal (Real OAuth Authentication Flow) */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-6 relative">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-5 right-5 p-2 rounded-xl bg-[#07090E] border border-[#1E293B] text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-brand-400" />
                <span>Authorize {platformsMeta[selectedPlatform]?.name || "Social"} Account</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Real OAuth 2.0 connection. Securely redirects to {platformsMeta[selectedPlatform]?.name} to verify identity and fetch live metrics.
              </p>
            </div>

            {modalError && (
              <div className="p-3.5 bg-rose-950/30 border border-rose-500/30 rounded-xl text-xs text-rose-300 font-mono">
                {modalError}
              </div>
            )}

            {/* Platform Selector Tabs */}
            <div className="flex flex-wrap gap-2 p-1.5 bg-[#07090E] rounded-2xl border border-[#1E293B]">
              {platformList.map((pKey) => (
                <button
                  key={pKey}
                  type="button"
                  onClick={() => setSelectedPlatform(pKey)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    selectedPlatform === pKey
                      ? "bg-brand-600 text-white shadow-md"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {platformsMeta[pKey]?.name || pKey}
                </button>
              ))}
            </div>

            <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] text-xs text-slate-300 space-y-3 font-mono">
              <p>
                Clicking Authorize initiates a secure OAuth 2.0 handshake with <strong>{platformsMeta[selectedPlatform]?.name}</strong> for:
              </p>
              <ul className="list-disc pl-5 space-y-1 text-slate-400 text-[11px]">
                <li>Real profile identity, handle, and avatar synchronization</li>
                <li>Live follower, audience, and engagement insights</li>
                <li>Authorized multi-platform publishing and comment replies</li>
              </ul>
              <div className="flex items-center gap-2 text-cyan-400 text-[11px] pt-1">
                <ShieldCheck className="w-4 h-4 flex-shrink-0" />
                <span>Protected by RFC 7636 PKCE & state nonces with AES-256 Vault token encryption.</span>
              </div>

              {oauthStatus[selectedPlatform] && !oauthStatus[selectedPlatform].configured && (
                <div className="p-3.5 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-300 text-[11px] space-y-2">
                  <div className="flex items-center gap-1.5 font-bold">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                    <span>Developer App Setup for Live {platformsMeta[selectedPlatform]?.name} API</span>
                  </div>
                  <p className="text-slate-300">
                    To connect your real {platformsMeta[selectedPlatform]?.name} account and fetch live follower analytics:
                  </p>
                  <div className="bg-[#07090E] p-2.5 rounded-lg border border-[#1E293B] space-y-1">
                    <p className="text-slate-400">
                      1. Register app at:{" "}
                      {platformsMeta[selectedPlatform]?.portalUrl && (
                        <a
                          href={platformsMeta[selectedPlatform].portalUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="text-cyan-300 underline font-semibold inline-flex items-center gap-1"
                        >
                          <span>{platformsMeta[selectedPlatform].portalName || "Developer Portal"}</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </p>
                    <p className="text-slate-400">
                      2. Add Callback URL: <code className="text-cyan-300 font-bold">{window.location.origin}/oauth/callback</code>
                    </p>
                    <p className="text-slate-400">
                      3. Set in <code className="text-cyan-300">.env</code>: <span className="text-emerald-400 font-mono text-[10px]">{platformsMeta[selectedPlatform]?.envVars}</span>
                    </p>
                  </div>
                </div>
              )}

              {oauthStatus[selectedPlatform]?.configured && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-300 text-[11px] flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  <span>Production OAuth App Ready ({oauthStatus[selectedPlatform].client_id_preview})</span>
                </div>
              )}
            </div>

            <div className="pt-2 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleOAuthConnect(selectedPlatform)}
                disabled={modalSubmitting || connectingPlatform === selectedPlatform}
                className="px-5 py-2.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-brand-600/20 flex items-center gap-2"
              >
                {modalSubmitting ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Connecting...</span>
                  </>
                ) : (
                  <span>Authorize via OAuth 2.0</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
