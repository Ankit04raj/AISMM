# AISMM Architecture Documentation

## Phase 2 — Architecture Design

This directory contains the architecture design documents for AISMM, created during Phase 2.

### Documents

| Document | Scope |
|----------|-------|
| [01_core_architecture.md](./01_core_architecture.md) | High-level architecture, layered design, data flows, components, database ERD, events, frontend, security, deployment, config, tech stack, ADRs |
| [02_platform_adapter.md](./02_platform_adapter.md) | Platform adapter contract, directory structure, capability system, content normalization, error translation, rate limits, registry, mock adapter |
| [03_ai_engine.md](./03_ai_engine.md) | AI engine architecture, base engine interface, engine specs, model registry, training pipeline, feature engineering, recommendation engine, monitoring |

### Architecture Summary

```
AISMM Core (Intelligence)
    │
    ├── Content Engine
    ├── AI Engine (9 engines: Scheduling, Sentiment, Engagement, Growth, Caption, Hashtag, Auto-Reply, Recommendation)
    ├── Analytics Engine
    └── Platform Registry
            │
            ├── Instagram Adapter
            ├── Facebook Adapter
            ├── X Adapter
            ├── LinkedIn Adapter
            └── YouTube Adapter
                    │
                    └── External APIs
```

### Key Principles (from CLAUDE.md)

1. **Platform-agnostic**: Core never depends on platform-specific implementation
2. **Capability-based**: Each platform declares what it supports dynamically
3. **Universal data models**: Platform-neutral entities + per-platform publications
4. **AI independence**: Engines consume normalized data only
5. **Event-driven**: Normalized internal events for post-posting intelligence
6. **Configuration-driven**: No hardcoded platform assumptions
7. **Model registry**: Versioned models with lifecycle management
8. **Mock testing**: Full system testable without external APIs

---

*Status: DRAFT — Awaiting Review (Phase 2)*
