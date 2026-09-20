# AISMM — Product Requirements Document (PRD)

**Document Version:** 1.0.0  
**Product:** AISMM (AI-Powered Universal Social Media Management System)  
**Status:** Active / Source of Truth  
**Target Architecture:** Multi-Platform, Platform-Agnostic, Capability-Driven, Research-Validated AI Core  

---

## 1. Executive Summary & Product Vision

AISMM is an enterprise-grade, multi-platform social media management and AI intelligence platform. It enables individual creators, social media managers, marketing teams, and enterprises to:

1. **Unify Social Presence**: Connect, authenticate, and manage social accounts across Meta (Instagram, Facebook Pages), X (Twitter v2), LinkedIn (REST/UGC), and YouTube (Data API v3 & Analytics) through a single zero-trust control plane.
2. **Accelerate Content Operations**: Compose multi-platform campaigns once, automatically transform and validate media/text per target platform capabilities, generate AI-optimized variants, preview accurately, and schedule across global timezones.
3. **Execute AI-Driven Strategy**: Leverage research-backed machine learning algorithms (Random Forest + Gradient Boosting ensembles, VADER + emoji sentiment, TF-IDF + Logistic Regression auto-reply routing, platform-specific Random Forest growth regressors, and multi-model strategic synthesis) to optimize engagement, reach, and timing.
4. **Automate Engagement & Community Intelligence**: Sync comments in near-real-time, monitor sentiment trajectories, detect viral/crisis spikes, and execute safe automated replies with configurable human-in-the-loop approval thresholds.
5. **Provide Truthful Analytics & Continuous Improvement**: Ingest and normalize platform metrics without synthetic fabrication, deliver cross-platform benchmarking, temporal 7x24 heatmaps, and track continuous ML model drift, feature importances, and evaluation metrics.

---

## 2. Target Users & Problem Statements

### User Personas
- **Solo Creators & Influencers**: Need rapid caption crafting, Top-K hashtag suggestions, multi-platform adaptation, and intelligent posting times without managing multiple separate native apps.
- **Social Media Managers & Agencies**: Need cross-account isolation, scheduled publishing with atomic execution, engagement inbox with auto-reply suggestions, human-in-the-loop review queues, and exportable client performance reports.
- **Enterprise Marketing Teams**: Require strong authentication (bcrypt, single-use refresh token rotation, TOTP 2FA, recovery codes), AES-256 encrypted credential storage, strict audit logging, rate limiting, and reliable OAuth 2.0 PKCE token lifecycles.

### Core Problems Solved
1. **Platform Fragmentation**: Incompatible native APIs, differing media constraints, fragmented comment streams, and siloed analytics.
2. **Timing Guesswork**: Ineffective, manual posting schedules that miss platform-specific audience peak windows.
3. **Engagement Bottlenecks**: High comment volumes causing slow customer support response times and unaddressed negative sentiment crises.
4. **Data Dishonesty**: Tools that mask offline states or extrapolate synthetic fake metrics instead of reporting honest provider telemetry.

---

## 3. End-to-End User Journeys

```
+---------------------------------------------------------------------------------------------------+
|                                      AISMM CORE USER JOURNEY                                      |
+---------------------------------------------------------------------------------------------------+
  [1. Identity & Auth]
    User Registration -> Secure Password Hashing -> 6-Digit Email OTP Delivery -> Verification
    -> Login -> JWT Access + Refresh Session -> Optional TOTP MFA + Recovery Codes -> Protected Studio
        |
  [2. Social Connection & Token Vault]
    OAuth 2.0 PKCE Init -> State Validation -> Provider Callback -> AES-256 Vault Token Encryption
    -> SocialAccount Record -> Capability Matrix Detection -> Account Profile Ingestion
        |
  [3. Content Creation & AI Optimization]
    Composer Tab -> Universal Content Input -> Dual-Phase Sentiment Analysis (PrePostAnalyzer)
    -> Caption Quality Scoring -> Top-K Hashtag Recommendation -> Platform-Specific Adaptation
    -> Accurate Live Previews (IG, FB, X, LinkedIn, YouTube)
        |
  [4. Intelligent Scheduling & Publishing]
    RF + GradientBoosting Ensemble Slot Scoring -> Timezone Resolution -> Schedule Record
    -> Background Async Scheduler Worker -> Atomic DB Claim (`status='publishing'`)
    -> Owner-Bound Platform Adapter -> Platform API Dispatch -> PostPublication Confirmation
        |
  [5. Post-Publish Sync & Community Intelligence]
    Post-Posting Sync -> Comment Ingestion -> Temporal Sentiment Trajectory Tracking
    -> Spike & Crisis Alerting -> TF-IDF Intent Classification -> Safe Auto-Reply Routing
    -> Human-in-the-Loop Approval (if confidence < threshold or sensitive) -> Reply Dispatch
        |
  [6. Analytics, Growth & Strategy Synthesis]
    Normalized Metrics Ingestion -> Deduplicated Time-Series Storage -> 7x24 Temporal Heatmap
    -> Platform-Specific Random Forest Growth Horizons (7d/30d/90d) -> AI Strategy Engine Synthesis
    -> Continuous Model Evaluation & Drift Monitoring -> Automated CSV/JSON Client Reports
+---------------------------------------------------------------------------------------------------+
```

---

## 4. Functional Requirements

### FR-01: Authentication & Access Control
- **FR-01.1**: Email & password registration with password length ≤ 72 UTF-8 bytes (bcrypt limit) and minimum complexity enforcement.
- **FR-01.2**: 6-digit cryptographic Email OTP verification with 5-minute expiry, SHA-256 storage hash, max 5 attempts, and explicit delivery via SMTP.
- **FR-01.3**: JWT token pair issuance (30-minute access token, 7-day refresh token) backed by durable database `AuthSession` with single-use refresh rotation.
- **FR-01.4**: RFC 6238 TOTP two-factor authentication with SVG QR code setup, `last_totp_step` replay prevention, and 8 hashed backup recovery codes.
- **FR-01.5**: Secure password reset flow via time-limited OTP or token with rate limiting and automated session invalidation.

### FR-02: Platform Connection & OAuth Lifecycle
- **FR-02.1**: Support OAuth 2.0 (with PKCE where required) for Instagram Graph API (v20.0), Facebook Graph API (v20.0), X (Twitter v2), LinkedIn UGC/REST, and YouTube Data API v3.
- **FR-02.2**: 32-byte cryptographic state parameters with SHA-256 hash validation in `OAuthState` / `OAuthAttempt` tables to prevent CSRF and token injection.
- **FR-02.3**: Secret vault encryption using Fernet / AES-256 for all OAuth access tokens, refresh tokens, and 2FA secrets at the ORM boundary (`EncryptedText`).
- **FR-02.4**: Clear presentation of connection statuses: `Live OAuth (Active)`, `Expired / Reconnect Needed`, `Unverified / Direct`.
- **FR-02.5**: Platform account disconnect and cascade cleanup of credentials.

### FR-03: Content Composition & Multi-Platform Management
- **FR-03.1**: Universal content composer supporting text, captions, media attachments (images, video, reels, carousels), hashtags, and mentions.
- **FR-03.2**: Platform capability enforcement (character limits, media formats, aspect ratios, story/reel/carousel support) rejecting incompatible payloads before dispatch.
- **FR-03.3**: Live multi-device preview generation replicating native platform cards for Instagram, Facebook, X, LinkedIn, and YouTube.
- **FR-03.4**: Session-persisted draft state in frontend to prevent data loss across tab navigation and browser refreshes.

### FR-04: AI Content & Optimization Engines
- **FR-04.1 (Sentiment)**: Dual-phase VADER + emoji polarity scoring (-1.0 to +1.0) with configurable thresholds and confidence estimates.
- **FR-04.2 (Caption)**: Readability, hook strength, engagement probability, and length optimization tailored per target platform.
- **FR-04.3 (Hashtags)**: Top-K statistical recommendation ranking hashtags by domain relevance, reach potential, and platform density.
- **FR-04.4 (Unified Content Optimizer)**: Single-call synthesis returning sentiment, caption analysis, hashtags, and customized variants for all selected platforms.

### FR-05: Scheduling & Background Execution
- **FR-05.1 (Intelligent Slot Recommendation)**: Random Forest + Gradient Boosting ensemble scoring 168 weekly hour slots based on platform-specific audience peak distributions.
- **FR-05.2 (Timezone Handling)**: User-configurable timezone persistence with UTC database normalization and localized calendar rendering.
- **FR-05.3 (Atomic Worker Dispatch)**: Background asynchronous scheduler executing every 10 seconds, utilizing row locking (`status='publishing'`) to ensure exactly-once dispatch without double-publishing.
- **FR-05.4 (Retry & Resilience)**: Exponential backoff with circuit breakers on transient platform 5xx errors; immediate permanent failure recording on 4xx authorization errors.

### FR-06: Post-Posting Intelligence & Community Inbox
- **FR-06.1 (Comment Synchronization)**: On-demand and scheduled comment ingestion from connected platforms into `Comment` entities.
- **FR-06.2 (Temporal Sentiment)**: Tracking sentiment score trajectory across post lifetime (1h, 6h, 24h, 7d).
- **FR-06.3 (Spike & Crisis Detection)**: Real-time generation of alerts on sudden comment volume spikes or negative sentiment surges.
- **FR-06.4 (Auto-Reply Routing)**: TF-IDF + Logistic Regression intent classifier categorizing comments into Inquiries, Compliments, Complaints, Spam, and General.
- **FR-06.5 (Human-in-the-Loop)**: High-confidence routine replies executed automatically; negative, ambiguous, or complaint replies routed to manual operator review queue.

### FR-07: Analytics, Growth & AI Strategy
- **FR-07.1 (Truthful Analytics)**: Aggregation of platform metrics (impressions, reach, engagement rate, video views, likes, shares, comments) with latest-snapshot deduplication. Zero synthetic fabrication for empty accounts.
- **FR-07.2 (Growth Forecasting)**: Platform-specific Random Forest Regressors generating 7-day, 30-day, and 90-day follower and reach projections with $R^2$ confidence indicators.
- **FR-07.3 (AI Strategy Engine)**: Synthesis of scheduling, sentiment, growth, and content performance into ranked actionable strategic recommendations and platform profiles.
- **FR-07.4 (Continuous Model Evaluation)**: Registry of active ML models (`ml_models`, `model_predictions`) tracking holdout test accuracy, $R^2$, F1-score, feature importances, and drift metrics.
- **FR-07.5 (Exportable Reports)**: Multi-format (JSON/CSV) report generation with custom date ranges and platform filtering.

---

## 5. Non-Functional Requirements

| Metric | Target | Verification Method |
| :--- | :--- | :--- |
| **API Response Time** | P95 < 150ms for DB reads; P95 < 350ms for AI inference | Built-in correlation & `X-Process-Time-Ms` middleware |
| **Test Coverage** | ≥ 300 backend unit/integration tests; ≥ 15 frontend tests | Automated pytest and node test runners |
| **Security Standards** | OWASP Top 10 compliant; zero secret exposure; encrypted vault | Bandit / safety / security test suite |
| **Database Support** | PostgreSQL 16 (production) & SQLite (local development) | Platform-independent `GUID`, `EncryptedText`, Alembic migrations |
| **Browser Support** | Modern evergreen browsers (Chrome, Firefox, Safari, Edge) | Vite 8.2.2 bundle, responsive Tailwind CSS layout |
| **Fail-Safe Operation** | Fail-loud HTTP 503/502 on missing credentials; zero fake numbers | Strict schema validation, explicit error responses |

---

## 6. Acceptance Criteria

A feature in AISMM is considered complete and accepted ONLY when:
1. **Contract Defined**: Pydantic schema and database model are fully typed and migrated.
2. **Business Logic Implemented**: Service handles all success, edge, and error branches.
3. **API Exposed**: REST route is documented in OpenAPI with proper authentication dependencies.
4. **Frontend Connected**: UI component triggers real API calls, renders loading/empty/error states, and eliminates mock data.
5. **Security Enforced**: Tenant isolation verified (`user_id` scoping), inputs sanitized, secrets encrypted.
6. **Automated Verification**: Unit and integration tests pass with zero regressions.
7. **Production Documented**: Documented in `ARCHITECTURE.md`, `PRD.md`, and tracked in `TASKS.md`.
