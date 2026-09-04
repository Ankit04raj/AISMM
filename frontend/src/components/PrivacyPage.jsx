import React from 'react';
import { Shield, ArrowLeft, Lock, CheckCircle2 } from 'lucide-react';

export default function PrivacyPage({ onBack }) {
  return (
    <div className="min-h-screen bg-[#07090E] text-[#F1F5F9] font-['Plus_Jakarta_Sans'] py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8 animate-fadeIn">
      <button
        onClick={onBack}
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white px-3 py-1.5 rounded-xl bg-[#0D121F] border border-[#1E293B] transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Studio</span>
      </button>

      <div className="border-b border-[#1E293B] pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-bold uppercase mb-3">
          <Lock className="w-3.5 h-3.5 text-cyan-400" />
          <span>Data Protection & Privacy</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">Privacy Policy</h1>
        <p className="text-xs text-slate-400 mt-2 font-mono">Last Updated: September 4, 2026 • AISMM Platform v1.0</p>
      </div>

      <div className="space-y-6 text-xs text-slate-300 leading-relaxed bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 shadow-xl">
        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-cyan-400">1. Data Collected & Stored</h2>
          <p>
            AISMM collects only the information necessary to provide multi-platform social management: user email, hashed authentication password, connected social account public IDs, usernames, and authorized OAuth tokens.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-cyan-400">2. Encryption at Rest & Token Protection</h2>
          <p>
            All social tokens and client secrets are stored exclusively in our AES-256 authenticated SecretVault with dynamic PBKDF2 per-record salts. Raw OAuth secrets are never logged in plain text or rendered in client-side bundles.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-cyan-400">3. Artificial Intelligence & Analytics Data Processing</h2>
          <p>
            Content analyzed by our AI engines (sentiment, caption scoring, hashtag recommendation, scheduling prediction) is processed in isolated session memory. We do not use your private drafts to train public foundational language models.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-cyan-400">4. Third-Party Platform APIs</h2>
          <p>
            When you connect Instagram, Facebook, X, LinkedIn, or YouTube, data is transmitted strictly over TLS 1.3 encrypted connections directly to the respective platform's official API endpoints.
          </p>
        </section>
      </div>
    </div>
  );
}
