# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-3%20Core%20Foundation-blue)
![Tests](https://img.shields.io/badge/tests-27%2F27%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)

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

## ✅ Current Status: Phase 3 Complete

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project Audit | ✅ Done |
| 1 | Requirement Matrix | ✅ Done |
| 2 | Architecture Design | ✅ Done |
| **3** | **Core Foundation** | **✅ Complete** |
| 4 | First Platform (Instagram) | 🔄 Next |
| 5 | Second Platform (Validation) | ⏳ Pending |

### Phase 3 Deliverables

| Component | File | Description |
|-----------|------|-------------|
| **Normalization** | `backend/app/core/normalization/` | Content + Metric normalization with cross-platform mapping |
| **Base Adapter** | `backend/app/core/platform_adapters/base.py` | Abstract contract with 25 capabilities |
| **Registry** | `backend/app/core/platform_adapters/registry.py` | Dynamic adapter discovery |
| **Error System** | `backend/app/core/errors/platform_errors.py` | 12 platform-specific exception types |
| **Instagram Adapter** | `backend/app/core/platform_adapters/instagram/adapter.py` | Full Graph API integration |
| **Instagram Auth** | `backend/app/core/platform_adapters/instagram/auth.py` | OAuth 2.0 + long-lived tokens |
| **Instagram Config** | `backend/app/core/platform_adapters/instagram/config.py` | Dev/Staging/Prod presets |
| **Instagram Publisher** | `backend/app/core/platform_adapters/instagram/publisher.py` | 2-phase media publishing |
| **Instagram Insights** | `backend/app/core/platform_adapters/instagram/insights.py` | Media/account metrics |
| **Instagram Webhooks** | `backend/app/core/platform_adapters/instagram/webhook.py` | Real-time event handling |

### Test Results
```
27 passed
  25 Instagram adapter tests (unit + integration)
  2 normalization tests
```

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/Ankit04raj/AISMM.git
cd AISMM

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest -v
```

---

## 🔑 Instagram Adapter Usage

```python
from backend.app.core.platform_adapters.instagram.adapter import InstagramAdapter
from backend.app.core.platform_adapters.instagram.config import InstagramConfigPresets

# Configuration
config = InstagramConfigPresets.development()
adapter = InstagramAdapter(config.to_adapter_config())

# Authenticate (OAuth code exchange)
await adapter.authenticate({"code": "oauth_code_from_redirect"})

# Or reconnect with existing token
await adapter.authenticate({"access_token": "...", "ig_user_id": "..."})

# Publish a post
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType
content = UniversalContent(
    content_type=ContentType.POST,
    text="Hello Instagram!",
    media=[UniversalMedia(type=MediaType.IMAGE, url="https://example.com/image.jpg")]
)
result = await adapter.publish_post(content)

# Schedule a post
from datetime import datetime, timedelta
scheduled = await adapter.schedule_post(content, datetime.utcnow() + timedelta(hours=1))

# Fetch analytics
insights = await adapter.get_post_analytics(result.platform_post_id)
```

---

## 📁 Project Structure

```
AISMM/
├── CLAUDE.md                    # Master development prompt (single source of truth)
├── SESSION_HISTORY.md           # Session continuity log
├── REQUIREMENT_MATRIX.md        # Research → implementation mapping
├── README.md                    # This file
├── backend/
│   ├── requirements.txt
│   ├── pytest.ini
│   └── app/
│       ├── core/
│       │   ├── errors/          # Platform error hierarchy
│       │   ├── normalization/   # Cross-platform content/metric normalization
│       │   ├── platform_adapters/
│       │   │   ├── base.py      # BasePlatformAdapter contract
│       │   │   ├── registry.py  # Adapter registry
│       │   │   ├── capabilities.py
│       │   │   ├── errors.py
│       │   │   └── instagram/   # Instagram Graph API adapter
│       │   │       ├── adapter.py
│       │   │       ├── auth.py
│       │       │       ├── config.py
│       │   │       ├── endpoints.py
│       │   │       ├── insights.py
│       │   │       ├── media.py
│       │   │       ├── publisher.py
│       │   │       └── webhook.py
│       │   └── schemas/         # Pydantic request/response schemas
│       ├── db/                  # SQLAlchemy models (Phase 4)
│       └── services/            # Business logic (Phase 4)
├── docs/
│   └── architecture/
│       ├── 01_core_architecture.md
│       ├── 02_platform_adapter.md
│       └── 03_ai_engine.md
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🔬 Research Alignment

This implementation faithfully reproduces the AISMM research paper's six core modules while enhancing the architecture for platform extensibility:

| Research Module | Implementation Status |
|-----------------|----------------------|
| Centralized Multi-Platform Dashboard | Phase 4 |
| Intelligent Time Scheduling | Phase 4 (adapter contract ready) |
| Dual-Phase Sentiment Analysis | Phase 4 (adapter contract ready) |
| Predictive Growth Modeling | Phase 4 (adapter contract ready) |
| Auto-Reply | Phase 4 (adapter contract ready) |
| Caption & Hashtag Optimization | Phase 4 (adapter contract ready) |

---

## 🎯 Next Steps (Phase 4)

1. **Database Layer** — SQLAlchemy models for User, SocialAccount, Post, Media, Analytics, Comment
2. **Migrations** — Alembic migration scripts
3. **API Endpoints** — FastAPI routes for platform connections, content CRUD, scheduling
4. **Service Layer** — PostService, AnalyticsService, SchedulingService
5. **Frontend** — React dashboard with dynamic capability-driven UI
6. **End-to-End Tests** — Full Create → Optimize → Schedule → Publish → Analyze flow

---

## 📜 Development Rules

This project follows the **AISMM Master Development Prompt** (see `CLAUDE.md`):
- **Platform-agnostic core** — Never hardcode platform logic in AI/business layers
- **Capability-driven** — Features render based on `adapter.supports(Capability)`
- **Normalization first** — All platform data → universal format → AI engines
- **Single source of truth** — `CLAUDE.md` tracks phase, status, next action
- **GitHub every session** — Commit + push + verify required

---

## 📝 License

Proprietary — AISMM Research Implementation

---

*Last updated: 2026-09-01 | Phase 3 Core Foundation Complete*
