# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-9%20Post%20Intelligence%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-87%2F87%20passing%20(100%25)-brightgreen)
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
| **9** | **Post-Posting Intelligence** | ✅ **100% Verified** | **87/87 Tests Passing** (Comment Sync, Temporal Sentiment Trajectory, Spike & Inflow Alerts) |
| **10** | **Auto-Reply Engine** | 🔄 **Next** | TF-IDF + Logistic Regression comment classification & approval workflow |

---

### Phase 9 Post-Posting Intelligence Deliverables

| Component | Module | Description | Research Alignment |
|-----------|--------|-------------|-------------------|
| **Multi-Platform Comment Sync** | `backend/app/services/intelligence_service.py` | Fetches live comments from all connected platforms, runs real-time sentiment scoring, and persists to DB | Unified feedback loop |
| **Temporal Sentiment Trajectory** | `backend/app/services/intelligence_service.py` | Bins audience reaction into temporal windows (`0-1h`, `1-6h`, `6-24h`, `24-72h`, `>72h`) and evaluates trajectory trends (`improving`, `declining`, `stable`) | Dual-Phase Sentiment temporal extension |
| **Spike & Viral Alerts Engine** | `backend/app/services/intelligence_service.py` | Monitors for negative sentiment surges (>30%), viral comment spikes, and unanswered customer inquiries | Real-time notifications |
| **Intelligence REST API** | `backend/app/api/v1/intelligence.py` | `/api/v1/intelligence/posts/{id}/sync-comments`, `/sentiment-trajectory`, `/alerts`, `/report` | FastAPI v1 endpoints |

---

## 🧪 Test Results: 87/87 Passing (100%)

```
backend/tests/test_post_intelligence.py ......                           [  7%]
backend/tests/test_scheduling_engine.py .......                          [ 15%]
backend/tests/test_ai_content_engine.py ............                     [ 29%]
backend/tests/test_api_v1.py .....                                       [ 34%]
backend/tests/test_content_management.py ....                            [ 39%]
backend/tests/test_e2e_instagram.py .                                    [ 40%]
backend/tests/test_facebook_adapter.py ..........                        [ 52%]
backend/tests/test_foundation.py ...........                             [ 64%]
backend/tests/test_instagram_adapter.py .........................        [ 93%]
backend/tests/test_normalization.py ..                                   [ 95%]
backend/tests/test_services.py ....                                      [100%]

======================= 87 passed in 10.59s =======================
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

# Run full test suite (87 tests)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 📊 Post Intelligence Usage

```python
from uuid import UUID
from backend.app.services.intelligence_service import IntelligenceService
from backend.app.db.session import get_db_context

async with get_db_context() as session:
    service = IntelligenceService(session)
    post_id = UUID("...")
    user_id = UUID("...")

    # 1. Synchronize live comments from all connected platforms and run sentiment
    sync_result = await service.sync_comments_for_post(post_id, user_id)
    print(f"Synced {sync_result.total_synced} comments across platforms.")

    # 2. Track temporal sentiment evolution across the post's lifetime
    trajectory = await service.get_temporal_sentiment_trajectory(post_id, user_id)
    print(f"Overall Sentiment: {trajectory.overall_sentiment_label} (Trend: {trajectory.trajectory_trend})")
    for pt in trajectory.time_series:
        print(f"[{pt.time_window}] {pt.comment_count} comments — Score: {pt.avg_sentiment_score}")

    # 3. Check for viral spikes or negative sentiment waves
    alerts = await service.get_post_alerts(post_id, user_id)
    for alert in alerts.active_alerts:
        print(f"ALERT [{alert.severity.upper()}]: {alert.message}")
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
│   │   │       ├── intelligence.py # Post Intelligence & Temporal Sentiment
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
│   │   │   ├── intelligence_service.py # Post Intelligence Service
│   │   │   ├── metrics_service.py
│   │   │   ├── post_service.py
│   │   │   ├── preview_service.py
│   │   │   ├── scheduling_service.py
│   │   │   └── user_service.py
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 87 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 10 — Auto-Reply Engine

1. **Comment Intent Classification** — TF-IDF + Multinomial Logistic Regression baseline (88.00% accuracy)
2. **Reply Engine Abstraction** — Template matching, TF-IDF classifier, and LLM hybrid generation
3. **Human-in-the-Loop Approval Workflow** — Confidence thresholds (`>=0.90` automatic, `0.70-0.90` approval required, `<0.70` manual)
4. **Automated Reply Execution** via platform adapters

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
