# AISMM REQUIREMENT MATRIX
**Phase 1 — Requirement Mapping**  
**Created:** 2026-08-25  
**Status:** IN PROGRESS

---

## Legend
| Status | Meaning |
|--------|---------|
| 🟦 **NOT STARTED** | No work begun |
| 🟨 **PARTIAL** | Some implementation exists |
| 🟩 **IMPLEMENTED** | Feature complete, needs testing |
| 🟢 **TESTED** | Tests written and passing |
| ✅ **VERIFIED** | End-to-end verified, production ready |

---

## Research-Defined Core Modules (from AISMM Paper)

| # | Requirement | Research Baseline | Target Implementation | Status | Notes |
|---|-------------|-------------------|----------------------|--------|-------|
| **1** | **Centralized Multi-Platform Dashboard** | Unified view for Instagram, Facebook, Twitter | Platform-agnostic dashboard with dynamic UI per capabilities | 🟦 NOT STARTED | Core architecture dependency |
| **2** | **Intelligent Time Scheduling** | Random Forest + XGBoost + Hard Voting (88.08%) | Platform-aware scheduling engine with ML pipeline | 🟦 NOT STARTED | Phase 8 |
| **3** | **Dual-Phase Sentiment Analysis** | VADER + k-NN (89.00%, k=5, 0.019s) | Pre-post & post-post analyzers with temporal aggregation | 🟦 NOT STARTED | Phase 7, 9 |
| **4** | **Predictive Growth Modeling** | Random Forest Regressor (IG: 89.2%, FB: 87.5%, TW: 85.8% R²) | Platform-specific growth models with model registry | 🟦 NOT STARTED | Phase 11 |
| **5** | **Auto-Reply** | TF-IDF + Multiclass Logistic Regression (88.00%) | ReplyEngine abstraction (TFIDF/LLM/Hybrid) with human-in-loop | 🟦 NOT STARTED | Phase 10 |
| **6** | **Caption & Hashtag Optimization** | Top-K=5 (92.70%) | CaptionEngine + HashtagEngine with platform adaptation | 🟦 NOT STARTED | Phase 7 |

---

## Architectural Requirements (Platform-Agnostic Design)

| # | Requirement | Specification | Target Implementation | Status | Notes |
|---|-------------|---------------|----------------------|--------|-------|
| **A1** | **Platform Adapter Architecture** | BasePlatformAdapter with capability reporting | Abstract base + 5 platform adapters | 🟦 NOT STARTED | Phase 3, 4, 5 |
| **A2** | **Platform Registry** | Central registry for adapter discovery/loading | PlatformRegistry with dynamic capability loading | 🟦 NOT STARTED | Phase 3 |
| **A3** | **Capability-Based System** | Dynamic capability declaration per platform | PlatformCapabilities enum + supports() method | 🟦 NOT STARTED | Phase 3 |
| **A4** | **Universal Data Models** | User, SocialAccount, Post, PostPublication, UniversalContent | SQLAlchemy/Prisma models with platform-neutral fields | 🟦 NOT STARTED | Phase 3 |
| **A5** | **Content Normalization** | UniversalContent → PlatformSpecificPayload mappers | Mapper per platform (mapper.py in each adapter) | 🟦 NOT STARTED | Phase 3, 4 |
| **A6** | **Cross-Platform Posting** | Create once → customize → publish to selected | PostComposer with platform-specific variants | 🟦 NOT STARTED | Phase 6 |
| **A7** | **AI Core Independence** | AI receives normalized data only | Sentiment, Scheduling, Growth, Reply engines use normalized inputs | 🟦 NOT STARTED | Phase 3, 7-13 |
| **A8** | **Event-Driven Architecture** | Normalized internal events (PostCreated, CommentReceived, etc.) | Event bus with webhook gateway | 🟦 NOT STARTED | Phase 3, 9 |
| **A9** | **Configuration-Driven** | platform_config, model_config, feature_config | YAML/JSON config files, no hardcoded platform logic | 🟦 NOT STARTED | Phase 3 |
| **A10** | **Plugin Architecture** | Install plugin → register adapter → auto-appear | Entry-point based plugin system | 🟦 NOT STARTED | Phase 14 |

---

## Platform-Specific Requirements

| Platform | Auth | Publishing | Media | Scheduling | Comments | Analytics | Webhooks | Status |
|----------|------|------------|-------|------------|----------|-----------|----------|--------|
| **Instagram** | OAuth 2.0 | Feed, Stories, Reels | Image, Video, Carousel | ✅ Native | ✅ | ✅ Insights | ✅ | 🟦 NOT STARTED |
| **Facebook** | OAuth 2.0 | Feed, Stories, Reels | Image, Video, Carousel | ✅ Native | ✅ | ✅ Insights | ✅ | 🟦 NOT STARTED |
| **X (Twitter)** | OAuth 1.0a/2.0 | Tweets, Threads | Image, Video, GIF | ✅ Native | ✅ | ✅ Analytics | ✅ | 🟦 NOT STARTED |
| **LinkedIn** | OAuth 2.0 | Posts, Articles | Image, Video, Document | ❌ Limited | ✅ | ✅ Analytics | ❌ | 🟦 NOT STARTED |
| **YouTube** | OAuth 2.0 | Videos, Shorts | Video only | ✅ Native | ✅ | ✅ Analytics | ✅ | 🟦 NOT STARTED |

---

## Data Layer Requirements

| # | Requirement | Specification | Status |
|---|-------------|---------------|--------|
| **D1** | **Database Schema** | Users, SocialAccounts, Posts, Publications, Metrics, Comments, Models | 🟦 NOT STARTED |
| **D2** | **Raw Platform Data Storage** | Store raw API responses for debugging/auditing | 🟦 NOT STARTED |
| **D3** | **Normalized Data Storage** | AISMM-normalized entities for AI/analytics | 🟦 NOT STARTED |
| **D4** | **Model Registry** | Versioned models with dataset/feature/training metadata | 🟦 NOT STARTED |
| **D5** | **Migrations** | Alembic/Prisma migrations for schema evolution | 🟦 NOT STARTED |

---

## AI/ML Pipeline Requirements

| # | Requirement | Specification | Status |
|---|-------------|---------------|--------|
| **M1** | **Training Pipeline** | Validation → Cleaning → Feature Eng → Versioning → Train → Eval → Registry → Deploy | 🟦 NOT STARTED |
| **M2** | **Model Versioning** | development/staging/production/deprecated states | 🟦 NOT STARTED |
| **M3** | **Performance Monitoring** | Prediction → Actual → Compare → Drift Detection → Retrain Recommendation | 🟦 NOT STARTED |
| **M4** | **Feature Store** | Shared feature engineering for scheduling, sentiment, growth | 🟦 NOT STARTED |
| **M5** | **Mock Platform Adapter** | Simulate publishing, comments, analytics, errors, rate limits for testing | 🟦 NOT STARTED |

---

## Frontend Requirements

| # | Requirement | Specification | Status |
|---|-------------|---------------|--------|
| **F1** | **Dynamic UI Components** | PlatformSelector, PostComposer, MediaUploader, CaptionEditor, HashtagSelector, SchedulePicker, SentimentPanel, AnalyticsPanel, CommentPanel, ReplyPanel, GrowthChart, RecommendationPanel, PlatformStatus | 🟦 NOT STARTED |
| **F2** | **Dashboard Structure** | Overview, Platforms, Create Post, AI Optimize, Calendar, Scheduled Posts, Published Posts, Comments, Auto Reply, Sentiment, Analytics, Growth Prediction, AI Recommendations, Notifications, Models, Settings | 🟦 NOT STARTED |
| **F3** | **Platform Connection Page** | Connection status, account name, permissions, token status, capabilities, last sync, disconnect | 🟦 NOT STARTED |
| **F4** | **Capability-Driven Rendering** | UI asks backend for capabilities, renders accordingly | 🟦 NOT STARTED |

---

## Backend/API Requirements

| # | Requirement | Specification | Status |
|---|-------------|---------------|--------|
| **B1** | **Authentication System** | JWT/OAuth, secure credential store, token refresh | 🟦 NOT STARTED |
| **B2** | **REST/GraphQL API** | CRUD for posts, accounts, analytics, scheduling, AI recommendations | 🟦 NOT STARTED |
| **B3** | **Rate Limit Management** | Exponential backoff, retry limits, request throttling per platform | 🟦 NOT STARTED |
| **B4** | **Error Handling** | PlatformError hierarchy (Auth, RateLimit, Validation, Publishing, Analytics, UnsupportedCapability) | 🟦 NOT STARTED |
| **B5** | **Webhook Gateway** | Event normalization → Event bus → Relevant service | 🟦 NOT STARTED |
| **B6** | **Notification Engine** | Browser, in-app, email, mobile push for POST_SCHEDULED, POST_PUBLISHED, HIGH_ENGAGEMENT, NEGATIVE_SENTIMENT, REPLY_REQUIRED, GROWTH_ALERT, MODEL_ALERT, PLATFORM_ERROR, TOKEN_EXPIRING | 🟦 NOT STARTED |

---

## Testing Requirements

| # | Requirement | Specification | Status |
|---|-------------|---------------|--------|
| **T1** | **Unit Tests** | Adapters, normalization, feature engineering, sentiment, scheduler, recommendation, analytics | 🟦 NOT STARTED |
| **T2** | **Integration Tests** | Frontend → Backend → Database → AI Engine → Platform Adapter | 🟦 NOT STARTED |
| **T3** | **End-to-End Tests** | Create Post → AI Optimize → Sentiment → Schedule → Publish → Fetch Comment → Analyze Sentiment → Auto Reply → Update Analytics → Growth Prediction | 🟦 NOT STARTED |
| **T4** | **Mock Platform Testing** | Full system test without external APIs | 🟦 NOT STARTED |

---

## Production Hardening Requirements

| # | Requirement | Specification | Status |
|---|-------------|---------------|--------|
| **P1** | **Security** | Auth security, authorization, secret management, audit logs | 🟦 NOT STARTED |
| **P2** | **Monitoring** | Health checks, logging, metrics, alerting | 🟦 NOT STARTED |
| **P3** | **Database Backups** | Automated backup/restore strategy | 🟦 NOT STARTED |
| **P4** | **API Retries** | Circuit breakers, dead letter queues | 🟦 NOT STARTED |

---

## Phase-to-Requirement Mapping

| Phase | Requirements Covered |
|-------|---------------------|
| **Phase 1** | This matrix (requirement mapping) |
| **Phase 2** | Architecture design for A1-A10, D1-D5, M1-M5, F1-F4, B1-B6, T1-T4, P1-P4 |
| **Phase 3** | A1, A2, A3, A4, A5, A9, D1, D2, D3, D5, B1, B3, B4 (Core Foundation) |
| **Phase 4** | A1, A5, A6, A7, A8 (First Platform - Instagram recommended) |
| **Phase 5** | A1, A5, A6, A7, A8 (Second Platform - Facebook/X for validation) |
| **Phase 6** | A6, F1, F2, B2 (Content Management) |
| **Phase 7** | Req 3 (Pre-post), Req 6, M1 (AI Content Engine) |
| **Phase 8** | Req 2, M1, M4 (Scheduling Engine) |
| **Phase 9** | Req 3 (Post-post), A8, B5 (Post-Posting Intelligence) |
| **Phase 10** | Req 5, A7, A8 (Auto-Reply) |
| **Phase 11** | Req 4, M1, M2, M3 (Growth Prediction) |
| **Phase 12** | F2, F3, D3, B2 (Analytics) |
| **Phase 13** | Req 1, 2, 3, 4, 5, 6, A7 (AI Strategy Engine) |
| **Phase 14** | A10, Platform expansion process (Multi-Platform) |
| **Phase 15** | M1, M3, M4 (Model Improvement) |
| **Phase 16** | P1, P2, P3, P4 (Production Hardening) |
| **Phase 17** | All (Final Verification) |

---

## Next Steps

1. ✅ **Phase 0** — Project Audit complete
2. 🟨 **Phase 1** — Requirement Mapping **IN PROGRESS** (this matrix)
3. ⏳ **Phase 2** — Architecture Design (awaiting approval of this matrix)
4. ⏳ **Phase 3** — Core Foundation

---

**Approval Required:** This requirement matrix must be reviewed and approved before proceeding to Phase 2 (Architecture Design).
