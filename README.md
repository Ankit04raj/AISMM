# AISMM — Universal Multi-Platform AI Social Media Management

![Phase](https://img.shields.io/badge/phase-5%20Second%20Platform%20Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-58%2F58%20passing%20(100%25)-brightgreen)
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
| **5** | **Second Platform (Validation)** | ✅ **100% Verified** | **58/58 Tests Passing** (Facebook Adapter, Zero Core Rewrites) |
| **6** | **Content Management** | 🔄 **Next** | Multi-platform post composer, customization, and previews |

---

### Architectural Validation (Phase 5)

Phase 5 confirmed that adding a second platform (**Facebook Page**) required:
- **Zero changes** to core services (`PostService`, `AccountService`, `MetricsService`, `UserService`).
- **Zero changes** to database models (`User`, `SocialAccount`, `Post`, `PostPublication`, `Comment`, `Metric`).
- **Zero changes** to API routing architecture (`/api/v1/posts`, `/api/v1/accounts`, `/api/v1/platforms`).
- All platform-specific details remain strictly isolated within `backend/app/core/platform_adapters/facebook/`.

---

## 🧪 Test Results: 58/58 Passing (100%)

```
backend/tests/test_api_v1.py .....                                       [  8%]
backend/tests/test_e2e_instagram.py .                                    [ 10%]
backend/tests/test_facebook_adapter.py ..........                        [ 27%]
backend/tests/test_foundation.py ...........                             [ 46%]
backend/tests/test_instagram_adapter.py .........................        [ 89%]
backend/tests/test_normalization.py ..                                   [ 93%]
backend/tests/test_services.py ....                                      [100%]

======================= 58 passed in 1.36s =======================
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

# Run full test suite (58 tests)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

---

## 🔑 Multi-Platform Adapter Usage

```python
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType

# 1. Instagram
ig_adapter = PlatformRegistry.get_adapter("instagram")
await ig_adapter.authenticate({"access_token": "...", "ig_user_id": "..."})

# 2. Facebook
fb_adapter = PlatformRegistry.get_adapter("facebook")
await fb_adapter.authenticate({"access_token": "...", "page_id": "..."})

# Universal content created ONCE
content = UniversalContent(
    content_type=ContentType.POST,
    text="Cross-platform announcement! #aismm #ai",
    media=[UniversalMedia(type=MediaType.IMAGE, url="https://example.com/announcement.jpg")]
)

# Publish to both platforms independently
ig_result = await ig_adapter.publish_post(content)
fb_result = await fb_adapter.publish_post(content)
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
│   │   │   │   ├── instagram/   # Instagram Graph API Adapter
│   │   │   │   └── facebook/    # Facebook Graph API Adapter
│   │   │   ├── schemas/         # Pydantic API schemas
│   │   │   └── security.py      # JWT & bcrypt security utilities
│   │   ├── db/                  # Database session & models
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── logging/             # Structured JSON logger
│   │   ├── services/            # Business logic service layer
│   │   └── main.py              # FastAPI application entry point
│   └── tests/                   # 58 unit, integration & E2E tests
├── docs/
│   └── architecture/            # Architecture specifications (29 ADRs)
└── frontend/                    # React dashboard (Phase 4+)
```

---

## 🎯 Next Phase: Phase 6 — Content Management

1. **Cross-Platform Post Composer** — Multi-platform content adaptation, customization per platform
2. **Media Processing Pipeline** — Image cropping, video validation, and thumbnail extraction
3. **Platform-Specific Preview Engine** — Native preview rendering for Instagram, Facebook, and X
4. **Post Revision & Publishing History** — Tracking versioned publication status across platforms

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
