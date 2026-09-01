# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-4%20First%20Platform%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-48%2F48%20passing%20(100%25)-brightgreen)
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
| **4** | **First Platform (Instagram)** | ✅ **100% Verified** | **48/48 Tests Passing** (API v1, OAuth, E2E Lifecycle) |
| **5** | **Second Platform (Validation)** | 🔄 **Next** | Architecture validation with Facebook/X |

---

### Phase 4 Deliverables Summary

| Component | File / Location | Description |
|-----------|-----------------|-------------|
| **Modular API v1** | `backend/app/api/v1/` | RESTful endpoints: `auth`, `accounts`, `posts`, `metrics`, `comments`, `webhooks`, `platforms` |
| **OAuth Flow & Lifecycle** | `InstagramAuth` & `auth.py` | PKCE state generation, token exchange, long-lived 60-day expansion, profile resolution, token revocation |
| **Account Management** | `AccountService` & `accounts.py` | Connection storage, profile sync, token refresh, and disconnection |
| **Publishing & Scheduling** | `PostService` & `posts.py` | 2-phase container creation and publishing for images, carousels, reels, and stories |
| **Real-time Webhooks** | `InstagramWebhookHandler` & `webhooks.py` | Meta challenge verification (`hub.challenge`), HMAC-SHA256 signature validation, and event dispatch |
| **Comment Management** | `InstagramAdapter` & `comments.py` | Fetching, replying, hiding, and deleting comments on published posts |
| **Analytics & Insights** | `MetricsService` & `metrics.py` | Account insights, post insights, top posts ranking, and engagement trend reporting |
| **E2E Test Suite** | `backend/tests/test_e2e_instagram.py` | Full lifecycle verification: Connect Account → Publish → Schedule → Analytics → Webhook → Comment Reply |

---

## 🧪 Test Results: 48/48 Passing (100%)

```
backend/tests/test_api_v1.py .....                                       [ 10%]
backend/tests/test_e2e_instagram.py .                                    [ 12%]
backend/tests/test_foundation.py ...........                             [ 35%]
backend/tests/test_instagram_adapter.py .........................        [ 87%]
backend/tests/test_normalization.py ..                                   [ 91%]
backend/tests/test_services.py ....                                      [100%]

======================= 48 passed in 1.25s =======================
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

# Run full test suite (48 tests)
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

# Publish post (2-phase container upload & publish)
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
│   │   ├── api/                 # Modular API v1 routers
│   │   │   └── v1/
│   │   │       ├── accounts.py
│   │   │       ├── auth.py
│   │   │       ├── comments.py
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
│   │   │   │   └── instagram/   # Instagram Graph API Adapter
│   │   │   ├── schemas/         # Pydantic API schemas
│   │   │   └── security.py      # JWT & bcrypt security utilities
│   │   ├── db/                  # Database session & models
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── logging/             # Structured JSON logger
│   │   ├── services/            # Business logic service layer
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 48 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 5 — Second Platform (Facebook / X Validation)

The purpose of Phase 5 is **architectural validation**:
1. Implement the **Facebook / X Adapter** using the exact same `BasePlatformAdapter` contract.
2. Confirm that adding a second platform requires **zero changes** to core AISMM business logic, database models, or API routers.
3. Validate dynamic UI capability negotiation for platforms with different feature matrices.

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
