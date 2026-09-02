import React, { useState } from 'react';
import {
  Sparkles,
  Share2,
  Image as ImageIcon,
  Video,
  Send,
  Calendar,
  Layers,
  Smile,
  Hash,
  CheckCircle2,
  AlertCircle,
  Eye,
  RefreshCw,
  Zap
} from 'lucide-react';
import { api } from '../api/client';

export default function ComposerTab() {
  const [caption, setCaption] = useState(
    "Excited to unveil our new AI Social Media Management architecture! 🚀 Built with modular platform adapters, ML scheduling, and dual-phase sentiment analysis. What feature are you most curious about? Link in bio! #AISMM #AI #Tech"
  );
  const [selectedPlatforms, setSelectedPlatforms] = useState(["instagram", "facebook", "x", "linkedin"]);
  const [previewPlatform, setPreviewPlatform] = useState("instagram");
  const [mediaType, setMediaType] = useState("image");
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [qualityScore, setQualityScore] = useState(86.8);
  const [sentimentResult, setSentimentResult] = useState({ label: "Very Positive", score: "+0.72", confidence: "89.4%" });
  const [recommendedHashtags, setRecommendedHashtags] = useState(["#ai", "#artificialintelligence", "#automation", "#machinelearning", "#tech"]);
  const [publishStatus, setPublishStatus] = useState(null);

  const togglePlatform = (id) => {
    if (selectedPlatforms.includes(id)) {
      setSelectedPlatforms(selectedPlatforms.filter(p => p !== id));
    } else {
      setSelectedPlatforms([...selectedPlatforms, id]);
    }
  };

  const handleAIOptimize = async () => {
    setIsOptimizing(true);
    setTimeout(() => {
      setQualityScore(92.4);
      setSentimentResult({ label: "Very Positive", score: "+0.84", confidence: "94.2%" });
      setRecommendedHashtags(["#aismm", "#automation", "#digitalgrowth", "#futureoftech", "#ai"]);
      setIsOptimizing(false);
    }, 500);
  };

  const handlePublish = () => {
    setPublishStatus("publishing");
    setTimeout(() => {
      setPublishStatus("success");
      setTimeout(() => setPublishStatus(null), 4000);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">Universal Post Composer & AI Studio</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Create once, optimize with AI, and publish simultaneously to selected platforms (CLAUDE.md Section 8)
          </p>
        </div>
        {publishStatus === "success" && (
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold animate-bounce">
            <CheckCircle2 className="h-4 w-4" />
            <span>Successfully published across {selectedPlatforms.length} platforms!</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Composer Form */}
        <div className="lg:col-span-7 space-y-5">
          {/* Target Platform Selector */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-4 shadow-xl">
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2.5">
              Select Publishing Channels ({selectedPlatforms.length}/5)
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                { id: "instagram", name: "Instagram", color: "from-pink-500 to-purple-600" },
                { id: "facebook", name: "Facebook", color: "from-blue-600 to-indigo-600" },
                { id: "x", name: "X (Twitter)", color: "from-gray-700 to-black" },
                { id: "linkedin", name: "LinkedIn", color: "from-blue-700 to-cyan-700" },
                { id: "youtube", name: "YouTube", color: "from-red-600 to-rose-700" },
              ].map((p) => {
                const isSelected = selectedPlatforms.includes(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => togglePlatform(p.id)}
                    className={`px-3 py-2 rounded-xl text-xs font-bold flex items-center space-x-2 transition-all ${
                      isSelected
                        ? "bg-brand-600 text-white shadow-md shadow-brand-600/30"
                        : "bg-gray-950 border border-gray-800 text-gray-400 hover:text-gray-200"
                    }`}
                  >
                    <span className={`h-2 w-2 rounded-full ${isSelected ? "bg-white" : "bg-gray-600"}`}></span>
                    <span>{p.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Caption Editor & AI Controls */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-gray-400">
                Primary Content & Caption
              </label>
              <button
                onClick={handleAIOptimize}
                disabled={isOptimizing}
                className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold shadow-md shadow-brand-600/20 flex items-center space-x-1.5 transition-all"
              >
                <Sparkles className="h-3.5 w-3.5" />
                <span>{isOptimizing ? "Optimizing..." : "AI Auto-Optimize"}</span>
              </button>
            </div>

            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              rows={6}
              className="w-full bg-gray-950 border border-gray-800 rounded-xl p-4 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all resize-none leading-relaxed"
              placeholder="Write your primary message here..."
            />

            {/* Media Format Selector */}
            <div className="flex items-center space-x-2 pt-2 border-t border-gray-800">
              <span className="text-xs font-semibold text-gray-400 mr-2">Media Format:</span>
              {["image", "video", "carousel"].map((fmt) => (
                <button
                  key={fmt}
                  onClick={() => setMediaType(fmt)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-all ${
                    mediaType === fmt
                      ? "bg-gray-800 text-brand-400 border border-brand-500/30"
                      : "bg-gray-950 text-gray-400 border border-gray-800"
                  }`}
                >
                  {fmt}
                </button>
              ))}
            </div>

            {/* Top-K Hashtags */}
            <div className="pt-2">
              <div className="text-[11px] font-bold text-gray-400 mb-1.5 flex items-center justify-between">
                <span>Top-K Recommended Hashtags (93.1% Top-K Accuracy)</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {recommendedHashtags.map((tag) => (
                  <span
                    key={tag}
                    onClick={() => setCaption(c => c.includes(tag) ? c : `${c} ${tag}`)}
                    className="text-xs font-mono px-2 py-0.5 rounded-md bg-brand-500/10 text-brand-300 border border-brand-500/20 cursor-pointer hover:bg-brand-500/20 transition-all"
                  >
                    {tag} +
                  </span>
                ))}
              </div>
            </div>

            {/* AI Diagnostics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-3 border-t border-gray-800">
              <div className="p-2.5 rounded-xl bg-gray-950 border border-gray-800">
                <div className="text-[10px] text-gray-400">Quality Score</div>
                <div className="text-sm font-black text-emerald-400 mt-0.5">{qualityScore} / 100</div>
              </div>
              <div className="p-2.5 rounded-xl bg-gray-950 border border-gray-800">
                <div className="text-[10px] text-gray-400">Pre-Post Sentiment</div>
                <div className="text-sm font-black text-emerald-400 mt-0.5">{sentimentResult.label} ({sentimentResult.score})</div>
              </div>
              <div className="p-2.5 rounded-xl bg-gray-950 border border-gray-800 col-span-2 sm:col-span-1">
                <div className="text-[10px] text-gray-400">Peak Window</div>
                <div className="text-sm font-black text-indigo-400 mt-0.5">Wed 19:00 UTC</div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-800">
              <span className="text-xs text-gray-400">
                Targeting <strong className="text-white">{selectedPlatforms.length}</strong> channels
              </span>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handlePublish}
                  disabled={publishStatus === "publishing" || selectedPlatforms.length === 0}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-brand-600/30 flex items-center space-x-2 transition-all disabled:opacity-50"
                >
                  <Send className="h-3.5 w-3.5" />
                  <span>{publishStatus === "publishing" ? "Publishing..." : "Publish to All Channels"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Live Multi-Platform Native Preview Frame */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-gray-800">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-300 flex items-center space-x-2">
                <Eye className="h-4 w-4 text-brand-400" />
                <span>Live Native Preview</span>
              </span>
              <div className="flex space-x-1">
                {["instagram", "facebook", "x", "linkedin", "youtube"].map((p) => (
                  <button
                    key={p}
                    onClick={() => setPreviewPlatform(p)}
                    className={`px-2 py-1 rounded text-[10px] font-bold uppercase transition-all ${
                      previewPlatform === p ? "bg-brand-600 text-white" : "bg-gray-800 text-gray-400"
                    }`}
                  >
                    {p === "x" ? "X" : p.slice(0, 2)}
                  </button>
                ))}
              </div>
            </div>

            {/* Styled Native Preview Canvas */}
            <div className="mt-4 bg-gray-950 border border-gray-800 rounded-xl overflow-hidden shadow-inner">
              {/* Mock Header */}
              <div className="p-3 bg-gray-900/90 border-b border-gray-800/80 flex items-center space-x-2.5">
                <div className="h-7 w-7 rounded-full bg-gradient-to-tr from-brand-500 to-purple-600 flex items-center justify-center text-white text-xs font-black">
                  A
                </div>
                <div>
                  <div className="text-xs font-bold text-gray-200">AISMM Official</div>
                  <div className="text-[10px] text-gray-400 capitalize">{previewPlatform} Feed • Just now</div>
                </div>
              </div>

              {/* Mock Media Placeholder */}
              <div className="h-48 bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-950/40 flex flex-col items-center justify-center text-gray-500 relative">
                <div className="p-3 rounded-full bg-gray-800/80 mb-2">
                  <ImageIcon className="h-6 w-6 text-brand-400" />
                </div>
                <span className="text-xs font-semibold text-gray-400">High-Resolution Visual Asset (1080x1080)</span>
                <span className="text-[10px] text-gray-500">Auto-formatted for {previewPlatform}</span>
              </div>

              {/* Mock Content */}
              <div className="p-3.5 space-y-2 text-xs">
                <p className="text-gray-200 whitespace-pre-wrap leading-relaxed">
                  {caption}
                </p>
                <div className="text-[11px] text-brand-400 font-semibold">
                  #AISMM #AI #Tech #Innovation
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
