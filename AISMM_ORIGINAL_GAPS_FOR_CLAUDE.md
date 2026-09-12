c# AISMM: Claude implementation handoff and original-repository gap audit

**Prepared:** 2026-09-09 (Asia/Kolkata)  
**Original repository:** https://github.com/Ankit04raj/AISMM  
**Audited source commit:** `8df4694aea777b2e2da5e246713e6e3d87d925c3`  
**Purpose:** Copy this document into your Claude instructions, or put it beside `CLAUDE.md` and instruct Claude to read it completely before editing.

## 0. Instructions to Claude — read before doing work

You are completing AISMM, not demonstrating a mock social-media dashboard. Work as a security-first full-stack engineer. Preserve useful existing implementation; verify every completion claim yourself. Do not equate green mocked adapter tests with successful live OAuth, publishing, delivery, or production readiness.

There are **two distinct code states**:

1. **Original AISMM at the audited commit.** The defects in section 2 were found in this source. Do not assume repairs described in the companion report already exist there.
2. **Separate hardening repository/working tree.** An actual repair pass implemented many fixes. `WORK_COMPLETED.md` documents those changes. `docs/verification/` contains fresh execution evidence. The original remote repository was not modified by this pass.

First identify which code state you are editing. If the original has advanced since the audited commit, compare the newer source before applying this audit. Do not blindly copy historical migrations onto an existing production database. Do not replace the original repository with the repair tree without reviewing the diff and obtaining the owner's approval.

### Non-negotiable working rules

- Read `README.md`, `CLAUDE.md`, `CLAUDE2.md`, `CLAUDE3.md`, `CLAUDE4.md`, `SESSION_HISTORY.md`, `REQUIREMENT_MATRIX.md`, this file, `WORK_COMPLETED.md`, and `DEPLOYMENT.md` where present. Historical "100%" claims are not proof.
- Establish a fresh baseline, including dependencies, tests, build, lint, migrations, and source scan. Record exact outputs, not remembered counts.
- Do not expose secrets in commits, client bundles, logs, test artifacts, screenshots, exceptions, or chat. Use environment variables/secret stores; ask the owner to authenticate through a secure mechanism.
- Bind every account operation and resource read/write to the authenticated owner. Never reuse a mutable, credential-bearing adapter instance across users.
- Reject invalid/missing OAuth state. Bind state to user, provider, redirect URI, expiry, and single-use consumption. Persist state/PKCE across processes.
- Never claim success solely because a function returned a string or a frontend button changed state. Verify persistence or provider acknowledgement.
- A new account has **zero** connected accounts, posts, comments, impressions, reach, and recorded analytics. No estimated fallback should look like an observed metric.
- If a feature cannot be implemented or validated, disable it explicitly and document the limitation. No fake API keys, fabricated comments, static "live" charts, or invented percentages.
- Treat synthetic model diagnostics as experimental—not validated business forecasts and not directly comparable to published research results unless datasets/methods are comparable.
- Make targeted, reviewable changes. Keep the public source repository untouched unless the owner specifically authorizes changes there.
- After each section, report: changed files, implementation details, exact proof commands/output, remaining gaps, and **IMPLEMENTED / PARTIAL / BLOCKED / VERIFIED LOCALLY / VERIFIED LIVE**. Do not conflate these statuses.

## 1. Verified facts about the original repository

- It already contains React/Vite UI modules, FastAPI routes/services, SQLAlchemy models, Alembic revisions, multiple social-platform adapters, ML/heuristic engines, and a substantial test suite. Do not rewrite everything from scratch.
- The portable `GUID` TypeDecorator **already exists at the audited commit**. The UUID fix requested by older `CLAUDE4.md` is not automatically a missing task. Re-test portability instead of reapplying a duplicate fix.
- Existing JWT, TOTP, verification, vault, scheduler, and adapter helpers do not by themselves prove that the UI and production execution paths use them correctly.
- Existing mocked tests and historical completion percentages did not establish production readiness.

## 2. Original-repository defects and actual repair-pass disposition

Read the final column carefully: **implemented in the separate repair tree** does not mean pushed into the original AISMM repository.

| Area | Defect observed at original audited commit | Repair-tree disposition |
|---|---|---|
| Email verification UI | Registration kept a pending session in component state without installing the bearer token needed for verification; `/verify-email?token=...` had no complete route flow. | Token installation and verification routes implemented; real SMTP delivery still unverified. |
| 2FA UI | UI-only code path could display success based on input length instead of verifying the second factor with the backend. | Real login challenge/verification and settings setup with local QR implemented. |
| 2FA storage and setup | Secret stored as ordinary text; setup could overwrite an enabled authenticator; login codes could be reused. | ORM encryption, enabled-secret replacement guard, atomic login time-step replay prevention implemented. Recovery/operations review remains. |
| Logout/session lifecycle | UI cleared browser state; server blacklist was process-local; refresh tokens were not atomically single-use. | Durable `AuthSession`, refresh hash rotation, shared session revocation, and frontend logout API call implemented. |
| Recovery/settings | Profile/password success messages did not persist real changes; reset schema existed without complete end-to-end recovery UI. | Profile update, password change, reset request/confirmation, and session invalidation implemented; real mail delivery unverified. |
| Account gates | Protected routes were not consistently gated by verification; frontend navigation could enter dashboard views without a verified session. | Business-router verification gates and protected path routes implemented. |
| OAuth | Init/callback lacked authenticated user-bound, persistent, single-use state validation; redirect handling was inconsistent; tokens could be returned to the browser; X PKCE was not safely carried between workers. | Persisted `OAuthAttempt`, fixed callback allowlisting, user binding, one-use state, X verifier restoration, and server-side storage implemented. Live provider acceptance pending. |
| Meta OAuth | Adapter targets an older Meta API flow and lacks a complete Page/business-account selection journey. | **Explicitly disabled** in the repair tree, not falsely marked fixed or verified. |
| Credential encryption | Vault helper existed but normal social-account credential columns were plaintext. | `EncryptedText` ORM boundary and legacy-value encryption migration implemented. Backup/rotation and real upgrade rehearsal remain. |
| Publishing ownership | Publishing used registry adapters without resolving the requesting user's connected account and injecting its credentials. | Owner-scoped adapter construction before publishing, retry and account operations implemented. Live publishing still requires provider validation. |
| Scheduling | Could schedule remotely early and dispatch again later; background worker used unbound adapters; an unavailable adapter could be treated as simulated publish success. | Local scheduling only, durable atomic claim, owner-bound dispatch and fail-on-unconfirmed-provider result implemented. Interrupted-claim recovery still operationally incomplete. |
| Comment authorization | Arbitrary provider post/comment IDs could reach adapters without proving an owned local resource. | Owned post/comment lookups and account-bound reply/delete/hide implemented. |
| Inbox | Hardcoded comments/messages were inserted when no live comments existed. | Fabricated feed removed; stored owner-scoped inbox and explicit platform-comment sync implemented. Direct messages remain unavailable. |
| Auto-reply | Unsafe generic dispatch could act on caller-supplied identifiers. | Reviewed approval routes use owned comments. Unattended generic dispatch disabled. |
| Frontend navigation | In-memory views/hash handling lacked full path routing and robust form/session continuity. | BrowserRouter paths, direct links, legacy hash redirects, retained visited tabs and session-stored composer drafts implemented. Remaining subtabs/accessibility require review. |
| Fake settings | Client-generated sample API keys and notification controls appeared functional without persistence. | Fake API keys removed; unavailable settings explicitly marked unavailable. |
| Analytics frontend | Fixed percentage gains, sample platform rows, static activity events and chart shapes looked live. | Replaced by actual API tables/counts and explicit empty states; static scheduling/growth graphics removed. |
| Analytics backend | Fallback impressions/reach, example platform metrics, invented sentiment counts, fixed heatmap samples, hashtag rankings and growth-drift history. | Stored metric aggregation, latest-snapshot selection, zero/unknown no-data responses and insufficient-data drift response implemented. Live ingestion coverage needs verification. |
| ML persistence | Account/user IDs were used as if they were valid ML model foreign keys. | Invalid advisory prediction writes removed. Advisory outputs are not claimed as persisted validated predictions. |
| Strategy | Frontend expected different response fields and could crash; feedback returned "recorded" without storing it. | Response mapping corrected; `StrategyFeedback` persistence and migration implemented. |
| Model operations | Any signed-in user could attempt shared-model promotion. | Promotion requires superuser. Full model operations remain experimental. |
| Rate limiting | Redis/multi-worker support was advertised but not actually used; a token-prefix key was unsuitable. | Production Redis-backed atomic fixed-window guard and fail-closed behavior implemented; trusted proxy and multi-worker deployment tests remain. |
| Validation/errors | Request-validation details could include submitted input; raw provider errors could leak sensitive data. | Request errors omit raw input; key provider error paths sanitized. Complete log/trace review still required. |
| Production config | Missing strict production CORS/HTTPS checks; mandatory SMS prevented an email-only production configuration. | Explicit origins, HTTPS, SMTP checks and optional SMS configuration implemented. |
| Database initialization | Pool settings conflicted with some SQLite configurations; timestamp defaults were evaluated at import time. | Conditional pooling and callable UTC timestamp defaults implemented. |
| Migrations | Sync Alembic engine attempted to use an async driver; relative script path and model/migration discrepancies existed; MFA columns were absent from the migration chain. | Async migration execution, script location, portable UUID migration behavior, MFA/session/OAuth/recovery/feedback schema migrations implemented. Existing migration files changed: review before real upgrades. |
| Frontend build | Tailwind depended on a runtime CDN despite a nominal successful production build; browser API address differed by deployment. | Compiled local Tailwind/PostCSS and same-origin API/proxy setup implemented. |
| Containers | Backend Dockerfile installed root requirements before copying the referenced backend requirements; frontend proxy/deployment setup was incomplete. | Dockerfiles, internal-service Compose topology, migrate-before-start and Nginx API proxy/security headers rewritten. **Containers not built/executed here.** |
| Dependencies | Old heavyweight runtime requirements were incompatible with the available Python environment; audited dependency chains included known advisories. | Tested Python 3.13 runtime lock; unused ML stacks removed; JWT moved to PyJWT and sentiment to standalone vaderSentiment. Final runtime audits reported no known advisories at scan time. |
| Documentation | Historical percentages overstated verification and some crypto claims were inaccurate. | Current-status warnings and separate reports added; Fernet accurately described instead of blanket AES-256 claims. |

## 3. Remaining work, in execution order

### P0 — Repository and baseline control

1. Confirm the source commit and branch. Review changes since the audited original commit.
2. If adopting the repair repository, review `docs/verification/changed-tracked-files.txt` and the full Git diff against the audited SHA. Do not transplant only frontend files while leaving the original backend contracts unchanged.
3. Run the full commands in section 4. A passing historical report is not sufficient.
4. Inspect modifications to old tests. Several old assertions explicitly expected insecure/public OAuth, arbitrary comment identifiers, fabricated analytics, or duplicate scheduling. New real-database tests cover the repaired boundary. Do not restore insecure behavior just to satisfy an obsolete test.

### P0 — Live provider and credential acceptance

**Owner input needed:** real provider developer accounts, approved apps/scopes, redirect domains, test accounts, and authorization to publish disposable test content.

For X, LinkedIn and YouTube individually:

- Check current official provider docs; validate endpoint versions, scopes, identity/profile shapes, author/channel selection, upload requirements and access tiers.
- Complete live login → consent → callback → encrypted account persistence → refresh → revoke/disconnect.
- Reject altered user/provider/state/redirect, replayed/expired states and missing PKCE verifiers. Verify same-process and cross-process callbacks.
- Confirm no raw token/secret is returned to the browser or logs.
- Publish disposable content, independently inspect it on the provider, fetch its metrics/comments, reply, then remove it. Record real provider IDs without exposing credentials.
- Validate no-account, expired-token, disconnected-account, quota-limit, permission-denied and partial multi-platform failure states.
- Implement explicit account selection for multiple accounts per platform. Current repair logic rejects ambiguous multiple-account publishing.

**Meta is not done:** update the API integration, implement Page/business-account discovery and selection, token handling and permissions, then run the same live acceptance tests. Keep Meta disabled until these pass.

### P0 — Mail, authentication and session operations

- Configure real SMTP (or a transactional provider), verified sender/domain, DNS/SPF/DKIM/DMARC as required, and HTTPS links.
- Prove registration mail and reset mail are delivered; test wrong/expired/replayed tokens, resends, outages and abuse throttling.
- Review enumeration behavior, password-policy/byte-length handling, error messages and email-bombing controls.
- Test TOTP setup/enable/challenge/disable/replay and lost-authenticator recovery. Implement a deliberate recovery-code or verified recovery procedure; email password reset must not silently bypass 2FA.
- Decide whether enabling/changing 2FA should invalidate other sessions; test reauthentication for sensitive actions.
- Validate session revocation/rotation across multiple workers, restarts, browser tabs and concurrent refreshes. Add expired-session/state cleanup jobs.
- Browser access/refresh tokens currently use local storage. Review XSS exposure and whether to migrate refresh sessions to secure HttpOnly cookies. If changing cookies, implement and test CSRF/SameSite/origin controls.

### P0 — Data, migrations, keys and scheduler safety

- Rehearse upgrades **from the actual existing database**, not just a fresh database. Some historical migrations were edited in the repair tree. Audit Alembic revision history, column types, enum values, constraints and indexes before applying it.
- Back up DB **and** encryption master key. Prove restore, encrypt/decrypt round-trip and failure on wrong keys; design key rotation/versioning.
- Enable/test actual PostgreSQL referential integrity; do not substitute user/account IDs for model foreign keys.
- Confirm all reads/writes—including account insights, metrics, intelligence, comments, post retry/delete, scheduling and model administration—are tenant-scoped.
- Test concurrent schedule workers, media/customization preservation, timezone/DST boundaries, cancellations and partial failures.
- Add an operator workflow for schedules stuck in `publishing`. Inspect provider state before retrying. No exactly-once guarantee is established across database and provider APIs.
- Review provider retry behavior for duplicate side effects, timeouts, rate limits and idempotency support.
- Implement cleanup and bounded retention for sessions, OAuth attempts, metrics, logs and feedback.

### P1 — Finish product features without fake placeholders

- Decide the scope of API-key issuance, notification preferences, media uploads, direct-message aggregation and unattended auto-reply. Implement fully or keep visibly unavailable.
- Media uploads need trusted storage, authorization, type/size validation, image/video processing limits, public/CDN delivery strategy and SSRF-safe fetch handling. Current URL allowlisting is a starting control, not a complete hostile-media security review.
- Validate comment sync and metric ingestion end-to-end for every enabled platform; report partial sync failures accurately. Confirm imported metric snapshots are linked to the correct owned post and avoid double-counting periods/entities.
- Validate account-dependent views with zero, one, many, disconnected and expired accounts. Ensure successful publishing, failed publishing and draft retention are clear.
- Finish direct routes for any remaining subtabs/filters, browser back/forward behavior, scroll restoration, keyboard focus, dialog traps, loading/error states and mobile layouts.
- Resolve remaining lint warnings and add repeatable CI browser/a11y tests. Horizontal-overflow checks are not a complete WCAG audit.

### P1 — ML honesty and performance

- Synthetic/regression diagnostics are not real production accuracy. Obtain lawful representative datasets, document provenance/consent, split by suitable time/account boundaries and measure leakage-free holdout performance.
- Maintain a real model registry with valid model IDs, training/evaluation artifacts, versions and persisted predictions before offering production drift monitoring.
- Separate heuristic caption/hashtag tools, experiment simulations and observed analytics. No fixed research percentage should be labeled current model confidence or verified audience accuracy.
- Profile synchronous ML work inside async handlers; move expensive work to an appropriate worker/thread/process pool. Benchmark startup, memory, request latency and concurrency.

### P1 — Deployment and operations

- Build and execute the Docker/Compose stack; validate the migration job, startup failure modes, Nginx API routing, deep-link fallback, CSP and health checks.
- Configure actual hosting/domain/TLS and trusted reverse-proxy IP handling. Database and Redis must remain private.
- Prove Redis-backed rate limiting across processes and fail-closed behavior during Redis outages.
- Run deployment-specific dependency/container scans, secret scans, threat review, load/soak tests and backup restore drills.
- Add observability, alert routing, retention, incident response and rollback runbooks.
- Finalize legal operator identity, support/privacy contacts, providers, processing locations, jurisdiction and retention. Current legal pages are explicit implementation drafts.

## 4. Exact commands for Claude

### 4.1 Identify and inspect the original state

```bash
git status --short
git remote -v
git rev-parse HEAD
git log -5 --oneline
find . -iname '*.md' -not -path './.git/*' -not -path './node_modules/*' -not -path './.venv/*'
# Original audit reference; inspect before assuming it equals current HEAD:
git show 8df4694aea777b2e2da5e246713e6e3d87d925c3:backend/app/db/models.py
```

If this is the original repository, first establish compatibility of its existing requirements. The repaired Python 3.13 setup commands below assume the repair-tree files are present. Do not silently pretend the old requirements are identical.

### 4.2 Reproduce the repair-tree local environment

Run from repository root using **Python 3.13 and Node 24**:

```bash
python --version
node --version
npm --version
python -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
npm --prefix frontend ci
# Only when .env does not already exist; never overwrite real keys:
python scripts/init_local.py
.venv/bin/alembic -c backend/alembic.ini upgrade head
.venv/bin/pytest -q
npm --prefix frontend run build
npm --prefix frontend run lint
git diff --check
```

`init_local.py` generates local secrets and refuses to overwrite `.env`. Local verification tokens are development-only and are **not email-delivery proof**. Existing `.env` owners should skip the initializer and validate their existing settings.

```bash
# Terminal A
.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
# Terminal B
npm --prefix frontend run dev
# Open http://localhost:5173
```

### 4.3 Targeted regression proof

```bash
.venv/bin/pytest backend/tests/test_auth_and_scoping.py -q
.venv/bin/pytest backend/tests/test_production_completion.py -q
.venv/bin/pytest backend/tests/test_analytics_dashboard.py -q
.venv/bin/pytest backend/tests/test_scheduling_engine.py -q
.venv/bin/pytest backend/tests/test_secrets_and_config.py -q
```

Important acceptance tests include durable logout, single-use refresh, unverified access rejection, empty-account truthfulness, no-account publishing rejection, profile/password persistence, encrypted DB values, reset replay rejection, cross-user OAuth state rejection, owner-scoped comment actions, local-only scheduling, MFA replay rejection, feedback persistence and latest-snapshot analytics.

### 4.4 Migration and PostgreSQL proof

Use **disposable databases only** for acceptance testing. Never point these commands at a customer DB by accident.

```bash
# Fresh SQLite migration, choose a NEW file:
DATABASE_URL=sqlite+aiosqlite:///./migration_acceptance.db \
  .venv/bin/alembic -c backend/alembic.ini upgrade head

# Supply a disposable PostgreSQL database URL through environment/secret tooling:
DATABASE_URL="$TEST_POSTGRES_DATABASE_URL" \
  .venv/bin/alembic -c backend/alembic.ini upgrade head
DATABASE_URL="$TEST_POSTGRES_DATABASE_URL" \
  .venv/bin/alembic -c backend/alembic.ini current
# Inspect proposed schema differences; investigate any output, do not blindly apply:
DATABASE_URL="$TEST_POSTGRES_DATABASE_URL" \
  .venv/bin/alembic -c backend/alembic.ini check

# Start a development API using that migrated PostgreSQL database:
DATABASE_URL="$TEST_POSTGRES_DATABASE_URL" \
  .venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
# Separate terminal, never production:
TEST_API_URL=http://127.0.0.1:8001/api/v1 \
  .venv/bin/python scripts/verify_postgres.py
```

The recorded PostgreSQL acceptance used a real HTTP server. The full pytest suite uses SQLite/mocks; do **not** claim the entire suite ran against PostgreSQL. Sharing an asyncpg session between pytest and a threaded TestClient caused event-loop errors in an attempted test harness; real-server HTTP verification was used instead.

### 4.5 Browser proof

```bash
npm --prefix frontend run build
# Backend must be running locally on port 8000.
# Set AGENT_BROWSER_CDP to an EXISTING Chromium debugging connection securely.
node scripts/verify_browser.cjs
```

The script uses a private test origin mapped to built frontend files and the real local API. It creates disposable QA accounts and checks the landing page, all 13 dashboard routes at desktop/mobile sizes, registration/verification, draft continuity and logout/direct-route guards. Inspect generated screenshots individually. Do not publish authenticator QR codes or secrets from screenshots. This does not validate real SMTP or social providers.

### 4.6 Dependency and source checks

```bash
.venv/bin/pip install pip-audit
.venv/bin/pip-audit -r backend/requirements.txt
npm --prefix frontend audit
# Leads for manual inspection, not automatic deletion:
rg -n 'Math.random|setTimeout|mock|simulat|fallback|Verified|100%|hardcoded' frontend/src backend/app
rg -n 'get_adapter\(|access_token|refresh_token|two_factor_secret' backend/app
rg -n 'default=datetime.now|onupdate=datetime.now' backend/app
# Review output locally and redact secrets; do not paste credentials into reports.
git status --short
git diff --stat
git diff --check
```

### 4.7 Production stack — not previously executed here

```bash
# Fill .env from .env.example through approved secret tooling first.
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=100 migrate
# Inspect logs carefully; redact sensitive data before sharing.
```

Do not claim deploy success until HTTPS/deep links/API/authentication/workers/Redis/migrations are verified on the actual host.

## 5. Completion report Claude must produce

For every section:

```text
SECTION:
SOURCE COMMIT / BRANCH:
CHANGED FILES:
REMOVED / DISABLED FEATURES:
REAL IMPLEMENTATION:
COMMANDS AND FRESH OUTPUT:
VERIFICATION SCOPE: unit / SQLite integration / PostgreSQL HTTP / browser / live provider / deployed
STATUS: IMPLEMENTED / PARTIAL / BLOCKED / VERIFIED LOCALLY / VERIFIED LIVE
REMAINING GAPS:
OWNER INPUT NEEDED:
```

Finish with a 13-module matrix showing authenticated reads, loading/error handling, core actions, and live-provider/deployment verification separately. "All tests pass" is not a valid substitute for that matrix.

## 6. Recorded evidence from this pass (rerun, do not assume)

- Backend: **246 passed, 20 warnings in 159.07s**.
- Production frontend build: successful (Vite 8.2.2; 1,849 modules transformed).
- Lint: **73 warnings, 0 errors** at the recorded final build—not zero-warning clean.
- Browser: landing plus 13 dashboard route checks; desktop/mobile overflow checks found none; recorded errors array empty. Registration/verification, retained draft navigation/reload and logout/direct-route tests passed.
- PostgreSQL: **14 real HTTP checks passed** on a disposable PostgreSQL-backed development API; fresh migration chain also ran.
- SQLite: fresh Alembic migration chain ran; real-database security/analytics tests included.
- Runtime dependency audit: no known advisories reported after replacing the affected JWT/NLP chains. Frontend npm audit reported zero known vulnerabilities. A scan is not a security guarantee.
- **Not verified:** real SMTP/SMS delivery, live social OAuth/publish/sync/delete, Docker execution, public deployment, full accessibility, production load/security/backup acceptance, or real-world ML accuracy.

The owner wants accurate work—not another unsupported "100% production ready" claim.
