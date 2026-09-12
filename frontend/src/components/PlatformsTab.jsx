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
  const [userAccounts, setUserAccounts] = useState([]);
  const [connectingPlatform, setConnectingPlatform] = useState(null);
  const [syncingAccountId, setSyncingAccountId] = useState(null);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('instagram');
  const [connectMethod, setConnectMethod] = useState('direct'); // 'direct' | 'oauth' | 'token'
  const [identifierInput, setIdentifierInput] = useState('');
  const [displayNameInput, setDisplayNameInput] = useState('');
  const [tokenInput, setTokenInput] = useState('');
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
    instagram: { name: "Instagram", standard: "Instagram Graph API v20.0", caps: ["post_image", "post_video", "post_carousel", "post_reel", "schedule_post", "get_insights", "reply_comment"], placeholder: "@username or https://instagram.com/username" },
    facebook: { name: "Facebook", standard: "Facebook Graph API v20.0", caps: ["post_text", "post_image", "post_video", "schedule_post", "get_insights", "reply_comment", "manage_webhooks"], placeholder: "Page Name or https://facebook.com/pagename" },
    x: { name: "X (Twitter)", standard: "X API v2 (OAuth 2.0 PKCE)", caps: ["post_text", "post_image", "post_video", "get_post", "get_insights", "reply_comment"], placeholder: "@handle or https://x.com/handle" },
    linkedin: { name: "LinkedIn", standard: "LinkedIn REST & UGC API", caps: ["post_text", "post_image", "post_video", "post_carousel", "get_insights", "reply_comment"], placeholder: "username or https://linkedin.com/in/username" },
    youtube: { name: "YouTube", standard: "YouTube Data API v3 & Analytics", caps: ["post_video", "delete_post", "get_analytics", "get_insights", "reply_comment"], placeholder: "Channel ID or https://youtube.com/@channel" },
  };

  const openConnectModal = (pKey = 'instagram') => {
    setSelectedPlatform(pKey);
    setIdentifierInput('');
    setDisplayNameInput('');
    setTokenInput('');
    setModalError(null);
    setConnectMethod('direct');
    setShowModal(true);
  };

  const handleOAuthConnect = async (pKey) => {
    setConnectingPlatform(pKey);
    setError(null);
    try {
      const oauth = await api.initOAuth(pKey);
      sessionStorage.setItem('aismm_oauth_platform', pKey);
      if (oauth?.authorization_url) {
        window.location.assign(oauth.authorization_url);
      }
    } catch (err) {
      setError(`Connection unavailable: ${err.message}`);
    } finally {
      setConnectingPlatform(null);
    }
  };

  const handleDirectSubmit = async (e) => {
    e.preventDefault();
    if (!identifierInput.trim()) {
      setModalError("Please enter your Username, Handle, or Profile URL.");
      return;
    }

    setModalSubmitting(true);
    setModalError(null);

    try {
      if (connectMethod === 'oauth') {
        await handleOAuthConnect(selectedPlatform);
        setShowModal(false);
        return;
      }

      await api.directConnectAccount({
        platform: selectedPlatform,
        identifier: identifierInput.trim(),
        display_name: displayNameInput.trim() || undefined,
        access_token: tokenInput.trim() || undefined,
      });

      setShowModal(false);
      setNotice(`Successfully connected ${platformsMeta[selectedPlatform]?.name || selectedPlatform}! Vault credentials encrypted.`);
      setTimeout(() => setNotice(null), 5000);
      loadData();
    } catch (err) {
      setModalError(err.message || "Failed to link social account.");
    } finally {
      setModalSubmitting(false);
    }
  };

  const handleDisconnect = async (accountId) => {
    if (!confirm("Are you sure you want to disconnect this platform account?")) return;
    try {
      await api.disconnectAccount(accountId);
      setNotice("Account disconnected successfully.");
      setTimeout(() => setNotice(null), 4000);
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

          return (
            <div
              key={pKey}
              className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl flex flex-col justify-between hover:border-brand-500/40 transition-all space-y-4"
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
                    isConnected
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "bg-[#07090E] text-slate-400 border border-[#1E293B]"
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
                    <span>{isConnected ? "Connected" : "Available"}</span>
                  </span>
                </div>

                {/* Account Details */}
                <div className="mt-4 p-3.5 rounded-2xl bg-[#07090E] border border-[#1E293B] text-xs space-y-2 font-mono">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Handle / ID:</span>
                    <span className="font-bold text-slate-200 truncate max-w-[170px]">
                      {linkedAccount ? `@${linkedAccount.username || linkedAccount.display_name}` : "Not Connected"}
                    </span>
                  </div>
                  {linkedAccount?.metadata?.followers_count !== undefined && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Audience:</span>
                      <span className="font-bold text-cyan-400">
                        {Number(linkedAccount.metadata.followers_count).toLocaleString()} Followers
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
                  {isConnected ? "Live Sync Active" : "Direct / OAuth"}
                </span>
                <div className="flex items-center gap-2">
                  {isConnected ? (
                    <>
                      <button
                        onClick={() => handleSync(linkedAccount.id)}
                        disabled={syncingAccountId === linkedAccount.id}
                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#07090E] hover:bg-slate-800 text-slate-300 border border-[#1E293B] transition-all flex items-center gap-1.5"
                        title="Sync live public profile & metrics"
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
                      onClick={() => openConnectModal(pKey)}
                      disabled={connectingPlatform === pKey}
                      className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white shadow-md shadow-brand-600/20 transition-all flex items-center gap-1.5"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Link Profile</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Connect Social Account Modal */}
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
                <LinkIcon className="w-5 h-5 text-brand-400" />
                <span>Link {platformsMeta[selectedPlatform]?.name || "Social"} Account</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Connect your account via Handle, Profile URL, or OAuth 2.0 Authorization.
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

            {/* Connection Method Tabs */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <button
                type="button"
                onClick={() => setConnectMethod('direct')}
                className={`p-2.5 rounded-xl border text-center font-bold transition-all ${
                  connectMethod === 'direct'
                    ? "bg-brand-600/20 border-brand-500 text-white"
                    : "bg-[#07090E] border-[#1E293B] text-slate-400 hover:text-slate-200"
                }`}
              >
                @Handle / Profile URL
              </button>
              <button
                type="button"
                onClick={() => setConnectMethod('oauth')}
                className={`p-2.5 rounded-xl border text-center font-bold transition-all ${
                  connectMethod === 'oauth'
                    ? "bg-brand-600/20 border-brand-500 text-white"
                    : "bg-[#07090E] border-[#1E293B] text-slate-400 hover:text-slate-200"
                }`}
              >
                OAuth 2.0 Auth Flow
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleDirectSubmit} className="space-y-4">
              {connectMethod === 'direct' ? (
                <>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1.5">
                      Username (@handle) or Profile URL
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        required
                        value={identifierInput}
                        onChange={(e) => setIdentifierInput(e.target.value)}
                        placeholder={platformsMeta[selectedPlatform]?.placeholder || "@handle or https://..."}
                        className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-white placeholder:text-slate-600 focus:border-brand-500 focus:outline-none font-mono"
                      />
                    </div>
                    <p className="text-[11px] text-slate-500 mt-1 font-mono">
                      e.g. @{selectedPlatform}_creator or your direct profile link.
                    </p>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1.5">
                      Display Name (Optional)
                    </label>
                    <input
                      type="text"
                      value={displayNameInput}
                      onChange={(e) => setDisplayNameInput(e.target.value)}
                      placeholder="My Creator Brand"
                      className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-white placeholder:text-slate-600 focus:border-brand-500 focus:outline-none font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1.5">
                      Access Token / API Key (Optional)
                    </label>
                    <input
                      type="password"
                      value={tokenInput}
                      onChange={(e) => setTokenInput(e.target.value)}
                      placeholder="OAuth token or API key for publishing access"
                      className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-white placeholder:text-slate-600 focus:border-brand-500 focus:outline-none font-mono"
                    />
                    <span className="text-[10px] text-emerald-400/80 font-mono mt-1 block">
                      🔒 Protected with AES-256 Vault Encryption at rest.
                    </span>
                  </div>
                </>
              ) : (
                <div className="p-4 rounded-2xl bg-[#07090E] border border-[#1E293B] text-xs text-slate-300 space-y-3 font-mono">
                  <p>
                    You will be securely redirected to <strong>{platformsMeta[selectedPlatform]?.name}</strong> to authorize public profile, metrics, and publishing permissions.
                  </p>
                  <div className="flex items-center gap-2 text-cyan-400 text-[11px]">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Uses RFC 7636 PKCE & state nonces for anti-tamper security.</span>
                  </div>
                </div>
              )}

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalSubmitting}
                  className="px-5 py-2.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-brand-600/20 flex items-center gap-2"
                >
                  {modalSubmitting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Connecting...</span>
                    </>
                  ) : (
                    <span>{connectMethod === 'oauth' ? "Authorize via OAuth" : "Connect & Save"}</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
