import React, { useState } from 'react';
import { FileText, Download, Calendar, CheckCircle2, AlertCircle, RefreshCw, BarChart2, Shield, Sparkles } from 'lucide-react';
import { api } from '../api/client';

export default function ReportsTab() {
  const [loading, setLoading] = useState(false);
  const [reportType, setReportType] = useState('executive');
  const [dateRange, setDateRange] = useState('30d');
  const [generatedReport, setGeneratedReport] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const [auditData, overviewData] = await Promise.all([
        api.evaluateAllModels(),
        api.getOverview(dateRange === '7d' ? 7 : (dateRange === '90d' ? 90 : 30)),
      ]);

      setGeneratedReport({
        type: reportType,
        range: dateRange,
        generatedAt: new Date().toISOString(),
        models: auditData.models || [],
        overview: overviewData || {},
      });
    } catch (err) {
      console.error("Failed to generate report:", err);
      setError("Unable to reach AISMM backend to generate live report.");
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (!generatedReport) return;
    const jsonStr = JSON.stringify(generatedReport, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `aismm_${generatedReport.type}_report_${generatedReport.range}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h2 className="text-xl font-bold text-white">Reports & Live Export Center</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Generate live executive summaries, platform performance audits, and AI accuracy verification reports (CLAUDE.md Module 12)
        </p>
      </div>

      {/* Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { id: "executive", title: "Executive Performance Audit", desc: "Consolidated KPIs, audience reach, net engagement, and channel ROI." },
          { id: "ai_evaluation", title: "AI Model Diagnostic Report", desc: "Research baseline benchmarking, accuracy splits, latency, and drift status." },
          { id: "sentiment_intelligence", title: "Sentiment & Community Health", desc: "Audience mood trajectories, complaint resolution rate, and response times." },
        ].map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setReportType(item.id)}
            className={`p-6 rounded-3xl border text-left transition-all ${
              reportType === item.id
                ? "bg-[#0D121F] border-brand-500/80 shadow-xl shadow-brand-600/10"
                : "bg-[#0D121F] border-[#1E293B] hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-2xl bg-[#07090E] border border-[#1E293B] flex items-center justify-center">
                <FileText className={`w-5 h-5 ${reportType === item.id ? "text-cyan-400" : "text-slate-400"}`} />
              </div>
              {reportType === item.id && <CheckCircle2 className="w-5 h-5 text-brand-400" />}
            </div>
            <h4 className="font-bold text-sm text-white">{item.title}</h4>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{item.desc}</p>
          </button>
        ))}
      </div>

      {/* Parameters & Trigger */}
      <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">Date Horizon:</span>
          <div className="flex bg-[#07090E] rounded-2xl p-1 border border-[#1E293B]">
            {['7d', '30d', '90d'].map((r) => (
              <button
                key={r}
                onClick={() => setDateRange(r)}
                className={`px-4 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  dateRange === r ? "bg-brand-600 text-white shadow" : "text-slate-400 hover:text-white"
                }`}
              >
                {r.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleGenerateReport}
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 text-white font-bold text-xs rounded-2xl shadow-lg shadow-brand-600/25 transition-all flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <BarChart2 className="w-4 h-4" />}
          <span>{loading ? "Compiling Live Telemetry..." : "Generate Live Report"}</span>
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl flex items-center gap-3 text-rose-300 text-xs">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Generated Report View */}
      {generatedReport && (
        <div className="bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 font-mono">Live Audit Deliverable</span>
              <h3 className="text-lg font-extrabold text-white capitalize mt-0.5">{generatedReport.type.replace("_", " ")} Report ({generatedReport.range})</h3>
              <p className="text-xs text-slate-500 mt-0.5 font-mono">Compiled at {new Date(generatedReport.generatedAt).toLocaleString()}</p>
            </div>
            <button
              onClick={handleExportCSV}
              className="px-4 py-2 bg-[#07090E] hover:bg-[#131B2E] text-slate-200 rounded-xl text-xs font-bold border border-[#1E293B] flex items-center gap-2 transition-all shadow"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export Deliverable</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono">
            <div className="p-4 bg-[#07090E] rounded-2xl border border-[#1E293B]">
              <span className="text-xs text-slate-400 block mb-1">Total Reach</span>
              <span className="text-xl font-bold text-white">{generatedReport.overview.total_reach?.toLocaleString() || "0"}</span>
            </div>
            <div className="p-4 bg-[#07090E] rounded-2xl border border-[#1E293B]">
              <span className="text-xs text-slate-400 block mb-1">Total Engagements</span>
              <span className="text-xl font-bold text-emerald-400">{generatedReport.overview.total_engagements?.toLocaleString() || "0"}</span>
            </div>
            <div className="p-4 bg-[#07090E] rounded-2xl border border-[#1E293B]">
              <span className="text-xs text-slate-400 block mb-1">Evaluated Models</span>
              <span className="text-xl font-bold text-brand-400">{generatedReport.models.length} Online</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
