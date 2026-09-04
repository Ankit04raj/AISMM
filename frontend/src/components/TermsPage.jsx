import React from 'react';
import { Shield, ArrowLeft, Lock, FileText, CheckCircle2 } from 'lucide-react';

export default function TermsPage({ onBack }) {
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-300 text-xs font-bold uppercase mb-3">
          <FileText className="w-3.5 h-3.5 text-cyan-400" />
          <span>Legal Agreement</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">Terms of Service</h1>
        <p className="text-xs text-slate-400 mt-2 font-mono">Last Updated: September 4, 2026 • AISMM Platform v1.0</p>
      </div>

      <div className="space-y-6 text-xs text-slate-300 leading-relaxed bg-[#0D121F] border border-[#1E293B] rounded-3xl p-6 sm:p-8 shadow-xl">
        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-brand-400">1. Platform Services & License</h2>
          <p>
            AISMM provides an autonomous, multi-platform social media operations platform allowing users to compose, schedule, analyze, and manage content across supported social networks (Instagram, Facebook, X/Twitter, LinkedIn, YouTube) through authorized developer APIs.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-brand-400">2. OAuth Credentials & Security Vault</h2>
          <p>
            You authorize AISMM to connect to your designated social accounts using official OAuth 2.0 protocols. All credentials, access tokens, and refresh tokens are encrypted at rest using AES-256 Fernet authenticated encryption with unique per-record PBKDF2 salts. AISMM never sells or transmits your private tokens to third parties.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-brand-400">3. Autonomous AI & Content Guidelines</h2>
          <p>
            Our intelligent scheduling and auto-reply engines operate on user-configured confidence thresholds. You remain responsible for all published media assets and compliance with each platform's community terms.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider text-brand-400">4. Account Termination & Data Deletion</h2>
          <p>
            You may disconnect any social adapter or delete your account at any time. Upon account deletion, all stored tokens, schedules, and analytics caches are permanently purged from the database.
          </p>
        </section>
      </div>
    </div>
  );
}
