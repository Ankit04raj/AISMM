# AISMM — Actual work completed in the separate hardening repository

**Prepared:** 2026-09-09 (Asia/Kolkata)  
**Source:** https://github.com/Ankit04raj/AISMM  
**Original source commit:** `8df4694aea777b2e2da5e246713e6e3d87d925c3`

## Outcome and boundaries

This repository contains actual source-code repairs, new migrations, new integration tests, production-build configuration and operational documentation. It is **not a deployed production service**. The original AISMM remote was not modified during this work. This copy retains the source history so changes can be reviewed against the audited commit.

For the original repository's complete gap list and copy/paste instructions for Claude, read **`AISMM_ORIGINAL_GAPS_FOR_CLAUDE.md`**. For setup and deployment, read **`DEPLOYMENT.md`**. Do not mistake changes implemented here for changes already merged into the original repository.

## 1. Authentication and account settings

### Implemented

- Rebuilt frontend registration/sign-in/verification flow to install the real bearer session before calling protected verification endpoints.
- Added real `/verify-email` and `/reset-password` routes, protected `/app/:tab/*` routes, and server profile restoration.
- Added real TOTP login challenge handling; removed the frontend code-length-only success path.
- Added authenticator setup UI with a locally generated QR code (no external QR service receives the secret), enable/disable requests and actual backend validation.
- Added a guard against replacing an enabled authenticator secret and atomic login time-step replay prevention.
- Added database-backed sessions with hashed refresh tokens, single-use rotation, durable revocation and expiry checks. Tokens without a valid durable session are rejected.
- Frontend logout calls the server, and refuses to silently claim confirmed logout if the request fails.
- Added profile update, password change, reset request/confirmation and all-session invalidation after password changes/resets.
- Added explicit verification gates to business routers while leaving appropriate authentication/verification endpoints reachable.
- Required registration acceptance in the frontend and enforced production-side terms acceptance; stored acceptance timestamp when supplied.
- Replaced fake profile/password-save feedback and sample API keys. Unimplemented notification/API-key sections say they are unavailable.

### Main files

`backend/app/api/v1/auth.py`, `backend/app/api/deps.py`, `backend/app/core/security.py`, `backend/app/core/schemas/auth.py`, `backend/app/services/session_service.py`, `backend/app/db/models.py`, `frontend/src/components/AuthView.jsx`, `frontend/src/components/SettingsTab.jsx`, `frontend/src/App.jsx`, `frontend/src/api/client.js`.

### Not established

Real mail delivery, lost-authenticator recovery operations, production multi-worker/browser-tab stress behavior, a completed HttpOnly-cookie redesign, or a full security review. Browser tokens still use local storage. Development token display is explicitly not email-delivery proof.

## 2. Credentials, OAuth and tenant boundaries

### Implemented

- Added `EncryptedText` at the ORM boundary for social access/refresh tokens and TOTP secrets, using the existing vault. Added encryption of legacy plaintext values during migration.
- Added `OAuthAttempt` records: user/provider/redirect binding, expiry, one-use consumption, hashed state identifier and encrypted PKCE verifier storage.
- OAuth callbacks no longer return raw provider tokens to the browser; they create an encrypted connected-account record.
- Added a fixed callback allowlist derived from `FRONTEND_URL` and provider credential configuration checks.
- Added request-local owner-bound adapters; publish/account/metrics/intelligence/comment paths no longer rely on credentialless shared registry instances for owned account actions.
- Reject no-account and ambiguous multiple-account publishing rather than guessing an identity.
- Added owner-scoped local comment lookup before reply/delete/hide and owner-scoped inbox reads.
- Restricted shared-model promotion to superusers.
- Sanitized important request/provider error paths so submitted passwords and raw provider bodies are not echoed.

### Deliberately disabled

- Meta connection: the inherited API flow needs modernization and actual Page/business-account selection before it is safe to expose as complete.
- Generic unattended auto-reply dispatch: disabled rather than allowing caller-supplied identifiers to reach an unscoped provider action.
- Raw platform-token refresh API: directs users to account-scoped refresh instead of returning credentials.

### Main files

`backend/app/services/oauth_service.py`, `backend/app/services/owned_adapter.py`, `backend/app/services/account_service.py`, `backend/app/api/v1/comments.py`, `backend/app/api/v1/reply.py`, `backend/app/api/v1/models.py`, `backend/app/api/v1/router.py`, `backend/app/services/metrics_service.py`, `backend/app/services/intelligence_service.py`.

### Not established

Live X/LinkedIn/YouTube provider acceptance, all scopes/account types/media formats, complete multiple-account selection, real token refresh/revocation, live comments/metrics ingestion and hostile-media security testing.

## 3. Publishing, scheduling and inbox

### Implemented

- Publishing resolves owned accounts before side effects and checks for an actual provider publication acknowledgement.
- Unified the single-platform create path through the multi-platform service; API record IDs remain local record IDs.
- Scheduled requests create local posts/publications/schedule records without scheduling remotely first.
- Worker claims are atomically persisted before external calls, preventing two workers from intentionally claiming the same pending schedule.
- Removed simulated success when an adapter is unavailable. Failures stay failures.
- Preserve per-platform content/media/customizations for queued dispatch.
- Added timezone-aware future-date validation; store UTC-naive database timestamps consistently with existing schema.
- Reject inappropriate retries; bind retry/delete to the owner; do not discard local posts after unconfirmed provider deletion.
- Rebuilt composer with a blank initial draft, connected-account selection, session-stored draft continuity, editable media URL/type, AI analysis, publish confirmation, scheduled time and per-platform result display.
- Replaced fabricated inbox entries with stored comments and an explicit platform synchronization action. Partial synchronization errors are reported.

### Not established

Exactly-once delivery across a database and remote APIs, a complete interrupted-claim recovery UI, full media-upload storage, all provider idempotency/timeout behaviors, or live dispatch acceptance. Operators must inspect provider state before retrying interrupted/uncertain publishes.

## 4. Truthful analytics, strategy and ML labeling

### Implemented

- Removed sample analytics rows, fixed percentage gains, artificial activity events, default comment samples, decorative forecast curves and static timing matrices presented as live information.
- Backend overview/comparison/content analytics use stored metric snapshots rather than invented impressions/reach/engagement estimates.
- Latest-snapshot selection avoids summing successive snapshots of the same metric entity/period.
- Empty accounts return empty comparisons, zero recorded sentiment counts, unknown/no-data labels, and zero-sample temporal slots—not fictional positive performance.
- Removed fabricated growth-drift history; missing validation history is explicitly insufficient data.
- Corrected the strategy frontend to match backend fields; removed the crash from reading the nonexistent directives shape.
- Added durable owner-scoped strategy feedback records instead of success-only responses.
- Removed invalid advisory prediction persistence that used user/account IDs as ML model foreign keys.
- Labeled model/forecast modules experimental, distinguished research references from measured results, and replaced misleading validation badges and `null R²` display.
- Reworked reports to export actual selected JSON data and distinguish experimental model diagnostics.

### Not established

Representative real-data ML accuracy, production drift monitoring, validated attribution/ROI, complete provider ingestion coverage, or production model-training/deployment operations.

## 5. Frontend and navigation

- Built a new responsive dark/violet landing page without unsupported research/production claims.
- Replaced runtime Tailwind CDN dependency with compiled local Tailwind/PostCSS.
- Added true path routing, browser-back/direct-link continuity and legacy hash redirects.
- Retained visited dashboard tabs and persisted composer drafts across navigation and reload within the browser tab.
- Added mobile navigation, an application error boundary, visible focus styles and reduced-motion support.
- Replaced fake navbar connection/date/test-count badges with truthful controls.
- Added implementation-specific Terms/Privacy drafts that explicitly require operator/legal completion before launch.
- Centralized API error parsing, bounded request timeouts and single-flight token refresh.
- Use same-origin `/api/v1` and Vite/Nginx API forwarding instead of hardcoded production localhost requests.

**Remaining:** 73 recorded lint warnings, full accessibility/keyboard review, remaining subtabs/filter URL conventions, production-browser testing and unsupported product features listed in the gap handoff.

## 6. Database, configuration and deployment work

- The inherited portable `GUID` already existed; no duplicate UUID implementation was claimed as newly written.
- Made SQLite engine options conditional and timestamp defaults callable rather than evaluated once at import.
- Fixed Alembic async execution and relative script path; reconciled portable UUID/phone migration behavior.
- Added migration `5d6e7f8a9b0c` for sessions, OAuth state, recovery, MFA and encryption; added `6e7f8a9b0c1d` for strategy feedback.
- Added production HTTPS/CORS/SMTP validation; made SMS optional rather than mandatory for an email-first deployment.
- Added production Redis-backed atomic fixed-window throttling with fail-closed behavior; removed unsafe authorization-prefix rate-limit keys.
- Repaired Dockerfiles, private-service Compose topology, migration-before-start, API proxy, response security headers and SPA fallback.
- Added current production environment templates, a non-overwriting local secret initializer, Makefile commands and CI.
- Updated runtime dependencies for Python 3.13. Replaced python-jose/ecdsa and NLTK-dependent runtime paths with PyJWT and standalone vaderSentiment after audit findings. Removed unused heavyweight dependency requirements.
- Corrected crypto wording: Fernet is authenticated encryption; blanket AES-256 claims were not accurate.

**Important:** historical migration files were modified. Fresh migrations passing does not prove an upgrade from every existing deployment. Back up DB and master key and rehearse a real upgrade before production. Docker/Compose was not executed in this environment.

## 7. Verification actually run

| Check | Observed result | Scope / limitation |
|---|---|---|
| Full backend pytest | **246 passed, 20 warnings in 159.07s** | Unit/mocked-provider + SQLite integration. Not all PostgreSQL, not live social APIs. |
| Added real-database tests | **15 new tests** in `test_production_completion.py` | Session security, gates, encrypted fields, owned actions, scheduling, MFA, feedback and analytics. |
| Frontend build | **Success**, Vite 8.2.2, 1,849 modules transformed | Actual compiled production build. |
| Frontend lint | **73 warnings, 0 errors** | Warnings remain; not lint-clean. |
| Browser | Landing + **13 dashboard routes**, desktop/mobile; errors array empty; overflow checks empty | Real built frontend + real local API through private CDP test-origin proxy. Not deployed hosting. |
| Browser journeys | Registration/development verification; navigation and reload preserve draft; logout/protected direct route | Real local requests; no live email or provider calls. |
| PostgreSQL HTTP | **14 checks passed** | Disposable PostgreSQL-backed API: registration through revocation. |
| Fresh migrations | SQLite and PostgreSQL chains completed | Not a populated customer-data upgrade/rollback rehearsal. |
| Dependency audits | Runtime pip audit: **no known advisories**; npm audit: **0 vulnerabilities** | Point-in-time package scan, not a penetration test or complete supply-chain guarantee. |

The 15 new tests did not simply relax old tests. Several old tests expected insecure or fabricated behavior and were revised to enforce new contracts. Provider-contract tests mock their dependency boundaries explicitly; those mocks are not counted as live-provider proof.

### Recorded files

- `docs/verification/backend-tests.txt`
- `docs/verification/frontend-build.txt`
- `docs/verification/frontend-lint.txt`
- `docs/verification/browser-results.json`
- `docs/verification/postgres-http.txt`
- `docs/verification/postgres-migrations.txt`
- `docs/verification/sqlite-migrations.txt`
- `docs/verification/backend-audit.txt` and `.json`
- `docs/verification/frontend-audit.json`
- `docs/verification/changed-tracked-files.txt`
- `docs/verification/file-manifest.json`

Local exploratory runs also found failures; the supplied passing summaries correspond to the later verified repair state. In particular, a cross-event-loop asyncpg/TestClient harness was not valid PostgreSQL proof, so the PostgreSQL acceptance was performed through a real running HTTP server instead.

## 8. 13-module status matrix

Legend: ✅ implemented/locally verified; ⚠️ partial, experimental or external acceptance missing; — not applicable.

| Module | Authenticated API reads | Loading/error handling | Core action | Live provider / production status |
|---|---:|---:|---|---|
| Overview | ✅ | ✅ | Real summary and composer/platform navigation ✅ | Stored metrics only; ingestion acceptance ⚠️ |
| Analytics | ✅ | ✅ | Windowed real stored metrics and empty states ✅ | Provider metric ingestion/attribution ⚠️ |
| Composer | ✅ | ✅ | Draft/AI/publish/schedule implemented; owned-account tests ✅ | Real social publishing/media ⚠️ |
| Scheduling | ✅ | ✅ | Local queue and atomic worker dispatch tested ✅ | Provider/idempotency/recovery operations ⚠️ |
| AI Engine | ✅ | ✅ | Caption/sentiment/hashtag requests ✅ | Experimental/heuristic quality ⚠️ |
| Inbox | ✅ | ✅ | Owned stored comments, explicit sync, reviewed actions ✅ | Live provider coverage; direct messages ⚠️ |
| Growth | ✅ | ✅ | Explicit simulation requests ✅ | Real-data validated forecasts not available ⚠️ |
| Platforms | ✅ | ✅ | State-safe OAuth/account handling implemented | X/LinkedIn/YouTube live acceptance ⚠️; Meta disabled |
| Strategy | ✅ | ✅ | Correct response mapping and persisted feedback ✅ | Advice remains experimental ⚠️ |
| Reports | ✅ | ✅ | Actual JSON export and selected API data ✅ | Observed-provider coverage/advanced reporting ⚠️ |
| Models | ✅ | ✅ | Diagnostics and admin-gated promotion boundary ✅ | Production training/registry lifecycle ⚠️ |
| Settings | ✅ | ✅ | Profile/password/MFA ✅; fake keys removed | Recovery ops/legal/notifications/API keys ⚠️ |
| Security | ✅ (application access) | ✅ | Real process/database probes ✅ | Redis/multi-worker/full security/load acceptance ⚠️ |

Public landing, authentication, verification/recovery and legal routes are additional to these dashboard modules.

## 9. What was not done

- No commits were pushed into `Ankit04raj/AISMM`.
- No public production deployment was created.
- No real SMTP/SMS delivery or social-provider acceptance was claimed.
- No complete Meta implementation, upload pipeline, direct-message aggregation, unattended auto-reply, workspace API-key system or custom notification preferences was delivered.
- No claim of full WCAG compliance, load certification, legal readiness, trained real-world ML accuracy, or complete independent security review is made.
- The new repository is a separate, reviewable code handoff—not a claim that the original repository is now fixed remotely.

## 10. Where Claude should start next

Read `AISMM_ORIGINAL_GAPS_FOR_CLAUDE.md` completely, identify whether working in the original or repair repository, reproduce the baseline, then follow P0 gates before adding more cosmetic features. Ask for live provider/hosting inputs only when they are needed. Preserve explicit unavailable states until real acceptance succeeds.
