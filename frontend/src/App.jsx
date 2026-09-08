import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation, useParams, Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import LandingPage from './components/LandingPage';
import AuthView from './components/AuthView';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import OverviewTab from './components/OverviewTab';
import AnalyticsTab from './components/AnalyticsTab';
import ComposerTab from './components/ComposerTab';
import SchedulingTab from './components/SchedulingTab';
import AIEngineTab from './components/AIEngineTab';
import InboxTab from './components/InboxTab';
import GrowthTab from './components/GrowthTab';
import PlatformsTab from './components/PlatformsTab';
import StrategyTab from './components/StrategyTab';
import ReportsTab from './components/ReportsTab';
import ModelsTab from './components/ModelsTab';
import SettingsTab from './components/SettingsTab';
import SecurityTab from './components/SecurityTab';
import TermsPage from './components/TermsPage';
import PrivacyPage from './components/PrivacyPage';
import { api, getStoredUser, clearAuthSession, setAuthSession } from './api/client';

const tabs = { overview: OverviewTab, analytics: AnalyticsTab, composer: ComposerTab, scheduling: SchedulingTab,
  'ai-engine': AIEngineTab, inbox: InboxTab, growth: GrowthTab, platforms: PlatformsTab, strategy: StrategyTab,
  reports: ReportsTab, models: ModelsTab, settings: SettingsTab, security: SecurityTab };

class ErrorBoundary extends React.Component {
  state = { error: false };
  static getDerivedStateFromError() { return { error: true }; }
  render() { return this.state.error ? <div className="panel m-6"><h1 className="text-xl">Something went wrong.</h1><p className="text-slate-400 my-4">Your saved drafts are still available. Reload to try again.</p><button className="btn" onClick={()=>window.location.reload()}>Reload workspace</button></div> : this.props.children; }
}

function Studio({ user, onLogout, onUser }) {
  const { tab = 'overview' } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [menu, setMenu] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const [visited, setVisited] = useState(new Set([tab]));
  const scroll = useRef({});
  const container = useRef(null);
  useEffect(() => {
    setVisited(v => new Set([...v, tab]));
    const element = container.current;
    if (element) element.scrollTop = scroll.current[tab] || 0;
    return () => { if (element) scroll.current[tab] = element.scrollTop; };
  }, [tab]);
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace/>;
  if (!user.is_verified && !user.phone_verified) return <Navigate to="/verify-email" replace/>;
  if (!tabs[tab]) return <Navigate to="/app/overview" replace/>;
  const go = (name) => { setMenu(false); navigate(`/app/${name}`); };
  const rendered = new Set([...visited, tab]);
  return <div className="h-screen flex flex-col overflow-hidden bg-obsidian-bg">
    <Navbar activeTab={tab} currentUser={user} onGoHome={()=>navigate('/')} onRefresh={()=>setRefresh(x=>x+1)} onLogout={onLogout}/>
    <div className="lg:hidden px-4 border-b border-slate-800"><button className="flex items-center gap-2 text-sm" onClick={()=>setMenu(!menu)} aria-expanded={menu} aria-label="Toggle navigation">{menu ? <X size={18}/> : <Menu size={18}/>} Navigation</button></div>
    <div className="flex flex-1 min-h-0">
      <div className={`${menu ? 'block absolute z-40 left-0 top-28 bottom-0 w-64 shadow-2xl' : 'hidden'} lg:block overflow-y-auto bg-obsidian-bg`}><Sidebar activeTab={tab} setActiveTab={go}/></div>
      <main ref={container} id="main-content" className="flex-1 min-w-0 overflow-y-auto p-4 lg:p-8">
        {Array.from(rendered).filter(name=>tabs[name]).map(name=> {
          const Component = tabs[name];
          return <div key={name} hidden={name!==tab} className="max-w-7xl mx-auto"><Component key={name==='composer' ? name : `${name}-${refresh}`} onNavigateTab={go} onUser={onUser}/></div>;
        })}
      </main>
    </div>
  </div>;
}

function VerifyEmail({ onSuccess, onCancel }) {
  const [error, setError] = useState('');
  const [working, setWorking] = useState(false);
  const token = new URLSearchParams(window.location.search).get('token');
  async function verify() {
    setWorking(true); setError('');
    try { await api.verifyEmail(token); const me = await api.getMe(); setAuthSession(null,null,me); onSuccess(me); }
    catch (err) { setError(err.message); } finally { setWorking(false); }
  }
  if (!token) return <AuthView initialMode="verify" onAuthSuccess={onSuccess} onCancel={onCancel}/>;
  return <div className="max-w-lg mx-auto p-6 mt-16"><div className="panel"><h1 className="text-2xl font-bold mb-4">Verify your email</h1><p className="text-slate-400 mb-6">Confirm your address to unlock your workspace. If you opened this link on another device, sign in first, then reopen the link.</p>{error && <div className="error mb-4">{error}</div>}<button className="btn w-full" disabled={working} onClick={verify}>{working ? 'Verifying…' : 'Confirm email address'}</button><Link className="block text-brand-300 mt-4" to="/login">Sign in</Link></div></div>;
}

function ResetPassword() {
  const [password, setPassword] = useState(''); const [message,setMessage] = useState(''); const [error,setError] = useState(''); const [busy,setBusy] = useState(false);
  async function submit(e) { e.preventDefault(); setBusy(true); setError(''); try { const result = await api.resetPassword(new URLSearchParams(window.location.search).get('token') || '',password); clearAuthSession(); setMessage(result.message); } catch(err) { setError(err.message); } finally { setBusy(false); } }
  return <div className="max-w-lg mx-auto p-6 mt-16 panel"><h1 className="text-2xl font-bold mb-6">Choose a new password</h1>{error && <div className="error">{error}</div>}{message ? <div className="notice">{message}<Link to="/login" className="block underline mt-3">Sign in</Link></div> : <form className="space-y-4" onSubmit={submit}><label className="block">New password<input className="field mt-2" type="password" autoComplete="new-password" required minLength={8} maxLength={72} value={password} onChange={e=>setPassword(e.target.value)}/></label><button className="btn" disabled={busy}>Reset password</button></form>}</div>;
}

function OAuthCallback() {
  const [message,setMessage] = useState('Completing your secure platform connection…'); const [error,setError] = useState(false); const done = useRef(false);
  useEffect(()=> { if(done.current) return; done.current=true; const query = new URLSearchParams(window.location.search);
    if(query.get('error')) { setError(true); setMessage('Platform authorization was cancelled or denied. No account was connected.'); return; }
    const platform = sessionStorage.getItem('aismm_oauth_platform');
    api.completeOAuth({ platform, code:query.get('code'), state:query.get('state'), redirect_uri: `${window.location.origin}/oauth/callback` })
      .then(()=>{sessionStorage.removeItem('aismm_oauth_platform'); setMessage('Your platform account is connected.'); window.history.replaceState({},'', '/oauth/callback');})
      .catch(err=>{setError(true);setMessage(err.message);});
  },[]);
  return <div className="max-w-lg mx-auto p-6 mt-16 panel"><h1 className="text-2xl font-bold mb-6">Platform connection</h1><p className={error?'error':'notice'}>{message}</p><Link className="btn mt-6" to="/app/platforms">Back to platforms</Link></div>;
}

function Application() {
  const [user,setUser] = useState(getStoredUser); const [checking,setChecking] = useState(Boolean(getStoredUser())); const [error,setError] = useState('');
  const navigate=useNavigate(); const location=useLocation();
  useEffect(()=> {
    const hash = window.location.hash.slice(1);
    if(hash.startsWith('tab-')) navigate(`/app/${hash.slice(4)}`, {replace:true});
    else if(['terms','privacy'].includes(hash)) navigate(`/${hash}`, {replace:true});
    let alive=true;
    if(getStoredUser()) api.getMe().then(me=>{ if(alive){setUser(me);setAuthSession(null,null,me);} }).catch(()=>{if(alive){clearAuthSession();setUser(null);}}).finally(()=>{if(alive)setChecking(false);});
    const expired=()=>{setUser(null);navigate('/login');}; window.addEventListener('aismm:session-expired',expired);
    return ()=>{alive=false;window.removeEventListener('aismm:session-expired',expired);};
  },[]);
  async function logout() { setError(''); try { await api.logout(); clearAuthSession(); Object.keys(sessionStorage).filter(k=>k.startsWith('aismm')).forEach(k=>sessionStorage.removeItem(k)); setUser(null); navigate('/'); } catch(err){setError(`Logout could not be confirmed: ${err.message} Please retry.`);} }
  const success = me => {setUser(me);navigate(location.state?.from || '/app/overview',{replace:true});};
  const updateUser = me => {setUser(me);setAuthSession(null,null,me);};
  if(checking) return <div className="p-12 text-slate-400" role="status">Restoring your secure session…</div>;
  return <><a href="#main-content" className="sr-only focus:not-sr-only">Skip to content</a>{error && <div role="alert" className="error">{error}<button className="ml-3 underline" onClick={logout}>Retry logout</button></div>}
    <Routes>
      <Route path="/" element={<LandingPage onLaunchDashboard={()=>navigate(user?'/app/overview':'/register')} onOpenAuth={()=>navigate('/login')}/>}/>
      <Route path="/login" element={<AuthView onAuthSuccess={success} onCancel={()=>navigate('/')}/>}/>
      <Route path="/register" element={<AuthView initialMode="register" onAuthSuccess={success} onCancel={()=>navigate('/')}/>}/>
      <Route path="/verify-email" element={<VerifyEmail onSuccess={success} onCancel={()=>navigate('/')}/>}/>
      <Route path="/reset-password" element={<ResetPassword/>}/>
      <Route path="/oauth/callback" element={<OAuthCallback/>}/>
      <Route path="/terms" element={<TermsPage onBack={()=>navigate('/')}/>}/>
      <Route path="/privacy" element={<PrivacyPage onBack={()=>navigate('/')}/>}/>
      <Route path="/app" element={<Navigate to="/app/overview" replace/>}/>
      <Route path="/app/:tab/*" element={<Studio user={user} onLogout={logout} onUser={updateUser}/>}/>
      <Route path="*" element={<div className="panel m-8"><h1 className="text-2xl">Page not found</h1><Link className="btn mt-6" to="/">Return home</Link></div>}/>
    </Routes>
  </>;
}
export default function App(){return <ErrorBoundary><BrowserRouter><Application/></BrowserRouter></ErrorBoundary>;}
