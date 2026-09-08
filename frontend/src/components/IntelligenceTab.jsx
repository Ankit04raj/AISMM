import React, { useState, useEffect } from 'react';
import { MessageSquare, RefreshCw, AlertTriangle, Activity } from 'lucide-react';
import { api } from '../api/client';

export default function IntelligenceTab() {
  const [posts, setPosts] = useState([]);
  const [selectedPostId, setSelectedPostId] = useState('');
  const [trajectory, setTrajectory] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);

  const loadPosts = async () => {
    setLoading(true); setError(null);
    try {
      const res = await api.getPosts(1, 30);
      const postList = res.posts || [];
      setPosts(postList);
      if (postList.length > 0) setSelectedPostId(postList[0].id);
    } catch (err) { setError(`Unable to reach AISMM backend. ${err.message}`); }
    finally { setLoading(false); }
  };

  const loadDetails = async (id) => {
    if (!id) return;
    try {
      const [traj, alt] = await Promise.all([
        api.getPostSentimentTrajectory(id).catch(() => null),
        api.getPostAlerts(id).catch(() => null),
      ]);
      setTrajectory(traj); setAlerts(alt);
    } catch (err) { setError(`Unable to fetch post intelligence: ${err.message}`); }
  };

  useEffect(() => { loadPosts(); }, []);
  useEffect(() => { if (selectedPostId) loadDetails(selectedPostId); }, [selectedPostId]);

  const syncComments = async () => {
    if (!selectedPostId) return;
    setSyncing(true);
    try {
      await api.syncPostComments(selectedPostId);
      await loadDetails(selectedPostId);
    } catch (err) { setError(`Comment sync failed: ${err.message}`); }
    finally { setSyncing(false); }
  };

  return <div className="space-y-6 animate-fadeIn">
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div><h2 className="text-xl font-bold text-white">Post-Posting Intelligence</h2><p className="text-xs text-gray-400 mt-1">Temporal sentiment evolution across post lifetimes and automated anomaly detection.</p></div>
      {selectedPostId && <button onClick={syncComments} disabled={syncing} className="px-4 py-2 bg-brand-600 hover:bg-brand-500 rounded-xl text-xs font-bold text-white flex items-center gap-2 disabled:opacity-50"><RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />Sync Comments</button>}
    </div>
    {error && <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-xl flex gap-2 text-sm text-red-300"><AlertTriangle className="w-4 h-4 shrink-0" />{error}</div>}

    {posts.length === 0 && !loading ? <div className="p-12 text-center text-sm text-gray-500 bg-[#0d121f] border border-gray-800 rounded-2xl">No posts published yet. Create and publish a post in the Composer to inspect post intelligence signals.</div> : <div className="space-y-6">
      <div className="flex gap-2 overflow-x-auto pb-2">
        {posts.map(p=><button key={p.id} onClick={()=>setSelectedPostId(p.id)} className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap border transition-all ${selectedPostId===p.id?'bg-brand-600 text-white border-brand-500':'bg-[#0d121f] border-gray-800 text-gray-400'}`}><span className="uppercase text-[10px] text-gray-400 mr-1.5">{p.platform}</span> {p.id.slice(0,8)}</button>)}
      </div>

      <div className="bg-[#0d121f] border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-white mb-4">Sentiment Trajectory Windows</h3>
        {trajectory?.windows ? <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {Object.entries(trajectory.windows).map(([wKey, wData]) => (
            <div key={wKey} className="bg-gray-950 border border-gray-800 rounded-xl p-4">
              <span className="text-[10px] uppercase font-bold text-gray-500">{wKey}</span>
              <div className="text-2xl font-black text-emerald-400 mt-2">{wData.average_sentiment?.toFixed(2) || '0.00'}</div>
              <div className="text-xs text-gray-300 mt-1 capitalize">{wData.dominant_sentiment || 'Neutral'}</div>
              <div className="mt-3 text-[11px] text-gray-500">{wData.total_comments || 0} comments</div>
            </div>
          ))}
        </div> : <div className="py-12 text-center text-sm text-gray-500">No trajectory records yet. Sync post comments to process sentiment windows.</div>}
      </div>
    </div>}
  </div>;
}