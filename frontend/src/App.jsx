import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import OverviewTab from './components/OverviewTab';
import PlatformsTab from './components/PlatformsTab';
import ComposerTab from './components/ComposerTab';
import SchedulingTab from './components/SchedulingTab';
import IntelligenceTab from './components/IntelligenceTab';
import AutoReplyTab from './components/AutoReplyTab';
import GrowthTab from './components/GrowthTab';
import AnalyticsTab from './components/AnalyticsTab';
import StrategyTab from './components/StrategyTab';
import ModelsTab from './components/ModelsTab';
import SecurityTab from './components/SecurityTab';

export default function App() {
  const [view, setView] = useState('landing'); // 'landing' or 'dashboard'
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
  };

  if (view === 'landing') {
    return <LandingPage onLaunchDashboard={() => setView('dashboard')} />;
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex flex-col selection:bg-brand-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        onGoHome={() => setView('landing')}
        activeTab={activeTab}
        onRefresh={handleRefresh}
      />

      {/* Main Studio Shell */}
      <div className="flex-1 flex flex-row overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 p-6 lg:p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {activeTab === 'overview' && <OverviewTab onNavigateTab={setActiveTab} key={refreshKey} />}
          {activeTab === 'platforms' && <PlatformsTab key={refreshKey} />}
          {activeTab === 'composer' && <ComposerTab key={refreshKey} />}
          {activeTab === 'scheduling' && <SchedulingTab key={refreshKey} />}
          {activeTab === 'intelligence' && <IntelligenceTab key={refreshKey} />}
          {activeTab === 'auto-reply' && <AutoReplyTab key={refreshKey} />}
          {activeTab === 'growth' && <GrowthTab key={refreshKey} />}
          {activeTab === 'analytics' && <AnalyticsTab key={refreshKey} />}
          {activeTab === 'strategy' && <StrategyTab key={refreshKey} />}
          {activeTab === 'models' && <ModelsTab key={refreshKey} />}
          {activeTab === 'security' && <SecurityTab key={refreshKey} />}
        </main>
      </div>
    </div>
  );
}
