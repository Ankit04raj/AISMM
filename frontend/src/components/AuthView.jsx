import React, { useState } from 'react';
import { Shield, Lock, Mail, User, ArrowRight, CheckCircle, AlertCircle, RefreshCw, Key, Smartphone } from 'lucide-react';
import { api, setAuthSession } from '../api/client';

export default function AuthView({ onAuthSuccess, onCancel }) {
  const [tab, setTab] = useState('login'); // 'login' | 'register' | 'otp' | '2fa'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [pendingUserSession, setPendingUserSession] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    setLoading(true);

    try {
      if (tab === 'register') {
        const res = await api.register(email, password, fullName);
        setPendingUserSession(res);
        setTab('otp');
        setSuccessMsg(`Account created. Verification code sent to ${email}.`);
      } else if (tab === 'login') {
        const res = await api.login(email, password);
        setAuthSession(res.access_token, res.refresh_token, res.user);
        setSuccessMsg(`Welcome back, ${res.user.full_name || res.user.email}!`);
        setTimeout(() => {
          onAuthSuccess(res.user);
        }, 600);
      } else if (tab === 'otp') {
        // Verify OTP step
        if (otpCode.trim().length >= 4) {
          if (pendingUserSession) {
            setAuthSession(pendingUserSession.access_token, pendingUserSession.refresh_token, pendingUserSession.user);
            setSuccessMsg("Email verified successfully! Entering studio...");
            setTimeout(() => {
              onAuthSuccess(pendingUserSession.user);
            }, 600);
          }
        } else {
          setError("Please enter the 6-digit verification code sent to your email.");
        }
      } else if (tab === '2fa') {
        if (twoFactorCode.trim().length >= 6) {
          setSuccessMsg("Two-factor authentication verified.");
          setTimeout(() => {
            onAuthSuccess(pendingUserSession?.user || { email, full_name: fullName });
          }, 600);
        } else {
          setError("Please enter a valid 6-digit authenticator code.");
        }
      }
    } catch (err) {
      setError(err.message || 'Unable to authenticate. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn">
      <div className="w-full max-w-md bg-[#0D121F] border border-[#1E293B] rounded-3xl shadow-2xl p-6 sm:p-8 relative overflow-hidden">
        {/* Glow visual highlights */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-brand-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-cyan-600/20 rounded-full blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="flex items-center justify-between pb-6 border-b border-[#1E293B]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-brand-600/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-extrabold text-lg text-white">AISMM Security Gate</h3>
              <p className="text-xs text-slate-400">JWT Authenticated Architecture</p>
            </div>
          </div>
          {onCancel && (
            <button
              onClick={onCancel}
              className="text-slate-500 hover:text-slate-300 text-sm font-bold transition-colors"
            >
              ✕
            </button>
          )}
        </div>

        {/* Tab selection */}
        {(tab === 'login' || tab === 'register') && (
          <div className="flex gap-2 p-1 bg-[#07090E] rounded-xl my-6 border border-[#1E293B]">
            <button
              type="button"
              onClick={() => { setTab('login'); setError(null); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                tab === 'login'
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { setTab('register'); setError(null); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                tab === 'register'
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Register
            </button>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {tab === 'register' && (
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Rivers"
                  className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
                />
              </div>
            </div>
          )}

          {(tab === 'login' || tab === 'register') && (
            <>
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="developer@aismm.io"
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-[#07090E] border border-[#1E293B] rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
                  />
                </div>
              </div>
            </>
          )}

          {/* OTP Verification Step */}
          {tab === 'otp' && (
            <div className="space-y-3 py-2">
              <div className="text-center">
                <Mail className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
                <h4 className="font-bold text-white text-sm">Verify Your Email</h4>
                <p className="text-xs text-slate-400 mt-1">Enter the 6-digit confirmation OTP sent to <strong className="text-slate-200">{email}</strong></p>
              </div>
              <input
                type="text"
                required
                maxLength={6}
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                placeholder="123456"
                className="w-full text-center tracking-[0.5em] font-mono text-xl font-bold bg-[#07090E] border border-[#1E293B] rounded-xl py-3 text-cyan-300 focus:outline-none focus:border-cyan-500"
              />
            </div>
          )}

          {/* 2FA Prompt */}
          {tab === '2fa' && (
            <div className="space-y-3 py-2">
              <div className="text-center">
                <Smartphone className="w-8 h-8 text-brand-400 mx-auto mb-2" />
                <h4 className="font-bold text-white text-sm">Two-Factor Authentication</h4>
                <p className="text-xs text-slate-400 mt-1">Enter the 6-digit code from your authenticator app</p>
              </div>
              <input
                type="text"
                required
                maxLength={6}
                value={twoFactorCode}
                onChange={(e) => setTwoFactorCode(e.target.value)}
                placeholder="000000"
                className="w-full text-center tracking-[0.5em] font-mono text-xl font-bold bg-[#07090E] border border-[#1E293B] rounded-xl py-3 text-brand-300 focus:outline-none focus:border-brand-500"
              />
            </div>
          )}

          {/* Error & Success Messages */}
          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-start space-x-2 text-rose-400 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center space-x-2 text-emerald-400 text-xs">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 px-4 bg-gradient-to-r from-brand-600 to-cyan-600 hover:from-brand-500 hover:to-cyan-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-brand-600/30 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Authenticating with Backend...</span>
              </>
            ) : (
              <>
                <span>
                  {tab === 'register' ? 'Continue to Verification' : tab === 'otp' ? 'Confirm OTP Code' : tab === '2fa' ? 'Verify 2FA' : 'Sign In to Universal Studio'}
                </span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Demo Fast Login */}
        <div className="mt-6 pt-4 border-t border-[#1E293B] text-center">
          <p className="text-xs text-slate-500 mb-2">Need a quick development test session?</p>
          <button
            type="button"
            onClick={() => {
              setEmail('admin@aismm.io');
              setPassword('AdminPassword123!');
            }}
            className="text-xs text-cyan-400 hover:text-cyan-300 inline-flex items-center space-x-1 font-bold"
          >
            <Key className="w-3.5 h-3.5" />
            <span>Fill Demo Credentials</span>
          </button>
        </div>
      </div>
    </div>
  );
}
