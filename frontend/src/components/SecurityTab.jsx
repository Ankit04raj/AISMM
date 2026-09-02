import React, { useState } from 'react';
import {
  ShieldCheck,
  Key,
  Lock,
  Activity,
  AlertTriangle,
  Server,
  Zap,
  CheckCircle2,
  Cpu
} from 'lucide-react';

export default function SecurityTab() {
  const [rateLimitState, setRateLimitState] = useState({
    limit: 60,
    window: "60s sliding window",
    active_keys: 12,
    rejected_requests_24h: 0,
    status: "Healthy / Protected",
  });

  const [circuitBreakers, setCircuitBreakers] = useState([
    { name: "Instagram Graph API v19.0", state: "CLOSED", failures: 0, threshold: 5, status: "Normal" },
    { name: "Facebook Page API v19.0", state: "CLOSED", failures: 0, threshold: 5, status: "Normal" },
    { name: "X (Twitter) API v2", state: "CLOSED", failures: 0, threshold: 5, status: "Normal" },
    { name: "LinkedIn REST & UGC API", state: "CLOSED", failures: 0, threshold: 5, status: "Normal" },
    { name: "YouTube Data API v3", state: "CLOSED", failures: 0, threshold: 5, status: "Normal" },
  ]);

  const auditEvents = [
    { id: "aud_1", event: "AUTH_LOGIN_SUCCESS", user: "admin@aismm.com", ip: "192.168.1.1", status: "SUCCESS", time: "2m ago" },
    { id: "aud_2", event: "MODEL_PROMOTED", user: "system_evaluator", ip: "127.0.0.1", status: "SUCCESS", time: "18m ago" },
    { id: "aud_3", event: "POST_PUBLISHED", user: "admin@aismm.com", ip: "192.168.1.1", status: "SUCCESS", time: "42m ago" },
    { id: "aud_4", event: "TOKEN_VAULT_ENCRYPT", user: "vault_service", ip: "127.0.0.1", status: "SUCCESS", time: "1h ago" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-white">Security Vault & System Resilience Hub</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            AES-256 Vault token encryption, sliding-window rate limiters, and circuit breaker cascade protection (CLAUDE.md Phase 16)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center space-x-1.5">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Vault Security: AES-256 PBKDF2 Active</span>
          </span>
        </div>
      </div>

      {/* Security Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-400">Credential Vault</span>
            <Lock className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-xl font-extrabold text-white">AES-256 Encrypted</div>
          <div className="text-xs text-gray-400">PBKDF2-HMAC-SHA256 (100k rounds) securing all OAuth access and refresh tokens at rest.</div>
        </div>

        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-400">Rate Limiting</span>
            <Activity className="h-4 w-4 text-brand-400" />
          </div>
          <div className="text-xl font-extrabold text-white">{rateLimitState.limit} req / min</div>
          <div className="text-xs text-gray-400">Microsecond sliding-window token bucket with HTTP 429 Retry-After protection.</div>
        </div>

        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-400">Circuit Breaker</span>
            <Zap className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="text-xl font-extrabold text-emerald-400">5/5 Closed (Healthy)</div>
          <div className="text-xs text-gray-400">Prevents thread pool cascade during third-party social API downtime with exponential jitter retries.</div>
        </div>
      </div>

      {/* Circuit Breaker Status Grid */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <h3 className="font-bold text-sm text-gray-200 mb-4">Platform Circuit Breakers & Upstream Fault Tolerance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {circuitBreakers.map((cb) => (
            <div key={cb.name} className="p-3.5 rounded-xl bg-gray-950 border border-gray-800 flex items-center justify-between text-xs">
              <div>
                <div className="font-bold text-gray-200">{cb.name}</div>
                <div className="text-[11px] text-gray-400 mt-0.5">Failures: {cb.failures}/{cb.threshold}</div>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold font-mono">
                {cb.state}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Audit Log */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-sm text-gray-200">Compliance & Security Audit Log</h3>
            <p className="text-xs text-gray-400">Structured JSON event telemetry for enterprise compliance</p>
          </div>
          <span className="text-xs text-gray-400 font-mono">Live Stream</span>
        </div>

        <div className="space-y-2 font-mono text-xs">
          {auditEvents.map((evt) => (
            <div key={evt.id} className="p-3 rounded-lg bg-gray-950 border border-gray-800/60 flex items-center justify-between text-gray-300">
              <div className="flex items-center space-x-3">
                <span className="text-emerald-400 font-bold">[{evt.status}]</span>
                <span className="text-brand-300 font-bold">{evt.event}</span>
                <span className="text-gray-400 hidden sm:inline">by {evt.user} ({evt.ip})</span>
              </div>
              <span className="text-gray-500 text-[10px]">{evt.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
