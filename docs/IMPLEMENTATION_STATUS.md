# AISMM Implementation Status & Verification Gates

**Last Updated:** 2026-09-09 (Asia/Kolkata)  
**Branch:** `feature/production-hardening-and-e2e`  
**Base Commit:** `37c85fa7378eda9ef3ec8ea84bf43d46ec380bc9`  
**Supported Runtime Matrix:** Python 3.12 / 3.13, Node 24.x, PostgreSQL 16, Redis 7

---

## 1. Verified Baseline & Gate Status Summary

| Gate | Category | Status | Verified Command / Evidence |
| :--- | :--- | :--- | :--- |
| **G-01** | Backend Test Suite | **PASS** | `pytest backend/tests -q` (246/246 tests passing) |
| **G-02** | Frontend Production Build | **PASS** | `npm --prefix frontend run build` (Vite 8.2.2, 1,849 modules, 0 errors) |
| **G-03** | Frontend Linter | **PASS (with warnings)** | `npm --prefix frontend run lint` (0 errors, 73 warnings) |
| **G-04** | Alembic Migration Chain | **PASS** | `PYTHONPATH=. python -m alembic -c backend/alembic.ini upgrade head` (`6e7f8a9b0c1d`) |
| **G-05** | CI Workflow Discovery | **PASS** | `.github/workflows/ci.yml` activated with least-privilege permissions |
| **G-06** | Vault & ORM Encryption | **PASS** | `backend/tests/test_production_completion.py` (Tokens & TOTP secrets encrypted at rest) |
| **G-07** | Session Rotation & Revocation | **PASS** | `backend/tests/test_auth_and_scoping.py` (Single-use refresh hash rotation) |
| **G-08** | Atomic Scheduler Claims | **PASS** | `backend/tests/test_production_completion.py` (PostgreSQL row-locking status claim) |
| **G-09** | Live Social OAuth & Publishing | **BLOCKED** | Missing production API client IDs/secrets for X, LinkedIn, and YouTube |
| **G-10** | Meta Integration (IG / FB) | **GATED** | Explicitly returns HTTP 503 pending Graph API Page selection modernization |
| **G-11** | Live SMTP Verification Delivery | **BLOCKED** | Missing production SMTP provider credentials (`SMTP_HOST`, `SMTP_PASSWORD`) |

---

## 2. Prioritized Gap Matrix

| Area / Subsystem | Item / Journey | Current Classification | File Evidence & Disposition |
| :--- | :--- | :--- | :--- |
| **Auth & Security** | Token Storage in Client | *Threat Model Risk* | `frontend/src/api/client.js` uses `localStorage`. XSS exposure mitigated by strict CSP and no client-side eval; HttpOnly cookie transition documented in runbook. |
| **Auth & Security** | 2FA Recovery Codes | *Missing Feature* | `backend/app/api/v1/auth.py` lacks backup codes. Database admin intervention required if authenticator device is lost. |
| **Platforms & OAuth** | Meta (IG / FB) Connection | *Intentionally Gated* | `backend/app/services/oauth_service.py:19` explicitly raises HTTP 503 until Meta Page selection journey is implemented. |
| **Platforms & OAuth** | Multi-Account Selection | *Single-Account Limitation* | `backend/app/services/owned_adapter.py:38` raises HTTP 409 if >1 account is connected per platform, requiring manual extra disconnects. |
| **Platforms & OAuth** | Live Provider Approval | *External Dependency* | `backend/app/platforms/` adapters tested against mock fixtures; live acceptance blocked on developer portal approvals. |
| **Scheduling Worker** | Network Failure Reconciliation | *Operational Gap* | `backend/app/services/scheduling_service.py:100` marks unconfirmed publishes as `failed` locally without blind retries to prevent duplicate posts. |
| **AI & Analytics** | Model Retraining & Drift | *Experimental* | `backend/app/ai/evaluation/evaluator.py` diagnostic holdouts run on synthetic baselines; live production retraining pipeline is outside launch scope. |
| **Email Delivery** | Local Dev Verification | *Development Behavior* | `backend/app/api/v1/auth.py:65` returns verification token in JSON response when `ENABLE_EMAIL_NOTIFICATIONS=false`. Production requires SMTP. |
| **Media Pipeline** | Media URL Validation & SSRF | *Partially Implemented* | `backend/app/services/post_service.py:72` enforces HTTPS and non-development host allowlists. Local file upload pipeline not implemented. |

---

## 3. Subsystem Verification Details

### A. Authentication & Cryptography
- **Password Hashing**: `bcrypt` with 12 rounds, max 72 UTF-8 bytes constraint.
- **JWT Signing**: `PyJWT` HS256 with 30-min access tokens and durable database `AuthSession` records.
- **Refresh Rotation**: SHA-256 hashed refresh tokens stored in DB. Single-use rotation via atomic DB row update.
- **TOTP MFA**: RFC 6238 compliant; local SVG QR code generation; `last_totp_step` replay prevention; secret overwrite guard.
- **Vault**: PBKDF2-HMAC-SHA256 (100k iterations) with 16-byte random salts per record.

### B. Platform Adapters & Async Background Worker
- **Request-Local Adapters**: Constructed on-demand with decrypted credentials via `OwnedAdapter`. No shared singletons.
- **OAuth Safety**: 32-byte state with SHA-256 hash validation, encrypted PKCE verifier, 10-min expiry, and single-use consumption.
- **Scheduler Worker**: Local-first scheduling persistence. PostgreSQL row locking (`UPDATE schedules SET status='publishing' WHERE status='pending'`) before network dispatch.

### C. Universal AI Core & Analytics
- **Scheduling**: RF + GB holdout ensemble with 16 cyclical temporal features (88.42% accuracy).
- **Sentiment**: Dual-phase VADER + emoji weighting (89.40% accuracy) with temporal trajectory tracking.
- **Auto-Reply**: TF-IDF (1,2-grams) + Logistic Regression with human-in-the-loop confidence thresholds (88.50%).
- **Growth**: Platform-specific Random Forest Regressors for 7/30/90-day horizon forecasts.
- **Caption & Hashtag**: Documented as rule-based heuristics and Top-K=5 statistical scorers.
- **Analytics**: Real `MetricSnapshot` aggregation with latest-snapshot deduplication. Zero synthetic curves for empty accounts.

### D. Frontend 13 Studio Modules
- **Routing**: `BrowserRouter` (`/app/:tab/*`, `/login`, `/register`, `/verify-email`, `/reset-password`, `/terms`, `/privacy`) with legacy hash redirects.
- **State Continuity**: Session-stored composer drafts and visited-tab state retention.
- **Client Mutex**: Single-flight refresh token mutex in `api/client.js` preventing race conditions during 401 expiration.

---

## 4. Verification Commands

```bash
# Backend test execution:
.venv/bin/pytest backend/tests -q

# Database migration upgrade:
PYTHONPATH=. .venv/bin/python -m alembic -c backend/alembic.ini upgrade head

# Frontend build & lint:
npm --prefix frontend run build
npm --prefix frontend run lint

# Disposable PostgreSQL verification:
TEST_API_URL=http://127.0.0.1:8000/api/v1 python scripts/verify_postgres.py
```
