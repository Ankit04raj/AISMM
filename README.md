# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-3%20Core%20Foundation%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-42%2F42%20passing%20(100%25)-brightgreen)
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
| **0** | **Project Discovery & Audit** | ✅ Verified | Baseline established |
| **1** | **Requirement Matrix** | ✅ Verified | All 17 phases mapped |
| **2** | **Architecture Design** | ✅ Verified | 3 specification documents, 29 ADRs |
| **3** | **Core Foundation** | ✅ **100% Verified** | **42/42 Tests Passing** |
| **4** | **First Platform (Instagram)** | 🔄 **Next** | Full Instagram Graph API E2E |
| **5** | **Second Platform (Validation)** | ⏳ Planned | Architecture validation |

### Phase 3 Deliverables Summary

| Component | File / Location | Description |
|-----------|-----------------|-------------|
| **Normalization** | `backend/app/core/normalization/` | UniversalContent + MetricNormalizer with cross-platform mapping |
| **Base Adapter Contract** | `backend/app/core/platform_adapters/base.py` | Abstract contract with 25 capabilities and universal payload types |
| **Platform Registry** | `backend/app/core/platform_adapters/registry.py` | Dynamic discovery, instantiation, and verification |
| **Error Hierarchy** | `backend/app/core/errors/` | Unified `AISMMError` root + 16 specialized domain/platform error classes |
| **Database & Models** | `backend/app/db/models.py`, `backend/app/core/models/` | 11 core SQLAlchemy models covering users, accounts, posts, media, publications, metrics, schedules, ML models |
| **Migrations** | `backend/alembic/` | Alembic configuration + initial migration (`1c2e5404a0b3`) |
| **Security & Auth** | `backend/app/core/security.py` | JWT access/refresh tokens, bcrypt password hashing, secure API key generation |
| **Structured Logging** | `backend/app/logging/` | Structured JSON and standard log formatters with contextual metadata |
| **Service Layer** | `backend/app/services/` | `UserService`, `PostService`, `AccountService`, `MetricsService` |
| **FastAPI Application** | `backend/app/main.py` | Application lifespan, CORS, exception handlers, RESTful v1 endpoints |
| **Instagram Adapter** | `backend/app/core/platform_adapters/instagram/` | Full Graph API implementation (OAuth, 2-phase publish, insights, webhooks) |

---

## 🧪 Test Results: 42/42 Passing (100%)

```
backend/tests/test_foundation.py ...........                             [ 26%]
backend/tests/test_instagram_adapter.py .........................        [ 85%]
backend/tests/test_normalization.py ..                                   [ 90%]
backend/tests/test_services.py ....                                      [100%]

======================= 42 passed in 0.93s =======================
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

# Run tests
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 🔑 Platform Adapter Usage

```python
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType

# Get registered adapter
adapter = PlatformRegistry.get_adapter("instagram")

# Authenticate via OAuth code or direct token
await adapter.authenticate({"access_token": "...", "ig_user_id": "..."})

# Universal content creation
content = UniversalContent(
    content_type=ContentType.POST,
    text="Hello world from AISMM! #ai #socialmedia",
    media=[UniversalMedia(type=MediaType.IMAGE, url="https://example.com/image.jpg")]
)

# Publish post
result = await adapter.publish_post(content)

# Fetch normalized analytics
insights = await adapter.get_post_analytics(result.platform_post_id)
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
│   │   └── versions/
│   │       └── 1c2e5404a0b3_initial_schema.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── config/              # Application settings (Pydantic Settings)
│   │   ├── core/
│   │   │   ├── errors/          # AISMM error hierarchy
│   │   │   ├── normalization/   # Universal content & metric normalizers
│   │   │   ├── platform_adapters/
│   │   │   │   ├── base.py      # Abstract BasePlatformAdapter contract
│   │   │   │   ├── registry.py  # Central PlatformRegistry
│   │   │   │   ├── capabilities.py
│   │   │   │   └── instagram/   # Instagram Graph API Adapter
│   │   │   ├── schemas/         # Pydantic API schemas
│   │   │   └── security.py      # JWT & bcrypt security utilities
│   │   ├── db/                  # Database session & models
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── logging/             # Structured JSON logger
│   │   ├── services/            # Business logic service layer
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 42 unit & integration tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 4 — First Platform (Instagram E2E)

1. **OAuth Flow Integration** — Live OAuth connection & token lifecycle management
2. **API Routes Connection** — End-to-end testing of FastAPI routes with live database session
3. **Automated Publishing & Scheduling** — Cron/Celery background scheduler execution
4. **Real-time Webhook Receiver** — Live webhook event processing and persistence
5. **Frontend Foundation** — Dynamic capability-driven dashboard UI

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
