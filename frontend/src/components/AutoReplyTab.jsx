import React, { useState } from 'react';
import {
  Bot,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldCheck,
  Zap,
  ArrowRight,
  Send,
  Sparkles
} from 'lucide-react';

export default function AutoReplyTab() {
  const [pendingApprovals, setPendingApprovals] = useState([
    {
      id: "apr_1",
      platform: "Instagram",
      author: "@growth_agency",
      comment: "What are your enterprise subscription rates for a team of 15 members?",
      intent: "pricing_inquiry",
      confidence: 89.2,
      action: "approval_required",
      suggested_reply: "Thanks for reaching out! Our team plan starts at $49/mo with full multi-channel automation. I've sent you a direct message with full details! 🚀",
    },
    {
      id: "apr_2",
      platform: "LinkedIn",
      author: "David Miller",
      comment: "Is there documentation available for the custom WebSub webhook endpoints?",
      intent: "general_inquiry",
      confidence: 84.5,
      action: "approval_required",
      suggested_reply: "Hi David, yes! Full technical documentation for our WebSub and Account Activity webhooks is available in our developer portal at docs.aismm.com 👍",
    },
  ]);

  const [approvedList, setApprovedList] = useState([]);

  const handleApprove = (id) => {
    const item = pendingApprovals.find(p => p.id === id);
    if (item) {
      setApprovedList([...approvedList, item]);
      setPendingApprovals(pendingApprovals.filter(p => p.id !== id));
    }
  };

  const handleReject = (id) => {
    setPendingApprovals(pendingApprovals.filter(p => p.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">Auto-Reply Engine & Human-in-the-Loop</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            TF-IDF + Multinomial Logistic Regression (88.5% accuracy) with automated confidence gating (CLAUDE.md Section 22)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300">
            Policy: ≥0.90 Auto • 0.70-0.90 Approval • &lt;0.70 Manual
          </span>
        </div>
      </div>

      {/* Human-in-the-Loop Review Queue */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-sm text-gray-200">Pending Human Approvals ({pendingApprovals.length})</h3>
            <p className="text-xs text-gray-400">Comments classified between 70% and 90% confidence awaiting team review</p>
          </div>
          <span className="text-xs text-amber-400 font-bold px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20">
            {pendingApprovals.length} Awaiting Approval
          </span>
        </div>

        {pendingApprovals.length === 0 ? (
          <div className="p-8 rounded-xl bg-gray-950 border border-gray-800 text-center text-xs text-gray-400">
            <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
            <div className="font-bold text-gray-200">Approval Inbox Clean</div>
            <div>All classified comments have been processed or automatically handled.</div>
          </div>
        ) : (
          <div className="space-y-4">
            {pendingApprovals.map((item) => (
              <div
                key={item.id}
                className="p-5 rounded-xl bg-gray-950 border border-gray-800/80 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-brand-400">{item.author}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-gray-900 text-gray-400 border border-gray-800">
                      {item.platform}
                    </span>
                    <span className="text-[10px] text-amber-400 font-semibold px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                      {item.intent.replace("_", " ")} ({item.confidence}%)
                    </span>
                  </div>
                </div>

                <p className="text-xs text-gray-300 italic bg-gray-900/50 p-2.5 rounded-lg border border-gray-800/60">
                  "{item.comment}"
                </p>

                <div className="p-3.5 rounded-xl bg-brand-950/20 border border-brand-500/30">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-brand-400 mb-1 flex items-center space-x-1.5">
                    <Bot className="h-3.5 w-3.5" />
                    <span>AI Generated Response (Ready to Dispatch)</span>
                  </div>
                  <p className="text-xs text-gray-200 leading-relaxed">
                    {item.suggested_reply}
                  </p>
                </div>

                <div className="flex items-center justify-end space-x-3 pt-2">
                  <button
                    onClick={() => handleReject(item.id)}
                    className="px-3.5 py-1.5 rounded-lg bg-gray-900 hover:bg-gray-800 text-gray-400 text-xs font-semibold border border-gray-800"
                  >
                    Dismiss / Manual
                  </button>
                  <button
                    onClick={() => handleApprove(item.id)}
                    className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-600/20 flex items-center space-x-1.5"
                  >
                    <Send className="h-3.5 w-3.5" />
                    <span>Approve & Send</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Automatically Dispatched Logs */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-gray-200 mb-3">Recently Dispatched Automated Replies (&gt;90% Confidence)</h3>
        <div className="space-y-2.5 text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-gray-950 border border-gray-800/60 text-gray-300">
            <div>
              <span className="font-bold text-emerald-400 mr-2">[Auto-Dispatched]</span>
              <span>Replied to <strong>@sarah_tech</strong> on Instagram (Pricing Inquiry • 94.2% Confidence)</span>
            </div>
            <span className="text-[10px] text-gray-500">14m ago</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-gray-950 border border-gray-800/60 text-gray-300">
            <div>
              <span className="font-bold text-emerald-400 mr-2">[Auto-Dispatched]</span>
              <span>Replied to <strong>Alex Reed</strong> on LinkedIn (Praise • 96.8% Confidence)</span>
            </div>
            <span className="text-[10px] text-gray-500">45m ago</span>
          </div>
        </div>
      </div>
    </div>
  );
}
