# Technical Design Spec: Dashboard Real-Time Backend Integration & Dynamic Platform Sync

## 1. Executive Summary & Objective
This specification defines the end-to-end architecture, backend integration, dynamic date/time synchronization, and real-time streaming pipeline for the AISMM Dashboard. It addresses all issues identified during the comprehensive audit of all 15 tab screenshots in `/home/ankit/CLAUDE/ss`, ensuring that every tab, chart, KPI card, and platform connection operates with live backend data and accurate real-time updates.

---

## 2. Architecture & Real-Time Sync Strategy

### 2.1 Dual-Channel Hybrid Real-Time System
1. **WebSocket Live Event Stream (`/api/v1/ws/events`)**:
   - Connection lifecycle managed with JWT token authentication on connect (`?token=<jwt>`).
   - Push events:
     - `INBOX_MESSAGE_RECEIVED`: Incoming social media comments, mentions, and DMs.
     - `POST_STATUS_UPDATED`: Scheduler dispatch updates (`SCHEDULED` -> `PUBLISHING` -> `PUBLISHED` / `FAILED`).
     - `PLATFORM_SYNC_COMPLETED`: Dynamic account follower/metric sync status.
     - `METRIC_ALERT`: Real-time sentiment or growth anomaly alerts.
   - Resilient client reconnection with exponential backoff (1s, 2s, 5s, max 10s) and keepalive ping/pong heartbeat.

2. **Smart SWR & Dynamic REST Polling Pipeline**:
   - Revalidates on window focus (`focus` event), tab switching, and manual refresh triggers.
   - Provides resilient fallback if WebSocket is offline or reconnecting.
   - Powers analytical aggregations, growth trajectory ML models, and strategy balance matrices.

---

## 3. Screen-by-Screen & Tab-by-Tab Integration Blueprint

### Tab 1: Overview Dashboard (`OverviewTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-18-51.png`
- **Current Issue**: Hardcoded top KPI cards (2.4M reach, 184.7K engagement, 45.2K visits, 12.8K clicks, 2.1K conversions), static SVG line chart coordinates (`May 20 - May 26`), static donut chart values, and mock AI insight badges.
- **Backend Integration**:
  - Connect to `GET /api/v1/analytics/overview?days=30` and `GET /api/v1/posts/feed?page=1&limit=10`.
  - Dynamic KPI binding: Calculate dynamic sum and trend percentages from actual platform metrics.
  - Dynamic SVG Line Chart: Compute X/Y polyline and area path coordinates dynamically from real daily metric arrays with sliding date axis labels (`dayjs().subtract(i, 'day')`).
  - Dynamic SVG Donut Chart: Compute stroke-dasharray and percentages dynamically from per-platform share breakdown (`data.platform_breakdown`).
  - Dynamic AI Insights: Map live recommendations from `/api/v1/strategy` or heuristic engine.

### Tab 2: Analytics Tab (`AnalyticsTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-18-58.png`
- **Current Issue**: Credential error handling banner and date window range formatting.
- **Backend Integration**:
  - Connect to `GET /api/v1/analytics/aggregate?days={selectedWindow}` and `GET /api/v1/analytics/sentiment-trends`.
  - Graceful credential handling: When platform token needs refresh, show clean inline reconnect action rather than breaking full-page layout.
  - Dynamically format date intervals according to user's localized timezone.

### Tab 3: Content Composer (`ComposerTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-05.png`
- **Current Issue**: Local vs UTC timezone preview synchronization.
- **Backend Integration**:
  - Connect to `POST /api/v1/posts/publish` and `POST /api/v1/posts/schedule`.
  - User selects time in local timezone (`Intl.DateTimeFormat().resolvedOptions().timeZone` / user profile preference).
  - Explicit conversion to ISO UTC string (`new Date(scheduledAt).toISOString()`) before submitting payload to backend scheduler.

### Tab 4: Smart Scheduling (`SchedulingTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-12.png`
- **Current Issue**: Hardcoded static "May 2024" calendar month with fixed dots, static "Today 7:00 PM, Tomorrow 6:30 PM, May 22 8:00 PM" best times.
- **Backend Integration**:
  - Connect to `GET /api/v1/scheduling/recommendations` and `GET /api/v1/posts/scheduled`.
  - Dynamic calendar generation: Render current active month and year dynamically based on `new Date()`, showing real scheduled posts as active dot markers.
  - Best Time Recommendations: Dynamically display AI calculated optimal publishing slots from backend engagement ML model.

### Tab 5: AI Content Engine (`AIEngineTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-16.png`
- **Current Issue**: Hardcoded checklist improvements and static scores (72 to 92).
- **Backend Integration**:
  - Connect to `POST /api/v1/ai/optimize`, `POST /api/v1/ai/hashtags`, and `POST /api/v1/ai/sentiment`.
  - Dynamically render computed readability/engagement scores, dynamic improvement bullet points, and AI-suggested platform-specific variants.

### Tab 6: Inbox & Engagement (`InboxTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-22.png`
- **Current Issue**: Static fallback comments from demo usernames (`tech_lover`, `business_owner`, etc.) when no comments found.
- **Backend Integration**:
  - Connect to `GET /api/v1/inbox` and `POST /api/v1/reply/suggest`.
  - Real-time WebSocket streaming for incoming comments and direct messages across Instagram, X, Facebook, LinkedIn, YouTube.
  - If inbox is empty, display an elegant zero-state empty container rather than fake mock users.
  - Dynamic AI Auto-Reply dispatch via `POST /api/v1/reply/send`.

### Tab 7: Growth Intelligence (`GrowthTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-28.png`
- **Current Issue**: Hardcoded audience demographics (India 32%, 25-34 age group) and static trajectory numbers (+780, +3200, +10450).
- **Backend Integration**:
  - Connect to `GET /api/v1/growth/predict` and `GET /api/v1/growth/demographics`.
  - Render real ML Random Forest model outputs (R², MSE, predicted follower trajectory across 7, 30, and 90-day horizons).

### Tab 8: Platforms Connection Hub (`PlatformsTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-15 12-45-53.png` & `2026-09-16 13-19-34.png`
- **Current Issue**: Dynamic status updates when connecting or reconnecting accounts.
- **Backend Integration**:
  - Connect to `GET /api/v1/accounts/me`, `POST /api/v1/accounts/connect/{platform}`, and `DELETE /api/v1/accounts/{id}`.
  - Display actual live handles, follower counts, avatar URLs, token expiration times, and AES-256 vault status.
  - Live refresh via WebSocket event `PLATFORM_SYNC_COMPLETED`.

### Tab 9: AI Strategy Engine (`StrategyTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-40.png`
- **Current Issue**: Static mock strategy pillars and hardcoded SVG radar chart coordinates.
- **Backend Integration**:
  - Connect to `GET /api/v1/strategy/pillars` and `GET /api/v1/strategy/recommendations`.
  - Compute dynamic radar polygon vertices `(x, y)` mathematically from real pillar scores (Engagement, Reach, Consistency, Quality, Conversion).

### Tab 10: Reports & Insights (`ReportsTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-47.png`
- **Current Issue**: Hardcoded date range string `May 20, 2024 - May 26, 2024` and client-side static JSON generator.
- **Backend Integration**:
  - Dynamic date range picker initialized to current sliding window (e.g. Last 7 Days, Last 30 Days).
  - Connect to `POST /api/v1/analytics/export` to generate genuine, server-calculated CSV/JSON reports.

### Tab 11: Model Registry & Evaluation (`ModelsTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-54.png`
- **Backend Integration**:
  - Connect to `GET /api/v1/models/registry` to render live ML model evaluation metrics, inference latencies, and training dates.

### Tab 12: Settings & Configuration (`SettingsTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-19-59.png`
- **Current Issue**: Timezone selection only modifies local React state and is not persisted.
- **Backend Integration**:
  - Connect to `GET /api/v1/auth/me` and `PATCH /api/v1/auth/profile` to save timezone, locale, and notification preferences to the user database record.

### Tab 13: Security & Health (`SecurityTab.jsx`)
- **Screenshot Ref**: `Screenshot from 2026-09-16 13-20-06.png`
- **Backend Integration**:
  - Connect to `GET /api/v1/health/live`, `GET /api/v1/health/ready`, and `GET /api/v1/health/security-vault`.

---

## 4. Backend WebSocket Implementation Details
- **Module**: `backend/app/api/v1/endpoints/ws.py`
- **Router Integration**: Added to `backend/app/api/v1/router.py`
- **Connection Manager**:
  - Tracks active connections by `user_id`.
  - Provides `broadcast_to_user(user_id, event_type, payload)`.
  - Integrated into background task dispatchers (scheduler, webhooks, comment synchronization).

---

## 5. Verification & Testing Strategy
1. **Unit & Integration Tests**:
   - Verify WebSocket connection auth and event broadcasting.
   - Verify all API endpoints return live schema-compliant responses with dynamic timestamps.
2. **Frontend End-to-End Testing**:
   - Verify all 15 tabs render without static mock date fallbacks ("May 2024").
   - Verify real-time event updates reflect on the UI immediately without manual page refresh.
   - Verify timezones correctly convert between user local time and server UTC.
