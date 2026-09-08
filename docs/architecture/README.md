# AISMM Architecture Documentation

**Phase 2 — Architecture Design**  
**Version:** 1.0  
**Date:** 2026-08-25  
**Status:** DESIGN — AWAITING APPROVAL

---

## Document Index

| Document | Description | Key Contents |
|----------|-------------|--------------|
| **[01_core_architecture.md](01_core_architecture.md)** | High-level system architecture | Layered architecture, tech stack, database ERD, event architecture, API design, security, config, frontend, deployment, 10 ADRs |
| **[02_platform_adapter.md](02_platform_adapter.md)** | Platform adapter architecture | BasePlatformAdapter contract, capability system, directory structure, content normalization (mapper), error translation, rate limiting, platform registry, mock adapter, onboarding checklist, 8 ADRs |
| **[03_ai_engine.md](03_ai_engine.md)** | AI engine architecture | Normalized inputs, feature store, 7 engines (Sentiment, Scheduling, Growth, Reply, Caption, Hashtag, Recommendation), model registry, training pipeline, performance monitoring, 11 ADRs, research baselines |

---

## Architecture Principles Summary

### 1. Platform-Agnostic Core
> **AISMM Core contains intelligence. Platform adapters contain platform-specific complexity.**

The core system knows about: Posts, Media, Captions, Hashtags, Comments, Engagement, Audience, Schedules, Sentiment, Predictions, Recommendations — **NOT** Instagram/Facebook/X-specific details.

### 2. Capability-Based System
Every platform declares what it supports. The frontend renders dynamically based on capabilities.

```python
# Example: Instagram capabilities
capabilities = [
    "publishing", "scheduling", "image_post", "video_post",
    "carousel_post", "stories", "short_video", "comments",
    "replies", "analytics", "audience_metrics", "webhooks",
    "hashtags", "mentions"
]
```

### 3. Universal Data Models
- **Raw Platform Data** — stored for debugging/auditing
- **Normalized AISMM Data** — used by AI/analytics
- **Post → PostPublication (1:N)** — one content, multiple platform publications

### 4. AI Independence
AI engines receive `NormalizedPost`, `NormalizedEngagement`, `NormalizedComment`, `NormalizedAudience` — **never raw API objects**.

### 5. Event-Driven Architecture
Normalized internal events: `PostCreated`, `PostPublished`, `CommentReceived`, `SentimentCalculated`, `PredictionGenerated`, `ScheduleTriggered`, `TokenExpiring`, etc.

### 6. Configuration-Driven
All platform assumptions in config files: `platform_config.yaml`, `model_config.yaml`, `feature_config.yaml`, `scheduler_config.yaml`, `sentiment_config.yaml`, `notification_config.yaml`

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python 3.11+) |
| **Frontend** | React 18 + TypeScript |
| **Database** | PostgreSQL 16 + SQLAlchemy 2.0 |
| **Cache/Queue** | Redis 7 |
| **ML** | scikit-learn, XGBoost, MLflow |
| **Auth** | JWT + OAuth2 |
| **Config** | Pydantic Settings + YAML |
| **Testing** | pytest, pytest-asyncio |
| **Monitoring** | Prometheus + Grafana |

---

## Directory Structure

```
aismm/
├── backend/
│   ├── app/
│   │   ├── config/           # Configuration files
│   │   ├── core/             # Domain layer (models, schemas, events, normalization, errors)
│   │   ├── services/         # Application services
│   │   ├── ai/               # AI Engine layer
│   │   │   ├── sentiment/
│   │   │   ├── scheduling/
│   │   │   ├── growth/
│   │   │   ├── reply/
│   │   │   ├── caption/
│   │   │   ├── hashtag/
│   │   │   ├── recommendation/
│   │   │   └── registry/
│   │   ├── platforms/        # Platform adapters
│   │   │   ├── base/
│   │   │   ├── instagram/
│   │   │   ├── facebook/
│   │   │   ├── x/
│   │   │   ├── linkedin/
│   │   │   ├── youtube/
│   │   │   └── mock/
│   │   ├── api/              # API routes (v1)
│   │   ├── db/               # Database
│   │   ├── security/
│   │   ├── logging/
│   │   └── middleware/
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable platform-agnostic components
│   │   ├── pages/            # Dashboard pages
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   └── types/
├── ml/
│   ├── pipelines/
│   ├── datasets/
│   ├── models/
│   └── registry/
└── docs/
    └── architecture/
```

---

## Phase 2 Deliverables Checklist

| Architecture Area | Document | Status |
|------------------|----------|--------|
| Core Architecture | [01_core_architecture.md](01_core_architecture.md) | ✅ Complete |
| Platform Adapter | [02_platform_adapter.md](02_platform_adapter.md) | ✅ Complete |
| AI Engine | [03_ai_engine.md](03_ai_engine.md) | ✅ Complete |
| Database Architecture | Included in 01_core_architecture.md | ✅ Complete |
| Event Architecture | Included in 01_core_architecture.md | ✅ Complete |
| API Architecture | Included in 01_core_architecture.md | ✅ Complete |
| Frontend Architecture | Included in 01_core_architecture.md | ✅ Complete |
| Model Architecture | Included in 03_ai_engine.md | ✅ Complete |
| Security Architecture | Included in 01_core_architecture.md | ✅ Complete |

**Total ADRs Documented: 29**

---

## Next Steps

1. **Review** all three architecture documents
2. **Approve** for Phase 3 implementation
3. **Begin Phase 3 — Core Foundation**:
   - Configuration system
   - Database models & migrations
   - Authentication & credential management
   - Logging & error handling
   - Platform registry & base adapter
   - Capability system
   - Universal data models
   - Normalization framework

---

## Decision Records (ADRs) Summary

| ADR | Area | Decision |
|-----|------|----------|
| ADR-001 | Core | Platform-agnostic adapter architecture |
| ADR-002 | Core | Capability-based platform system |
| ADR-003 | Core | Universal data models (normalized + raw) |
| ADR-004 | Core | AI core independent from platforms |
| ADR-005 | Core | Event-driven architecture |
| ADR-006 | Core | Configuration-driven system |
| ADR-007 | Core | Model registry with versioning |
| ADR-008 | Core | Mock platform adapter for testing |
| ADR-009 | Core | Dynamic UI from capabilities |
| ADR-010 | Core | Secure credential vault |
| ADR-011 | Adapter | Single abstract base adapter |
| ADR-012 | Adapter | Capability enum + dynamic discovery |
| ADR-013 | Adapter | UniversalContent as internal format |
| ADR-014 | Adapter | Mapper per platform |
| ADR-015 | Adapter | Error translation in adapters |
| ADR-016 | Adapter | Rate limiter per adapter instance |
| ADR-017 | Adapter | Mock adapter for testing |
| ADR-018 | Adapter | Registry auto-discovers plugins |
| ADR-019 | AI | Normalized input for all AI engines |
| ADR-020 | AI | Dual-phase sentiment (VADER + k-NN) |
| ADR-021 | AI | Platform-specific scheduling models |
| ADR-022 | AI | Platform-specific growth models |
| ADR-023 | AI | ReplyEngine abstraction |
| ADR-024 | AI | Human-in-the-loop with confidence thresholds |
| ADR-025 | AI | Central RecommendationEngine |
| ADR-026 | AI | Model registry with versioning |
| ADR-027 | AI | Training pipeline with feature versioning |
| ADR-028 | AI | Performance monitoring + drift detection |
| ADR-029 | AI | Mock data support for all engines |

---

**Status:** DESIGN — AWAITING APPROVAL  
**Approval Required:** All three architecture documents must be approved before Phase 3 begins.