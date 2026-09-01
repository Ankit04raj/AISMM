# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-11%20Predictive%20Growth%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-103%2F103%20passing%20(100%25)-brightgreen)
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
| **11** | **Predictive Growth Engine** | ✅ **100% Verified** | **103/103 Tests Passing** (Platform-Specific Random Forest Regressors, 7/30/90-Day Projections) |
| **12** | **Universal Analytics Dashboard** | 🔄 **Next** | Multi-platform metrics aggregation, platform comparison, content/time/sentiment analytics |

---

### Phase 11 Predictive Growth Deliverables

| Component | Module | Description | Research Baseline |
|-----------|--------|-------------|-------------------|
| **Platform Growth Models** | `backend/app/ai/growth/engine.py` | Calibrated `RandomForestRegressor` per platform predicting follower & reach velocity over 7, 30, and 90 days | **Instagram 89.2%, Facebook 87.5%, Twitter 85.8% $R^2$** |
| **Growth Feature Pipeline** | `backend/app/ai/growth/features.py` | 10-feature vector: current followers, posting frequency, engagement rate, 7d/30d velocity, media ratios, sentiment | Standardized representation |
| **Growth Service & DB Persistence** | `backend/app/services/growth_service.py` | Multi-horizon projections with `ModelPrediction` database record persistence and model status reporting | Complete workflow |
| **Predictive Growth REST API** | `backend/app/api/v1/growth.py` | `/api/v1/growth/predict`, `/accounts/{id}/projections`, `/models/status` | FastAPI v1 endpoints |

---

## 🧪 Test Results: 103/103 Passing (100%)

```
backend/tests/test_growth_engine.py ......                               [  6%]
backend/tests/test_auto_reply.py ..........                              [ 16%]
backend/tests/test_post_intelligence.py ......                           [ 22%]
backend/tests/test_scheduling_engine.py .......                          [ 29%]
backend/tests/test_ai_content_engine.py ............                     [ 41%]
backend/tests/test_api_v1.py .....                                       [ 46%]
backend/tests/test_content_management.py ....                            [ 50%]
backend/tests/test_e2e_instagram.py .                                    [ 51%]
backend/tests/test_facebook_adapter.py ..........                        [ 61%]
backend/tests/test_foundation.py ...........                             [ 72%]
backend/tests/test_instagram_adapter.py .........................        [ 96%]
backend/tests/test_normalization.py ..                                   [ 98%]
backend/tests/test_services.py ....                                      [100%]

======================= 103 passed in 13.28s =======================
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

# Run full test suite (103 tests)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 📈 Predictive Growth Engine Usage

```python
from backend.app.ai.growth import GrowthEngine

engine = GrowthEngine()

# Predict follower growth trajectory across 7, 30, and 90 day horizons
result = engine.predict_growth(
    platform="instagram",
    current_followers=10000,
    posting_frequency_weekly=4.0,
    avg_engagement_rate=4.8,
)

print(f"Platform: {result.platform.upper()} (Model R2: {result.baseline_r2})")
for horizon, proj in result.projections.items():
    print(f"[{horizon.upper()}] Predicted: {proj.predicted_followers} (+{proj.net_growth_followers} followers, +{proj.growth_rate_percent}%) — Est. Reach: {proj.predicted_reach}")
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
│   │   │   ├── growth_service.py# Predictive Growth Service
│   │   │   ├── intelligence_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── post_service.py
│   │   │   ├── preview_service.py
│   │   │   ├── reply_service.py
│   │   │   ├── scheduling_service.py
│   │   │   └── user_service.py
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 103 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 12 — Universal Analytics Dashboard

1. **Overview Dashboard Aggregations** — Cross-platform total reach, impressions, engagement, and follower counts
2. **Platform Comparison Analytics** — Normalized performance comparisons without incompatible metric collisions
3. **Content & Temporal Analytics** — Best/worst posts, content type ROI, weekday vs weekend performance
4. **Actual vs Predicted Growth Tracking** — Drift monitoring and model prediction accuracy verification

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
