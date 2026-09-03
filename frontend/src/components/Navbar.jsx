import React from 'react';
import {
  Zap,
  Activity,
  ShieldCheck,
  Home,
  Bell,
  RefreshCw,
  Search,
  User,
  LogOut,
  LogIn,
  Calendar
} from 'lucide-react';
import { getStoredUser } from '../api/client';

export default function Navbar({ onGoHome, activeTab, onRefresh, onOpenAuth, currentUser, onLogout }) {
  const user = currentUser || getStoredUser();

  return (
    <header className="h-16 border-b border-[#1E293B] bg-[#07090E]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40 font-['Plus_Jakarta_Sans']">
      <div className="flex items-center space-x-4">
        <button
          onClick={onGoHome}
          className="flex items-center space-x-1.5 text-xs font-bold text-slate-400 hover:text-white px-3 py-1.5 rounded-xl bg-[#0D121F] border border-[#1E293B] transition-all"
        >
          <Home className="h-3.5 w-3.5" />
          <span>Home</span>
        </button>

        <div className="h-4 w-px bg-[#1E293B]" />

        <div>
          <span className="text-xs font-extrabold text-white capitalize font-mono">
            {activeTab.replace("-", " ")}
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Date Horizon Picker */}
        <div className="hidden lg:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-[#0D121F] border border-[#1E293B] text-slate-300 text-xs font-medium cursor-pointer hover:border-slate-700">
          <Calendar className="w-3.5 h-3.5 text-[#06B6D4]" />
          <span>May 20 - May 26, 2024 ▾</span>
        </div>

        {/* System Health Badge */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>5/5 Connected • 8 AI Engines</span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          className="p-2 rounded-xl bg-[#0D121F] hover:bg-[#131B2E] border border-[#1E293B] text-slate-400 hover:text-white transition-all"
          title="Refresh Studio State"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </button>

        {/* User Auth Session */}
        {user ? (
          <div className="flex items-center gap-2 pl-2 border-l border-[#1E293B]">
            <div className="flex items-center gap-2 px-3 py-1 bg-[#0D121F] border border-[#1E293B] rounded-xl">
              <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-[#7C3AED] to-[#06B6D4] flex items-center justify-center text-[10px] font-bold text-white">
                {(user.full_name || user.email || "A").charAt(0).toUpperCase()}
              </div>
              <span className="text-xs font-bold text-slate-200 max-w-[120px] truncate hidden md:inline">
                {user.full_name || user.email}
              </span>
            </div>
            <button
              onClick={onLogout}
              className="p-2 rounded-xl bg-[#0D121F] hover:bg-rose-950/40 border border-[#1E293B] text-slate-400 hover:text-rose-400 transition-all"
              title="Sign Out"
            >
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        ) : (
          <button
            onClick={onOpenAuth}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-[#7C3AED] hover:bg-[#6D28D9] text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-[#7C3AED]/20"
          >
            <LogIn className="h-3.5 w-3.5" />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
}
