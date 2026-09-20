# AISMM — System Architecture & Technical Specification

**Document Version:** 1.0.0  
**Status:** Active / Source of Truth  
**Target Architecture:** Multi-Platform, Platform-Agnostic, Capability-Driven, Research-Validated AI Core  

---

## 1. System Architecture Overview

AISMM is architected with strict separation of concerns across presentation, API gateway, business services, AI intelligence, and platform integration layers.

```
+---------------------------------------------------------------------------------------------------+
|                                     AISMM SYSTEM ARCHITECTURE                                     |
+---------------------------------------------------------------------------------------------------+

                          [ Browser Client / React 18 + Vite SPA ]
                         /                   |                    \
                  (App Navigation)     (State Store)       (API Client)
                        |                    |                    |
                        +--------------------+--------------------+
                                             |
                               [ HTTP / REST / JSON + JWT ]
                                             |
+--------------------------------------------v------------------------------------------------------+
|                                   FASTAPI BACKEND GATEWAY                                         |
|                                                                                                   |
|  +---------------------------------------------------------------------------------------------+  |
|  | Middleware: CORS | Correlation ID (X-Correlation-ID) | Process Time | Sliding Rate Limiter   |  |
|  +---------------------------------------------------------------------------------------------+  |
|  | Auth Dependencies: get_current_user | get_current_verified_user | get_current_superuser     |  |
|  +---------------------------------------------------------------------------------------------+  |
|                                                                                                   |
|  [ API v1 Routers (17 Modules) ]                                                                  |
|  - /auth         - /accounts       - /posts         - /content       - /ai         - /scheduling  |
|  - /reply        - /growth         - /analytics     - /strategy      - /models     - /intelligence|
|  - /metrics      - /comments       - /platforms     - /webhooks      - /health                    |
+--------------------------------------------+------------------------------------------------------+
                                             |
+--------------------------------------------v------------------------------------------------------+
|                                      BUSINESS SERVICES LAYER                                      |
|                                                                                                   |
|  [ UserService / SessionService / EmailService ]  [ PostService / PreviewService ]                |
|  [ SchedulingService (Async Background Worker) ]  [ IntelligenceService / ReplyService ]          |
|  [ AnalyticsService / MetricsService ]            [ GrowthService / StrategyService / ModelService|
|  [ OAuthService & State Manager ]                 [ OwnedAdapter Factory (Tenant Isolated) ]      |
+----------------------+----------------------------------------------------+-----------------------+
                       |                                                    |
+----------------------v----------------------+     +-----------------------v-----------------------+
|          AI & MACHINE LEARNING CORE         |     |          PLATFORM ADAPTER LAYER               |
|                                             |     |                                               |
|  [ PrePost & PostPost Sentiment (VADER) ]   |     |  [ BasePlatformAdapter & Capabilities ]       |
|  [ Caption Quality & Platform Optimizer ]   |     |  [ PlatformRegistry (Dynamic Discovery) ]     |
|  [ Top-K Statistical Hashtag Engine ]       |     |  [ CircuitBreaker & Exponential Backoff ]     |
|  [ Scheduling Ensemble (RF + GradBoost) ]   |     |  -------------------------------------------  |
|  [ Predictive Growth Regressors (RF) ]      |     |  [ Instagram Graph API Adapter (v20.0) ]      |
|  [ TF-IDF + Logistic Regression AutoReply ] |     |  [ Facebook Pages Graph API Adapter (v20.0) ] |
|  [ AI Strategy Synthesis Orchestrator ]     |     |  [ X / Twitter API v2 Adapter (PKCE OAuth) ]  |
|  [ Model Evaluation, Drift & Registry ]     |     |  [ LinkedIn REST & UGC Adapter (OAuth 2.0) ]  |
|                                             |     |  [ YouTube Data API v3 & Analytics Adapter ]  |
+----------------------+----------------------+     +-----------------------+-----------------------+
                       |                                                    |
+----------------------v----------------------------------------------------v-----------------------+
|                                  DATA & PERSISTENCE LAYER                                         |
|                                                                                                   |
|  [ SQLAlchemy 2.0 Async ORM ]                                                                     |
|  - Platform-Independent GUID Type (PostgreSQL native UUID / SQLite String(36))                    |
|  - EncryptedText TypeDecorator (AES-256 Vault Encryption for Access Tokens & 2FA Secrets)         |
|  - Models: User, OtpChallenge, AuthSession, SocialAccount, Post, PostMedia, PostPublication,      |
|            Comment, Metric, Schedule, MLModel, ModelPrediction, SentimentAnalysis, StrategyFeedback |
|                                                                                                   |
|  [ Storage Engines: PostgreSQL 16 (Production) / SQLite 3 (Local Development) ]                   |
|  [ Database Migrations: Alembic Version Control ]                                                 |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Frontend Architecture

### Technology Stack
- **Framework**: React 18.3.1 with Vite 8.2.2 bundler.
- **Routing**: `react-router-dom` v7 with canonical URL paths (`/app/:tab`, `/login`, `/register`, `/verify-email`, `/reset-password`, `/oauth/callback`, `/terms`, `/privacy`).
- **Icons & Styling**: `lucide-react`, Tailwind CSS with custom obsidian dark-theme design tokens.
- **State Management**: Local React state + Session Storage continuity for Composer drafts and active navigation contexts.

### Component Structure & 13 Studio Tabs
1. **OverviewTab**: High-level cross-platform KPIs, dynamic SVG audience charts, recent publication summaries, quick actions.
2. **ComposerTab**: Universal post creation, multi-platform targeting, media preview/validation, live character counters, real-time AI optimization trigger.
3. **SchedulingTab**: Visual 7-day calendar, scheduled queue, AI optimal slot recommendations, timezone selector.
4. **PlatformsTab**: Connected social account cards, live connection statuses (`Live OAuth`, `Expired`, `Unverified`), OAuth 2.0 connection triggers, direct handle connects, disconnect actions.
5. **AIEngineTab**: Interactive AI playground for Caption scoring, Hashtag extraction, Sentiment analysis, and Platform tone rewriting.
6. **InboxTab**: Unified social comment inbox, sentiment badges, automated reply suggestions, manual response input, sync trigger.
7. **AnalyticsTab**: Normalized cross-platform metric comparisons, engagement rates, impressions, reach, content ROI rankings.
8. **GrowthTab**: Historical follower growth trends, 7d/30d/90d predictive horizon cards with $R^2$ confidence indicators, demographic breakdown.
9. **StrategyTab**: Multi-model strategic directives synthesized by AI Strategy Engine, radar benchmark chart, actionable recommendations with feedback loops.
10. **ModelsTab**: Real-time ML model registry, active production models, holdout test metrics, feature importances, data drift monitors.
11. **ReportsTab**: Date-range filtered reporting engine with one-click JSON/CSV server export.
12. **SecurityTab**: Password modification, TOTP MFA setup with SVG QR code, backup recovery code regeneration, session revocation.
13. **SettingsTab**: User profile settings, display name, avatar, timezone selection, language preferences.

### API Client & Session Mutex (`frontend/src/api/client.js`)
- **Bearer Token & HttpOnly Cookie Hybrid**: Automatically attaches `Authorization: Bearer <token>` while allowing browser cookies to flow.
- **401 Single-Flight Refresh Mutex**: Intercepts 401 Unauthorized responses, executes a single asynchronous token refresh request, updates session tokens, and retries the original failed call without cascading race conditions.
- **No Mock Fallbacks**: Throws explicit HTTP status errors when the backend is offline or an endpoint fails.

---

## 3. Backend Architecture & API Gateway

### FastAPI Application Factory (`backend/app/main.py`)
- **Lifespan Manager**: Initializes database connections, runs health checks, outputs social OAuth startup diagnostics, and spawns the background async scheduler worker task.
- **Middleware Pipeline**:
  1. `CORSMiddleware`: Strict origin allowlisting from `settings.CORS_ORIGINS`.
  2. `add_process_time_and_correlation_header`: Generates/propagates `X-Correlation-ID` and measures processing latency via `X-Process-Time-Ms`.
- **Exception Hierarchy**: Unified error handlers converting domain exceptions (`NotFoundError`, `ValidationError`, `AuthenticationError`, `PlatformError`, `RateLimitError`) into standardized JSON error responses.

### Router Hierarchy (`backend/app/api/v1/router.py`)
All endpoints are versioned under `/api/v1/` and protected by dependency injection:
- `get_current_user`: Validates JWT signature, checks expiration, and validates active `AuthSession` in database.
- `get_current_verified_user`: Enforces that `is_verified` or `phone_verified` is True, protecting all operational social endpoints.
- `get_current_active_superuser`: Restricts admin-only endpoints.

---

## 4. Database Architecture & Migrations

### Dual-Database Compatibility
The data layer is built on SQLAlchemy 2.0 Async with two custom TypeDecorators ensuring seamless cross-database compatibility between PostgreSQL 16 and SQLite:
1. **`GUID`**: Emits native PostgreSQL `UUID` on Postgres and `CHAR(36)` on SQLite, automatically handling Python `uuid.UUID` serialization.
2. **`EncryptedText`**: Automatically intercepts read/write operations at the ORM boundary to encrypt sensitive data (OAuth tokens, TOTP secrets) before writing to disk and decrypt upon retrieval.

### Core Data Models
- **`User`**: Core user entity, password hashes, email/phone verification timestamps, 2FA configuration, recovery codes.
- **`OtpChallenge`**: Server-side tracking for email/password OTPs with cryptographic hashes, attempt counters, and expiration timestamps.
- **`AuthSession`**: Active JWT sessions, SHA-256 hashed refresh tokens, expiration and revocation flags.
- **`OAuthState` / `OAuthAttempt`**: Transient OAuth authorization requests, encrypted PKCE code verifiers, state hashes.
- **`SocialAccount`**: Connected social accounts, encrypted access/refresh tokens, token expiration, platform metadata, permissions.
- **`Post`**: Social content, captions, hashtags, mentions, lifecycle status (`draft`, `scheduled`, `publishing`, `published`, `failed`).
- **`PostMedia`**: Attached media items, URLs, dimensions, mime-types, durations.
- **`PostPublication`**: Platform-specific publication records, platform post IDs, permalinks, container IDs, publication status.
- **`Comment`**: Synced social comments with thread hierarchy and hidden status.
- **`Metric`**: Normalized time-series analytics snapshots per platform and entity.
- **`Schedule`**: Publishing schedules, retry counters, execution timestamps, timezones.
- **`MLModel` & `ModelPrediction`**: Model registry, parameters, metrics, artifact locations, inference prediction log.
- **`SentimentAnalysis`**: Sentiment classification scores, confidence, entities, and keywords.
- **`StrategyFeedback`**: User feedback records for AI strategy recommendations.

### Alembic Migration History
```
<base>
  └─ 1c2e5404a0b3 (Initial Schema)
      └─ 2a3f7b8c9d0e (Auth Security Attributes)
          └─ 3b4c5d6e7f8a (Email Verification Fields)
              └─ 4c5d6e7f8a9b (Phone Verification Fields)
                  └─ 5d6e7f8a9b0c (Durable Sessions, OAuth State, Vault)
                      └─ 6e7f8a9b0c1d (Strategy Feedback)
                          └─ 7f8a9b0c1d2e (2FA Recovery Codes & Publication Account ID)
                              └─ 8a9b0c1d2e3f (OAuth Verified At Timestamp)
                                  └─ 9b8c1e2f3a4d (OtpChallenge Table & email_verified_at) [HEAD]
```

---

## 5. Security & Vault Architecture

### Authentication & Secrets
- **Password Hashing**: `bcrypt` with 12 salt rounds; passwords constrained to max 72 UTF-8 bytes to prevent truncation attacks.
- **Token Cryptography**: `PyJWT` HS256 algorithm signing access tokens with configurable expiration (default 30 mins) and secret rotation capability.
- **Secret Vault (`backend/app/core/vault.py`)**: `Fernet` symmetric encryption utilizing PBKDF2-HMAC-SHA256 (100,000 iterations) with cryptographic random salts per record. All stored OAuth tokens are prefixed with `v2$` envelope metadata.
- **Two-Factor Authentication (TOTP)**: RFC 6238 time-based one-time passwords with 30-second windows and replay protection tracking `two_factor_last_step`.

### Network & Application Hardening
- **Sliding Window Rate Limiting (`backend/app/core/rate_limit.py`)**: Per-IP and per-user sliding window limiters protecting authentication endpoints from brute-force attempts.
- **Audit Logging (`backend/app/core/audit.py`)**: Structured compliance audit logs capturing authentication attempts, credential changes, and publishing events with IP address and correlation tracking.
- **Media SSRF Protection**: Strict validation of media URLs in `PostService`, rejecting loopback, local network, and non-HTTPS endpoints.

---

## 6. Platform Adapter Architecture

### Design Principles
1. **Platform-Agnostic Core**: Business logic only interacts with `UniversalContent`, `UniversalMedia`, and `NormalizedMetric` objects.
2. **Capability-Driven**: Every adapter explicitly declares its `SUPPORTED_CAPABILITIES` (e.g. `POST_IMAGE`, `POST_REEL`, `GET_ANALYTICS`). Adapters reject unsupported operations with `UnsupportedCapabilityError`.
3. **Resilience by Default**: All outgoing platform HTTP calls are wrapped in `CircuitBreaker` and `async_retry_with_backoff` to handle transient network and provider 5xx errors.
4. **Tenant-Isolated Construction (`owned_adapter`)**: Adapter instances are never shared singletons. They are instantiated per-request with the authenticated user's decrypted credentials.

### Supported Adapters
- **Instagram Adapter (`backend/app/core/platform_adapters/instagram/`)**: Meta Graph API v20.0, container-based publishing, carousel creation, reel publishing, story publishing, webhook verification.
- **Facebook Adapter (`backend/app/core/platform_adapters/facebook/`)**: Meta Graph API v20.0, Page feed publishing, photo/video uploading, Page insights, feed webhooks.
- **X (Twitter) Adapter (`backend/app/core/platform_adapters/x/`)**: Twitter API v2, OAuth 2.0 PKCE, tweet publishing, chunked media upload, CRC challenge webhook verification.
- **LinkedIn Adapter (`backend/app/core/platform_adapters/linkedin/`)**: 3-legged OAuth 2.0, UGC Post API, share statistics, organization & member targeting.
- **YouTube Adapter (`backend/app/core/platform_adapters/youtube/`)**: Google OAuth 2.0, YouTube Data API v3 resumable video upload, YouTube Analytics API, WebSub Atom feed pub/sub.

---

## 7. AI Core & Machine Learning Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                     AISMM AI ENGINE SUITE                                         |
+---------------------------------------------------------------------------------------------------+

  [ 1. Sentiment Engine ]
    - Research Baseline: VADER + Emoji Lexicon Weighting
    - Output: Compound Polarity (-1.0 to +1.0), Pos/Neu/Neg breakdown, Confidence score
    - Dual-Phase Execution: Pre-posting draft analysis & Post-posting comment trajectory

  [ 2. Caption Optimization Engine ]
    - Analyzes length, readability, hook strength, and platform tone
    - Rewrites and formats text specifically for Instagram, Facebook, X, LinkedIn

  [ 3. Top-K Hashtag Recommendation Engine ]
    - Evaluates keyword relevance, platform density, and engagement lift
    - Emits ranked Top-K hashtag recommendations (default K=5)

  [ 4. Intelligent Scheduling Engine ]
    - Ensemble: Random Forest Classifier + Gradient Boosting Classifier
    - Features: 16 cyclical temporal and content features (Hour, DOW, Is_Weekend, Format, Tags)
    - Output: Ranked 168 weekly hour slots with predicted engagement scores

  [ 5. Auto-Reply & Comment Intelligence Engine ]
    - Classifier: TF-IDF Vectorizer + Multinomial Logistic Regression
    - Categories: Inquiries, Compliments, Complaints, Spam, General
    - Policy Router: Automatic execution vs. Human-in-the-loop review queue

  [ 6. Predictive Growth Engine ]
    - Model: Platform-specific Random Forest Regressors
    - Multi-Horizon Forecasting: 7-day, 30-day, and 90-day follower and reach projections
    - Metrics: $R^2$ confidence indicators, RMSE, and feature importances

  [ 7. Master AI Strategy Engine ]
    - Orchestrator: Multi-model synthesis cross-referencing all 6 individual engines
    - Output: Ranked strategic recommendations, optimal posting windows, platform profiles

  [ 8. Model Improvement & Registry ]
    - Tracks active models, versions, training/evaluation metrics, and drift statistics
    - Automated staging-to-production promotion criteria
+---------------------------------------------------------------------------------------------------+
```

---

## 8. Scheduling & Background Worker Pipeline

```
+---------------------------------------------------------------------------------------------------+
|                                 SCHEDULER EXECUTION PIPELINE                                      |
+---------------------------------------------------------------------------------------------------+
  1. Lifespan Task (`run_scheduler_background_worker`) wakes every 10 seconds.
  2. Queries `schedules` table for `status='pending'` and `scheduled_at <= now()`.
  3. Executes atomic database claim: `UPDATE schedules SET status='publishing' WHERE id=:id AND status='pending'`.
  4. If claim succeeds, loads associated `Post` and `User`.
  5. Resolves target platforms from `PostPublication` records.
  6. Instantiates tenant-isolated `owned_adapter` for each platform.
  7. Publishes content through platform adapter.
  8. On Success:
     - Updates `PostPublication` status to `'published'` with platform post ID and permalink.
     - Sets `Schedule` status to `'sent'`.
     - Updates `Post` status to `PUBLISHED` and records `published_at`.
  9. On Transient Failure (Network/5xx):
     - Increments `retry_count`, calculates exponential backoff delay, sets `status='pending'`.
  10. On Permanent Failure (Auth/4xx):
     - Sets `Schedule` status to `'failed'`, records `error_message`, and marks `Post` as `FAILED`.
+---------------------------------------------------------------------------------------------------+
```

---

## 9. Observability, Telemetry & Logging

- **Structured Logging (`backend/app/logging/`)**: JSON-formatted logs with timestamps, log levels, module names, correlation IDs, and sanitized payloads.
- **Correlation ID Tracking**: Automatically extracted from incoming `X-Correlation-ID` header or generated as a UUIDv4, passed across all async service boundaries.
- **Health Probes (`/health`, `/health/liveness`, `/health/readiness`)**:
  - `/health/liveness`: Verifies process health and memory status.
  - `/health/readiness`: Verifies database connectivity and OAuth registry state.
  - `/health/telemetry`: Reports operational performance metrics and error rates.
