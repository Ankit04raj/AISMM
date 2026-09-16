# Implementation Plan: End-to-End AISMM Dashboard Integration

> **Plan file:** `docs/superpowers/plans/2026-09-16-aismm-dashboard-integration.md`
> **Spec:** `docs/superpowers/specs/2026-09-16-dashboard-realtime-backend-integration-design.md`
> **Branch:** `feature/production-hardening-and-e2e`

**Goal:** Replace all static mock data, outdated date strings ("May 2024"), and disconnected charts across 13 dashboard tabs with live backend-bound APIs and accurate real-time sync.

**Execution mode:** Subagent-driven per tab batch (recommended per superpowers).

---

### Block A — Overview (Task A1-A4)
**Files:** `frontend/src/components/OverviewTab.jsx`
- [A1] Replace hardcoded KPIs with `data.overview` binding from `api.getOverview()`;
- [A2] Replace SVG line chart static `d` paths with dynamic `data.daily_metrics` mapped to `viewBox` points;
- [A3] Replace donut chart static `strokeDasharray` with computed per-platform percentages from `data.platform_breakdown`;
- [A4] Update date header from `"May 20 - May 26, 2024"` to dynamic `new Date()` range.

### Block B — Scheduling (Task B1-B3)
**Files:** `frontend/src/components/SchedulingTab.jsx`
- [B1] Replace static best-time array with `api.getSchedulingRecommendations()`;
- [B2] Replace calendar `May 2024` with dynamic current month grid computed from `new Date()` with real scheduled post dots from API;
- [B3] Ensure timezone conversion (`toISOString`) on schedule submit.

### Block C — Growth & Strategy (Task C1-C4)
**Files:** `frontend/src/components/GrowthTab.jsx`, `frontend/src/components/StrategyTab.jsx`
- [C1] Bind demographics from `/growth/demographics` instead of hardcoded India 32%;
- [C2] Bind trajectory cards from `/growth/predict` with real ML R² values;
- [C3] Build radar polygon dynamically from `/strategy/pillars` scores (not static coordinates);
- [C4] Remove hardcoded demo comments from `InboxTab.jsx`.

### Block D — Reports, Settings, Security (Task D1-D3)
**Files:** `frontend/src/components/ReportsTab.jsx`, `frontend/src/components/SettingsTab.jsx`, `frontend/src/components/SecurityTab.jsx`
- [D1] Replace fixed `May 20 - May 26` with dynamic sliding picker and server-side export (`POST /analytics/export`);
- [D2] Persist timezone selection to `/auth/me` via `PATCH`;
- [D3] Wire `SecurityTab` health checks to `/health/live`, `/health/ready`.

---

**Verification:** All 13 tabs load without static "May 2024" or mock numbers; real-time WebSocket events propagate to inbox/post status; timezone settings persist after reload.
