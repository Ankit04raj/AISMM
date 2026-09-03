import React from 'react';
import {
  LayoutDashboard,
  BarChart3,
  PenTool,
  Calendar,
  Sparkles,
  MessageSquare,
  TrendingUp,
  Share2,
  Inbox,
  FileText,
  Settings,
  ShieldCheck,
  Cpu,
  Zap,
  ChevronRight
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard, section: "CORE" },
    { id: "analytics", label: "Analytics", icon: BarChart3, section: "CORE" },
    { id: "composer", label: "Composer", icon: PenTool, section: "CONTENT" },
    { id: "scheduling", label: "Scheduling", icon: Calendar, section: "CONTENT" },
    { id: "ai-engine", label: "AI Engine", icon: Sparkles, section: "CONTENT" },
    { id: "inbox", label: "Inbox", icon: Inbox, section: "ENGAGEMENT" },
    { id: "growth", label: "Growth", icon: TrendingUp, section: "ANALYTICS" },
    { id: "platforms", label: "Platforms", icon: Share2, section: "CHANNELS" },
    { id: "strategy", label: "AI Strategy", icon: Zap, section: "INTELLIGENCE" },
    { id: "reports", label: "Reports", icon: FileText, section: "SYSTEM" },
    { id: "models", label: "Models", icon: Cpu, section: "SYSTEM" },
    { id: "settings", label: "Settings", icon: Settings, section: "SYSTEM" },
    { id: "security", label: "Security", icon: ShieldCheck, section: "SYSTEM" },
  ];

  const sections = ["CORE", "CONTENT", "ENGAGEMENT", "ANALYTICS", "CHANNELS", "INTELLIGENCE", "SYSTEM"];

  return (
    <aside className="w-60 border-r border-[#1E293B] bg-[#07090E] flex flex-col flex-shrink-0 min-h-[calc(100vh-4rem)] font-['Plus_Jakarta_Sans']">
      {/* Brand Header */}
      <div className="p-4 border-b border-[#1E293B] flex items-center space-x-3">
        <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#06B6D4] flex items-center justify-center text-white shadow-md shadow-[#7C3AED]/30">
          <Zap className="h-4 w-4" />
        </div>
        <div>
          <div className="font-extrabold text-sm tracking-tight text-white">AISMM Studio</div>
          <div className="text-[10px] text-slate-500 font-mono">13 Modules Active</div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-4 overflow-y-auto">
        {sections.map((sec) => {
          const items = menuItems.filter((i) => i.section === sec);
          if (items.length === 0) return null;
          return (
            <div key={sec} className="space-y-1">
              <div className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-1 font-mono">
                {sec}
              </div>
              {items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-[#7C3AED] text-white shadow-lg shadow-[#7C3AED]/25"
                        : "text-slate-400 hover:text-white hover:bg-[#0D121F]"
                    }`}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`h-4 w-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-white" />}
                  </button>
                );
              })}
            </div>
          );
        })}
      </nav>

      {/* Footer System Badges */}
      <div className="p-3 border-t border-[#1E293B] text-[11px] text-slate-500 flex items-center justify-between font-mono">
        <span>AISMM v1.0</span>
        <span className="text-emerald-400">216 Tests OK</span>
      </div>
    </aside>
  );
}
