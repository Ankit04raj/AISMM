import React, { useEffect, useState } from 'react';
import { Sparkles, Send, Calendar, Eye, AlertTriangle, RefreshCw, CheckCircle2, Image, Video, Layers, Hash } from 'lucide-react';
import { api } from '../api/client';

const availablePlatforms = [
  { id: 'instagram', name: 'Instagram', maxChars: 2200, color: 'from-pink-500 to-purple-600' },
  { id: 'facebook', name: 'Facebook', maxChars: 63206, color: 'from-blue-600 to-indigo-600' },
  { id: 'twitter', name: 'X (Twitter)', maxChars: 280, color: 'from-slate-700 to-black' },
  { id: 'linkedin', name: 'LinkedIn', maxChars: 3000, color: 'from-blue-700 to-cyan-700' },
  { id: 'youtube', name: 'YouTube', maxChars: 5000, color: 'from-red-600 to-rose-700' },
];

export default function ComposerTab() {
  const [caption, setCaption] = useState('Excited to unveil our new AI Social Media Management platform! 🚀 Built with modular platform adapters, ML scheduling, and dual-phase sentiment analysis. Link in bio! #AISMM #AI #Tech');
  const [selectedPlatforms, setSelectedPlatforms] = useState(['instagram', 'facebook', 'twitter', 'linkedin']);
  const [previewPlatform, setPreviewPlatform] = useState('instagram');
  const [mediaType, setMediaType] = useState('image');
  const [mediaUrls, setMediaUrls] = useState([
    { type: 'image', url: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=80' }
  ]);
  const [analysis, setAnalysis] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);

  const togglePlatform = (pId) => {
    setSelectedPlatforms((current) =>
      current.includes(pId)
        ? (current.length > 1 ? current.filter((item) => item !== pId) : current)
        : [...current, pId]
    );
  };

  useEffect(() => {
    if (!caption.trim() || !selectedPlatforms.length) {
      setAnalysis(null);
      setPreview(null);
      return undefined;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const [aiData, previewData] = await Promise.all([
          api.optimizeContentAll({ text: caption, platforms: selectedPlatforms, top_k_hashtags: 5 }),
          api.previewContent({ platforms: selectedPlatforms, content_type: mediaType === 'image' ? 'post' : mediaType, caption, text: caption }),
        ]);
        setAnalysis(aiData);
        setPreview(previewData);
      } catch (err) {
        setError(`Unable to reach AISMM backend: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [caption, selectedPlatforms, mediaType]);

  const handleAIOptimize = async () => {
    if (!caption.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.optimizeContentAll({ text: caption, platforms: selectedPlatforms, top_k_hashtags: 5 });
      setAnalysis(data);
      const targetPlatform = previewPlatform || selectedPlatforms[0];
      const variant = data.platform_variants?.[targetPlatform]?.text;
      if (variant) {
        setCaption(variant);
      }
    } catch (err) {
      setError(`Unable to reach AISMM backend: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!caption.trim() || !selectedPlatforms.length) return;
    setPublishing(true);
    setError(null);
    setStatus(null);
    try {
      const data = await api.publishMultiPlatform({
        platforms: selectedPlatforms,
        content_type: mediaType === 'image' ? 'post' : mediaType,
        caption,
        text: caption,
        publish_now: true,
        media: mediaUrls,
      });
      setStatus(data.overall_status || 'published');
    } catch (err) {
      setError(`Unable to publish through AISMM backend: ${err.message}`);
    } finally {
      setPublishing(false);
    }
  };

  const currentPlatformLimit = availablePlatforms.find(p => p.id === previewPlatform)?.maxChars || 2200;

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white">Universal Post Composer & AI Studio</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Compose once with character verification, media attachments, and simultaneous multi-platform dispatch
          </p>
        </div>
        {status && (
          <span className="px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold flex gap-2 items-center animate-bounce">
            <CheckCircle2 className="w-4 h-4" />
            <span>Published Successfully ({status})</span>
          </span>
        )}
      </div>

      {error && (
        <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-2xl flex items-center justify-between text-xs text-rose-300">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="underline hover:text-white">Dismiss</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Composer Editor & Controls */}
        <div className="lg:col-span-7 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl space-y-5">
          {/* Target Platform Chips */}
          <div>
            <label className="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-2.5">
              Publishing Channels ({selectedPlatforms.length} / 5)
            </label>
            <div className="flex flex-wrap gap-2">
              {availablePlatforms.map((p) => {
                const isSelected = selectedPlatforms.includes(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => togglePlatform(p.id)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
                      isSelected
                        ? "bg-brand-600 text-white shadow-md shadow-brand-600/30"
                        : "bg-[#07090E] border border-[#1E293B] text-slate-400 hover:text-white"
                    }`}
                  >
                    <span className={`w-2 h-2 rounded-full ${isSelected ? "bg-white" : "bg-slate-600"}`} />
                    <span>{p.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Caption Textarea & Character Counter */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-[11px] uppercase tracking-wider text-slate-400 font-bold">
                Primary Content / Caption
              </label>
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className={caption.length > currentPlatformLimit ? "text-rose-400 font-bold" : "text-slate-400"}>
                  {caption.length} / {currentPlatformLimit} chars
                </span>
                <span className="text-slate-500">
                  {caption.split(/\s+/).filter(Boolean).length} words
                </span>
              </div>
            </div>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              rows={8}
              placeholder="Write your post content here..."
              className="w-full bg-[#07090E] border border-[#1E293B] rounded-2xl p-4 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none leading-relaxed"
            />
          </div>

          {/* Media Tray */}
          <div>
            <label className="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-2">
              Media Attachment Format
            </label>
            <div className="flex gap-2 mb-3">
              {[
                { id: 'image', label: 'Single Image', icon: Image },
                { id: 'video', label: 'Video / Reel', icon: Video },
                { id: 'carousel', label: 'Carousel (Multi)', icon: Layers },
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setMediaType(id)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                    mediaType === id
                      ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/20'
                      : 'bg-[#07090E] border border-[#1E293B] text-slate-400 hover:text-white'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={handleAIOptimize}
              disabled={loading || !caption.trim()}
              className="flex-1 min-w-[160px] py-3 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 rounded-xl text-xs font-bold text-white disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-brand-600/20 transition-all"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              <span>{loading ? 'Optimizing with AI...' : 'AI Auto-Optimize'}</span>
            </button>
            <button
              onClick={handlePublish}
              disabled={publishing || !caption.trim() || !selectedPlatforms.length}
              className="flex-1 min-w-[160px] py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-xs font-bold text-white disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 transition-all"
            >
              {publishing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              <span>{publishing ? 'Publishing...' : 'Publish to All Channels'}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Live Native Preview */}
        <div className="lg:col-span-5 bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex justify-between items-center border-b border-[#1E293B] pb-3">
            <div>
              <h3 className="font-bold text-sm text-white">Live Native Feed Preview</h3>
              <p className="text-xs text-slate-400">Direct payload inspection</p>
            </div>
            <div className="flex gap-1">
              {availablePlatforms.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPreviewPlatform(p.id)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase transition-all ${
                    previewPlatform === p.id
                      ? "bg-brand-600 text-white"
                      : "bg-[#07090E] text-slate-400 hover:text-white border border-[#1E293B]"
                  }`}
                >
                  {p.id.slice(0, 2)}
                </button>
              ))}
            </div>
          </div>

          {/* Preview Canvas */}
          <div className="bg-[#07090E] border border-[#1E293B] rounded-2xl overflow-hidden shadow-inner">
            {/* Mock Feed Header */}
            <div className="p-3 bg-[#0D121F] border-b border-[#1E293B] flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-brand-500 to-cyan-500 flex items-center justify-center text-white text-xs font-bold">
                A
              </div>
              <div>
                <div className="text-xs font-bold text-slate-100">AISMM Studio</div>
                <div className="text-[10px] text-slate-500 capitalize">{previewPlatform} Feed • Just now</div>
              </div>
            </div>

            {/* Media Canvas Mock */}
            <div className="h-44 bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-950 flex flex-col items-center justify-center text-slate-500">
              <Image className="w-7 h-7 text-brand-400 mb-1.5" />
              <span className="text-xs font-semibold text-slate-300">1080 × 1080 Visual Payload</span>
              <span className="text-[10px] text-slate-500 capitalize">{mediaType} formatted for {previewPlatform}</span>
            </div>

            {/* Content Text */}
            <div className="p-4 space-y-2 text-xs">
              <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">
                {preview?.previews?.[previewPlatform]?.caption || preview?.previews?.[previewPlatform]?.text || caption}
              </p>
            </div>
          </div>

          {/* AI Signal Quality */}
          {analysis && (
            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="p-3 bg-[#07090E] rounded-xl border border-[#1E293B]">
                <span className="text-[10px] uppercase font-bold text-slate-500">Sentiment</span>
                <p className="text-xs font-bold text-emerald-400 mt-1">{analysis.sentiment?.label || 'Positive'}</p>
              </div>
              <div className="p-3 bg-[#07090E] rounded-xl border border-[#1E293B]">
                <span className="text-[10px] uppercase font-bold text-slate-500">Caption Score</span>
                <p className="text-xs font-bold text-cyan-400 mt-1">{analysis.caption_analysis?.score || 85} / 100</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
