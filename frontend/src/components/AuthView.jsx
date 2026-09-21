import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { X, ShieldCheck, ArrowRight, Loader2 } from 'lucide-react';
import { api, setAuthSession, getStoredUser } from '../api/client';

export default function AuthView({ onAuthSuccess, onCancel, initialMode = 'login' }) {
  const [mode, setMode] = useState(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [pending, setPending] = useState(getStoredUser());
  const [resendCooldown, setResendCooldown] = useState(0);

  async function finishLogin(res) {
    if (res.requires_2fa) {
      setMode('2fa');
      setCode('');
      return;
    }
    if (!res.access_token) throw new Error('Sign-in did not return a session. Please retry.');
    setAuthSession(res.access_token, res.refresh_token, res.user);
    setPending(res.user);
    if (!res.user.is_verified && !res.user.phone_verified) {
      setMode('verify');
      setCode('');
      setMessage('A 6-digit verification code has been sent to your email. Enter it below to activate your account.');
    } else {
      onAuthSuccess(res.user);
    }
  }

  async function submit(event) {
    if (event && event.preventDefault) event.preventDefault();
    setBusy(true);
    setError('');
    setMessage('');

    try {
      const cleanEmail = (email || '').trim().toLowerCase();
      const cleanPassword = password || '';

      // Validate email format if required for mode
      if (['login', 'register', 'forgot'].includes(mode)) {
        if (!cleanEmail) {
          throw new Error('Please enter your email address.');
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
          throw new Error('Please enter a valid email address (e.g. name@example.com).');
        }
      }

      if (mode === 'register') {
        if (!name.trim()) throw new Error('Please enter your full name.');
        if (!cleanPassword) throw new Error('Please enter a password.');
        if (cleanPassword.length < 8) throw new Error('Password must be at least 8 characters long.');
        if (!accepted) throw new Error('Please accept the Terms of Service and Privacy Policy to continue.');

        const res = await api.register(cleanEmail, cleanPassword, name.trim(), null, 'email');
        await finishLogin(res);
      } else if (mode === 'login') {
        if (!cleanPassword) throw new Error('Please enter your password.');
        try {
          const res = await api.login(cleanEmail, cleanPassword);
          await finishLogin(res);
        } catch (err) {
          if (err.status === 403 || err.message?.includes('Email verification required')) {
            // Unverified user tried to login - switch to verify mode
            setMode('verify');
            setCode('');
            setMessage('Your account is not verified yet. Please enter the 6-digit code sent to your email.');
            return;
          }
          throw err;
        }
      } else if (mode === '2fa') {
        if (!code.trim()) throw new Error('Please enter your 2FA authentication code.');
        await finishLogin(await api.login(cleanEmail, cleanPassword, code.trim()));
      } else if (mode === 'verify') {
        const cleanCode = code.trim();
        if (!cleanCode) throw new Error('Please enter the 6-digit verification code.');
        if (!/^[0-9]{6}$/.test(cleanCode)) throw new Error('Verification code must be exactly 6 digits.');

        await api.verifyEmail(cleanCode);
        const user = await api.getMe();
        setAuthSession(null, null, user);
        onAuthSuccess(user);
      } else if (mode === 'forgot') {
        const result = await api.forgotPassword(cleanEmail);
        setMessage(result.message || 'If an account exists, a reset code has been sent.');
        setMode('verify-reset-otp');
        setCode('');
      } else if (mode === 'verify-reset-otp') {
        const cleanCode = code.trim();
        if (!cleanCode) throw new Error('Please enter the 6-digit reset code.');
        if (!/^[0-9]{6}$/.test(cleanCode)) throw new Error('Reset code must be exactly 6 digits.');

        const result = await api.verifyPasswordResetOtp(cleanEmail, cleanCode);
        setResetToken(result.reset_token);
        setMessage(result.message || 'Code accepted. Please enter your new password.');
        setMode('new-password');
        setNewPassword('');
      } else if (mode === 'new-password') {
        if (!newPassword || newPassword.length < 8) {
          throw new Error('New password must be at least 8 characters long.');
        }
        const result = await api.resetPassword(resetToken, newPassword);
        setMessage(result.message || 'Password reset successfully. Sign in with your new password.');
        setMode('login');
        setPassword('');
        setCode('');
      }
    } catch (err) {
      setError(err.message || 'An unexpected error occurred. Please try again.');
    } finally {
      setBusy(false);
    }
  }

  async function resend() {
    setBusy(true);
    setError('');
    try {
      const cleanEmail = (email || pending?.email || '').trim().toLowerCase();
      const res = await api.resendEmailOtp(cleanEmail);
      setMessage(res.message || 'A new verification code has been sent. Check your inbox.');
      setResendCooldown(60);
      const timer = setInterval(() => {
        setResendCooldown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err) {
      setError(err.message || 'Failed to resend verification code.');
    } finally {
      setBusy(false);
    }
  }

  const title = {
    login: 'Welcome back.',
    register: 'Create your workspace.',
    '2fa': 'Two-Factor Authentication.',
    verify: 'Verify your email.',
    forgot: 'Reset your password.',
    'verify-reset-otp': 'Enter reset code.',
    'new-password': 'Create new password.',
  }[mode];

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md overflow-y-auto p-4 sm:p-8 flex items-start sm:items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="auth-title"
    >
      <section className="panel w-full max-w-md relative my-auto shadow-2xl">
        <button
          aria-label="Close sign in"
          onClick={onCancel}
          className="absolute top-3 right-3 p-2 text-slate-400 hover:text-white"
        >
          <X size={20} />
        </button>
        <div className="w-12 h-12 rounded-xl bg-brand-600/20 text-brand-300 flex items-center justify-center mb-6">
          <ShieldCheck />
        </div>
        <p className="text-cyan-300 text-xs tracking-widest font-semibold uppercase mb-2">AISMM Studio</p>
        <h1 id="auth-title" className="text-2xl font-bold mb-2">
          {title}
        </h1>
        <p className="text-slate-400 text-sm mb-6">
          {mode === 'verify'
            ? `Enter the 6-digit code sent to ${email || pending?.email || 'your email'}.`
            : mode === 'verify-reset-otp'
            ? `Enter the 6-digit password reset code sent to ${email}.`
            : mode === 'new-password'
            ? 'Choose a strong password with at least 8 characters.'
            : 'One workspace for your content, channels, and next move.'}
        </p>

        {error && (
          <div className="error mb-4" role="alert">
            {error}
          </div>
        )}

        {message && (
          <div className="notice mb-4" role="status">
            {message}
          </div>
        )}

        <form onSubmit={submit} noValidate className="space-y-4">
          {mode === 'register' && (
            <label className="block text-sm">
              Full name
              <input
                className="field mt-1"
                autoComplete="name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
              />
            </label>
          )}

          {['login', 'register', 'forgot'].includes(mode) && (
            <label className="block text-sm">
              Email
              <input
                className="field mt-1"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
              />
            </label>
          )}

          {['login', 'register'].includes(mode) && (
            <label className="block text-sm">
              Password
              <input
                className="field mt-1"
                type="password"
                autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
                minLength={8}
                maxLength={72}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
              />
            </label>
          )}

          {['2fa', 'verify', 'verify-reset-otp'].includes(mode) && (
            <label className="block text-sm">
              {mode === '2fa'
                ? 'Authenticator code / Recovery code'
                : '6-Digit Verification Code'}
              <input
                className="field mt-1 text-center font-mono tracking-widest text-lg"
                autoComplete="one-time-code"
                inputMode="numeric"
                pattern={mode === '2fa' ? '[0-9A-Za-z-]{6,19}' : '[0-9]{6}'}
                maxLength={mode === '2fa' ? 19 : 6}
                placeholder={mode === '2fa' ? 'Enter 6-digit or recovery code' : 'Enter 6-digit code'}
                required
                autoFocus
                value={code}
                onChange={(e) => setCode(e.target.value.trim())}
              />
            </label>
          )}

          {mode === 'new-password' && (
            <label className="block text-sm">
              New Password
              <input
                className="field mt-1"
                type="password"
                autoComplete="new-password"
                minLength={8}
                maxLength={72}
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="At least 8 characters"
              />
            </label>
          )}

          {mode === 'register' && (
            <label className="flex items-start gap-3 text-sm text-slate-300">
              <input
                className="mt-1 w-5 h-5 shrink-0 accent-brand-600 rounded cursor-pointer"
                type="checkbox"
                required
                checked={accepted}
                onChange={(e) => setAccepted(e.target.checked)}
              />
              <span>
                I agree to the{' '}
                <Link className="underline text-brand-300 hover:text-brand-200" to="/terms" target="_blank">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link className="underline text-brand-300 hover:text-brand-200" to="/privacy" target="_blank">
                  Privacy Policy
                </Link>
                .
              </span>
            </label>
          )}

          <button disabled={busy} className="btn w-full" type="submit">
            {busy ? <Loader2 className="animate-spin" size={18} /> : <ArrowRight size={18} />}
            {mode === 'register'
              ? (busy ? 'Creating workspace...' : 'Create account')
              : mode === 'verify'
              ? (busy ? 'Verifying code...' : 'Verify email')
              : mode === 'forgot'
              ? (busy ? 'Sending reset code...' : 'Send reset code')
              : mode === 'verify-reset-otp'
              ? (busy ? 'Verifying...' : 'Verify code')
              : mode === 'new-password'
              ? (busy ? 'Updating password...' : 'Set new password')
              : (busy ? 'Signing in...' : 'Sign in')}
          </button>
        </form>

        {mode === 'verify' && (
          <>
            <button
              className="btn-secondary w-full mt-3"
              onClick={resend}
              disabled={busy || resendCooldown > 0}
            >
              {resendCooldown > 0
                ? `Resend code in ${resendCooldown}s`
                : 'Resend verification code'}
            </button>
            <button
              type="button"
              className="text-xs text-slate-400 hover:text-cyan-300 underline mt-3 block text-center w-full transition-colors"
              onClick={() => {
                clearAuthSession();
                setPending(null);
                setEmail('');
                setPassword('');
                setName('');
                setCode('');
                setError('');
                setMessage('');
                setMode('register');
              }}
            >
              ← Use a different email or sign up again
            </button>
          </>
        )}

        {mode === 'verify-reset-otp' && (
          <button
            className="text-sm text-slate-300 underline mt-4 block text-center"
            onClick={() => {
              setMode('forgot');
              setError('');
              setMessage('');
              setCode('');
            }}
          >
            Request a new reset code
          </button>
        )}

        {mode === 'login' && (
          <button
            className="text-sm text-slate-300 underline mt-4 block text-center"
            onClick={() => {
              setMode('forgot');
              setError('');
              setMessage('');
              setCode('');
            }}
          >
            Forgot password?
          </button>
        )}

        {!['verify', '2fa', 'verify-reset-otp', 'new-password'].includes(mode) && (
          <button
            className="text-sm text-brand-300 mt-4 block text-center w-full hover:underline"
            onClick={() => {
              setMode(mode === 'login' ? 'register' : 'login');
              setError('');
              setMessage('');
              setCode('');
            }}
          >
            {mode === 'login' ? 'New here? Create an account' : 'Already have an account? Sign in'}
          </button>
        )}
      </section>
    </div>
  );
}
