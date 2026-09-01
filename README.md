# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-12%20Universal%20Analytics%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-112%2F112%20passing%20(100%25)-brightgreen)
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
| **12** | **Universal Analytics Dashboard** | ✅ **100% Verified** | **112/112 Tests Passing** (Cross-Platform Aggregations, Benchmarking, Temporal Heatmaps, Growth Drift) |
| **13** | **AI Strategy Engine** | 🔄 **Next** | Unified cross-model strategic recommendation synthesis |

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

## 🧪 Test Results: 112/112 Passing (100%)

```
backend/tests/test_analytics_dashboard.py .........                      [  8%]
backend/tests/test_growth_engine.py ......                               [ 13%]
backend/tests/test_auto_reply.py ..........                              [ 22%]
backend/tests/test_post_intelligence.py ......                           [ 27%]
backend/tests/test_scheduling_engine.py .......                          [ 33%]
backend/tests/test_ai_content_engine.py ............                     [ 44%]
backend/tests/test_api_v1.py .....                                       [ 48%]
backend/tests/test_content_management.py ....                            [ 52%]
backend/tests/test_e2e_instagram.py .                                    [ 53%]
backend/tests/test_facebook_adapter.py ..........                        [ 62%]
backend/tests/test_foundation.py ...........                             [ 71%]
backend/tests/test_instagram_adapter.py .........................        [ 94%]
backend/tests/test_normalization.py ..                                   [ 96%]
backend/tests/test_services.py ....                                      [100%]

======================= 112 passed in 13.18s =======================
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

# Run full test suite (112 tests)
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
│   │   │   ├── errors/          # AISMM error hierarchy
│   │   │   ├── normalization/   # Universal content & metric normalizers
│   │   │   ├── platform_adapters/
│   │   │   │   ├── base.py      # Abstract BasePlatformAdapter contract
│   │   │   │   ├── registry.py  # Central PlatformRegistry
│   │   │   │   ├── capabilities.py
│   │   │   │   ├── instagram/   # Instagram Graph API Adapter
│   │   │   │   └── facebook/    # Facebook Graph API Adapter
│   │   │   ├── schemas/         # Pydantic API schemas
│   │   │   └── security.py      # JWT & bcrypt security utilities
│   │   ├── db/                  # Database session & models
│   │   ├── logging/             # Structured JSON logger
│   │   ├── services/            # Business logic service layer
│   │   │   ├── account_service.py
│   │   │   ├── analytics_service.py # Universal Analytics Service
│   │   │   ├── growth_service.py
│   │   │   ├── intelligence_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── post_service.py
│   │   │   ├── preview_service.py
│   │   │   ├── reply_service.py
│   │   │   ├── scheduling_service.py
│   │   │   └── user_service.py
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 112 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 13 — AI Strategy Engine

1. **Multi-Model Synthesis** — Consuming sentiment, scheduling, growth, caption, hashtag, and comment intelligence
2. **Actionable Strategic Recommendations** — What to post, where to post, when to post, and expected ROI
3. **Automated Continuous Learning Loop** — Closing the feedback loop between predictions, actual outcomes, and recommendation weights

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
