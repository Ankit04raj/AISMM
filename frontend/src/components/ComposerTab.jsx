import React, { useState, useEffect } from 'react';
import { Send, Calendar, Sparkles, Save, Trash2 } from 'lucide-react';
import { api } from '../api/client';

const empty = { text:'', platforms:[], mediaUrl:'', mediaType:'image', scheduledAt:'' };
function readDraft() { try { return {...empty,...JSON.parse(sessionStorage.getItem('aismm_composer')||'{}')}; } catch { return empty; } }
export default function ComposerTab({ onNavigateTab }) {
  const [draft,setDraft] = useState(readDraft); const [accounts,setAccounts] = useState([]);
  const [loading,setLoading] = useState(true); const [busy,setBusy] = useState(false);
  const [error,setError] = useState(''); const [result,setResult] = useState(null); const [analysis,setAnalysis] = useState(null);
  useEffect(()=>{api.getAccounts().then(data=>setAccounts(data.accounts||[])).catch(err=>setError(err.message)).finally(()=>setLoading(false));},[]);
  useEffect(()=>{try{sessionStorage.setItem('aismm_composer',JSON.stringify(draft));}catch{/* Storage blocked: in-memory draft still retained. */}},[draft]);
  const update = (field,value)=>setDraft(d=>({...d,[field]:value}));
  const platforms=[...new Set(accounts.filter(a=>a.is_active).map(a=>a.platform))];
  async function analyze() {setBusy(true);setError('');try{const data=await api.optimizeContentAll({text:draft.text,platforms:draft.platforms,top_k_hashtags:5});setAnalysis(data);}catch(err){setError(err.message);}finally{setBusy(false);}}
  async function publish(scheduled) {
    if(!draft.text.trim()||!draft.platforms.length){setError('Add content and select at least one connected platform.');return;}
    if(scheduled&&(!draft.scheduledAt||new Date(draft.scheduledAt)<=new Date())){setError('Choose a future date and time.');return;}
    if(!window.confirm(scheduled?'Schedule this post for the selected accounts?':'Publish this post now to the selected accounts?'))return;
    setBusy(true);setError('');setResult(null);
    try {const data=await api.publishMultiPlatform({platforms:draft.platforms,content_type:'post',text:draft.text,caption:draft.text,publish_now:!scheduled,scheduled_at:scheduled?new Date(draft.scheduledAt).toISOString():null,media:draft.mediaUrl?[{type:draft.mediaType,url:draft.mediaUrl}]:[]});setResult(data);
      if(data.overall_status==='failed')setError('One or more publications failed. Review each result below; your draft is retained.');
    }catch(err){setError(err.message);}finally{setBusy(false);}
  }
  return <div className="space-y-6"><header className="flex flex-wrap justify-between items-center gap-4"><div><p className="text-xs text-cyan-300 uppercase tracking-widest mb-2">Create with intent</p><h1 className="text-2xl font-bold">Content composer</h1><p className="text-slate-400 mt-2">One draft. Your connected channels. You approve every publish.</p></div><span className="text-sm text-slate-400 flex items-center gap-2"><Save size={16}/> Draft saved in this browser tab</span></header>
    {error&&<div className="error" role="alert">{error}</div>}
    {loading?<p role="status">Loading your connected accounts…</p>:platforms.length===0&&<div className="notice flex flex-wrap gap-4 justify-between items-center"><p>Connect a platform before publishing. You can still write and save your draft.</p><button className="btn" onClick={()=>onNavigateTab('platforms')}>Connect a platform</button></div>}
    <div className="grid xl:grid-cols-5 gap-6"><section className="panel xl:col-span-3 space-y-6"><fieldset><legend className="font-semibold mb-3">Publish to</legend><div className="flex flex-wrap gap-2">{platforms.map(platform=><label key={platform} className="btn-secondary gap-3"><input type="checkbox" checked={draft.platforms.includes(platform)} onChange={e=>update('platforms',e.target.checked?[...draft.platforms,platform]:draft.platforms.filter(p=>p!==platform))}/>{platform}</label>)}{!platforms.length&&<span className="text-slate-500 text-sm">No connected channels</span>}</div></fieldset>
      <label className="block font-semibold">Post content<textarea className="field mt-3 min-h-56 resize-y font-normal" placeholder="What would you like to share?" value={draft.text} onChange={e=>update('text',e.target.value)}/><span className="block text-right text-xs text-slate-400 mt-2">{draft.text.length} characters</span></label>
      <div className="space-y-3"><label className="block text-sm">Media URL (optional)<input className="field mt-2" type="url" placeholder="https://your-approved-media-host/image.jpg" value={draft.mediaUrl} onChange={e=>update('mediaUrl',e.target.value)}/></label><p className="text-xs text-slate-400">Use a public HTTPS URL on an operator-approved media host. Local file uploads are not available yet. Instagram and YouTube require compatible media.</p><label className="block text-sm">Media type<select className="field mt-2" value={draft.mediaType} onChange={e=>update('mediaType',e.target.value)}><option value="image">Image</option><option value="video">Video</option></select></label></div>
      <div className="flex flex-wrap gap-3"><button className="btn-secondary" disabled={busy||!draft.text||!draft.platforms.length} onClick={analyze}><Sparkles size={16}/>Analyze with AI</button><button className="btn-secondary" onClick={()=>{if(confirm('Discard this saved draft?')){setDraft(empty);setAnalysis(null);setResult(null);}}}><Trash2 size={16}/>Discard draft</button></div>
    </section><aside className="xl:col-span-2 space-y-6"><section className="panel space-y-5"><h2 className="text-lg font-semibold">Ready when you are</h2><p className="text-sm text-slate-400">Publishing sends content to live accounts. Review your text, channels, and permissions before continuing.</p><button className="btn w-full" disabled={busy||!draft.platforms.length||!draft.text} onClick={()=>publish(false)}><Send size={16}/>{busy?'Working…':'Publish now'}</button><div className="border-t border-slate-800 pt-5"><label className="block text-sm">Schedule in your local timezone<input className="field mt-2" type="datetime-local" value={draft.scheduledAt} onChange={e=>update('scheduledAt',e.target.value)}/></label><p className="text-xs text-slate-400 mt-2">{Intl.DateTimeFormat().resolvedOptions().timeZone} · Stored and dispatched in UTC</p><button className="btn-secondary w-full mt-4" disabled={busy||!draft.platforms.length||!draft.text} onClick={()=>publish(true)}><Calendar size={16}/>Schedule post</button></div></section>
      {result&&<section className="panel space-y-3" aria-live="polite"><h2 className="font-semibold">Publication result: {result.overall_status}</h2>{Object.entries(result.results||{}).map(([platform,res])=><div key={platform} className="text-sm border-t border-slate-800 pt-3"><strong>{platform}</strong>: {res.status}{res.permalink&&<a href={res.permalink} target="_blank" rel="noreferrer" className="block text-brand-300 underline mt-1">View published post</a>}{res.platform_data?.error&&<p className="text-rose-300 mt-1">{res.platform_data.error}</p>}</div>)}</section>}
      {analysis&&<section className="panel"><h2 className="font-semibold mb-4">AI analysis</h2><p className="text-sm text-slate-400 mb-4">Suggestions only — your draft is not changed automatically.</p><pre className="text-xs whitespace-pre-wrap break-words max-h-96 overflow-auto">{JSON.stringify(analysis,null,2)}</pre></section>}
    </aside></div>
  </div>;
}
