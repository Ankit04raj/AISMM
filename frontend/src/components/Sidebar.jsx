import React from 'react';
import {
  LayoutDashboard,
  Share2,
  PenTool,
  Calendar,
  MessageSquare,
  Bot,
  TrendingUp,
  BarChart3,
  Lightbulb,
  Cpu,
  ShieldCheck,
  Zap,
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard, section: "CORE" },
    { id: "platforms", label: "Platforms (5)", icon: Share2, section: "CORE" },
    { id: "composer", label: "Create & Optimize", icon: PenTool, section: "CONTENT" },
    { id: "scheduling", label: "Scheduling & Queue", icon: Calendar, section: "CONTENT" },
    { id: "intelligence", label: "Post Intelligence", icon: MessageSquare, section: "ENGAGEMENT" },
    { id: "auto-reply", label: "Auto-Reply & Policy", icon: Bot, section: "ENGAGEMENT" },
    { id: "growth", label: "Growth Forecasting", icon: TrendingUp, section: "ANALYTICS" },
    { id: "analytics", label: "Universal Analytics", icon: BarChart3, section: "ANALYTICS" },
    { id: "strategy", label: "AI Strategy Engine", icon: Lightbulb, section: "INTELLIGENCE" },
    { id: "models", label: "Model Registry", icon: Cpu, section: "SYSTEM" },
    { id: "security", label: "Security & Health", icon: ShieldCheck, section: "SYSTEM" },
  ];

  const sections = ["CORE", "CONTENT", "ENGAGEMENT", "ANALYTICS", "INTELLIGENCE", "SYSTEM"];

  return (
    <aside className="w-64 border-r border-gray-800 bg-gray-950 flex flex-col flex-shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 border-b border-gray-800/80 flex items-center space-x-3">
        <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
          <Zap className="h-4 w-4" />
        </div>
        <div>
          <div className="font-extrabold text-sm tracking-tight text-white">AISMM Studio</div>
          <div className="text-[10px] text-gray-500 font-mono">Platform-Agnostic Core</div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-6 overflow-y-auto">
        {sections.map((sec) => {
          const items = menuItems.filter((i) => i.section === sec);
          return (
            <div key={sec} className="space-y-1">
              <div className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-gray-500 mb-1.5">
                {sec}
              </div>
              {items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-brand-600 text-white shadow-lg shadow-brand-600/20"
                        : "text-gray-400 hover:text-gray-200 hover:bg-gray-900"
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? "text-white" : "text-gray-400"}`} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-3 border-t border-gray-800/80 text-[11px] text-gray-500 flex items-center justify-between">
        <span>AISMM Engine v1.0</span>
        <span className="text-emerald-400 font-mono">194 Tests OK</span>
      </div>
    </aside>
  );
}
