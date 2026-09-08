# AISMM — MASTER REMEDIATION + PRODUCTION ENGINEERING PROMPT
## End-to-End Repository Audit, UI Fidelity, Real Backend Wiring, AI Integrity, Security, Integrations, Testing & Production Readiness

> **RECONCILIATION NOTE — read this before anything below.**
> This document was cross-checked against the actual live repository (`github.com/Ankit04raj/AISMM`, cloned and run directly — dependencies installed, test suite executed, source read file-by-file) before being finalized. Two corrections to the original draft, plus known findings folded in as an accelerant:
>
> 1. **`CLAUDE2.md` does not exist in the repository.** Only `CLAUDE.md`, `SESSION_HISTORY.md`, and `REQUIREMENT_MATRIX.md` are present. Every instruction below that references `CLAUDE2.md` should be read as: *check for it — if present, treat it as authoritative per the priority order in Section 2; if absent (the current state), rely on `CLAUDE.md` + `REQUIREMENT_MATRIX.md` + this document alone.* Do not block work waiting for a file that isn't there.
> 2. **The local path `/home/ankit/AISMM_DEV` is environment-specific.** Treat it as "wherever this repository is checked out locally" — verify with `pwd`/`git remote -v` at the start of the session rather than assuming that exact path.
> 3. **Visual direction confirmed:** the supplied UI screenshot's dark, violet-primary/cyan-secondary SaaS dashboard aesthetic (Section 4) is the accepted target — this supersedes any alternate palette proposed in earlier design exploration. Build to the screenshot's visual language.
> 4. **Section 58's "first action" still applies in full** — Claude Code should still independently verify everything below via the actual repo/runtime, not take this note's findings on faith. They're listed to point the audit at the right files faster, not to replace Steps 0–14.
>
> **KNOWN FINDINGS FROM INDEPENDENT AUDIT (verified firsthand — re-confirm each before fixing, since the repo may have moved since):**
> - **Auth is not enforced anywhere.** Zero routers under `backend/app/api/v1/` use `Depends(get_current_user)`. `auth.py` only implements social-platform OAuth, not app login — there is no `/register` or `/login` endpoint. `posts.py` uses a hardcoded `DEFAULT_USER_ID` constant instead of a session user.
> - **Hardcoded secrets in source**, including inside the committed `docker-compose.yml` (`SECRET_KEY=aismm_production_master_secret_key_2026_docker`), plus fallback defaults in `backend/app/core/config.py` and `backend/app/config/settings.py`, plus a **static hardcoded PBKDF2 salt** (`b"aismm_vault_salt_v1"`) in `backend/app/core/vault.py` reused for every encryption operation.
> - **`cryptography` is imported directly but not declared** in `requirements.txt` (only present transitively via `python-jose[cryptography]`) — fragile install.
> - **ML fabrication, specifically:** `backend/app/ai/growth/engine.py` trains RandomForest on synthetic data whose *label* is a formula of the *same input features* plus noise, then computes R² **on the training set — no holdout split**. `backend/app/ai/scheduling/engine.py` trains an ensemble to relearn a hardcoded peak-hour dictionary it was given. `backend/app/ai/evaluation/evaluator.py` reports **hardcoded accuracy literals** (e.g. `accuracy = 88.42  # Calibrated ensemble accuracy`) for scheduling/sentiment/auto-reply/hashtag/caption — not computed from any run. The TF-IDF auto-reply classifier (`backend/app/ai/reply/engine.py`) is the one honest component — real, if small, hand-labeled corpus, actually fit.
> - **No scheduled-post execution mechanism.** `SchedulingService.execute_due_schedules()` exists and is exposed at an endpoint, but nothing calls it automatically — no Celery worker despite Celery being a declared, unused dependency (zero imports found anywhere in `backend/app`), no cron, no APScheduler.
> - **Rate limiter / circuit breaker / audit logger are implemented and unit-tested in isolation but never wired into `main.py` or any router.** They pass their own tests; they protect nothing in the running app.
> - **Dead code:** an orphaned top-level `aismm/` package (its own auth/db/config, superseded by `backend/app/`, zero imports from it anywhere), a duplicate unused ORM tree at `backend/app/core/models/*.py` (~1,200 lines, never imported — the real one Alembic targets is `backend/app/db/models.py`), and three parallel `Settings` classes (only `backend/app/config/settings.py` is actually wired).
> - **Frontend is mostly disconnected from the backend.** Of the original component set, only `ComposerTab.jsx` and `OverviewTab.jsx` imported the API client at all — the rest held hardcoded JS state. `API_BASE` was hardcoded to `localhost:8000`.
> - **Test suite: 194 tests exist (not 123), and 194/194 pass** when run with correct dependencies installed (`nltk` vader_lexicon + `cryptography` had to be added manually to get a clean run) — this one claim in the original project docs is true once corrected to the real count. But a meaningful share of those tests exercise isolated utility classes (the unwired rate limiter/circuit breaker/audit logger) rather than the integrated app — don't count them as integration coverage.
>
> Everything from here down is the original document, unmodified in substance.

---

# 0. ABSOLUTE OPERATING RULE

This is a **remediation and completion mission**, not a greenfield implementation.

The target is:

> Existing AISMM implementation + research requirements + CLAUDE.md + CLAUDE2.md + supplied UI design = one coherent, real, testable, secure, flexible, production-oriented application.

The supplied UI image is a **product/UI reference and acceptance target**. Preserve its visual language and information architecture while making the implementation real.

The application must not merely look functional.

Every important user-visible capability must be connected through:

`UI → frontend state → API client → authenticated API → service/domain layer → database/queue/AI engine/platform adapter → real response → UI`

Where an external platform or service cannot be used because credentials, permissions, quota or environment are unavailable:

- do NOT fabricate success;
- do NOT invent analytics;
- do NOT silently substitute fake metrics;
- do NOT claim live integration;
- implement a clearly identified development/sandbox/mock boundary where appropriate;
- expose the true integration status to the user;
- keep the production path separate from mock/test paths.

---

# 1. READ EVERYTHING BEFORE CHANGING ANYTHING

Before modifying code, perform an exhaustive repository discovery.

Read completely:

1. `CLAUDE.md`
2. `CLAUDE2.md`
3. `REQUIREMENT_MATRIX.md`
4. `SESSION_HISTORY.md`
5. all architecture documents under `docs/architecture/`
6. root configuration files
7. backend source
8. backend tests
9. Alembic migrations
10. frontend source
11. frontend tests/E2E
12. environment templates
13. Docker files
14. Makefile
15. package manifests
16. Python requirements
17. any datasets/models/configuration
18. any existing generated/legacy/orphan packages
19. all API routers
20. all services
21. all AI engines
22. all platform adapters
23. all security code
24. all database models/schemas
25. all frontend components and API calls.

Do not infer the repository structure from documentation.

Generate the structure from the actual filesystem.

Use commands such as:

```bash
pwd
git status --short --branch
git log --oneline --decorate -20
find . -type f -not -path './.git/*' | sort
find backend frontend docs -type f | sort
git grep -n "TODO\|FIXME\|DEFAULT_USER_ID\|localhost\|127.0.0.1"
git grep -n "SECRET\|TOKEN\|PASSWORD\|API_KEY"
```

Use additional static-analysis, dependency, test and build commands as required.

**Do not modify application code during the first discovery pass.**

---

# 2. TWO MASTER DOCUMENTS — RECONCILE, DO NOT BLINDLY OBEY

There are two major instruction documents:

- `CLAUDE.md`
- `CLAUDE2.md`

Treat both as historical project specifications, but resolve contradictions using this priority:

1. Current actual code/runtime behavior
2. User's current UI/product requirement
3. explicit security/reliability requirements in `CLAUDE2.md`
4. research-defined AISMM requirements
5. architecture documents
6. `CLAUDE.md`
7. historical session claims

If an older document says something is complete but the runtime disproves it, the runtime wins.

Do not restore false claims merely to make the documents look consistent.

Do not erase historical information simply because it is wrong. Correct it with an evidence-based status where appropriate.

---

# 3. REQUIRED FIRST DELIVERABLE: TRUTHFUL CURRENT-STATE AUDIT

Before major implementation, create a detailed audit in the working session output.

For every subsystem report:

| Area | Files | Intended behavior | Actual behavior | Evidence | Gap | Severity | Fix |
|---|---|---|---|---|---|---|---|

Audit at minimum:

- repository structure
- backend architecture
- frontend architecture
- database
- migrations
- authentication
- authorization
- configuration
- secret management
- API routes
- platform adapters
- social OAuth
- publishing
- scheduling
- comments/messages
- analytics
- AI engines
- ML evaluation
- datasets
- model registry
- notifications
- reports/export
- frontend/backend integration
- error/loading states
- Docker
- Redis
- PostgreSQL
- tests
- E2E
- observability
- security
- dependency health
- dead/duplicate code
- deployment readiness.

Also create a **feature truth table**:

`FEATURE → UI → ROUTE → API → SERVICE → DB/ENGINE → TEST → REALITY`

No feature is “complete” merely because a file exists.

---

# 4. THE UI IMAGE IS A PRODUCT ACCEPTANCE TARGET

The supplied UI represents the desired AISMM product.

Visual direction:

- dark Obsidian/Cyber-Neon interface
- near-black background
- electric violet primary accent
- cyan secondary accent
- restrained gradients/glows
- dense but readable professional dashboard
- responsive layouts
- cards with subtle borders
- modern SaaS/product feel
- consistent typography
- consistent iconography
- strong hierarchy
- polished loading/error/empty states.

Do not redesign the information architecture unless the existing implementation makes the target impossible. Prefer adapting the existing code.

The UI must not contain fake values simply because the screenshot contains sample values.

Sample values are visual references only.

---

# 5. UI MODULES — IMPLEMENT THE COMPLETE PRODUCT FLOW

The UI target contains 13 major modules.

## MODULE 01 — LANDING PAGE

Must include:

- AISMM branding
- navigation
- Features
- Solutions
- Research
- Pricing
- Docs
- About
- Sign In
- Get Started
- hero statement
- AI visual/hero composition
- AI Engine Live Preview
- AI Adapted Outputs
- live diagnostics
- caption quality
- sentiment score
- best time to post
- platform integration cards
- Instagram
- X/Twitter
- Facebook
- LinkedIn
- YouTube
- capability highlights:
  - AI Powered
  - Real-time
  - Secure
  - Scalable.

Rules:

- no fake “live” data presented as real;
- demo content must be explicitly demo content;
- links/buttons must actually work;
- auth buttons must route correctly.

---

# 6. MODULE 02 — AUTHENTICATION

Target flow:

1. Sign in
2. Create account
3. Verify email
4. Two-factor authentication
5. Successful account creation/login
6. Redirect to dashboard

Implement real:

- registration
- login
- password hashing
- JWT access token
- refresh token
- token expiration
- logout/session invalidation as appropriate
- email verification abstraction
- 2FA/TOTP where specified
- protected routes
- user ownership
- secure error messages
- rate limiting
- audit events.

Do not confuse:

`AISMM user authentication`

with:

`social-platform OAuth connection`.

They are different systems.

---

# 7. MODULE 03 — DASHBOARD OVERVIEW

Target elements:

- greeting
- date/time context
- Total Reach
- Engagement
- Profile Visits
- Clicks
- Conversions
- performance-over-time chart
- platform-performance chart
- AI insights
- recent/real activity
- platform breakdown.

All numbers must originate from real backend data.

No:

```js
const reach = 2400000;
```

No generated fallback metric.

If data is unavailable:

- show loading;
- then empty state;
- or explicit backend/integration error.

Never silently fabricate.

---

# 8. MODULE 04 — ANALYTICS

Implement real analytics capabilities:

- real-time/recent activity feed where data exists
- reach
- impressions/views where supported
- engagement
- likes/reactions
- comments
- shares/reposts where supported
- clicks
- CTR
- follower growth
- profile visits
- conversions where supported
- platform comparison
- date filtering
- time-series aggregation
- post-level analytics
- audience analytics where the platform API provides them
- unavailable metric handling.

Important:

If a platform does not provide a metric, represent it as:

- unavailable
- not supported
- not authorized
- not returned

Never turn missing data into zero unless zero is actually returned.

---

# 9. MODULE 05 — CONTENT COMPOSER

Implement:

- multi-platform selection
- universal content editor
- platform-specific variants
- character limits
- media upload
- image/video handling
- previews
- hashtags
- mentions
- links
- platform validation
- content warnings
- AI optimization
- save draft
- publish now
- schedule
- platform-specific customization.

Architecture:

`UniversalContent`
→ platform capability check
→ platform-specific transformation
→ adapter payload.

Do not duplicate business logic for each platform.

---

# 10. MODULE 06 — AI CONTENT ENGINE

UI target:

- Optimize
- Adapt
- Enhance
- Hashtags

Display:

- original score
- optimized score
- improvement reasons
- caption analysis
- hashtag recommendations
- platform adaptation
- content quality signals.

AI claims must be honest.

If an engine is heuristic/rule-based:

label it as heuristic.

If it is ML:

show actual model/evaluation status.

If an LLM is used:

keep provider abstraction/configuration separate from business logic.

Never claim “AI generated” when a static rule generated the result.

---

# 11. MODULE 07 — INTELLIGENT SCHEDULING

Implement:

- best-time recommendations
- historical engagement analysis
- timezone-aware scheduling
- calendar
- queue
- schedule creation
- update/cancel
- publishing worker
- retries
- failure handling
- idempotency
- concurrency safety.

Critical requirement:

A scheduled post must execute automatically.

No manual endpoint call should be necessary.

Use an appropriate production mechanism such as:

- Celery + Beat
- or another properly justified durable scheduler.

Redis is already part of the intended architecture.

The chosen scheduler must be documented.

Use safe state transitions such as:

`scheduled → publishing → published`

or

`scheduled → failed`

with retry policy.

Prevent double publishing.

---

# 12. MODULE 08 — PLATFORM MANAGEMENT

Target platforms:

- Instagram
- Facebook
- X/Twitter
- LinkedIn
- YouTube

Each platform must have:

- connection state
- OAuth flow
- token handling
- refresh behavior where supported
- disconnect
- capability declaration
- API version awareness
- permission/scopes
- publishing capabilities
- analytics capabilities
- comments/replies capabilities
- media constraints
- error translation
- rate limits.

No fake “Connected” state.

A platform should display Connected only when the credential/account connection is actually established and valid.

---

# 13. MODULE 09 — INBOX & ENGAGEMENT

Implement:

- All
- Messages
- Comments
- Mentions
- filtering
- platform identification
- timestamps
- conversation/thread context
- comment/reply actions
- AI-assisted response
- human approval routing
- spam handling
- unread/read state where supported
- sync mechanisms.

Auto-reply must not bypass safety/approval rules.

---

# 14. MODULE 10 — GROWTH INTELLIGENCE

Implement:

- follower growth
- engagement growth
- growth rate
- audience insights where supported
- demographics where actually available
- top locations
- top age groups where actually available
- top interests where actually available
- prediction horizon
- confidence
- forecast chart
- model status
- data coverage.

Predictions must be scientifically honest.

Never report a hardcoded R²/accuracy.

Never evaluate on training data only.

If there is insufficient real data:

say:

`Insufficient historical data for reliable forecast`

rather than fabricating a prediction.

---

# 15. MODULE 11 — AI STRATEGY ENGINE

Implement:

- content pillars
- recommendations
- posting strategy
- platform strategy
- engagement recommendations
- growth opportunities
- trend signals
- explainability
- confidence
- supporting evidence.

Every recommendation should be traceable to input data/model/rules.

Avoid generic hardcoded recommendations masquerading as personalized intelligence.

---

# 16. MODULE 12 — REPORTS & INSIGHTS

Implement:

- Performance Report
- Audience Report
- Content Report
- Engagement Report
- date range
- platform selection
- report generation
- CSV export
- PDF export
- correct timezone
- real data
- report metadata.

Exports must contain data actually retrieved/calculated by the backend.

No placeholder report.

---

# 17. MODULE 13 — SETTINGS

Tabs:

- General
- Security
- Notifications
- API Key Vault

Implement real persistence.

General:

- profile
- email
- timezone
- language
- theme.

Security:

- password change
- sessions where supported
- 2FA
- security events
- token/session controls.

Notifications:

- preferences
- failures
- scheduled post events
- platform connection events
- AI/recommendation notifications.

API/Secret Vault:

- encrypted secret storage
- never expose raw secrets after creation
- masked display
- rotation/deletion
- audit events
- authorization.

---

# 18. FRONTEND ENGINEERING RULES

Inspect every component currently in:

`frontend/src/components/`

including existing components such as:

- AnalyticsTab
- AutoReplyTab
- ComposerTab
- GrowthTab
- IntelligenceTab
- LandingPage
- ModelsTab
- Navbar
- OverviewTab
- PlatformsTab
- SchedulingTab
- SecurityTab
- Sidebar
- StrategyTab

Do not delete these merely because their names differ from the target UI.

Map each existing component to the desired product architecture.

Identify:

- unused components
- duplicate components
- disconnected components
- components with fake state
- components with hardcoded metrics
- missing API calls
- missing loading/error states
- incorrect routes
- inconsistent design.

Centralize frontend API access.

The repository currently contains an API client under:

`frontend/src/api/client.js`

and the historical remediation instructions refer to a centralized client.

Use ONE authoritative API client.

Do not create multiple competing API clients unless technically justified.

API base URL must be environment-driven.

No hardcoded:

`http://localhost:8000`

in application logic.

Use environment-specific configuration.

---

# 19. FRONTEND REALITY TEST

For every dashboard screen:

1. Stop backend.
2. Open screen.
3. Verify it shows a clear backend-unavailable state.
4. Start backend.
5. Authenticate.
6. Seed/modify real database data.
7. Refresh UI.
8. Verify UI reflects changed data.
9. Perform an action in UI.
10. Verify database/backend state changed.

This is the acceptance test for “live UI”.

A screenshot that looks correct is not proof.

---

# 20. BACKEND AUTHORIZATION

Every business endpoint must enforce authenticated user context.

Protected areas include, at minimum:

- accounts
- content
- posts
- analytics
- growth
- scheduling
- strategy
- intelligence
- reply
- models
- metrics
- settings
- reports.

Public/exception routes may include:

- health/liveness/readiness
- login
- registration
- verification
- public OAuth callbacks/webhooks where required.

Every protected query must enforce ownership.

Never use:

`DEFAULT_USER_ID`

for real application requests.

Test:

- unauthenticated → 401
- authenticated user A → own data
- authenticated user B → cannot access A data.

---

# 21. SECURITY — PRODUCTION BASELINE

Perform a full security audit.

Check:

- hardcoded secrets
- JWT secret defaults
- database passwords
- OAuth secrets
- API keys
- encryption keys
- static salts
- insecure CORS
- debug mode
- SQL injection
- unsafe query construction
- XSS
- CSRF where applicable
- SSRF risks
- path traversal
- unsafe file uploads
- MIME spoofing
- file-size limits
- malicious media
- token leakage
- log leakage
- PII exposure
- authorization bypass
- IDOR
- rate limits
- brute-force login
- refresh-token abuse
- webhook verification
- OAuth state validation
- redirect URI validation
- dependency vulnerabilities.

Never commit secrets.

Never create a new secret in source.

Secrets must come from environment/secret management.

---

# 22. SECRET VAULT

The existing project has a SecretVault concept.

Verify:

- authenticated encryption
- strong key derivation
- random salt
- no static universal salt
- no default master secret
- secret rotation
- secure storage
- masked output
- audit events.

Production startup must fail if required secrets are missing or obvious placeholder secrets are used.

---

# 23. RATE LIMITING, CIRCUIT BREAKER & RETRIES

The existing project contains production-hardening components.

Do not assume they are wired.

Verify actual runtime wiring.

Rate limiting:

- login/register
- expensive endpoints
- external platform calls
- abuse-sensitive operations.

Circuit breaker:

- external platform HTTP failures
- repeated failures
- OPEN/HALF_OPEN/CLOSED behavior.

Retry:

- exponential backoff
- jitter
- only retry safe/transient failures
- do not duplicate non-idempotent publishing.

Prove these behaviors with integration tests.

---

# 24. SOCIAL PLATFORM ADAPTER ARCHITECTURE

The core must remain platform-agnostic.

Desired architecture:

`AISMM Core`
→ `PlatformAdapter`
→ platform implementation.

Common abstractions:

- authenticate
- refresh
- disconnect
- validate content
- upload media
- publish
- schedule if supported
- fetch posts
- update/delete
- fetch comments
- fetch replies
- reply
- fetch analytics
- audience metrics
- webhooks
- capability reporting.

Each platform declares its real capabilities.

The frontend must dynamically adapt to capabilities.

Example:

If scheduling is unsupported:

do not display a functional scheduling action for that platform.

If analytics are unsupported:

show unavailable.

Never invent unsupported platform functionality.

---

# 25. UNIVERSAL DATA MODEL

Use normalized internal entities.

At minimum reason about:

- User
- SocialAccount
- Post
- PostPublication
- Media
- Comment
- Reply
- Engagement
- Audience
- Schedule
- Sentiment
- Prediction
- Recommendation
- Report
- AuditEvent
- ModelVersion
- Notification.

Platform-specific records belong at the adapter/publication boundary.

Do not pollute core domain models with dozens of platform-specific fields.

---

# 26. AI/ML INTEGRITY — ZERO FABRICATION

Audit every AI engine.

Known intended engines include:

- Sentiment
- Scheduling
- Growth
- Auto-Reply
- Caption
- Hashtag
- Recommendation
- Strategy/Intelligence
- Engagement-related analysis where present.

For each:

1. identify model;
2. identify training data;
3. identify features;
4. identify labels/targets;
5. identify preprocessing;
6. identify train/test split;
7. identify evaluation method;
8. identify metrics;
9. identify persistence/versioning;
10. identify inference API;
11. identify frontend usage;
12. identify monitoring;
13. identify drift handling.

Never accept:

- hardcoded accuracy
- hardcoded R²
- training-set-only evaluation
- labels derived from the same rule being “learned” without clearly labeling it
- fake “AI” claims
- static recommendations presented as model output.

If data is synthetic, label it synthetic.

If an engine is heuristic, label it heuristic.

If real training data is unavailable, do not fake evaluation.

---

# 27. GROWTH MODEL

For growth prediction:

- use real train/test separation;
- preferably temporal validation for time-series behavior;
- avoid leakage;
- separate prediction horizons where possible;
- report confidence/uncertainty;
- store model version;
- track actual outcome vs prediction.

Never present derived multiples as independently trained models.

---

# 28. SCHEDULING MODEL

For intelligent scheduling:

- distinguish learned model from heuristic;
- use historical data;
- include time/day/platform/media/content features as appropriate;
- prevent target leakage;
- evaluate out-of-sample;
- compare against baseline;
- expose recommendation reason;
- store model/version information.

If no reliable data exists, explicitly fall back to a documented heuristic.

---

# 29. SENTIMENT

Preserve research-defined sentiment behavior where applicable.

But verify:

- preprocessing
- thresholds
- positive/negative/neutral mapping
- confidence
- pre/post publishing use
- comment trajectory
- aggregation
- temporal analysis.

Do not call sentiment “live” unless it is actually calculated from live/retrieved content.

---

# 30. AUTO-REPLY

Implement:

- comment/message normalization
- intent classification
- confidence
- automatic reply threshold
- approval-required routing
- spam handling
- human-in-the-loop
- reply history
- audit events.

Do not auto-send low-confidence responses.

---

# 31. MODEL REGISTRY & EVALUATION

Model registry must contain truthful metadata:

- model ID
- version
- engine
- training data
- feature schema
- training timestamp
- evaluation timestamp
- metrics
- environment
- status
- production/staging/deprecated.

Evaluation must compute metrics at runtime.

No typed-in accuracy numbers.

---

# 32. DATABASE & MIGRATION DISCIPLINE

Audit:

- ORM models
- relationships
- indexes
- constraints
- foreign keys
- unique constraints
- nullable fields
- timestamps
- timezone handling
- transaction boundaries.

Every schema change after the current baseline must use a new Alembic revision.

Do not silently edit a historical production migration to change live schema semantics.

Test:

- upgrade
- downgrade where supported
- fresh database
- existing database upgrade.

---

# 33. SCHEDULER CONCURRENCY

Scheduled publishing must be:

- idempotent
- transaction-safe
- concurrency-safe
- retryable
- observable.

Use row locking or an equivalent claim mechanism.

A post must never be published twice because two workers/polls run simultaneously.

---

# 34. REAL-TIME / EVENTS

Where the product claims real-time behavior, determine the correct mechanism:

- polling
- WebSocket
- Server-Sent Events
- webhooks
- Redis pub/sub
- queue.

Do not label ordinary static API fetching as real-time.

For social platform updates, use webhooks where supported and polling where required.

---

# 35. API CONTRACT

Audit every route.

For each endpoint document:

- method
- path
- auth
- request schema
- response schema
- errors
- ownership
- rate limit
- external dependency
- side effects
- idempotency
- test.

No undocumented business endpoint should remain unexplained.

---

# 36. ERROR HANDLING

Frontend:

- loading
- empty
- error
- retry
- unauthorized
- forbidden
- validation
- conflict
- offline/backend unavailable.

Backend:

- validation
- authentication
- authorization
- platform API errors
- rate-limit errors
- timeout
- retryable vs non-retryable
- database errors
- queue errors
- model errors.

Do not catch every exception and return 200.

---

# 37. OBSERVABILITY

Maintain:

- structured logs
- correlation ID
- request timing
- health probes
- readiness
- liveness
- dependency health
- job status
- publishing status
- audit logs
- model inference timing/errors
- platform API failures.

Never log:

- passwords
- raw JWTs
- OAuth access tokens
- refresh tokens
- encryption keys
- API secrets.

---

# 38. DOCKER / DEPLOYMENT

Verify:

- backend image
- frontend image
- PostgreSQL
- Redis
- worker
- scheduler
- environment injection
- health checks
- dependency ordering
- persistent volumes
- non-root containers where practical
- production configuration
- frontend API URL
- backend CORS
- migrations.

Do not declare deployment production-ready merely because `docker compose up` works.

Test the actual application through the containers.

---

# 39. TESTING STRATEGY

Maintain multiple levels:

### Unit
- utility logic
- models
- AI logic
- normalization
- adapters

### Integration
- API
- database
- authentication
- authorization
- platform adapters
- scheduler
- queue
- vault

### E2E
- register
- login
- connect platform
- compose
- optimize
- schedule
- publish
- analytics
- inbox
- growth
- strategy
- reports
- settings.

### Security
- unauthorized access
- cross-user access
- brute force
- secrets
- webhook verification
- token leakage.

A passing unit suite is not enough.

---

# 40. PROOF-BASED DEFINITION OF DONE

A feature is DONE only when all applicable conditions are true:

- code exists;
- integrated into the actual application;
- reachable through the intended UI/API;
- correct database behavior;
- correct authentication/authorization;
- correct external integration;
- tests exist;
- integration test passes;
- E2E proof exists when applicable;
- no fake data;
- no dead implementation;
- error path works;
- loading/empty state works;
- documentation reflects truth.

Use this status vocabulary:

- NOT STARTED
- PARTIAL
- IMPLEMENTED
- INTEGRATED
- TESTED
- VERIFIED
- BLOCKED

Do not use VERIFIED without evidence.

---

# 41. NO FAKE DATA RULE

The following are forbidden in production paths:

- hardcoded KPI values
- fake engagement numbers
- fake follower counts
- fake chart arrays
- fake “connected” platform status
- fake API success
- fake ML metrics
- fake live activity
- fake user data
- static “AI insights”
- fake scheduled-post success.

Mock data may exist only inside explicitly isolated test/demo fixtures.

The production application must never silently use the mock fixture.

---

# 42. NO SILENT FALLBACKS

If backend is unavailable:

show an explicit UI error.

If an external platform is unavailable:

show the actual integration state.

If AI model is unavailable:

show model unavailable/insufficient-data state.

If analytics permission is missing:

show permission limitation.

Do not replace failures with plausible-looking numbers.

---

# 43. FLEXIBILITY REQUIREMENT

AISMM must remain extensible.

Adding a new social platform should require:

1. adapter
2. capability declaration
3. configuration
4. OAuth/integration
5. normalization mapping
6. tests

It must NOT require rewriting:

- dashboard core
- scheduler
- AI engines
- analytics aggregation
- recommendation logic
- content core.

Frontend must render capability-aware features.

---

# 44. UI ↔ CAPABILITY CONTRACT

Create a clean capability model.

Example:

```text
PlatformCapabilities:
  publishing
  scheduling
  text_post
  image_post
  video_post
  carousel_post
  stories
  short_video
  comments
  replies
  analytics
  audience_metrics
  webhooks
  direct_messages
  hashtags
  mentions
```

Frontend behavior must depend on this contract.

Do not hardcode:

```js
if (platform === "instagram") ...
```

for common product behavior.

Platform-specific constraints belong to the adapter/capability layer.

---

# 45. CURRENT FRONTEND TARGET MAPPING

The existing code has components whose names do not perfectly match the supplied UI.

Resolve this intentionally.

Target product mapping:

| UI | Required responsibility |
|---|---|
| Landing | public product/marketing experience |
| Auth | user authentication + verification + 2FA |
| Overview | main dashboard |
| Analytics | analytics + activity |
| Composer | content creation |
| AI Engine | optimization/adaptation/enhancement/hashtags |
| Scheduling | calendar + intelligent scheduling |
| Platforms | social account management |
| Inbox | messages/comments/mentions/replies |
| Growth | growth intelligence |
| Strategy | strategy recommendations |
| Reports | report generation/export |
| Settings | account/security/notification/vault |

Existing AutoReply, Models and Security components may be retained and integrated into the appropriate modules or settings/AI/inbox flows.

Do not destroy useful existing implementation simply to make filenames match the screenshot.

---

# 46. UI QUALITY BAR

Every screen must have:

- responsive layout
- consistent spacing
- consistent typography
- accessible controls
- keyboard navigation where applicable
- visible focus states
- semantic buttons/inputs
- disabled states
- loading states
- empty states
- error states
- confirmation for destructive actions
- toast/status feedback
- no broken links
- no console errors
- no React warnings.

Charts must:

- use real API data;
- handle empty datasets;
- handle long labels;
- handle responsive width;
- show correct units;
- show correct date/time range.

---

# 47. PERFORMANCE

Audit:

- unnecessary rerenders
- duplicate API calls
- oversized bundles
- image optimization
- pagination
- N+1 database queries
- slow analytics aggregation
- blocking ML inference
- queue usage
- caching opportunities.

Do not optimize prematurely.

Measure first.

---

# 48. DATA QUALITY

Analytics must define:

- metric semantics
- aggregation windows
- timezone
- deduplication
- source
- freshness
- unavailable values.

Never mix:

- views
- impressions
- reach
- engagement

as if they were interchangeable.

---

# 49. EXTERNAL API REALITY

Before implementing/changing an external platform integration:

verify current official API behavior, permissions, scopes, endpoint versions, publishing constraints, analytics availability and rate limits.

Do not assume a platform feature exists.

Do not build around outdated endpoints.

When credentials are unavailable, test the adapter boundary with a controlled mock but clearly separate it from live mode.

---

# 50. GIT DISCIPLINE

Before each work session:

```bash
git status
git log --oneline -10
```

Before changing code:

- understand current branch;
- understand uncommitted changes;
- do not overwrite user work.

After a completed verified unit of work:

```bash
git diff
git status
```

Then commit the actual change.

The user wants every meaningful Claude Code session preserved in GitHub history.

Do not use destructive commands such as:

```bash
git reset --hard
git clean -fd
```

unless the user explicitly authorizes the exact operation.

Never overwrite unrelated work.

---

# 51. CLAUDE.MD / SESSION HISTORY DISCIPLINE

The existing project uses `CLAUDE.md` as a long-lived project state document.

After a verified work unit:

- update the state honestly;
- record files changed;
- record tests;
- record actual result;
- record blockers;
- record next exact action.

Do not write:

`production ready`

unless the evidence supports it.

Do not write:

`194/194 tests passing`

unless that exact command was actually executed in the current verified state.

Do not alter historical claims merely to make them look cleaner.

---

# 52. REQUIRED WORKING LOOP

For every remediation section:

```text
READ
↓
TRACE
↓
REPRODUCE
↓
PLAN
↓
IMPLEMENT
↓
TEST
↓
INTEGRATE
↓
RUN REAL APP
↓
VERIFY
↓
DOCUMENT
↓
COMMIT
↓
PUSH
↓
VERIFY PUSH
```

Never:

```text
guess → code → claim complete
```

---

# 53. REQUIRED REMEDIATION ORDER

Work in this order unless a discovered dependency requires a justified adjustment:

## STEP 0 — Full repository truth audit

No major code changes.

## STEP 1 — Secrets/configuration

Remove insecure defaults and establish valid environment handling.

## STEP 2 — Authentication/authorization

Make user identity real and enforce ownership.

## STEP 3 — Production hardening wiring

Wire rate limiting, circuit breaker, retries and audit logging.

## STEP 4 — Scheduled execution

Make scheduling actually execute automatically.

## STEP 5 — ML honesty

Remove fabricated metrics and correct evaluation.

## STEP 6 — Frontend/backend integration

Replace disconnected/hardcoded UI data with real APIs.

## STEP 7 — Repository hygiene

Remove confirmed dead/duplicate code only after dependency proof.

## STEP 8 — Database migration discipline

Ensure schema evolution is reviewable.

## STEP 9 — Complete UI remediation

Bring all 13 product modules to the supplied UI target and real backend behavior.

## STEP 10 — Platform integration verification

Verify all five declared platforms.

## STEP 11 — AI integration verification

Verify every AI engine end-to-end.

## STEP 12 — Full lifecycle E2E

Test from authentication through publishing and analytics.

## STEP 13 — Production deployment verification

Run through Docker/production-like environment.

## STEP 14 — Final independent audit

Act as a hostile external reviewer.

Only then update final production-readiness claims.

---

# 54. SECTION COMPLETION REPORT

At the end of EACH major section, stop.

Do not automatically start the next section.

Use exactly:

```text
SECTION: <number + name>

OBJECTIVE:
<what was being fixed>

CHANGED FILES:
<files>

DELETED FILES:
<files or none>

DATABASE CHANGES:
<none or migration names>

API CHANGES:
<routes>

FRONTEND CHANGES:
<screens/components>

INTEGRATION CHANGES:
<services/platforms>

TESTS RUN:
<exact commands>

PROOF:
<paste actual relevant command output, not invented summaries>

HONEST STATUS:
FULLY DONE
or
PARTIALLY DONE
or
BLOCKED

REMAINING:
<exact remaining work>

SECURITY IMPACT:
<summary>

NEXT ACTION:
<one exact next step>
```

Then STOP and wait for the next instruction.

---

# 55. FINAL END-TO-END ACCEPTANCE TEST

Before calling the system production-ready, reproduce a realistic user lifecycle:

1. Start infrastructure.
2. Run migrations.
3. Start backend.
4. Start frontend.
5. Register user.
6. Verify authentication.
7. Login.
8. Access protected dashboard.
9. Verify another user cannot access the first user's records.
10. Connect a social platform.
11. Verify OAuth state and credential storage.
12. Create content.
13. Upload media.
14. Select multiple platforms.
15. Validate platform capabilities.
16. Run AI optimization.
17. Review sentiment.
18. Generate hashtags.
19. Generate platform variants.
20. Select intelligent scheduling.
21. Schedule post.
22. Let the scheduler execute automatically.
23. Verify publication state.
24. Retrieve comments/engagement.
25. Run auto-reply workflow.
26. Verify human approval when required.
27. Retrieve analytics.
28. View growth prediction.
29. Generate strategy recommendations.
30. Generate report.
31. Export CSV.
32. Export PDF.
33. Change settings.
34. Verify audit/security events.
35. Stop backend.
36. Verify frontend reports backend unavailable instead of showing fake values.
37. Restart backend.
38. Verify recovery.
39. Inspect logs for secret leakage.
40. Run full test suite.
41. Run frontend build.
42. Run containerized verification.
43. Re-check Git diff.
44. Re-check secrets.
45. Re-check all claims.

---

# 56. FINAL HOSTILE AUDIT

Before the final status, ask yourself:

- Is every important button actually connected?
- Does every screen use real data?
- Can I trace every KPI back to a source?
- Can an unauthenticated user access business data?
- Can user B access user A's records?
- Can a scheduled post execute without a manual trigger?
- Can two workers publish the same post?
- Are platform tokens encrypted?
- Are secrets absent from source?
- Are OAuth callbacks protected?
- Are external API failures handled?
- Are rate limits actually wired?
- Is the circuit breaker actually wired?
- Are audit logs actually generated?
- Are AI metrics actually computed?
- Is any AI output merely hardcoded?
- Is any chart fabricated?
- Is any “live” state fake?
- Does the frontend fail honestly when backend is down?
- Does every supported platform report its actual capabilities?
- Are unsupported capabilities hidden/disabled correctly?
- Are migrations clean?
- Are Docker services actually working?
- Are tests testing the real app rather than isolated functions?
- Can a fresh developer run the project from the documented instructions?
- Does the product visually match the supplied UI?
- Is the implementation flexible enough for another platform without rewriting the core?

If any answer is “no”, do not call the system fully production-ready.

---

# 57. IMPORTANT: DO NOT OVERWRITE THE PRODUCT IDEA

The product idea is:

> AISMM is a universal, AI-powered, multi-platform social media management platform whose core intelligence is platform-independent and whose social networks are connected through capability-aware adapters.

The UI is a premium dark AI SaaS dashboard.

The application should feel like a real product, not a university demo.

Keep:

- modularity
- extensibility
- AI core independence
- platform adapter architecture
- real analytics
- intelligent scheduling
- sentiment
- growth intelligence
- auto-reply
- caption optimization
- hashtag recommendation
- strategy
- reports
- security
- auditability
- production reliability.

---

# 58. FIRST ACTION — MANDATORY

When this prompt is given to Claude Code:

**DO NOT START CODING.**

First say, in one sentence:

> “I understand the remediation protocol: I will audit the actual repository and runtime first, distrust unsupported completion claims, preserve existing work, and only mark functionality complete when it is integrated and proven.”

Then perform ONLY:

1. repository discovery;
2. complete `CLAUDE.md` reading;
3. complete `CLAUDE2.md` reading;
4. architecture/document reading;
5. frontend structure analysis;
6. backend structure analysis;
7. database/migration analysis;
8. API/router analysis;
9. AI/ML analysis;
10. platform adapter analysis;
11. test analysis;
12. configuration/security audit;
13. UI-vs-implementation comparison;
14. Git status/history check.

Produce:

# AISMM MASTER CURRENT-STATE AUDIT

with:

A. Repository map  
B. Architecture map  
C. Backend map  
D. Frontend map  
E. Database map  
F. API map  
G. Platform map  
H. AI/ML map  
I. Authentication/security map  
J. UI fidelity audit  
K. Feature truth matrix  
L. Broken/disconnected features  
M. Missing features  
N. Fake/hardcoded data  
O. Security vulnerabilities  
P. Integration gaps  
Q. Technical debt  
R. Test gaps  
S. Production blockers  
T. Exact remediation plan  
U. Exact recommended order.

**Do not make major application changes during this first audit.**

Do not fabricate any result.

Do not claim the UI is accurate until you compare the actual rendered implementation against the supplied UI target.

Do not claim the backend is live until you trace and execute the actual API path.

Do not claim an AI engine works until its output is produced by the actual engine.

Do not claim a social platform is live until the actual adapter/API path is verified.

Do not claim production readiness until the final hostile audit passes.

---

# 59. FINAL PRINCIPLE

The objective is not:

> “make the repository look complete.”

The objective is:

> **make AISMM actually work as a coherent end-to-end product.**

Every important feature must be:

**specified → implemented → integrated → exercised → tested → verified → observable → secure → truthful.**

No fake completeness.

No disconnected UI.

No fabricated AI.

No fake integrations.

No hidden failures.

No hardcoded secrets.

No arbitrary rewrites.

No unnecessary redesign.

No skipping evidence.

Build the real system.
