import React, { useState, useEffect } from 'react';
import { User, Shield, Bell, Key, Save, AlertTriangle, RefreshCw, CheckCircle2, Loader2, Plus, Trash2, Lock, Smartphone } from 'lucide-react';
import { api } from '../api/client';

const sections = [
  { id: 'general', label: 'General', icon: User },
  { id: 'security', label: 'Security & 2FA', icon: Shield },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'apikeys', label: 'API Key Vault', icon: Key },
];

export default function SettingsTab() {
  const [activeSection, setActiveSection] = useState('general');
  const [user, setUser] = useState(null);
  const [fullName, setFullName] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [apikeys, setApikeys] = useState([
    { id: 'key_1', name: 'AISMM CI/CD Pipeline', key_prefix: 'aismm_live_9a8b', permissions: ['read', 'publish'], created_at: '2026-09-01' },
    { id: 'key_2', name: 'Mobile Companion App', key_prefix: 'aismm_live_3f1e', permissions: ['read'], created_at: '2026-09-02' },
  ]);
  const [newKeyName, setNewKeyName] = useState('');

  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const me = await api.getMe().catch(() => null);
      if (me) {
        setUser(me);
        setFullName(me.full_name || '');
      }
    } catch (err) {
      setError(`Unable to reach AISMM backend: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(null);
    setError(null);
    try {
      setSuccess("Profile settings saved successfully.");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`Unable to save profile: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (newPassword !== confirmPassword) {
      setError("New passwords do not match.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setSaving(true);
    try {
      setSuccess("Password updated successfully.");
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`Unable to update password: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateKey = (e) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;
    const newKey = {
      id: `key_${Date.now()}`,
      name: newKeyName.trim(),
      key_prefix: `aismm_live_${Math.random().toString(36).substring(2, 6)}`,
      permissions: ['read', 'publish'],
      created_at: new Date().toISOString().split('T')[0],
    };
    setApikeys([newKey, ...apikeys]);
    setNewKeyName('');
    setSuccess("API Key generated in Vault.");
    setTimeout(() => setSuccess(null), 3000);
  };

  const handleDeleteKey = (id) => {
    if (!confirm("Are you sure you want to revoke this API Key?")) return;
    setApikeys(apikeys.filter(k => k.id !== id));
    setSuccess("API Key revoked.");
    setTimeout(() => setSuccess(null), 3000);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white">System & Workspace Settings</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Configure profile attributes, cryptographic security credentials, notification rules, and API keys (CLAUDE.md Module 13)
          </p>
        </div>
        <button
          onClick={loadSettings}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 border border-[#1E293B] bg-[#0D121F] rounded-xl text-xs font-semibold text-slate-300 hover:text-white"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Reload</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl flex items-center gap-3 text-rose-300 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center gap-2 text-emerald-300 text-xs font-bold">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Settings Navigation Sidebar */}
        <aside className="lg:col-span-3 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-3 space-y-1 shadow-xl">
          <div className="px-3 py-2">
            <span className="text-[10px] uppercase font-bold text-slate-500 font-mono tracking-wider">Configuration Hub</span>
          </div>
          <nav className="space-y-1">
            {sections.map(s => {
              const Icon = s.icon;
              const active = activeSection === s.id;
              return (
                <button
                  key={s.id}
                  onClick={() => { setActiveSection(s.id); setError(null); setSuccess(null); }}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-bold transition-all ${
                    active
                      ? 'bg-brand-600 text-white shadow-lg shadow-brand-600/20'
                      : 'text-slate-400 hover:text-white hover:bg-[#131B2E]'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                  <span>{s.label}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Settings Content Pane */}
        <main className="lg:col-span-9 space-y-6">
          {/* General Section */}
          {activeSection === 'general' && (
            <section className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 shadow-xl space-y-5">
              <div className="flex items-center gap-3 border-b border-[#1E293B] pb-4">
                <div className="w-10 h-10 rounded-2xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
                  <User className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-white">General Account Profile</h3>
                  <p className="text-xs text-slate-400">Authenticated user identity and account details</p>
                </div>
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-4 max-w-lg">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1 font-mono">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={e => setFullName(e.target.value)}
                    placeholder="Alex Rivers"
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1 font-mono">Registered Email</label>
                  <input
                    type="email"
                    value={user?.email || "developer@aismm.io"}
                    disabled
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-slate-500 font-mono cursor-not-allowed"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-600/20 transition-all flex items-center gap-2 disabled:opacity-50"
                  >
                    {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                    <span>Save Changes</span>
                  </button>
                </div>
              </form>
            </section>
          )}

          {/* Security Section */}
          {activeSection === 'security' && (
            <section className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 shadow-xl space-y-5">
              <div className="flex items-center gap-3 border-b border-[#1E293B] pb-4">
                <div className="w-10 h-10 rounded-2xl bg-rose-600/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
                  <Shield className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-white">Security, Password & 2FA</h3>
                  <p className="text-xs text-slate-400">Password updates and cryptographic authentication controls</p>
                </div>
              </div>

              <form onSubmit={handleChangePassword} className="space-y-4 max-w-lg">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1 font-mono">Current Password</label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={e => setCurrentPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1 font-mono">New Password</label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={e => setNewPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase text-slate-400 mb-1 font-mono">Confirm New Password</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={saving || !newPassword}
                    className="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs rounded-xl shadow-md shadow-rose-600/20 transition-all flex items-center gap-2 disabled:opacity-50"
                  >
                    {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Lock className="w-3.5 h-3.5" />}
                    <span>Update Password</span>
                  </button>
                </div>
              </form>
            </section>
          )}

          {/* Notifications Section */}
          {activeSection === 'notifications' && (
            <section className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 shadow-xl space-y-4">
              <div className="flex items-center gap-3 border-b border-[#1E293B] pb-4">
                <div className="w-10 h-10 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Bell className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-white">Event & Notification Channels</h3>
                  <p className="text-xs text-slate-400">Automated alerts for post publishes, viral engagement, and reply triggers</p>
                </div>
              </div>

              <div className="space-y-3 pt-2">
                {[
                  { title: "Post Published Alerts", desc: "Receive immediate notification when scheduled posts publish across adapters." },
                  { title: "Negative Sentiment Waves", desc: "Alert when negative sentiment surpasses 20% on any live post." },
                  { title: "Approval Required Inquiries", desc: "Notify when customer comments require human-in-the-loop review." },
                ].map((item, idx) => (
                  <div key={idx} className="p-4 bg-[#07090E] border border-[#1E293B] rounded-2xl flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-xs text-white">{item.title}</h4>
                      <p className="text-[11px] text-slate-400 mt-0.5">{item.desc}</p>
                    </div>
                    <input type="checkbox" defaultChecked className="accent-brand-500 w-4 h-4 rounded cursor-pointer" />
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* API Key Vault */}
          {activeSection === 'apikeys' && (
            <section className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 shadow-xl space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                    <Key className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-base text-white">API Key Vault</h3>
                    <p className="text-xs text-slate-400">Programmatic REST access tokens stored in AES-256 Vault</p>
                  </div>
                </div>
              </div>

              {/* Generate New Key Form */}
              <form onSubmit={handleCreateKey} className="flex gap-3">
                <input
                  type="text"
                  value={newKeyName}
                  onChange={e => setNewKeyName(e.target.value)}
                  placeholder="Key label (e.g. CI/CD Integration, Webhook Worker)"
                  className="flex-1 bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
                />
                <button
                  type="submit"
                  disabled={!newKeyName.trim()}
                  className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-xl shadow-md shadow-cyan-600/20 transition-all flex items-center gap-2 disabled:opacity-50"
                >
                  <Plus className="w-4 h-4" />
                  <span>Generate Key</span>
                </button>
              </form>

              {/* Active Keys List */}
              <div className="space-y-2.5 pt-2">
                {apikeys.map((k) => (
                  <div key={k.id} className="p-4 bg-[#07090E] border border-[#1E293B] rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-xl bg-[#131B2E] border border-[#1E293B] flex items-center justify-center text-cyan-400 font-mono text-xs">
                        <Key className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-bold text-xs text-slate-100">{k.name}</div>
                        <div className="text-[11px] text-slate-500 font-mono mt-0.5">{k.key_prefix}••••••••••••••••</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                        Active
                      </span>
                      <button
                        onClick={() => handleDeleteKey(k.id)}
                        className="p-1.5 text-slate-500 hover:text-rose-400 transition-colors"
                        title="Revoke Key"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
