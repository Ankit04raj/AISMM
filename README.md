# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-10%20Auto%20Reply%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-97%2F97%20passing%20(100%25)-brightgreen)
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
| **10** | **Auto-Reply Engine** | ✅ **100% Verified** | **97/97 Tests Passing** (TF-IDF Intent Classifier, Human-in-the-Loop Routing, Auto-Execution) |
| **11** | **Predictive Growth Engine** | 🔄 **Next** | Platform-specific growth regression models ($R^2$, RMSE) |

---

### Phase 10 Auto-Reply Deliverables

| Component | Module | Description | Research Alignment |
|-----------|--------|-------------|-------------------|
| **Comment Intent Classifier** | `backend/app/ai/reply/engine.py` | TF-IDF (1,2-grams) + Multinomial Logistic Regression identifying pricing inquiries, support issues, compliments, general questions, and spam | **88.00% accuracy baseline** |
| **Human-in-the-Loop Policy** | `backend/app/ai/reply/engine.py` | Automatic execution (`confidence >= 0.90`), Approval Required (`0.70-0.90`), Manual Routing (`<0.70` or support issues), and Spam Hiding | Full safety guardrails |
| **Reply Service & Execution** | `backend/app/services/reply_service.py` | Real-time comment ingestion, routing policy evaluation, automated response sending, and human approval execution | Complete workflow |
| **Auto-Reply REST API** | `backend/app/api/v1/reply.py` | `/api/v1/reply/classify`, `/suggest`, `/process-comment`, `/approve` | FastAPI v1 endpoints |

---

## 🧪 Test Results: 97/97 Passing (100%)

```
backend/tests/test_auto_reply.py ..........                              [ 10%]
backend/tests/test_post_intelligence.py ......                           [ 16%]
backend/tests/test_scheduling_engine.py .......                          [ 23%]
backend/tests/test_ai_content_engine.py ............                     [ 36%]
backend/tests/test_api_v1.py .....                                       [ 41%]
backend/tests/test_content_management.py ....                            [ 45%]
backend/tests/test_e2e_instagram.py .                                    [ 46%]
backend/tests/test_facebook_adapter.py ..........                        [ 56%]
backend/tests/test_foundation.py ...........                             [ 68%]
backend/tests/test_instagram_adapter.py .........................        [ 93%]
backend/tests/test_normalization.py ..                                   [ 95%]
backend/tests/test_services.py ....                                      [100%]

======================= 97 passed in 11.12s =======================
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

# Run full test suite (97 tests)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 💬 Auto-Reply Engine Usage

```python
from backend.app.ai.reply import TFIDFReplyEngine, ReplyAction

engine = TFIDFReplyEngine()

# 1. Classify incoming comment
classification = engine.classify_comment("What are your subscription rates for pro accounts?")
print(f"Detected Intent: {classification.intent.value} (Confidence: {classification.confidence})")

# 2. Generate response with Human-in-the-Loop policy
suggestion = engine.generate_reply("Love the new update, great work team! ❤️")
print(f"Action: {suggestion.routing_action.value}")  # "automatic"
print(f"Suggested Reply: {suggestion.suggested_reply}")
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
│   │   │   └── reply/           # Auto-Reply Engine (TF-IDF + Logistic Regression)
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
│   │   │   ├── intelligence_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── post_service.py
│   │   │   ├── preview_service.py
│   │   │   ├── reply_service.py # Auto-Reply Service
│   │   │   ├── scheduling_service.py
│   │   │   └── user_service.py
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 97 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 11 — Predictive Growth Engine

1. **Platform-Specific Growth Regression Models** — Random Forest Regressor predicting follower & reach trajectory over 7, 30, and 90 days ($R^2$ baseline: Instagram 89.2%, Facebook 87.5%)
2. **Growth Feature Pipeline** — Historical follower velocity, post frequency, engagement rate, content distribution
3. **Model Evaluation & Drift Monitoring** — Tracking actual vs predicted growth with RMSE metrics
4. **Growth REST API** — Projections, historical comparisons, and growth alert triggers

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
