# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-8%20Intelligent%20Scheduling%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-81%2F81%20passing%20(100%25)-brightgreen)
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
| **1** | **Requirement Matrix** | ✅ Verified | All 17 phases mapped to research requirements |
| **2** | **Architecture Design** | ✅ Verified | 3 specification documents, 29 ADRs |
| **3** | **Core Foundation** | ✅ Verified | Normalization, Base Adapter, Registry, Config, Security, Logging, Errors, DB Models, Alembic |
| **4** | **First Platform (Instagram)** | ✅ Verified | Full Instagram Graph API E2E, API v1 modular routers |
| **5** | **Second Platform (Validation)** | ✅ Verified | Facebook Page Adapter, zero core rewrites |
| **6** | **Content Management** | ✅ Verified | Multi-platform composer, platform customization, preview engine |
| **7** | **AI Content Engine** | ✅ Verified | Dual-Phase Sentiment, Caption Quality Analyzer, Top-K Hashtags |
| **8** | **Intelligent Scheduling Engine** | ✅ **100% Verified** | **81/81 Tests Passing** (ML Temporal Ensemble, Auto-Scheduler, Queue Dispatch) |
| **9** | **Post-Posting Intelligence** | 🔄 **Next** | Comment synchronization, temporal sentiment tracking, engagement updates |

---

### Phase 8 Intelligent Scheduling Deliverables

| Component | Module | Description | Research Baseline |
|-----------|--------|-------------|-------------------|
| **Temporal & Contextual Features** | `backend/app/ai/scheduling/features.py` | 16-feature vector: cyclical sin/cos hour and day-of-week encoding, caption length, hashtag count, media types | Feature Store representation |
| **Machine Learning Ensemble** | `backend/app/ai/scheduling/engine.py` | Random Forest + GradientBoosting with soft/hard voting for engagement probability scoring | 88.08% prediction baseline |
| **Platform-Aware Peak Windows** | `backend/app/ai/scheduling/engine.py` | Instagram (evening 7-9 PM), Facebook (8 PM), LinkedIn (morning 9-11 AM), Twitter (12 PM & 6 PM) | Platform-specific learning |
| **Scheduling Service & DB** | `backend/app/services/scheduling_service.py` | Constraint-aware time recommendations, auto-scheduling with DB persistence, due queue background dispatch | Complete workflow |
| **Scheduling REST API** | `backend/app/api/v1/scheduling.py` | `/recommend-times`, `/auto-schedule`, `/trigger-due` | FastAPI v1 endpoints |

---

## 🧪 Test Results: 81/81 Passing (100%)

```
backend/tests/test_scheduling_engine.py .......                          [ 10%]
backend/tests/test_ai_content_engine.py ............                     [ 25%]
backend/tests/test_api_v1.py .....                                       [ 31%]
backend/tests/test_content_management.py ....                            [ 36%]
backend/tests/test_e2e_instagram.py .                                    [ 37%]
backend/tests/test_facebook_adapter.py ..........                        [ 49%]
backend/tests/test_foundation.py ...........                             [ 63%]
backend/tests/test_instagram_adapter.py .........................        [ 94%]
backend/tests/test_normalization.py ..                                   [ 96%]
backend/tests/test_services.py ....                                      [100%]

======================= 81 passed in 10.88s =======================
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

# Run full test suite (81 tests)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 📅 Intelligent Scheduling Usage

```python
from backend.app.ai.scheduling import SchedulingEngine, TimeConstraints

engine = SchedulingEngine()

# Predict optimal posting times with user constraints (e.g. tomorrow evening)
constraints = TimeConstraints(
    start_hour=18,  # 6 PM
    end_hour=21,    # 9 PM
    allowed_days=[2, 3, 4]  # Wed, Thu, Fri
)

recommendation = engine.recommend_best_times(
    platform="instagram",
    text="Product drop tomorrow evening! 🔥 Link in bio #launch #tech",
    constraints=constraints,
    top_k=3
)

print(f"Optimal Posting Time: {recommendation.optimal_time}")
for slot in recommendation.recommendations:
    print(f"[{slot.day_name} {slot.hour_label}] Score: {slot.predicted_engagement_score}% — {slot.reason}")
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
│   │   │   └── scheduling/      # Intelligent Scheduling Engine (RF + GB)
│   │   ├── api/                 # Modular API v1 routers
│   │   │   └── v1/
│   │   │       ├── accounts.py
│   │   │       ├── ai.py        # AI Content Engine Endpoints
│   │   │       ├── auth.py
│   │   │       ├── comments.py
│   │   │       ├── content.py   # Multi-Platform Composer & Previews
│   │   │       ├── metrics.py
│   │   │       ├── platforms.py
│   │   │       ├── posts.py
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
│   │   │   ├── metrics_service.py
│   │   │   ├── post_service.py
│   │   │   ├── preview_service.py
│   │   │   ├── scheduling_service.py
│   │   │   └── user_service.py
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 81 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 9 — Post-Posting Intelligence

1. **Comment Synchronization Worker** — Scheduled background polling & webhook synchronization
2. **Post-Posting Audience Sentiment Aggregation** — Temporal tracking of audience sentiment evolution over time
3. **Engagement Score Updates** — Auto-updating post metrics and alerts for viral or high-negative engagement spikes

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
