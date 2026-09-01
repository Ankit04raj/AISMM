# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-7%20AI%20Content%20Engine%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-74%2F74%20passing%20(100%25)-brightgreen)
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
| **7** | **AI Content Engine** | ✅ **100% Verified** | **74/74 Tests Passing** (Dual-Phase Sentiment, Caption Quality, Hashtag Top-K) |
| **8** | **Intelligent Scheduling Engine** | 🔄 **Next** | ML posting time prediction (RF + XGBoost + Hard Voting) |

---

### Phase 7 AI Content Deliverables

| Component | Module | Description | Research Baseline |
|-----------|--------|-------------|-------------------|
| **Dual-Phase Sentiment Engine** | `backend/app/ai/sentiment/` | Pre-posting content scoring + Post-posting audience comment aggregation | VADER + refinement (89.00% accuracy) |
| **Caption Quality Engine** | `backend/app/ai/caption/` | 0-100 quality scoring, readability, CTA detection, platform-tailored adaptation | Multi-feature quality index |
| **Hashtag Recommendation** | `backend/app/ai/hashtag/` | Category keyword matching, frequency scoring, Top-K generation | Top-K=5 (92.70% baseline) |
| **Master AI Content Engine** | `backend/app/ai/content_engine.py` | Unified optimization orchestrator across all platforms | Platform-agnostic input |
| **AI REST API** | `backend/app/api/v1/ai.py` | Dedicated `/api/v1/ai/` endpoints for sentiment, caption, hashtag, and all-in-one optimization | FastAPI endpoints |

---

## 🧪 Test Results: 74/74 Passing (100%)

```
backend/tests/test_ai_content_engine.py ............                     [ 16%]
backend/tests/test_api_v1.py .....                                       [ 22%]
backend/tests/test_content_management.py ....                            [ 28%]
backend/tests/test_e2e_instagram.py .                                    [ 29%]
backend/tests/test_facebook_adapter.py ..........                        [ 43%]
backend/tests/test_foundation.py ...........                             [ 58%]
backend/tests/test_instagram_adapter.py .........................        [ 91%]
backend/tests/test_normalization.py ..                                   [ 94%]
backend/tests/test_services.py ....                                      [100%]

======================= 74 passed in 1.94s =======================
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

# Run full test suite (74 tests)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 🤖 AI Content Engine Usage

```python
from backend.app.ai.content_engine import AIContentEngine

ai = AIContentEngine()

# Optimize content across multiple platforms simultaneously
result = ai.optimize(
    text="Supercharge your startup growth with our new AI tools! 🚀 Check out the link in bio. What is your biggest challenge?",
    platforms=["instagram", "facebook", "twitter", "linkedin"],
    top_k_hashtags=5
)

# 1. Dual-phase sentiment score
print(f"Sentiment: {result.sentiment.label} (Score: {result.sentiment.score})")

# 2. Caption quality score & actionable suggestions
print(f"Caption Quality Score: {result.caption_analysis.score}/100 ({result.caption_analysis.grade})")
print(f"Suggestions: {result.caption_analysis.suggestions}")

# 3. Top-K recommended hashtags
print(f"Recommended Hashtags: {result.hashtags.top_k}")

# 4. Platform-adapted variants
for platform, variant in result.platform_variants.items():
    print(f"[{platform.upper()}] {variant.text} {variant.recommended_hashtags}")
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
│   │   │   └── hashtag/         # Top-K Hashtag Recommendation Engine
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
│   │   │   ├── schemas/         # Pydantic API schemas (post, account, auth, ai)
│   │   │   └── security.py      # JWT & bcrypt security utilities
│   │   ├── db/                  # Database session & models
│   │   ├── logging/             # Structured JSON logger
│   │   ├── services/            # Business logic service layer
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 74 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 8 — Intelligent Scheduling Engine

1. **Temporal & Contextual Feature Engineering** — Day-of-week, hour-of-day, caption length, hashtag count, historical engagement
2. **Machine Learning Model Training Pipeline** — Random Forest + XGBoost with Hard Voting baseline (88.08% accuracy)
3. **Best Posting Time Recommendation Engine** — Multi-platform optimal time prediction with user constraints
4. **Automated Schedule Trigger & Notification Dispatch**

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
