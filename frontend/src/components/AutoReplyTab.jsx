import React, { useState, useEffect } from 'react';
import { Bot, RefreshCw, AlertTriangle, Send, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';

export default function AutoReplyTab() {
  const [commentText, setCommentText] = useState('How much does the monthly team plan cost?');
  const [mode, setMode] = useState('automatic');
  const [suggestion, setSuggestion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getSuggestion = async () => {
    if (!commentText.trim()) return;
    setLoading(true); setError(null);
    try {
      const data = await api.suggestReply(commentText, "demo_comment_1", mode);
      setSuggestion(data);
    } catch (err) { setError(`Unable to reach AISMM backend. ${err.message}`); }
    finally { setLoading(false); }
  };

  useEffect(() => { const timer = setTimeout(getSuggestion, 400); return () => clearTimeout(timer); }, [commentText, mode]);

  return <div className="space-y-6 animate-fadeIn">
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div><h2 className="text-xl font-bold text-white">Auto-Reply & Policy Routing</h2><p className="text-xs text-gray-400 mt-1">Live TF-IDF intent classification with automated confidence gating.</p></div>
    </div>
    {error && <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-xl flex gap-2 text-sm text-red-300"><AlertTriangle className="w-4 h-4 shrink-0" />{error}</div>}

    <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <section className="lg:col-span-3 bg-[#0d121f] border border-gray-800 rounded-2xl p-6 shadow-xl space-y-5">
        <div><label className="block text-[11px] font-bold uppercase text-gray-500 mb-2">Automation Policy Mode</label><div className="flex gap-2">{['manual', 'assisted', 'automatic'].map(m=><button key={m} onClick={()=>setMode(m)} className={`px-4 py-2 rounded-xl text-xs font-semibold capitalize ${mode===m?'bg-brand-600 text-white':'bg-gray-950 border border-gray-800 text-gray-400 hover:text-white'}`}>{m}</button>)}</div></div>
        <div><label className="block text-[11px] font-bold uppercase text-gray-500 mb-2">Test Comment Payload</label><textarea value={commentText} onChange={e=>setCommentText(e.target.value)} rows={4} placeholder="Type incoming comment text to evaluate intent and response policy..." className="w-full bg-gray-950 border border-gray-800 rounded-xl p-4 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none" /></div>
      </section>

      <section className="lg:col-span-2 bg-[#0d121f] border border-gray-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
        <div>
          <h3 className="font-bold text-white mb-4">Intent Classification Output</h3>
          {loading ? <div className="h-40 flex items-center justify-center text-brand-400"><RefreshCw className="w-6 h-6 animate-spin" /></div> : suggestion ? <div className="space-y-4">
            <div className="p-4 bg-gray-950 border border-gray-800 rounded-xl space-y-1">
              <span className="text-[10px] uppercase text-gray-500 font-bold">Classified Intent</span>
              <div className="text-base font-bold text-white capitalize">{suggestion.intent.replace('_', ' ')}</div>
              <div className="text-xs text-emerald-400 font-semibold">Confidence: {Math.round(suggestion.confidence * 100)}%</div>
            </div>
            <div className="p-4 bg-gray-950 border border-gray-800 rounded-xl space-y-1">
              <span className="text-[10px] uppercase text-gray-500 font-bold">Routing Policy Action</span>
              <div className="text-sm font-bold text-brand-300 uppercase">{suggestion.routing_action.replace('_', ' ')}</div>
            </div>
            <div className="p-4 bg-indigo-950/20 border border-indigo-500/30 rounded-xl space-y-1">
              <span className="text-[10px] uppercase text-indigo-400 font-bold">Suggested AI Reply</span>
              <p className="text-xs text-gray-200 mt-1">{suggestion.suggested_reply || 'No auto-reply (spam/manual handling).'}</p>
            </div>
          </div> : null}
        </div>
      </section>
    </div>
  </div>;
}