import React from 'react';
import {
  Zap,
  Activity,
  ShieldCheck,
  Home,
  Bell,
  RefreshCw,
  Search
} from 'lucide-react';

export default function Navbar({ onGoHome, activeTab, onRefresh }) {
  return (
    <header className="h-16 border-b border-gray-800 bg-gray-950/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-4">
        <button
          onClick={onGoHome}
          className="flex items-center space-x-2 text-xs font-semibold text-gray-400 hover:text-white px-2.5 py-1.5 rounded-lg bg-gray-900 border border-gray-800 transition-all"
        >
          <Home className="h-3.5 w-3.5" />
          <span>Landing Page</span>
        </button>
        <div className="h-4 w-px bg-gray-800"></div>
        <div className="text-sm font-bold text-gray-200 capitalize">
          {activeTab.replace("-", " ")}
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* System Health Badge */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>5/5 Platforms Connected • 8/8 AI Engines Online</span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          className="p-2 rounded-lg bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-400 hover:text-gray-200 transition-all"
          title="Refresh dashboard state"
        >
          <RefreshCw className="h-4 w-4" />
        </button>

        {/* Security Vault Indicator */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-semibold">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span className="hidden md:inline">Vault AES-256</span>
        </div>
      </div>
    </header>
  );
}
