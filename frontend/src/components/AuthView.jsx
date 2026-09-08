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
  const [accepted, setAccepted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [pending, setPending] = useState(getStoredUser());

  async function finishLogin(res) {
    if (res.requires_2fa) { setMode('2fa'); setCode(''); return; }
    if (!res.access_token) throw new Error('Sign-in did not return a session. Please retry.');
    setAuthSession(res.access_token, res.refresh_token, res.user);
    setPending(res.user);
    if (!res.user.is_verified && !res.user.phone_verified) {
      setMode('verify');
      if (res.verification_token) {
        setCode(res.verification_token);
        setMessage('Local development only: email delivery is disabled. A test verification token is filled below.');
      } else setMessage('Verify your email to enter your workspace. Open the email link, or paste its token below.');
    } else onAuthSuccess(res.user);
  }

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setMessage('');
    try {
      if (mode === 'register') {
        if (!accepted) throw new Error('Please accept the Terms and Privacy Policy.');
        await finishLogin(await api.register(email, password, name, null, 'email'));
      } else if (mode === 'login' || mode === '2fa') {
        await finishLogin(await api.login(email, password, mode === '2fa' ? code : undefined));
      } else if (mode === 'verify') {
        await api.verifyEmail(code.trim());
        const user = await api.getMe(); setAuthSession(null, null, user); onAuthSuccess(user);
      } else if (mode === 'forgot') {
        const result = await api.forgotPassword(email); setMessage(result.message);
      }
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  async function resend() {
    setBusy(true); setError('');
    try {
      const res = await api.resendVerification();
      setMessage(res.message || 'Verification requested. Check your inbox.');
      if (res.verification_token) { setCode(res.verification_token); setMessage('Local development: email delivery is disabled; use the test token below.'); }
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  const title = { login: 'Welcome back.', register: 'Create your workspace.', '2fa': 'One more security check.', verify: 'Verify your email.', forgot: 'Reset your password.' }[mode];
  return <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md overflow-y-auto p-4 sm:p-8 flex items-start sm:items-center justify-center" role="dialog" aria-modal="true" aria-labelledby="auth-title">
    <section className="panel w-full max-w-md relative my-auto shadow-2xl">
      <button aria-label="Close sign in" onClick={onCancel} className="absolute top-3 right-3 p-2 text-slate-400"><X size={20}/></button>
      <div className="w-12 h-12 rounded-xl bg-brand-600/20 text-brand-300 flex items-center justify-center mb-6"><ShieldCheck/></div>
      <p className="text-cyan-300 text-xs tracking-widest font-semibold uppercase mb-2">AISMM Studio</p>
      <h1 id="auth-title" className="text-2xl font-bold mb-2">{title}</h1>
      <p className="text-slate-400 text-sm mb-6">{mode === 'verify' ? `Verification required for ${pending?.email || 'your account'}.` : 'One workspace for your content, channels, and next move.'}</p>
      {error && <div className="error mb-4" role="alert">{error}</div>}
      {message && <div className="notice mb-4" role="status">{message}</div>}
      <form onSubmit={submit} className="space-y-4">
        {mode === 'register' && <label className="block text-sm">Full name<input className="field mt-1" autoComplete="name" required value={name} onChange={e=>setName(e.target.value)}/></label>}
        {['login','register','forgot'].includes(mode) && <label className="block text-sm">Email<input className="field mt-1" type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)}/></label>}
        {['login','register'].includes(mode) && <label className="block text-sm">Password<input className="field mt-1" type="password" autoComplete={mode === 'register' ? 'new-password' : 'current-password'} minLength={8} maxLength={72} required value={password} onChange={e=>setPassword(e.target.value)}/></label>}
        {['2fa','verify'].includes(mode) && <label className="block text-sm">{mode === '2fa' ? 'Authenticator code' : 'Verification token'}<input className="field mt-1" autoComplete="one-time-code" inputMode={mode === '2fa' ? 'numeric' : 'text'} pattern={mode === '2fa' ? '[0-9]{6}' : undefined} required value={code} onChange={e=>setCode(e.target.value)}/></label>}
        {mode === 'register' && <label className="flex items-start gap-3 text-sm text-slate-300"><input className="mt-1 w-5 h-5 shrink-0" type="checkbox" required checked={accepted} onChange={e=>setAccepted(e.target.checked)}/><span>I agree to the <Link className="underline text-brand-300" to="/terms" target="_blank">Terms of Service</Link> and <Link className="underline text-brand-300" to="/privacy" target="_blank">Privacy Policy</Link>.</span></label>}
        <button disabled={busy} className="btn w-full" type="submit">{busy ? <Loader2 className="animate-spin" size={18}/> : <ArrowRight size={18}/>} {mode === 'register' ? 'Create account' : mode === 'verify' ? 'Verify email' : mode === 'forgot' ? 'Send reset link' : 'Sign in'}</button>
      </form>
      {mode === 'verify' && <button className="btn-secondary w-full mt-3" onClick={resend} disabled={busy}>Resend verification email</button>}
      {mode === 'login' && <button className="text-sm text-slate-300 underline mt-4 block" onClick={()=>{setMode('forgot');setError('');}}>Forgot password?</button>}
      {!['verify','2fa'].includes(mode) && <button className="text-sm text-brand-300 mt-4" onClick={()=>{setMode(mode==='login' ? 'register' : 'login');setError('');setMessage('');}}>{mode === 'login' ? 'New here? Create an account' : 'Already have an account? Sign in'}</button>}
    </section>
  </div>;
}
