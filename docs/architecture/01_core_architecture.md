# AISMM Core Architecture Design
**Phase 2 — Architecture Design**  
**Version:** 1.0  
**Date:** 2026-08-25  
**Status:** DESIGN — AWAITING APPROVAL

---

## 1. System Overview

AISMM is a **platform-agnostic AI social media management ecosystem**. The core principle is:

> **AISMM Core contains intelligence. Platform adapters contain platform-specific complexity.**

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                       │
│         Platform-agnostic, capability-driven UI components    │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST/WebSocket API
┌───────────────────────────┴─────────────────────────────────┐
│                     API LAYER (FastAPI)                       │
│              Authentication, Rate Limiting, Validation        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                 APPLICATION SERVICES LAYER                    │
│   PostService, AccountService, AnalyticsService, etc.        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    DOMAIN / CORE LAYER                        │
│         Universal Data Models, Business Logic, Events        │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
┌──────────┴───────────────┐    ┌─────────────┴──────────────────┐
│      AI ENGINE LAYER     │    │      PLATFORM REGISTRY         │
│  Sentiment, Scheduling,  │    │  Adapter discovery & routing   │
│  Growth, Reply, Caption, │    └─────────────┬──────────────────┘
│  Hashtag, Recommendation │                  │
└──────────┬───────────────┘    ┌─────────────┴──────────────────┐
           │                    │   PLATFORM ADAPTERS            │
┌──────────┴───────────────┐    │  Instagram, Facebook, X,      │
│    EVENT BUS / WEBHOOKS   │    │  LinkedIn, YouTube, Mock      │
└───────────────────────────┘    └─────────────┬──────────────────┘
                                              │
                                        ┌─────┴──────┐
                                        │  EXTERNAL  │
                                        │   APIs     │
                                        └────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|----------|
| **Backend** | FastAPI (Python 3.11+) | Async, type-safe, fast, good ML ecosystem |
| **Frontend** | React 18 + TypeScript | Component-based, dynamic UI, large ecosystem |
| **Database** | PostgreSQL 16 | ACID, JSON support, mature, scalable |
| **ORM** | SQLAlchemy 2.0 | Python-native, async support, migrations via Alembic |
| **Cache/Queue** | Redis 7 | Rate limiting, caching, background jobs |
| **Task Queue** | Celery / RQ | Async scheduling, webhook processing |
| **ML** | scikit-learn, XGBoost, MLflow | Research baselines, model registry |
| **Auth** | JWT + OAuth2 | Stateless auth, platform OAuth flows |
| **Config** | Pydantic Settings + YAML | Type-safe config, environment overrides |
| **Testing** | pytest, pytest-asyncio | Unit, integration, e2e |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards |
| **Logging** | structlog | Structured logging |

---

## 3. Directory Structure

```
aismm/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py         # Pydantic settings
│   │   │   ├── platform_config.yaml
│   │   │   ├── model_config.yaml
│   │   │   ├── feature_config.yaml
│   │   │   ├── scheduler_config.yaml
│   │   │   ├── sentiment_config.yaml
│   │   │   └── notification_config.yaml
│   │   ├── core/                   # Domain layer
│   │   │   ├── __init__.py
│   │   │   ├── models/             # SQLAlchemy models
│   │   │   │   ├── user.py
│   │   │   │   ├── account.py
│   │   │   │   ├── post.py
│   │   │   │   ├── publication.py
│   │   │   │   ├── comment.py
│   │   │   │   ├── metric.py
│   │   │   │   ├── sentiment.py
│   │   │   │   ├── schedule.py
│   │   │   │   ├── model.py
│   │   │   │   └── event.py
│   │   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── events/             # Event definitions & bus
│   │   │   │   ├── event_types.py
│   │   │   │   ├── event_bus.py
│   │   │   │   └── webhook_gateway.py
│   │   │   ├── normalization/      # Universal content normalization
│   │   │   │   ├── universal_content.py
│   │   │   │   └── normalizer.py
│   │   │   └── errors/             # Error hierarchy
│   │   │       ├── platform_errors.py
│   │   │       └── base_errors.py
│   │   ├── services/               # Application services
│   │   │   ├── post_service.py
│   │   │   ├── account_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── schedule_service.py
│   │   │   ├── notification_service.py
│   │   │   └── sync_service.py
│   │   ├── ai/                     # AI Engine layer
│   │   │   ├── sentiment/
│   │   │   ├── scheduling/
│   │   │   ├── growth/
│   │   │   ├── reply/
│   │   │   ├── caption/
│   │   │   ├── hashtag/
│   │   │   ├── recommendation/
│   │   │   └── registry/
│   │   ├── platforms/              # Platform adapter layer
│   │   │   ├── base/
│   │   │   │   ├── adapter.py
│   │   │   │   ├── capabilities.py
│   │   │   │   ├── models.py
│   │   │   │   └── rate_limit.py
│   │   │   ├── instagram/
│   │   │   ├── facebook/
│   │   │   ├── x/
│   │   │   ├── linkedin/
│   │   │   ├── youtube/
│   │   │   └── mock/
│   │   ├── api/                    # API routes
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── posts.py
│   │   │   │   ├── accounts.py
│   │   │   │   ├── platforms.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── scheduling.py
│   │   │   │   ├── sentiment.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── webhooks.py
│   │   │   │   └── notifications.py
│   │   │   └── deps.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── migrations/
│   │   ├── security/
│   │   │   ├── auth.py
│   │   │   ├── credentials.py
│   │   │   └── secrets.py
│   │   ├── logging/
│   │   │   └── logger.py
│   │   └── middleware/
│   │       ├── rate_limit.py
│   │       ├── auth.py
│   │       └── error_handler.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable platform-agnostic components
│   │   │   ├── PlatformSelector.tsx
│   │   │   ├── PostComposer.tsx
│   │   │   ├── MediaUploader.tsx
│   │   │   ├── CaptionEditor.tsx
│   │   │   ├── HashtagSelector.tsx
│   │   │   ├── SchedulePicker.tsx
│   │   │   ├── SentimentPanel.tsx
│   │   │   ├── AnalyticsPanel.tsx
│   │   │   ├── CommentPanel.tsx
│   │   │   ├── ReplyPanel.tsx
│   │   │   ├── GrowthChart.tsx
│   │   │   ├── RecommendationPanel.tsx
│   │   │   └── PlatformStatus.tsx
│   │   ├── pages/                  # Dashboard pages
│   │   │   ├── Overview.tsx
│   │   │   ├── Platforms.tsx
│   │   │   ├── CreatePost.tsx
│   │   │   ├── AIOptimize.tsx
│   │   │   ├── Calendar.tsx
│   │   │   ├── ScheduledPosts.tsx
│   │   │   ├── PublishedPosts.tsx
│   │   │   ├── Comments.tsx
│   │   │   ├── AutoReply.tsx
│   │   │   ├── Sentiment.tsx
│   │   │   ├── Analytics.tsx
│   │   │   ├── GrowthPrediction.tsx
│   │   │   ├── AIRecommendations.tsx
│   │   │   ├── Notifications.tsx
│   │   │   ├── Models.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/
│   │   ├── services/              # API client
│   │   ├── store/                 # State management
│   │   └── types/                 # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── ml/
│   ├── pipelines/
│   │   ├── training_pipeline.py
│   │   ├── feature_engineering.py
│   │   └── evaluation.py
│   ├── datasets/
│   ├── models/
│   └── registry/
└── docs/
    ├── architecture/
    └── api/
```

---

## 4. Database Schema (Entity Relationship Diagram)

```
┌──────────────┐       ┌──────────────────┐
│    users     │       │  social_accounts │
├──────────────┤       ├──────────────────┤
│ id (PK)      │◄──┐   │ id (PK)          │
│ email        │   └───┤ user_id (FK)     │
│ name         │       │ platform_id      │
│ password_hash│       │ platform_acc_id  │
│ created_at   │       │ account_name     │
│ updated_at   │       │ account_username │
└──────────────┘       │ access_token_ref │
                       │ refresh_token_ref│
                       │ status           │
                       │ capabilities     │
                       │ created_at       │
                       │ updated_at       │
                       └────────┬─────────┘
                                │
                                │ 1:N
                                ▼
┌──────────────┐       ┌──────────────────┐
│    posts     │       │ post_publications│
├──────────────┤       ├──────────────────┤
│ id (PK)      │◄──┐   │ id (PK)          │
│ user_id (FK) │   └───┤ post_id (FK)     │
│ content      │       │ account_id (FK)  │
│ caption      │       │ platform_post_id │
│ status       │       │ platform         │
│ scheduled_at │       │ published_at     │
│ published_at │       │ status           │
│ media (JSON) │       │ raw_response     │
│ metadata     │       │ metrics_id (FK)  │
└──────────────┘       └────────┬─────────┘
                                │
                                │ 1:N
                                ▼
                       ┌──────────────────┐
                       │    metrics       │
                       ├──────────────────┤
                       │ id (PK)          │
                       │ publication_id   │
                       │ metric_type      │
                       │ value            │
                       │ original_metric  │
                       │ source_platform  │
                       │ timestamp        │
                       └──────────────────┘

┌──────────────┐       ┌──────────────────┐
│   comments   │       │  sentiments      │
├──────────────┤       ├──────────────────┤
│ id (PK)      │       │ id (PK)          │
│ publication_id│◄──┐   │ target_type      │
│ platform_cmt │   └───┤ target_id        │
│ content      │       │ score            │
│ author       │       │ label            │
│ created_at   │       │ phase            │
│ sentiment_id │       │ timestamp        │
└──────────────┘       └──────────────────┘

┌──────────────┐       ┌──────────────────┐
│  schedules   │       │  ml_models       │
├──────────────┤       ├──────────────────┤
│ id (PK)      │       │ id (PK)          │
│ post_id (FK) │       │ name             │
│ platform     │       │ version          │
│ scheduled_at │       │ type             │
│ status       │       │ status           │
│ window_start │       │ dataset_version  │
│ window_end   │       │ feature_version  │
└──────────────┘       │ metrics (JSON)   │
                       │ trained_at       │
                       └──────────────────┘
```

---

## 5. Event Architecture

### Event Types (Normalized Internal Events)

```python
@dataclass
class AISMEvent:
    event_type: str
    aggregate_id: str
    payload: dict
    timestamp: datetime
    source_platform: str = None

# Event types
POST_CREATED = "post.created"
POST_PUBLISHED = "post.published"
COMMENT_RECEIVED = "comment.received"
REPLY_RECEIVED = "reply.received"
ENGAGEMENT_UPDATED = "engagement.updated"
SENTIMENT_CALCULATED = "sentiment.calculated"
PREDICTION_GENERATED = "prediction.generated"
SCHEDULE_CREATED = "schedule.created"
SCHEDULE_TRIGGERED = "schedule.triggered"
PLATFORM_CONNECTED = "platform.connected"
PLATFORM_DISCONNECTED = "platform.disconnected"
TOKEN_EXPIRING = "token.expiring"
```

### Event Flow (Webhook → Intelligence Loop)

```
Platform Webhook
    ↓
Webhook Gateway (validate signature)
    ↓
Event Normalizer (platform → AISMEvent)
    ↓
Event Bus (Redis Pub/Sub)
    ↓
┌───────────────┬───────────────┬───────────────┐
↓               ↓               ↓               ↓
Sentiment     Auto-Reply     Analytics      Notification
Engine        Engine         Service        Service
    ↓               ↓               ↓               ↓
Storage        Platform       Metrics         User Alert
                 Adapter
```

---

## 6. API Architecture

### API Versioning
- Versioned under `/api/v1/`
- OpenAPI docs at `/docs`
- WebSocket for real-time notifications at `/ws`

### Route Structure
```
/api/v1/
├── /auth/
│   ├── POST /login
│   ├── POST /register
│   ├── POST /refresh
│   └── POST /logout
├── /platforms/
│   ├── GET /                    # List platforms + capabilities
│   ├── GET /{platform}/connect # OAuth initiation
│   ├── GET /{platform}/callback# OAuth callback
│   ├── POST /{platform}/disconnect
│   └── GET /{platform}/status
├── /accounts/
│   ├── GET /                    # List connected accounts
│   ├── GET /{account_id}
│   └── POST /{account_id}/sync
├── /posts/
│   ├── GET /
│   ├── POST /
│   ├── GET /{post_id}
│   ├── PUT /{post_id}
│   ├── DELETE /{post_id}
│   └── POST /{post_id}/publish
├── /scheduling/
│   ├── POST /recommend         # AI best-time
│   ├── POST /create
│   └── GET /{schedule_id}
├── /sentiment/
│   ├── POST /analyze           # Pre-post
│   └── GET /{target_id}        # Post-post
├── /ai/
│   ├── POST /caption/optimize
│   ├── POST /hashtag/recommend
│   ├── POST /content/adapt
│   └── GET /recommendations
├── /analytics/
│   ├── GET /overview
│   ├── GET /platforms/compare
│   ├── GET /content
│   ├── GET /time
│   ├── GET /sentiment
│   └── GET /growth
├── /comments/
│   ├── GET /
│   └── POST /{comment_id}/reply
├── /webhooks/
│   └── POST /{platform}
└── /notifications/
    ├── GET /
    └── POST /{id}/read
```

---

## 7. Security Architecture

### Authentication Flow
```
User → /auth/login → JWT Access + Refresh Token
         ↓
   Store refresh in httpOnly cookie
         ↓
Access token in Authorization header
         ↓
   Middleware validates JWT
         ↓
   Scoped access to resources
```

### Platform OAuth Flow
```
AISMM → Platform OAuth URL (user authorizes)
         ↓
Platform → Authorization Code
         ↓
AISMM → Exchange code for tokens
         ↓
   Encrypt tokens → Store in credential vault
         ↓
   Access via credential service only
```

### Credential Storage
- **Never** store raw tokens in normal DB fields
- Use encrypted vault (HashiCorp Vault / AWS KMS / environment)
- Token references in DB point to vault keys
- Rotation on expiry

### Rate Limiting
- Per-platform rate limits from config
- Global API rate limit (100 req/min/user)
- Exponential backoff for platform APIs
- Redis-based sliding window counter

---

## 8. Configuration Architecture

### Config Files (in `app/config/`)
- `platform_config.yaml` — per-platform capabilities, limits, media types
- `model_config.yaml` — active model selection per task
- `feature_config.yaml` — feature engineering parameters
- `scheduler_config.yaml` — scheduling model parameters
- `sentiment_config.yaml` — thresholds, model paths
- `notification_config.yaml` — notification channels, events

### Example `platform_config.yaml`
```yaml
platforms:
  instagram:
    name: "Instagram"
    capabilities:
      - publishing
      - scheduling
      - image_post
      - video_post
      - carousel_post
      - stories
      - comments
      - replies
      - analytics
      - audience_metrics
      - webhooks
    limits:
      caption_max_length: 2200
      hashtag_max_count: 30
      media_max_count: 10
    supported_media: [image, video, carousel]
    api_version: "v18.0"
    rate_limit:
      requests_per_hour: 200
      retry_policy: exponential
      max_retries: 3
  facebook:
    ...
```

---

## 9. Frontend Architecture

### Component Design Principles
- **No platform-specific components** (e.g., no `InstagramDashboard.tsx`)
- All components receive `capabilities` prop
- Components render based on capability flags
- Shared state via React Context / Zustand

### Dynamic UI Example
```typescript
function PostComposer({ platform }: { platform: Platform }) {
  const capabilities = platform.capabilities;
  
  return (
    <div>
      {capabilities.includes('text_post') && <TextInput />}
      {capabilities.includes('image_post') && <MediaUploader type="image" />}
      {capabilities.includes('video_post') && <MediaUploader type="video" />}
      {capabilities.includes('scheduled_post') && <SchedulePicker />}
      {capabilities.includes('hashtags') && <HashtagSelector />}
      {capabilities.includes('comments') && <CommentPanel />}
      {capabilities.includes('analytics') && <AnalyticsPanel />}
    </div>
  );
}
```

---

## 10. Deployment Architecture

```
┌─────────────────────────────────────────────┐
│              Load Balancer (Nginx)           │
└──────────────┬──────────────────────────────┘
               │
┌──────────────┴──────────────┐
│   Frontend (React SPA)      │
│   Static files + CDN        │
└──────────────┬──────────────┘
               │
┌──────────────┴──────────────┐
│   Backend (FastAPI)         │
│   Multiple workers (uvicorn)│
│   + Celery workers          │
└────────┬──────────┬─────────┘
         │          │
    ┌────┴────┐  ┌──┴────────┐
    │PostgreSQL│  │  Redis    │
    │         │  │ (Cache/   │
    │         │  │  Queue/   │
    │         │  │  PubSub)  │
    └─────────┘  └───────────┘
```

### Container Strategy
- Docker Compose for dev
- Kubernetes for prod
- Separate containers: frontend, backend, celery, postgres, redis

---

## 11. Decision Records (ADRs)

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | Platform-agnostic adapter architecture | Future-proof, no rewrites for new platforms |
| ADR-002 | Capability-based platform system | Dynamic UI, graceful degradation |
| ADR-003 | Universal data models (normalized + raw) | AI/analytics on normalized, audit on raw |
| ADR-004 | AI core independent from platforms | Replaceable models, platform isolation |
| ADR-005 | Event-driven architecture | Loose coupling, real-time intelligence loop |
| ADR-006 | Configuration-driven system | No hardcoded platform logic |
| ADR-007 | Model registry with versioning | Reproducibility, A/B testing |
| ADR-008 | Mock platform adapter for testing | Test without external APIs |
| ADR-009 | Dynamic UI from capabilities | One UI for all platforms |
| ADR-010 | Secure credential vault | No raw secrets in DB |

---

## 12. Open Questions / Risks

| # | Question/Risk | Mitigation |
|---|---------------|-----------|
| 1 | LinkedIn scheduling not supported natively | AISMM-side scheduling fallback (configurable) |
| 2 | Rate limits vary widely per platform | Per-platform config + adaptive backoff |
| 3 | Model drift over time | Performance monitoring + retrain pipeline |
| 4 | OAuth token expiry | Refresh flow + TOKEN_EXPIRING event |
| 5 | API version changes | Adapter isolation, version-specific code |

---

**Status:** DESIGN — AWAITING APPROVAL  
**Next:** Upon approval, proceed to Phase 3 (Core Foundation) implementation.
