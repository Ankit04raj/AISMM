# AISMM — Product UX/UI Design System

**Document Version:** 1.0.0  
**Status:** Active / Source of Truth  
**Design Paradigm:** Modern Obsidian Dark-Theme, High-Density Information Architecture, Zero-Falsification UI  

---

## 1. Visual Identity & Design Principles

AISMM is crafted with a focused, low-distraction dark theme engineered for high-productivity content operations and analytics monitoring.

### Core Design Principles
1. **Truth in Telemetry**: Never fabricate metrics or render fake success states. If an account has zero data or a provider is disconnected, display clear empty/offline states with actionable resolution steps.
2. **Context Preservation**: Preserve user drafts and active tab contexts across navigation so content in progress is never lost.
3. **Information Density with Hierarchy**: Balance dense analytics tables and multi-platform preview cards with clean visual hierarchy, distinct card borders, and high-contrast typography.
4. **Instant AI Feedback**: Present AI suggestions (sentiment score, hashtag recommendations, caption rewrites) as inline non-blocking assistance directly within the creation flow.

---

## 2. Color Palette & Typography Tokens

### Theme Tokens (`tailwind.config.js`)
- **Background Obsidian Primary**: `#0b0f19` (`bg-obsidian-bg`)
- **Background Surface / Card**: `#111827` (`bg-slate-900`) / `#1e293b` (`bg-slate-800`)
- **Border Subtle**: `#1e293b` (`border-slate-800`) / `#334155` (`border-slate-700`)
- **Text Primary**: `#f8fafc` (`text-slate-50`)
- **Text Secondary / Muted**: `#94a3b8` (`text-slate-400`) / `#64748b` (`text-slate-500`)
- **Accent Primary (Indigo / Violet)**: `#6366f1` / `#8b5cf6` (`from-indigo-500 to-purple-600`)
- **Success / Positive**: `#10b981` (`emerald-500`)
- **Warning / Ambiguous**: `#f59e0b` (`amber-500`)
- **Danger / Negative / Offline**: `#ef4444` (`rose-500` / `red-500`)
- **Platform Brand Accents**:
  - Instagram: `#E1306C`
  - Facebook: `#1877F2`
  - X (Twitter): `#1DA1F2`
  - LinkedIn: `#0A66C2`
  - YouTube: `#FF0000`

### Typography
- **Font Family**: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif.
- **Scale**:
  - Headings: `text-2xl font-bold` (Page titles), `text-lg font-semibold` (Card headers)
  - Body: `text-sm text-slate-300` (Standard UI), `text-xs text-slate-400` (Metadata/Labels)
  - Code / Metrics: Monospace `font-mono text-xs` (IDs, Tokens, Correlation keys)

---

## 3. Application Layout & Navigation Structure

```
+---------------------------------------------------------------------------------------------------+
| [Logo: AISMM]  [Search / Quick Action]              [Tenant: Org / User]  [Profile Avatar] [Logout]|
+---------------------------------------------------------------------------------------------------+
| SIDEBAR (Left)  | MAIN CONTENT WORKSPACE (Center / Right)                                         |
|                 |                                                                                 |
| * Overview      | +-----------------------------------------------------------------------------+ |
| * Composer      | | Active Tab Workspace Header (e.g. Content Composer & AI Studio)            | |
| * Scheduling    | +-----------------------------------------------------------------------------+ |
| * Platforms     | |                                                                             | |
| * AI Engine     | | [ Card / Grid Components with Responsive Breakpoints ]                      | |
| * Inbox         | |                                                                             | |
| * Analytics     | |                                                                             | |
| * Growth        | |                                                                             | |
| * Strategy      | |                                                                             | |
| * Models        | |                                                                             | |
| * Reports       | |                                                                             | |
| * Security      | |                                                                             | |
| * Settings      | +-----------------------------------------------------------------------------+ |
+-----------------+---------------------------------------------------------------------------------+
```

- **Top Navbar**: Displays brand identity, active tenant indicators, system status beacon, user avatar, and session logout.
- **Collapsible Sidebar**: Vertical navigation spanning 13 core tabs with active highlight indicator and icon pairing. Collapses to a slide-out drawer on mobile viewports (< 1024px).
- **Tab Persistence (`App.jsx`)**: Active tab DOM elements use `hidden={name !== tab}` rather than unmounting, ensuring state continuity for unsaved drafts.

---

## 4. Component Design Specifications

### 1. Authentication & Onboarding (`AuthView.jsx`)
- **Card Container**: Centered glassmorphic card (`max-w-md bg-slate-900 border border-slate-800 rounded-xl p-8`).
- **Registration Form**: Email, password (with length limit indicator), full name, terms & privacy agreement checkbox.
- **6-Digit OTP Screen**: Formatted individual or grouped 6-digit input with automatic focus progression, 5-minute countdown timer, and "Resend Code" rate-limited action.
- **Login Flow**: Credentials form with inline 2FA TOTP field dynamically requested when MFA is enabled on the account.
- **Forgot Password**: Password reset request with OTP/Token verification and new password confirmation form.

### 2. Social Accounts & Platforms (`PlatformsTab.jsx`)
- **Platform Cards Grid**: 5 major platform cards (Instagram, Facebook, X, LinkedIn, YouTube).
- **Status Indicator Badges**:
  - `Live OAuth (Active)`: Emerald pill with verified timestamp.
  - `Expired / Reconnect Needed`: Amber pill with immediate "Reconnect Account" button.
  - `Unverified / Direct`: Slate pill indicating manual handle entry.
- **Developer Portal Guidance Drawer**: Expandable instructions with direct links to Meta Developer Portal, Twitter Developer Portal, LinkedIn Developers, and Google Cloud Console.

### 3. Universal Content Composer (`ComposerTab.jsx`)
- **Target Platform Multi-Select**: Toggleable chips for Instagram, Facebook, X, LinkedIn, YouTube with real-time character limit adjustment.
- **Editor Area**: Multi-line text input with rich hashtag parsing and live character count vs. platform limit indicator.
- **Media Attachment Tray**: URL / file upload input with media type detection (Image, Video, Carousel, Reel) and aspect-ratio validation warnings.
- **AI Assist Panel**: One-click "AI Optimize" button triggering concurrent Sentiment, Caption Quality, and Hashtag extraction, rendering interactive suggestion chips that append directly to the editor on click.
- **Live Device Preview**: Tabbed device preview mockup displaying exact rendered social post card per platform.
- **Publish & Schedule Toolbar**: "Publish Now", "AI Optimal Schedule", and "Custom Schedule" actions with date/time pickers.

### 4. Scheduling & Calendar (`SchedulingTab.jsx`)
- **7-Day Interactive Grid**: Hourly row matrix mapping scheduled posts with platform icons and status badges.
- **AI Peak Time Recommendation Bar**: Visual highlight of predicted high-engagement windows for the selected platform.
- **Scheduled Queue Table**: Chronological list of upcoming posts with edit, reschedule, and delete actions.

### 5. Unified Community Inbox & Auto-Reply (`InboxTab.jsx`)
- **Thread List**: Split-pane interface listing incoming comments across all platforms with sentiment score badges (Positive, Neutral, Negative).
- **Conversation Pane**: Displays comment thread, author handle, platform timestamp, and parent post context.
- **Auto-Reply Suggestions Card**: Displays classified intent (e.g. *Inquiry*, *Complaint*, *Compliment*), confidence percentage, and suggested AI response.
- **Human-in-the-Loop Actions**: "Approve & Send", "Edit Reply", and "Dismiss" buttons for routing approval.

### 6. Universal Analytics & Reporting (`AnalyticsTab.jsx`, `ReportsTab.jsx`)
- **Metric KPI Cards**: Total Reach, Net Followers, Engagement Rate, Video Views with historical trend arrows.
- **Performance Charts**: Dynamic SVG area charts and bar charts for daily impressions and engagement comparisons.
- **Temporal 7x24 Heatmap**: Hourly grid showing engagement distribution across days of the week.
- **Export Toolbar**: Date range filter (7d, 30d, 90d, Custom) with instant "Export CSV" and "Export JSON" download buttons.

### 7. Predictive Growth Engine (`GrowthTab.jsx`)
- **Follower Velocity Trends**: Historical curve showing net follower additions over time.
- **Horizon Forecast Cards**: 3 projection cards (7-Day, 30-Day, 90-Day) displaying predicted follower counts, growth rates, and model $R^2$ confidence indicators.
- **Feature Importance Breakdown**: Ranked horizontal bar chart displaying factors influencing growth (e.g. Posting Frequency, Video Ratio, Sentiment Score).

### 8. AI Strategy & Recommendations (`StrategyTab.jsx`)
- **Strategic Directives List**: Ranked recommendation cards categorized by Priority (*High*, *Medium*, *Low*) and Category (*Timing*, *Content*, *Audience*, *Platform*).
- **Benchmark Radar Chart**: Visual comparison of account performance metrics against platform category benchmarks.
- **Feedback Action**: "Mark as Applied" / "Not Relevant" buttons to capture user feedback into `StrategyFeedback`.

### 9. ML Models & Registry (`ModelsTab.jsx`)
- **Active Model Catalog**: Cards for each production model (Sentiment VADER, Scheduling Ensemble, Growth Regressors, Auto-Reply Classifier).
- **Model Health & Metrics**: Test accuracy, $R^2$, F1-scores, training timestamps, and data drift diagnostic gauges.

### 10. Security & Credentials (`SecurityTab.jsx`)
- **Password Management**: Current password, new password, and confirmation inputs.
- **Two-Factor Authentication (2FA)**: Step-by-step setup modal with SVG QR code, secret key display, 6-digit confirmation code input, and backup recovery codes grid.
- **Active Sessions Table**: List of active login sessions with IP address, user-agent, creation date, and "Revoke All Sessions" action.

---

## 5. Responsive Design & Accessibility Standards

- **Breakpoints**: Mobile (< 640px), Tablet (640px - 1024px), Desktop (> 1024px).
- **Accessibility**:
  - Full keyboard navigation across all forms, buttons, and tab switchers.
  - High-contrast text exceeding WCAG 2.1 AA standards (minimum 4.5:1 contrast ratio for normal text).
  - Explicit `aria-label`, `aria-expanded`, and `aria-hidden` attributes on interactive elements.
  - Accessible SVG charts with descriptive text fallbacks.
