import React, { useState, useEffect } from 'react';
import { Cpu, RefreshCw, AlertTriangle, ShieldCheck } from 'lucide-react';
import { api } from '../api/client';

export default function ModelsTab() {
  const [registry, setRegistry] = useState([]);
  const [evalAudit, setEvalAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadModels = async () => {
    setLoading(true); setError(null);
    try {
      const [reg, audit] = await Promise.all([
        api.getModelRegistry(),
        api.evaluateAllModels(),
      ]);
      setRegistry(reg || []); setEvalAudit(audit);
    } catch (err) { setError(`Unable to reach AISMM backend. ${err.message}`); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadModels(); }, []);

  return <div className="space-y-6 animate-fadeIn">
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div><h2 className="text-xl font-bold text-white">Model Registry & Evaluation Benchmark</h2><p className="text-xs text-gray-400 mt-1">Live empirical evaluation against research baselines with zero hardcoded accuracy literals.</p></div>
      <button onClick={loadModels} className="inline-flex items-center gap-2 px-3 py-2 border border-gray-800 bg-gray-900 rounded-xl text-xs text-gray-300 hover:text-white"><RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />Evaluate Live</button>
    </div>
    {error && <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-xl flex gap-2 text-sm text-red-300"><AlertTriangle className="w-4 h-4 shrink-0" />{error}</div>}

    {loading && !evalAudit ? <div className="h-64 flex flex-col items-center justify-center gap-3"><RefreshCw className="w-6 h-6 animate-spin text-brand-400" /><p className="text-xs text-gray-500">Benchmarking models on backend…</p></div> : evalAudit ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {evalAudit.models.map(m => (
        <div key={m.model_name} className="bg-[#0d121f] border border-gray-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-start mb-3">
              <div><h3 className="font-bold text-sm text-white">{m.model_name}</h3><span className="text-[10px] uppercase text-gray-500 font-semibold">{m.task} • {m.stage}</span></div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${m.meets_research_baseline?'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30':'bg-amber-500/10 text-amber-400 border border-amber-500/30'}`}>{m.meets_research_baseline?'Meets Baseline':'Evaluating'}</span>
            </div>
            <div className="space-y-1 text-xs text-gray-400 mt-4">
              <div className="flex justify-between"><span>Primary Metric</span><strong className="text-white font-mono">{m.accuracy ? `${m.accuracy}% Acc` : `${m.r2_score} R²`}</strong></div>
              <div className="flex justify-between"><span>Research Baseline</span><strong className="text-brand-300 font-mono">{m.research_baseline_metric}%</strong></div>
              <div className="flex justify-between"><span>Inference Latency</span><strong className="text-cyan-400 font-mono">{m.latency_ms} ms</strong></div>
            </div>
          </div>
        </div>
      ))}
    </div> : null}
  </div>;
}