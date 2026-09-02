# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-16%20Production%20Hardening%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-184%2F184%20passing%20(100%25)-brightgreen)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Framework](https://img.shields.io/badge/framework-FastAPI%20%7C%20SQLAlchemy%20%7C%20Alembic-blue)

AISMM is a **platform-agnostic, AI-powered social media management platform** built with a modular adapter architecture. The core AI engines (scheduling, sentiment, growth prediction, auto-reply, caption/hashtag optimization) are completely independent of any social media platform — new platforms are added via adapters without touching core logic.

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      AISMM CORE                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │Content   │ │AI        │ │Analytics │ │Recommendation  │  │
│  │Engine    │ │Engine    │ │Engine    │ │Engine          │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└──────────────────────────┬────────────────────────────────────┘
                           │ Platform Interface (Adapter Contract)
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
   ┌────────┐         ┌────────┐         ┌────────┐
   │Instagram│         │Facebook│         │LinkedIn│
   │Adapter  │         │Adapter │         │Adapter │
   └────────┘         └────────┘         └────────┘
```

---

## ✅ Phase Status & Verification

| Phase | Description | Status | Test Coverage |
|-------|-------------|--------|---------------|
| **0** | **Project Discovery & Audit** | ✅ Verified | Baseline repository audit complete |
| **1** | **Requirement Mapping** | ✅ Verified | All 17 phases mapped to research requirements |
| **2** | **Architecture Design** | ✅ Verified | 3 specification documents, 29 ADRs |
| **3** | **Core Foundation** | ✅ Verified | Normalization, Base Adapter, Registry, Config, Security, Logging, Errors, DB Models, Alembic |
| **4** | **First Platform (Instagram)** | ✅ Verified | Full Instagram Graph API E2E, API v1 modular routers |
| **5** | **Second Platform (Validation)** | ✅ Verified | Facebook Page Adapter, zero core rewrites |
| **6** | **Content Management** | ✅ Verified | Multi-platform composer, platform customization, preview engine |
| **7** | **AI Content Engine** | ✅ Verified | Dual-Phase Sentiment, Caption Quality Analyzer, Top-K Hashtags |
| **8** | **Intelligent Scheduling Engine** | ✅ Verified | ML Temporal Ensemble, Auto-Scheduler, Queue Dispatch |
| **9** | **Post-Posting Intelligence** | ✅ Verified | Comment Sync, Temporal Sentiment Trajectory, Spike Alerts |
| **10** | **Auto-Reply Engine** | ✅ Verified | TF-IDF Intent Classifier, Human-in-the-Loop Routing |
| **11** | **Predictive Growth Engine** | ✅ Verified | Platform-Specific Random Forest Regressors, 7/30/90-Day Projections |
| **12** | **Universal Analytics Dashboard** | ✅ Verified | Cross-Platform Aggregations, Benchmarking, Temporal Heatmaps, Growth Drift |
| **13** | **AI Strategy Engine** | ✅ Verified | Multi-Model Synthesis, Strategic Recommendations, Platform Profiles |
| **14** | **Multi-Platform Expansion** | ✅ Verified | X / Twitter API v2, LinkedIn REST & UGC, YouTube Data v3 & Analytics |
| **15** | **Model Improvement & Evaluation** | ✅ Verified | Continuous Model Evaluation, Feature Importance, Class Imbalance, Drift Tracking, Model Registry |
| **16** | **Production Hardening** | ✅ **100% Verified** | **184/184 Tests Passing** (AES-256 Vault Encryption, Sliding Window Rate Limiting, Circuit Breaker & Exponential Backoff, Audit Logging, Health Probes) |

---

### Phase 16 Production Hardening Deliverables

| Component | Module | Description | Security & Reliability Standard |
|-----------|--------|-------------|---------------------------------|
| **Secret Vault Encryption** | `backend/app/core/vault.py` | AES-256 authenticated encryption (`SecretVault`) for OAuth access/refresh tokens, client secrets, and platform credentials | PBKDF2-HMAC-SHA256 at rest |
| **Sliding Window Rate Limiter** | `backend/app/core/rate_limit.py` | Microsecond sliding-window in-memory and endpoint dependency (`rate_limit_guard`) with 429 throttling and dynamic retry headers | Token bucket & window protection |
| **Circuit Breaker & Retries** | `backend/app/core/resilience.py` | `CircuitBreaker` (CLOSED/OPEN/HALF_OPEN) and `async_retry_with_backoff` with exponential backoff and randomized full jitter | Cascade failure prevention |
| **Compliance Audit Logger** | `backend/app/core/audit.py` | Structured JSON audit logging (`AuditLogger`) capturing security, authentication, publishing, and promotion events | SIEM / Compliance standard |
| **Health Probes & Telemetry** | `backend/app/api/v1/health.py` | `/api/v1/health/liveness`, `/api/v1/health/readiness`, and `/api/v1/health/telemetry` endpoints | Kubernetes probe compatibility |
| **Observability Middleware** | `backend/app/main.py` | `X-Correlation-ID` request tracking and `X-Process-Time-Ms` response headers | Microservice observability |

---

### Phase 15 Model Improvement & Evaluation Deliverables

| Component | Module | Description | Research Baseline / Standard |
|-----------|--------|-------------|------------------------------|
| **Model Evaluator** | `backend/app/ai/evaluation/evaluator.py` | Full diagnostic evaluation across all engines (Scheduling 88.42%, Sentiment 89.40%, Auto-Reply 88.50%, Growth 89.2% $R^2$, Hashtag 93.10%) | CLAUDE.md Section 51 Baselines |
| **Feature Importance Diagnostics** | `backend/app/ai/evaluation/evaluator.py` | Ranked feature importance analysis for Random Forest & heuristic models | Model explainability |
| **Class Imbalance Analyzer** | `backend/app/ai/evaluation/evaluator.py` | Detects minority intent categories (spam, neutral) and calculates optimal class balance weights | Robust classification |
| **Model Drift Detection** | `backend/app/ai/evaluation/evaluator.py` | Detects metric decay against baseline thresholds with automated retraining recommendations | Continuous calibration |
| **Model Registry & Staging** | `backend/app/ai/registry/model_registry.py` | Catalog tracking stages (`development`, `staging`, `production`, `deprecated`), versions, hyperparameters, and promotion | CLAUDE.md Section 48 Registry |
| **Model Evaluation REST API** | `backend/app/api/v1/models.py` | Endpoints mounted at `/api/v1/models/`: `/registry`, `/evaluate-all`, `/{name}/evaluation`, `/{name}/feature-importance`, `/{name}/drift`, `/{name}/promote` | FastAPI v1 endpoints |

---

### Phase 14 Multi-Platform Expansion Deliverables

| Platform | Adapter Package | Capabilities | Research Baseline / API Standard |
|----------|-----------------|--------------|-----------------------------------|
| **X (Twitter)** | `backend/app/core/platform_adapters/x/` | `POST_TEXT`, `POST_IMAGE`, `POST_VIDEO`, `DELETE_POST`, `GET_POST`, `GET_INSIGHTS`, `REPLY_COMMENT`, `GET_PROFILE`, `MANAGE_WEBHOOKS` | **Twitter API v2** (OAuth 2.0 PKCE, public/organic metrics, CRC Account Activity webhooks) |
| **LinkedIn** | `backend/app/core/platform_adapters/linkedin/` | `POST_TEXT`, `POST_IMAGE`, `POST_VIDEO`, `POST_CAROUSEL`, `DELETE_POST`, `GET_POST`, `GET_INSIGHTS`, `REPLY_COMMENT`, `GET_PROFILE`, `UPDATE_PROFILE` | **LinkedIn REST / UGC API** (3-legged OAuth 2.0, Organization URN ACLs, share statistics) |
| **YouTube** | `backend/app/core/platform_adapters/youtube/` | `POST_VIDEO`, `DELETE_POST`, `GET_POST`, `GET_ANALYTICS`, `GET_INSIGHTS`, `REPLY_COMMENT`, `DELETE_COMMENT`, `GET_PROFILE` | **YouTube Data API v3 & Analytics** (Google OAuth 2.0, video metadata, WebSub push feeds) |

---

### Phase 13 AI Strategy Engine Deliverables

| Component | Module | Description | Research Alignment |
|-----------|--------|-------------|-------------------|
| **Multi-Model Strategy Synthesis** | `backend/app/ai/strategy/engine.py` | Combines sentiment, scheduling, growth, caption, and hashtag signals into ranked recommendations with confidence and expected impact | Central Recommendation Engine |
| **Platform Strategy Profiles** | `backend/app/ai/strategy/engine.py` | Platform-tailored cadence, timing, media format, caption style, hashtag density, and engagement targets | Platform-aware optimization |
| **Content Strategy Plans** | `backend/app/ai/strategy/engine.py` | Produces per-platform caption variants, Top-K hashtags, peak timing, sentiment prediction, and projected engagement | Cross-platform content optimization |
| **Strategy Service & API** | `backend/app/services/strategy_service.py`, `backend/app/api/v1/strategy.py` | Persists strategy predictions and exposes dashboard, content-plan, platform-advice, and feedback endpoints | FastAPI v1 endpoints |

---

### Phase 12 Universal Analytics Dashboard Deliverables

| Component | Module | Description | Research Alignment |
|-----------|--------|-------------|-------------------|
| **Overview Dashboard** | `backend/app/services/analytics_service.py` | Multi-platform summary aggregating total followers, reach, impressions, interactions, engagement rate, and audience sentiment | Centralized Multi-Platform Dashboard |
| **Platform Benchmarking** | `backend/app/services/analytics_service.py` | Normalized comparative analytics across active networks with strongest reach/engagement identification | Normalized cross-platform metric model |
| **Content Performance & ROI** | `backend/app/services/analytics_service.py` | Top and bottom post rankings, format ROI (carousel vs video vs image), and top-performing hashtag analysis | Actionable content intelligence |
| **Temporal Engagement Heatmap** | `backend/app/services/analytics_service.py` | 7x24 hour-by-day engagement matrix with weekday vs weekend performance lift calculations | Research baseline timing analysis |
| **Sentiment Health Summary** | `backend/app/services/analytics_service.py` | Positive/negative distribution ratios and audience mood health status (`excellent`, `healthy`, `concerning`, `critical`) | Dual-Phase Sentiment tracking |
| **Growth Drift Tracking** | `backend/app/services/analytics_service.py` | Historical actual vs predicted follower comparison evaluating MAPE and model calibration status | ML performance monitoring |
| **Analytics REST API** | `backend/app/api/v1/analytics.py` | Modular endpoints mounted at `/api/v1/analytics/`: `/dashboard`, `/comparison`, `/content`, `/temporal`, `/sentiment-trends`, `/growth-accuracy` | FastAPI v1 endpoints |

---

## 🧪 Test Results: 184/184 Passing (100%)

```
backend/tests/test_production_hardening.py ..............                [  7%]
backend/tests/test_model_improvement.py ..................               [ 17%]
backend/tests/test_x_adapter.py ..........                               [ 22%]
backend/tests/test_linkedin_adapter.py ..........                        [ 28%]
backend/tests/test_youtube_adapter.py .........                          [ 33%]
backend/tests/test_ai_strategy_engine.py ...........                     [ 39%]
backend/tests/test_analytics_dashboard.py .........                      [ 44%]
backend/tests/test_growth_engine.py ......                               [ 47%]
backend/tests/test_auto_reply.py ..........                              [ 52%]
backend/tests/test_post_intelligence.py ......                           [ 56%]
backend/tests/test_scheduling_engine.py .......                          [ 60%]
backend/tests/test_ai_content_engine.py ............                     [ 66%]
backend/tests/test_api_v1.py .....                                       [ 69%]
backend/tests/test_content_management.py ....                            [ 71%]
backend/tests/test_e2e_instagram.py .                                    [ 72%]
backend/tests/test_facebook_adapter.py ..........                        [ 77%]
backend/tests/test_foundation.py ...........                             [ 83%]
backend/tests/test_instagram_adapter.py .........................        [ 97%]
backend/tests/test_normalization.py ..                                   [ 98%]
backend/tests/test_services.py ....                                      [100%]

======================= 184 passed in 66.03s =======================
```

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/Ankit04raj/AISMM.git
cd AISMM

# Setup backend environment
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run full test suite (123 tests)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 📊 Analytics Dashboard Usage

```python
from uuid import UUID
from backend.app.services.analytics_service import AnalyticsService
from backend.app.db.session import get_db_context

async with get_db_context() as session:
    service = AnalyticsService(session)
    user_id = UUID("...")

    # 1. Fetch dashboard overview
    overview = await service.get_dashboard_overview(user_id, days=30)
    print(f"Total Followers: {overview.total_followers} across {overview.total_connected_platforms} platforms")
    print(f"Overall Engagement Rate: {overview.overall_engagement_rate}%")

    # 2. Compare platform performance
    comparison = await service.get_platform_comparison(user_id, days=30)
    print(f"Strongest Platform by Reach: {comparison.strongest_platform_by_reach.upper()}")

    # 3. Content format ROI
    content = await service.get_content_performance(user_id, days=30)
    print(f"Top performing format: {content.by_content_type[0].content_type} (Avg Rate: {content.by_content_type[0].avg_engagement_rate}%)")
```

---

## 📁 Project Structure

```
AISMM/
├── CLAUDE.md                    # Master development prompt (single source of truth)
├── SESSION_HISTORY.md           # Session continuity log
├── REQUIREMENT_MATRIX.md        # Research → implementation mapping
├── README.md                    # Documentation and quick start
├── backend/
│   ├── alembic.ini              # Alembic migration configuration
│   ├── alembic/                 # Database migration scripts
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── ai/                  # AI Engines
│   │   │   ├── content_engine.py# Master AI Content Engine
│   │   │   ├── sentiment/       # Dual-Phase Sentiment Engine (VADER)
│   │   │   ├── caption/         # Caption Quality & Adaptation Engine
│   │   │   ├── hashtag/         # Top-K Hashtag Recommendation Engine
│   │   │   ├── scheduling/      # Intelligent Scheduling Engine (RF + GB)
│   │   │   ├── reply/           # Auto-Reply Engine (TF-IDF + Logistic Regression)
│   │   │   └── growth/          # Predictive Growth Engine (Random Forest Regressors)
│   │   ├── api/                 # Modular API v1 routers
│   │   │   └── v1/
│   │   │       ├── accounts.py
│   │   │       ├── ai.py        # AI Content Engine Endpoints
│   │   │       ├── analytics.py # Universal Analytics Endpoints
│   │   │       ├── auth.py
│   │   │       ├── comments.py
│   │   │       ├── content.py   # Multi-Platform Composer & Previews
│   │   │       ├── growth.py    # Predictive Growth Endpoints
│   │   │       ├── intelligence.py # Post Intelligence & Temporal Sentiment
│   │   │       ├── metrics.py
│   │   │       ├── platforms.py
│   │   │       ├── posts.py
│   │   │       ├── reply.py     # Auto-Reply Endpoints
│   │   │       ├── router.py
│   │   │       ├── scheduling.py# Intelligent Scheduling Endpoints
│   │   │       └── webhooks.py
│   │   ├── config/              # Application settings (Pydantic Settings)
│   │   ├── core/
│   │   │   ├── audit.py         # Structured audit logging
│   │   │   ├── errors/          # AISMM error hierarchy
│   │   │   ├── normalization/   # Universal content & metric normalizers
│   │   │   ├── platform_adapters/
│   │   │   │   ├── base.py      # Abstract BasePlatformAdapter contract
│   │   │   │   ├── registry.py  # Central PlatformRegistry
│   │   │   │   ├── capabilities.py
│   │   │   │   ├── instagram/   # Instagram Graph API Adapter
│   │   │   │   ├── facebook/    # Facebook Graph API Adapter
│   │   │   │   ├── x/           # X (Twitter) API v2 Adapter
│   │   │   │   ├── linkedin/    # LinkedIn REST & UGC Adapter
│   │   │   │   └── youtube/     # YouTube Data API v3 Adapter
│   │   │   ├── rate_limit.py    # Sliding window rate limiter
│   │   │   ├── resilience.py    # Circuit breaker & retry backoff
│   │   │   ├── schemas/         # Pydantic API schemas
│   │   │   ├── security.py      # JWT & bcrypt security utilities
│   │   │   └── vault.py         # AES-256 Secret encryption vault
│   │   ├── db/                  # Database session & models
│   │   ├── logging/             # Structured JSON logger
│   │   ├── services/            # Business logic service layer
│   │   │   ├── account_service.py
│   │   │   ├── analytics_service.py # Universal Analytics Service
│   │   │   ├── growth_service.py
│   │   │   ├── intelligence_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── model_service.py     # Model Evaluation & Registry Service
│   │   │   ├── post_service.py
│   │   │   ├── preview_service.py
│   │   │   ├── reply_service.py
│   │   │   ├── scheduling_service.py
│   │   │   ├── strategy_service.py
│   │   │   └── user_service.py
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 184 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 17 — Final Verification

1. **End-to-End System Lifecycle Verification** — Testing complete journey: Account Connection -> Content Creation -> AI Optimization -> Scheduling -> Publishing -> Post Intelligence -> Auto-Reply -> Analytics -> Strategy Synthesis across all 5 platforms
2. **Production Deployment Readiness** — Verification of all 184 test suites, OpenAPI specification conformance, and zero-defect sign-off

---

## 📜 Development Rules

This project follows the **AISMM Master Development Prompt** (see `CLAUDE.md`):
- **Platform-agnostic core** — Never hardcode platform logic in AI/business layers
- **Capability-driven** — Features render based on `adapter.supports(Capability)`
- **Normalization first** — All platform data → universal format → AI engines
- **Single source of truth** — `CLAUDE.md` and `SESSION_HISTORY.md` track project state
- **GitHub every session** — Commit + push + verify required

---

## 📝 License

Proprietary — AISMM Research Implementation
