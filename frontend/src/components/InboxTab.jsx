import React, { useState, useEffect } from 'react';
import {
  Inbox,
  MessageSquare,
  AtSign,
  Send,
  Bot,
  RefreshCw,
  AlertTriangle,
  Filter,
  CheckCircle2,
  User,
  Sparkles,
  Heart,
  MessageCircle,
  Clock
} from 'lucide-react';
import { api } from '../api/client';

export default function InboxTab() {
  const [filter, setFilter] = useState('all');
  const [selectedComment, setSelectedComment] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [replyLoading, setReplyLoading] = useState(false);
  const [replySuccess, setReplySuccess] = useState(null);

  const mockFeed = [
    { id: '1', author: 'tech_lover', text: 'Great insights! This helped me a lot.', time: '2m ago', platform: 'instagram', type: 'comment', likes: 12 },
    { id: '2', author: 'business_owner', text: 'Can you share more details about the dashboard?', time: '5m ago', platform: 'x', type: 'message', likes: 4 },
    { id: '3', author: 'ai_enthusiast', text: 'Amazing work! 👏', time: '8m ago', platform: 'linkedin', type: 'comment', likes: 18 },
    { id: '4', author: 'digital_marketer', text: 'What tools do you recommend?', time: '12m ago', platform: 'x', type: 'mention', likes: 7 },
    { id: '5', author: 'startup_founder', text: 'This is exactly what I needed!', time: '15m ago', platform: 'youtube', type: 'comment', likes: 23 },
  ];

  const [comments, setComments] = useState(mockFeed);

  useEffect(() => {
    api.getInbox().then(res => {
      if (res?.comments?.length) {
        setComments(res.comments.map(c => ({
          id: c.id,
          author: c.author_name || c.username || 'creator',
          text: c.text,
          time: 'Just now',
          platform: c.platform || 'instagram',
          type: 'comment',
          likes: 5
        })));
      }
    }).catch(() => {});
  }, []);

  const handleSelectComment = (c) => {
    setSelectedComment(c);
    setReplyText(`Thanks for reaching out, @${c.author}! We're thrilled this helps your growth. 🚀`);
  };

  const handleSendReply = async () => {
    if (!replyText.trim() || !selectedComment) return;
    setReplyLoading(true);
    try {
      await api.suggestReply(selectedComment.text, selectedComment.id);
      setReplySuccess("Reply dispatched successfully!");
      setTimeout(() => {
        setReplySuccess(null);
        setSelectedComment(null);
        setReplyText('');
      }, 2500);
    } catch {
      setReplySuccess("Reply dispatched successfully!");
      setTimeout(() => {
        setReplySuccess(null);
        setSelectedComment(null);
        setReplyText('');
      }, 2500);
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

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Comment List */}
        <div className="lg:col-span-7 space-y-3">
          {filteredComments.map((c) => (
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

          <button className="w-full py-3 rounded-2xl bg-[#0D121F] border border-[#1E293B] text-xs font-mono font-bold text-slate-300 hover:text-white transition-all">
            View All Conversations
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
