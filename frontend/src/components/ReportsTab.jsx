import React, { useState } from 'react';
import {
  Download,
  Calendar,
  RefreshCw,
  BarChart2,
  Users,
  Activity,
  Layers,
  AlertTriangle
} from 'lucide-react';
import { api } from '../api/client';

export default function ReportsTab() {
  const [loading, setLoading] = useState(false);
  const [reportType, setReportType] = useState('performance');
  const [dateRange] = useState(() => {
    const now = new Date();
    const start = new Date(now);
    start.setDate(start.getDate() - 6);
    const fmt = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    return `${fmt(start)} - ${fmt(now)}, ${now.getFullYear()}`;
  });
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [exportError, setExportError] = useState(null);

  const reportCards = [
    { id: 'performance', title: 'Performance Report', desc: 'Comprehensive performance analysis', icon: BarChart2, color: 'text-brand-400' },
    { id: 'audience', title: 'Audience Report', desc: 'Detailed audience insights & retention', icon: Users, color: 'text-cyan-400' },
    { id: 'content', title: 'Content Report', desc: 'Content performance breakdown & ROI', icon: Layers, color: 'text-emerald-400' },
    { id: 'engagement', title: 'Engagement Report', desc: 'Engagement analytics & sentiment health', icon: Activity, color: 'text-blue-400' },
  ];

  const handleExport = async () => {
    setLoading(true);
    setExportError(null);
    setDownloadSuccess(false);
    try {
      const blob = await api.exportReport(reportType, dateRange);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `aismm_${reportType}_report.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 4000);
    } catch (err) {
      setExportError(err.message || "Failed to export report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white font-mono">12 Reports & Insights</h2>
        <p className="text-xs text-slate-400 mt-0.5 font-mono">
          Export institutional performance audits, audience analytics, and compliance reports
        </p>
      </div>

      {exportError && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl text-xs text-rose-300 font-mono flex items-center gap-2">
          <AlertTriangle size={16} className="text-rose-400 shrink-0" />
          <span>{exportError}</span>
        </div>
      )}

      {/* Export Reports Box */}
      <div className="p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-6">
        <div>
          <h3 className="text-sm font-bold text-white font-mono">Export Reports</h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">Select Report Type</p>
        </div>

        {/* 4 Cards Grid */}
        <div className="grid md:grid-cols-2 gap-4">
          {reportCards.map((rc) => {
            const Icon = rc.icon;
            const isSelected = reportType === rc.id;
            return (
              <div
                key={rc.id}
                onClick={() => setReportType(rc.id)}
                className={`p-5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between font-mono ${
                  isSelected
                    ? "bg-brand-600/10 border-brand-500 shadow-lg"
                    : "bg-[#07090E] border-[#1E293B] hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-3.5">
                  <div className={`p-2.5 rounded-xl bg-[#0D121F] border border-[#1E293B] ${rc.color}`}>
                    <Icon size={20} />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">{rc.title}</h4>
                    <p className="text-[11px] text-slate-400">{rc.desc}</p>
                  </div>
                </div>

                <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                  isSelected ? "border-cyan-400 bg-cyan-400" : "border-slate-600"
                }`}>
                  {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-black" />}
                </div>
              </div>
            );
          })}
        </div>

        {/* Date Range & Export Button */}
        <div className="pt-4 border-t border-[#1E293B] flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-xs">
          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            <span className="text-slate-400">Custom Date Range:</span>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#07090E] border border-[#1E293B] text-slate-200">
              <Calendar size={12} className="text-cyan-400" />
              <span>{dateRange}</span>
            </div>
          </div>

          <button
            onClick={handleExport}
            disabled={loading}
            className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white rounded-xl font-bold transition-all shadow-md shadow-brand-600/25 flex items-center justify-center gap-2"
          >
            {loading ? <RefreshCw className="animate-spin" size={14} /> : <Download size={14} />}
            <span>{downloadSuccess ? "✓ Report Exported" : "Export Report"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
