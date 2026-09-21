import React, { useState, useEffect } from 'react';
import {
  Inbox,
  Send,
  Bot,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { api } from '../api/client';

export default function InboxTab() {
  const [filter, setFilter] = useState('all');
  const [selectedComment, setSelectedComment] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [replyLoading, setReplyLoading] = useState(false);
  const [replySuccess, setReplySuccess] = useState(null);
  const [replyError, setReplyError] = useState(null);
  const [aiSuggestion, setAiSuggestion] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState(null);

  const [comments, setComments] = useState([]);
  const [inboxEmpty, setInboxEmpty] = useState(false);

  const loadInbox = () => {
    api.getInbox().then(res => {
      if (res?.comments?.length) {
        setComments(res.comments.map(c => ({
          id: c.id,
          author: c.author_name || c.username || 'creator',
          text: c.text,
          time: c.created_at ? new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent',
          platform: c.platform || 'instagram',
          type: 'comment',
          likes: 0
        })));
        setInboxEmpty(false);
      } else {
        setInboxEmpty(true);
      }
    }).catch((err) => {
      setSyncError(err.message);
      setInboxEmpty(true);
    });
  };

  useEffect(() => {
    loadInbox();
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    setSyncError(null);
    try {
      const res = await api.syncInbox();
      if (res?.errors?.length) {
        setSyncError(res.errors.join('; '));
      }
      loadInbox();
    } catch (err) {
      setSyncError(`Sync failed: ${err.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const handleSelectComment = async (c) => {
    setSelectedComment(c);
    setReplyError(null);
    setReplySuccess(null);
    setAiLoading(true);
    try {
      const suggestion = await api.suggestReply(c.text, c.id, 'automatic');
      setAiSuggestion(suggestion);
      setReplyText(suggestion.suggested_reply || `Thanks for reaching out, @${c.author}!`);
    } catch {
      setReplyText(`Thanks for reaching out, @${c.author}!`);
      setAiSuggestion(null);
    } finally {
      setAiLoading(false);
    }
  };

  const handleSendReply = async () => {
    if (!replyText.trim() || !selectedComment) return;
    setReplyLoading(true);
    setReplyError(null);
    setReplySuccess(null);
    try {
      await api.replyComment(selectedComment.platform || 'instagram', selectedComment.id, replyText);
      setReplySuccess("Reply dispatched successfully to platform!");
      setTimeout(() => {
        setReplySuccess(null);
        setSelectedComment(null);
        setReplyText('');
        setAiSuggestion(null);
      }, 2500);
    } catch (err) {
      setReplyError(err.message || "Failed to dispatch reply to social network.");
    } finally {
      setReplyLoading(false);
    }
  };

  const filteredComments = comments.filter((c) => {
    if (filter === 'messages') return c.type === 'message';
    if (filter === 'comments') return c.type === 'comment';
    if (filter === 'mentions') return c.type === 'mention' || c.text?.includes('@');
    return true;
  });

  return (
    <div className="space-y-6 animate-fadeIn font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono">09 Inbox & Engagement</h2>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">
            Unified audience engagement stream, comment synchronization, and AI auto-reply approval
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="px-3.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-[#0D121F] border border-[#1E293B] text-slate-300 hover:text-white flex items-center gap-2 transition-all disabled:opacity-50"
          >
            <RefreshCw size={13} className={syncing ? "animate-spin text-cyan-400" : ""} />
            <span>{syncing ? "Syncing…" : "Sync comments"}</span>
          </button>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 p-1 bg-[#0D121F] rounded-2xl border border-[#1E293B]">
            {['all', 'messages', 'comments', 'mentions'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold capitalize transition-all ${
                  filter === f
                    ? "bg-brand-600 text-white shadow-md"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      {syncError && (
        <div className="p-3 bg-amber-950/20 border border-amber-500/30 rounded-xl text-xs text-amber-300 font-mono flex items-center gap-2">
          <AlertTriangle size={14} className="shrink-0" />
          <span>{syncError}</span>
        </div>
      )}

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Comment List */}
        <div className="lg:col-span-7 space-y-3">
          {inboxEmpty ? (
            <div className="p-8 rounded-2xl bg-[#0D121F] border border-[#1E293B] text-center space-y-2">
              <Inbox size={40} className="mx-auto text-slate-500" />
              <p className="text-sm font-mono text-slate-300">No conversations in your inbox yet</p>
              <p className="text-xs text-slate-500 font-mono">Comments and messages from your audience will appear here</p>
            </div>
          ) : filteredComments.map((c) => (
            <div
              key={c.id}
              onClick={() => handleSelectComment(c)}
              className={`p-4 rounded-2xl border transition-all cursor-pointer space-y-2 ${
                selectedComment?.id === c.id
                  ? 'bg-[#0D121F] border-brand-500/60 shadow-lg shadow-brand-500/10'
                  : 'bg-[#0D121F] border-[#1E293B] hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center text-white font-bold text-xs">
                    {c.author.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-white font-mono">@{c.author}</p>
                    <span className="text-[10px] text-slate-500 font-mono capitalize">{c.platform}</span>
                  </div>
                </div>
                <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                  <Clock size={10} /> {c.time}
                </span>
              </div>

              <p className="text-xs text-slate-300 font-sans leading-relaxed pl-10">
                {c.text}
              </p>
            </div>
          ))}

          <button onClick={loadInbox} className="w-full py-3 rounded-2xl bg-[#0D121F] border border-[#1E293B] text-xs font-mono font-bold text-slate-300 hover:text-white transition-all">
            Refresh Inbox
          </button>
        </div>

        {/* Reply Panel */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-[#0D121F] border border-[#1E293B] shadow-xl space-y-5 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white font-mono flex items-center gap-2">
              <Bot size={18} className="text-cyan-400" />
              <span>AI Auto-Reply Assistant</span>
            </h3>
            <p className="text-xs text-slate-400 font-mono mt-1">
              {selectedComment ? `Responding to @${selectedComment.author}` : "Select a comment to draft an AI response"}
            </p>

            {aiLoading && (
              <div className="mt-2 text-xs text-cyan-400 font-mono flex items-center gap-2">
                <RefreshCw size={12} className="animate-spin" />
                <span>Classifying intent with TF-IDF model…</span>
              </div>
            )}

            {aiSuggestion && !aiLoading && (
              <div className="mt-3 p-3 rounded-xl bg-[#07090E] border border-[#1E293B] flex items-center justify-between text-xs font-mono">
                <div>
                  <span className="text-slate-500 text-[10px] uppercase block font-bold">Classified Intent</span>
                  <span className="text-white font-semibold capitalize">{aiSuggestion.intent?.replace('_', ' ')}</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 text-[10px] uppercase block font-bold">Routing</span>
                  <span className="text-emerald-400 font-semibold uppercase">{aiSuggestion.routing_action?.replace('_', ' ')}</span>
                </div>
              </div>
            )}
          </div>

          <div className="space-y-3">
            <textarea
              rows={6}
              disabled={!selectedComment}
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              placeholder="Select a conversation to generate or edit a reply..."
              className="w-full bg-[#07090E] border border-[#1E293B] rounded-2xl p-4 text-xs text-slate-200 focus:border-brand-500 focus:outline-none font-mono resize-none leading-relaxed disabled:opacity-50"
            />

            {replySuccess && (
              <div className="p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-xl text-xs text-emerald-400 font-mono flex items-center gap-2">
                <CheckCircle2 size={14} />
                <span>{replySuccess}</span>
              </div>
            )}

            {replyError && (
              <div className="p-3 bg-rose-950/20 border border-rose-500/30 rounded-xl text-xs text-rose-300 font-mono flex items-center gap-2">
                <AlertTriangle size={14} />
                <span>{replyError}</span>
              </div>
            )}
          </div>

          <div className="pt-2 flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-mono">
              Human-in-the-Loop Mode
            </span>
            <button
              onClick={handleSendReply}
              disabled={!selectedComment || replyLoading}
              className="px-5 py-2.5 bg-gradient-to-r from-brand-600 to-cyan-600 hover:opacity-90 disabled:opacity-50 text-white rounded-xl text-xs font-bold font-mono transition-all shadow-md shadow-brand-600/20 flex items-center gap-2"
            >
              <Send size={14} />
              <span>{replyLoading ? "Sending..." : "Send Reply"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
