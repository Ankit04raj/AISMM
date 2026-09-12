import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import {
  User,
  Shield,
  Bell,
  Key,
  CheckCircle2,
  Lock,
  Globe,
  Clock,
  Moon,
  RefreshCw,
  Save
} from 'lucide-react';
import { api, clearAuthSession } from '../api/client';

export default function SettingsTab({ onUser }) {
  const [user, setUser] = useState(null);
  const [name, setName] = useState('Ankit Raj');
  const [email, setEmail] = useState('ankit@example.com');
  const [timezoneVal, setTimezoneVal] = useState('Asia/Kolkata (GMT+5:30)');
  const [language, setLanguage] = useState('English');
  const [theme, setTheme] = useState('Dark');

  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [setup, setSetup] = useState(null);
  const [code, setCode] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [password, setPassword] = useState('');

  const navigate = useNavigate();
  const location = useLocation();
  const section = location.pathname.split('/')[3] || 'general';

  const load = () => {
    api.getMe()
      .then(me => {
        setUser(me);
        setName(me.full_name || 'Ankit Raj');
        setEmail(me.email || 'ankit@example.com');
      })
      .catch(err => setError(err.message));
  };

  useEffect(() => {
    load();
  }, []);

  async function action(fn) {
    setBusy(true);
    setError('');
    setMessage('');
    try {
      await fn();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    action(async () => {
      const me = await api.updateProfile(name);
      setUser(me);
      onUser?.(me);
      setMessage('Profile settings saved successfully.');
      setTimeout(() => setMessage(''), 4000);
    });
  };

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white font-mono">13 Settings & Configuration</h2>
        <p className="text-xs text-slate-400 mt-0.5 font-mono">
          Manage workspace profile, security credentials, and global system configurations
        </p>
      </div>

      {/* Subtab Navigation */}
      <div className="flex items-center gap-2 border-b border-[#1E293B] pb-3">
        {[
          { id: 'general', label: 'General', icon: User },
          { id: 'security', label: 'Security', icon: Shield },
          { id: 'notifications', label: 'Notifications', icon: Bell },
          { id: 'apikeys', label: 'API', icon: Key },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = section === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => navigate(`/app/settings/${tab.id}`)}
              className={`px-4 py-2 rounded-xl text-xs font-bold font-mono transition-all flex items-center gap-2 ${
                isActive
                  ? "bg-brand-600 text-white shadow-lg shadow-brand-600/20"
                  : "bg-[#0D121F] border border-[#1E293B] text-slate-400 hover:text-white"
              }`}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {error && <div role="alert" className="error">{error}</div>}
      {message && <div role="status" className="notice font-mono text-xs">{message}</div>}

      {/* General Settings Panel */}
      {section === 'general' && (
        <div className="max-w-2xl p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-6">
          <div className="border-b border-[#1E293B] pb-4">
            <h3 className="text-sm font-bold text-white font-mono">Profile Settings</h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">Customize your personal identity and workspace defaults</p>
          </div>

          <form onSubmit={handleSaveProfile} className="space-y-4 font-mono text-xs">
            <div>
              <label className="block font-bold text-slate-300 mb-1.5">Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-white focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-300 mb-1.5">Email</label>
              <input
                type="email"
                readOnly
                value={email}
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-slate-400 focus:outline-none cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-300 mb-1.5">Timezone</label>
              <select
                value={timezoneVal}
                onChange={(e) => setTimezoneVal(e.target.value)}
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-white focus:border-brand-500 focus:outline-none"
              >
                <option value="Asia/Kolkata (GMT+5:30)">Asia/Kolkata (GMT+5:30)</option>
                <option value="America/New_York (EST)">America/New_York (EST)</option>
                <option value="America/Los_Angeles (PST)">America/Los_Angeles (PST)</option>
                <option value="Europe/London (GMT)">Europe/London (GMT)</option>
                <option value="Asia/Tokyo (JST)">Asia/Tokyo (JST)</option>
              </select>
            </div>

            <div>
              <label className="block font-bold text-slate-300 mb-1.5">Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-white focus:border-brand-500 focus:outline-none"
              >
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="German">German</option>
                <option value="Japanese">Japanese</option>
              </select>
            </div>

            <div>
              <label className="block font-bold text-slate-300 mb-1.5">Theme</label>
              <select
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2.5 text-white focus:border-brand-500 focus:outline-none"
              >
                <option value="Dark">Dark (Cyber-Neon & Obsidian)</option>
                <option value="System">System Default</option>
              </select>
            </div>

            <div className="pt-3">
              <button
                type="submit"
                disabled={busy}
                className="px-6 py-2.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white font-bold rounded-xl shadow-md shadow-brand-600/20 flex items-center gap-2"
              >
                {busy ? <RefreshCw className="animate-spin" size={14} /> : <Save size={14} />}
                <span>Save Changes</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Security Settings Panel */}
      {section === 'security' && (
        <div className="grid xl:grid-cols-2 gap-6">
          <section className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-5">
            <h3 className="text-base font-bold text-white font-mono">Two-Factor Authentication (TOTP)</h3>
            <p className="text-slate-400 text-xs font-mono">
              RFC 6238 compliant authenticator protection. Replay guarded with atomic time-step locking.
            </p>
            <p className="notice font-mono text-xs">
              {user?.two_factor_enabled ? 'Enabled — an authenticator code is required at sign-in.' : 'Not enabled — protect your account with an authenticator app.'}
            </p>

            {!setup && !user?.two_factor_enabled && (
              <button
                className="px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl text-xs font-mono"
                disabled={busy}
                onClick={() => action(async () => setSetup(await api.setup2fa()))}
              >
                Set up Authenticator
              </button>
            )}

            {setup && (
              <div className="space-y-4">
                <div className="bg-white rounded-2xl p-4 w-fit shadow-md">
                  <QRCodeSVG value={setup.otpauth_url} size={160} title="Scan with your authenticator app" />
                </div>
                <code className="block break-all text-xs font-mono p-3 rounded-xl bg-[#07090E] border border-[#1E293B] text-cyan-400">
                  {setup.secret}
                </code>
              </div>
            )}

            {(setup || user?.two_factor_enabled) && (
              <form
                className="space-y-4 font-mono text-xs"
                onSubmit={(e) => {
                  e.preventDefault();
                  action(async () => {
                    if (user?.two_factor_enabled) await api.disable2fa(code);
                    else await api.enable2fa(code);
                    setCode('');
                    setSetup(null);
                    await load();
                    setMessage('Two-factor settings updated.');
                  });
                }}
              >
                <label className="block">
                  <span className="text-slate-300 font-bold block mb-1">6-Digit Code</span>
                  <input
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2 text-white font-mono"
                    inputMode="numeric"
                    required
                    pattern="[0-9]{6}"
                    placeholder="000000"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                  />
                </label>
                <button className="px-5 py-2.5 bg-brand-600 text-white rounded-xl font-bold" disabled={busy}>
                  {user?.two_factor_enabled ? 'Disable 2FA' : 'Verify & Enable 2FA'}
                </button>
              </form>
            )}
          </section>

          <form
            className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-4 font-mono text-xs"
            onSubmit={(e) => {
              e.preventDefault();
              action(async () => {
                await api.changePassword({ current_password: currentPassword, password });
                clearAuthSession();
                window.dispatchEvent(new Event('aismm:session-expired'));
              });
            }}
          >
            <h3 className="text-base font-bold text-white font-mono">Change Password</h3>
            <p className="text-slate-400">Changing your password invalidates all active sessions across devices.</p>

            <div>
              <label className="block text-slate-300 font-bold mb-1">Current Password</label>
              <input
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2 text-white"
                type="password"
                required
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-slate-300 font-bold mb-1">New Password</label>
              <input
                className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl px-4 py-2 text-white"
                type="password"
                minLength={8}
                maxLength={72}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button className="px-5 py-2.5 bg-brand-600 text-white rounded-xl font-bold" disabled={busy}>
              Change Password & Sign Out
            </button>
          </form>
        </div>
      )}

      {['notifications', 'apikeys'].includes(section) && (
        <div className="max-w-2xl p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] text-xs font-mono space-y-2">
          <h3 className="text-sm font-bold text-white">
            {section === 'apikeys' ? 'API Key Management' : 'Notification Preferences'}
          </h3>
          <p className="text-slate-400">
            {section === 'apikeys'
              ? 'Workspace API tokens are secured with AES-256 Vault keys and scoped per authorized operator.'
              : 'Email notifications and security alerts are configured via your verified account address.'}
          </p>
        </div>
      )}
    </div>
  );
}
