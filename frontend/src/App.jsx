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
  const [renderedTabs, setRenderedTabs] = useState(() => [tab]);
  const [prevTab, setPrevTab] = useState(tab);

  if (tab !== prevTab) {
    setPrevTab(tab);
    if (!renderedTabs.includes(tab) && tabs[tab]) {
      setRenderedTabs([...renderedTabs, tab]);
    }
  }

  const scroll = useRef({});
  const container = useRef(null);
  useEffect(() => {
    const element = container.current;
    const scrollMap = scroll.current;
    if (element) element.scrollTop = scrollMap[tab] || 0;
    return () => {
      if (element) scrollMap[tab] = element.scrollTop;
    };
  }, [tab]);
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace/>;
  if (!user.is_verified && !user.phone_verified) return <Navigate to="/verify-email" replace/>;
  if (!tabs[tab]) return <Navigate to="/app/overview" replace/>;
  const go = (name) => { setMenu(false); navigate(`/app/${name}`); };
  return <div className="h-screen flex flex-col overflow-hidden bg-obsidian-bg">
    <Navbar activeTab={tab} currentUser={user} onGoHome={()=>navigate('/')} onRefresh={()=>setRefresh(x=>x+1)} onLogout={onLogout}/>
    <div className="lg:hidden px-4 border-b border-slate-800"><button className="flex items-center gap-2 text-sm" onClick={()=>setMenu(!menu)} aria-expanded={menu} aria-label="Toggle navigation">{menu ? <X size={18}/> : <Menu size={18}/>} Navigation</button></div>
    <div className="flex flex-1 min-h-0">
      <div className={`${menu ? 'block absolute z-40 left-0 top-28 bottom-0 w-64 shadow-2xl' : 'hidden'} lg:block overflow-y-auto bg-obsidian-bg`}><Sidebar activeTab={tab} setActiveTab={go}/></div>
      <main ref={container} id="main-content" className="flex-1 min-w-0 overflow-y-auto p-4 lg:p-8">
        {renderedTabs.filter(name=>tabs[name]).map(name=> {
          const Component = tabs[name];
          return <div key={name} hidden={name!==tab} className="max-w-7xl mx-auto"><Component key={name==='composer' ? name : `${name}-${refresh}`} onNavigateTab={go} onUser={onUser}/></div>;
        })}
      </main>
    </div>
  </div>;
}

function VerifyEmail({ onSuccess, onCancel }) {
  return <AuthView initialMode="verify" onAuthSuccess={onSuccess} onCancel={onCancel} />;
}

function ResetPassword() {
  const navigate = useNavigate();
  return <AuthView initialMode="forgot" onAuthSuccess={() => navigate('/login')} onCancel={() => navigate('/')} />;
}

function OAuthCallback() {
  const query = new URLSearchParams(window.location.search);
  const initialError = !!query.get('error');
  const [message, setMessage] = useState(
    initialError
      ? 'Platform authorization was cancelled or denied. No account was connected.'
      : 'Completing your secure platform connection…'
  );
  const [error, setError] = useState(initialError);
  const done = useRef(false);
  useEffect(() => {
    if (done.current) return;
    done.current = true;
    const q = new URLSearchParams(window.location.search);
    if (q.get('error')) return;
    const platform = sessionStorage.getItem('aismm_oauth_platform');
    api.completeOAuth({ platform, code: q.get('code'), state: q.get('state'), redirect_uri: `${window.location.origin}/oauth/callback` })
      .then(() => {
        sessionStorage.removeItem('aismm_oauth_platform');
        setMessage('Your platform account is connected.');
        window.dispatchEvent(new CustomEvent('aismm:accounts-updated'));
        window.history.replaceState({}, '', '/oauth/callback');
      })
      .catch(err => {
        setError(true);
        setMessage(err.message);
      });
  }, []);
  return <div className="max-w-lg mx-auto p-6 mt-16 panel"><h1 className="text-2xl font-bold mb-6">Platform connection</h1><p className={error ? 'error' : 'notice'}>{message}</p><Link className="btn mt-6" to="/app/platforms">Back to platforms</Link></div>;
}

function Application() {
  const [user, setUser] = useState(getStoredUser);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (hash.startsWith('tab-')) navigate(`/app/${hash.slice(4)}`, { replace: true });
    else if (['terms', 'privacy'].includes(hash)) navigate(`/${hash}`, { replace: true });
    let alive = true;
    api.getMe().then(me => {
      if (alive) {
        setUser(me);
        setAuthSession(null, null, me);
      }
    }).catch(() => {
      if (alive) {
        clearAuthSession();
        setUser(null);
      }
    }).finally(() => {
      if (alive) setChecking(false);
    });
    const expired = () => {
      setUser(null);
      navigate('/login');
    };
    window.addEventListener('aismm:session-expired', expired);
    return () => {
      alive = false;
      window.removeEventListener('aismm:session-expired', expired);
    };
  }, [navigate]);
  async function logout() { setError(''); try { await api.logout(); clearAuthSession(); Object.keys(sessionStorage).filter(k=>k.startsWith('aismm')).forEach(k=>sessionStorage.removeItem(k)); setUser(null); navigate('/'); } catch(err){setError(`Logout could not be confirmed: ${err.message} Please retry.`);} }
  const success = me => {setUser(me);navigate(location.state?.from || '/app/overview',{replace:true});};
  const updateUser = me => {setUser(me);setAuthSession(null,null,me);};
  if(checking) return <div className="p-12 text-slate-400" role="status">Restoring your secure session…</div>;
  return <><a href="#main-content" className="sr-only focus:not-sr-only">Skip to content</a>{error && <div role="alert" className="error">{error}<button className="ml-3 underline" onClick={logout}>Retry logout</button></div>}
    <Routes>
      <Route path="/" element={<LandingPage onLaunchDashboard={()=>navigate((user && (user.is_verified || user.phone_verified)) ? '/app/overview' : '/register')} onOpenAuth={()=>navigate('/login')}/>}/>
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
