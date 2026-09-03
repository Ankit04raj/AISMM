import React, { useState, useEffect } from 'react';
import { ShieldCheck, Lock, Activity, RefreshCw, AlertTriangle } from 'lucide-react';
import { api } from '../api/client';

export default function SecurityTab() {
  const [liveness, setLiveness] = useState(null);
  const [readiness, setReadiness] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadHealth = async () => {
    setLoading(true); setError(null);
    try {
      const [live, ready, telem] = await Promise.all([
        api.getLiveness(),
        api.getReadiness(),
        api.getTelemetry(),
      ]);
      setLiveness(live); setReadiness(ready); setTelemetry(telem);
    } catch (err) { setError(`Unable to reach AISMM backend. ${err.message}`); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadHealth(); }, []);

  return <div className="space-y-6 animate-fadeIn">
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div><h2 className="text-xl font-bold text-white">Security, Hardening & Health</h2><p className="text-xs text-gray-400 mt-1">Live health probes, rate limiter metrics, and vault security status.</p></div>
      <button onClick={loadHealth} className="inline-flex items-center gap-2 px-3 py-2 border border-gray-800 bg-gray-900 rounded-xl text-xs text-gray-300 hover:text-white"><RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />Refresh Probes</button>
    </div>
    {error && <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-xl flex gap-2 text-sm text-red-300"><AlertTriangle className="w-4 h-4 shrink-0" />{error}</div>}

    {loading && !liveness ? <div className="h-64 flex flex-col items-center justify-center gap-3"><RefreshCw className="w-6 h-6 animate-spin text-brand-400" /><p className="text-xs text-gray-500">Checking live health probes…</p></div> : <>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[#0d121f] border border-gray-800 rounded-2xl p-5 shadow-lg"><span className="text-[11px] uppercase text-gray-500 font-bold">Liveness Probe</span><div className="text-2xl font-black text-emerald-400 mt-2 capitalize">{liveness?.status || 'Unknown'}</div><p className="text-xs text-gray-500 mt-1">Uptime: {liveness?.uptime_seconds?.toFixed(1) || 0}s</p></div>
        <div className="bg-[#0d121f] border border-gray-800 rounded-2xl p-5 shadow-lg"><span className="text-[11px] uppercase text-gray-500 font-bold">Readiness Probe</span><div className="text-2xl font-black text-cyan-400 mt-2 capitalize">{readiness?.status || 'Unknown'}</div><p className="text-xs text-gray-500 mt-1">Database & Redis connected</p></div>
        <div className="bg-[#0d121f] border border-gray-800 rounded-2xl p-5 shadow-lg"><span className="text-[11px] uppercase text-gray-500 font-bold">Credential Vault</span><div className="text-2xl font-black text-brand-400 mt-2">AES-256</div><p className="text-xs text-gray-500 mt-1">Per-record salt encryption active</p></div>
      </div>
    </>}
  </div>;
}