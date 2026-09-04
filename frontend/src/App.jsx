import React, { useState, useEffect } from 'react';
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
import { getStoredUser, clearAuthSession } from './api/client';

export default function App() {
  const [view, setView] = useState('landing'); // 'landing' | 'dashboard' | 'terms' | 'privacy'
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshKey, setRefreshKey] = useState(0);
  const [currentUser, setCurrentUser] = useState(getStoredUser());
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Synchronize initial URL hash for route continuity
  useEffect(() => {
    setCurrentUser(getStoredUser());

    const hash = window.location.hash.replace('#', '').toLowerCase();
    if (hash === 'terms') {
      setView('terms');
    } else if (hash === 'privacy') {
      setView('privacy');
    } else if (hash.startsWith('tab-')) {
      const tabName = hash.replace('tab-', '');
      setActiveTab(tabName);
      setView('dashboard');
    }

    const onHashChange = () => {
      const h = window.location.hash.replace('#', '').toLowerCase();
      if (h === 'terms') setView('terms');
      else if (h === 'privacy') setView('privacy');
      else if (h.startsWith('tab-')) {
        setActiveTab(h.replace('tab-', ''));
        setView('dashboard');
      } else if (h === 'landing' || !h) {
        setView('landing');
      }
    };

    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleNavigateTab = (tab) => {
    setActiveTab(tab);
    window.location.hash = `tab-${tab}`;
  };

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
  };

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    setShowAuthModal(false);
    setView('dashboard');
    window.location.hash = 'tab-overview';
  };

  const handleLogout = () => {
    clearAuthSession();
    setCurrentUser(null);
    setView('landing');
    window.location.hash = '';
  };

  if (view === 'terms') {
    return <TermsPage onBack={() => { setView('dashboard'); window.location.hash = 'tab-overview'; }} />;
  }

  if (view === 'privacy') {
    return <PrivacyPage onBack={() => { setView('dashboard'); window.location.hash = 'tab-overview'; }} />;
  }

  if (view === 'landing') {
    return (
      <>
        <LandingPage
          onLaunchDashboard={() => {
            if (currentUser) {
              setView('dashboard');
              window.location.hash = 'tab-overview';
            } else {
              setShowAuthModal(true);
            }
          }}
          onOpenAuth={() => setShowAuthModal(true)}
        />
        {showAuthModal && (
          <AuthView
            onAuthSuccess={handleAuthSuccess}
            onCancel={() => setShowAuthModal(false)}
          />
        )}
      </>
    );
  }

  return (
    <div className="min-h-screen bg-[#07090E] text-[#F1F5F9] flex flex-col selection:bg-[#7C3AED] selection:text-white font-['Plus_Jakarta_Sans']">
      {/* Top Navigation Bar */}
      <Navbar
        onGoHome={() => { setView('landing'); window.location.hash = ''; }}
        activeTab={activeTab}
        onRefresh={handleRefresh}
        onOpenAuth={() => setShowAuthModal(true)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* Main Studio Workspace Layout */}
      <div className="flex-1 flex flex-row overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={handleNavigateTab} />

        <main className="flex-1 p-6 lg:p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {/* Module 03: Dashboard Overview */}
          {activeTab === 'overview' && <OverviewTab onNavigateTab={handleNavigateTab} key={refreshKey} />}

          {/* Module 04: Analytics Dashboard */}
          {activeTab === 'analytics' && <AnalyticsTab key={refreshKey} />}

          {/* Module 05: Content Composer */}
          {activeTab === 'composer' && <ComposerTab key={refreshKey} />}

          {/* Module 07: Smart Scheduling */}
          {activeTab === 'scheduling' && <SchedulingTab key={refreshKey} />}

          {/* Module 06: AI Content Engine */}
          {activeTab === 'ai-engine' && <AIEngineTab key={refreshKey} />}

          {/* Module 09: Inbox & Engagement */}
          {activeTab === 'inbox' && <InboxTab key={refreshKey} />}

          {/* Module 10: Growth Intelligence */}
          {activeTab === 'growth' && <GrowthTab key={refreshKey} />}

          {/* Module 08: Platform Management */}
          {activeTab === 'platforms' && <PlatformsTab key={refreshKey} />}

          {/* Module 11: AI Strategy Engine */}
          {activeTab === 'strategy' && <StrategyTab key={refreshKey} />}

          {/* Module 12: Reports & Insights */}
          {activeTab === 'reports' && <ReportsTab key={refreshKey} />}

          {/* Models Registry */}
          {activeTab === 'models' && <ModelsTab key={refreshKey} />}

          {/* Module 13: Settings & Configuration */}
          {activeTab === 'settings' && <SettingsTab key={refreshKey} />}

          {/* Security & Health */}
          {activeTab === 'security' && <SecurityTab key={refreshKey} />}
        </main>
      </div>

      {showAuthModal && (
        <AuthView
          onAuthSuccess={handleAuthSuccess}
          onCancel={() => setShowAuthModal(false)}
        />
      )}
    </div>
  );
}
