# AISMM Core Architecture Design

## Overview
This document defines the high-level architecture for AISMM — a universal, platform-agnostic AI-powered social media management system.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AISMM WEB DASHBOARD (Frontend)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Overview   │ │  Platforms  │ │ Create Post │ │ AI Optimize │  ...     │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │  Content Mgmt   │ │   AI Engine     │ │  Analytics      │
        │   Service       │ │   Service       │ │  Service        │
        └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                 │                   │                   │
                 └───────────────────┼───────────────────┘
                                     ▼
                    ┌─────────────────────────────────┐
                    │      PLATFORM REGISTRY          │
                    │  (Central adapter discovery)    │
                    └─────────────────┬───────────────┘
                                      │
         ┌──────────────┬─────────────┼─────────────┬──────────────┐
         ▼              ▼             ▼             ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Instagram   │ │   Facebook   │ │      X       │ │  LinkedIn    │ │   YouTube    │
│   Adapter    │ │   Adapter    │ │   Adapter    │ │   Adapter    │ │   Adapter    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │                │
       ▼                ▼                ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Instagram    │ │ Facebook     │ │ X (Twitter)  │ │ LinkedIn     │ │ YouTube      │
│ Graph API    │ │ Graph API    │ │ API v2       │ │ API v2       │ │ Data API v3  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 2. Layered Architecture (Separation of Concerns)

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                           │
│  React/Vue + TypeScript | Dynamic UI | Capability-driven       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                             │
│  REST/GraphQL | Auth Middleware | Rate Limiting | Validation   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION SERVICES LAYER                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │  Content    │ │   Scheduling│ │  Sentiment  │ │  Growth  │  │
│  │  Service    │ │  Service    │ │  Service    │ │ Service  │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │  Auto-Reply │ │ Caption/    │ │Recommendation│ │Analytics │  │
│  │  Service    │ │ Hashtag Svc │ │  Service    │ │ Service  │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOMAIN / CORE LAYER                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │  Post       │ │  Social     │ │  Universal  │ │  Event   │  │
│  │  Entity     │ │  Account    │ │  Content    │ │  Bus     │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │  Metric     │ │  Comment    │ │  Schedule   │ │ Capability│  │
│  │  Entity     │ │  Entity     │ │  Entity     │ │  Registry│  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AI ENGINE LAYER                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │ Scheduling  │ │  Sentiment  │ │  Engagement │ │ Growth   │  │
│  │  Engine     │ │  Engine     │ │ Prediction  │ │ Engine   │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐  │
│  │Auto-Reply   │ │  Caption    │ │  Hashtag    │ │Recommend.│  │
│  │  Engine     │ │  Engine     │ │  Engine     │ │ Engine   │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘  │
│  All engines consume NORMALIZED data only                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PLATFORM ADAPTER LAYER                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    BasePlatformAdapter                   │    │
│  │  authenticate() | publish() | fetch_comments() | ...     │    │
│  │  supports(capability) | get_capabilities()               │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐  │
│  │Instagram │ │ Facebook │ │    X     │ │ LinkedIn │ │YouTube│  │
│  │ Adapter  │ │ Adapter  │ │ Adapter  │ │ Adapter  │ │Adapter│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────┘  │
│  Each adapter: auth.py, publisher.py, analytics.py, comments.py, │
│  mapper.py (UniversalContent → PlatformSpecificPayload)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL PLATFORM APIs                      │
│  Instagram Graph API | Facebook Graph API | X API v2           │
│  LinkedIn API v2 | YouTube Data API v3 | Future platforms      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Architecture

### 3.1 Post Creation Flow
```
User Input
    │
    ▼
PostComposer (Frontend) → UniversalContent
    │
    ▼
Content Service → Validate & Store Post Entity
    │
    ▼
AI Optimize (Optional) → CaptionEngine + HashtagEngine → Platform Variants
    │
    ▼
User Selects Platforms → PlatformContentStrategy per platform
    │
    ▼
Schedule Service → Scheduling Engine → Optimal Time (or user time)
    │
    ▼
Platform Adapter (per selected platform)
    │
    ├─► mapper.py: UniversalContent → PlatformSpecificPayload
    ├─► upload_media() → Media IDs
    └─► publish_post() / schedule_post() → Platform Post ID
    │
    ▼
Store PostPublication records (per platform)
    │
    ▼
Event: PostPublished → Event Bus → Analytics Service → Notification Engine
```

### 3.2 Post-Posting Intelligence Flow
```
Platform Webhook / Scheduled Sync
    │
    ▼
Event Gateway → Event Normalizer → Event Bus
    │
    ├─► CommentReceived → Comment Service → Store NormalizedComment
    │                     │
    │                     ▼
    │              Sentiment Engine (PostPostAnalyzer)
    │                     │
    │                     ▼
    │              Auto-Reply Engine (if confidence ≥ threshold)
    │                     │
    │                     ▼
    │              PlatformAdapter.reply() → Platform API
    │
    ├─► EngagementUpdated → Analytics Service → Update Metrics
    │                     │
    │                     ▼
    │              Growth Engine (retrain trigger)
    │
    └─► SentimentCalculated → Notification Engine (if NEGATIVE_SENTIMENT)
```

### 3.3 Scheduled Publishing Flow
```
Scheduler (Cron/Queue)
    │
    ▼
ScheduleTriggered Event → Event Bus
    │
    ▼
Publishing Service → PlatformAdapter.publish_post()
    │
    ├─► Success → PostPublished Event → Update PostPublication
    │
    └─► Failure → PlatformError → Retry with exponential backoff
                   │
                   └─► Max retries → NOTIFICATION: PLATFORM_ERROR
```

---

## 4. Component Specifications

### 4.1 Platform Registry
```python
class PlatformRegistry:
    """Central registry for platform adapter discovery and management."""
    
    def register(platform_id: str, adapter_class: Type[BasePlatformAdapter]) -> None
    def get(platform_id: str) -> BasePlatformAdapter
    def get_all() -> List[BasePlatformAdapter]
    def get_capabilities(platform_id: str) -> PlatformCapabilities
    def supports(platform_id: str, capability: str) -> bool
    def discover_platforms() -> List[PlatformMetadata]
```

### 4.2 Base Platform Adapter Contract
```python
class BasePlatformAdapter(ABC):
    """Abstract base class all platform adapters must implement."""
    
    # Authentication
    @abstractmethod
    async def authenticate(self, credentials: Dict) -> AuthResult
    @abstractmethod
    async def refresh_token(self) -> AuthResult
    @abstractmethod
    async def disconnect(self) -> bool
    @abstractmethod
    async def validate_credentials(self) -> bool
    
    # Publishing
    @abstractmethod
    async def validate_content(self, content: UniversalContent) -> ValidationResult
    @abstractmethod
    async def upload_media(self, media: MediaItem) -> MediaUploadResult
    @abstractmethod
    async def publish_post(self, payload: PlatformSpecificPayload) -> PublishResult
    @abstractmethod
    async def schedule_post(self, payload: PlatformSpecificPayload, 
                           scheduled_at: datetime) -> ScheduleResult
    @abstractmethod
    async def update_post(self, publication_id: str, payload: PlatformSpecificPayload) -> bool
    @abstractmethod
    async def delete_post(self, publication_id: str) -> bool
    
    # Content Fetching
    @abstractmethod
    async def fetch_posts(self, account_id: str, limit: int) -> List[NormalizedPost]
    @abstractmethod
    async def fetch_comments(self, publication_id: str) -> List[NormalizedComment]
    @abstractmethod
    async def fetch_replies(self, comment_id: str) -> List[NormalizedComment]
    
    # Engagement
    @abstractmethod
    async def reply_to_comment(self, comment_id: str, text: str) -> ReplyResult
    @abstractmethod
    async def fetch_engagement(self, publication_id: str) -> NormalizedEngagement
    @abstractmethod
    async def fetch_account_metrics(self, account_id: str) -> NormalizedAccountMetrics
    @abstractmethod
    async def fetch_post_analytics(self, publication_id: str) -> NormalizedPostAnalytics
    
    # Webhooks
    @abstractmethod
    async def register_webhook(self, url: str, events: List[str]) -> WebhookRegistration
    @abstractmethod
    async def handle_webhook(self, payload: Dict, signature: str) -> List[NormalizedEvent]
    
    # Capabilities
    @abstractmethod
    def get_capabilities(self) -> PlatformCapabilities
    @abstractmethod
    def supports(self, capability: str) -> bool
```

### 4.3 Universal Data Models

```python
# Core entities (platform-neutral)
class User:
    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

class SocialAccount:
    id: UUID
    user_id: UUID
    platform_id: str          # "instagram", "facebook", "x", "linkedin", "youtube"
    platform_account_id: str  # Platform's native user ID
    account_name: str
    account_username: str
    access_token_ref: str     # Reference to secure credential store
    refresh_token_ref: str    # Reference to secure credential store
    status: AccountStatus     # CONNECTED, DISCONNECTED, ERROR, TOKEN_EXPIRED
    capabilities: PlatformCapabilities
    last_synced_at: datetime
    created_at: datetime
    updated_at: datetime

class Post:
    id: UUID
    user_id: UUID
    content: str              # Main text content
    caption: str              # AI-optimized caption
    status: PostStatus        # DRAFT, SCHEDULED, PUBLISHING, PUBLISHED, FAILED
    created_at: datetime
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    media: List[MediaItem]
    metadata: Dict            # Platform-specific customizations

class PostPublication:
    id: UUID
    post_id: UUID
    social_account_id: UUID
    platform_id: str
    platform_post_id: str     # Platform's native post ID
    status: PublicationStatus
    platform_payload: Dict    # Exact payload sent to platform
    error_message: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime

class UniversalContent:
    """Platform-neutral content representation."""
    text: str
    caption: str
    title: Optional[str]
    media: List[MediaItem]
    hashtags: List[str]
    mentions: List[str]
    links: List[str]
    location: Optional[str]
    language: str
    content_type: ContentType  # POST, STORY, REEL, SHORT, ARTICLE, VIDEO
    metadata: Dict

class NormalizedEngagement:
    """Platform-normalized engagement metrics."""
    metric_type: MetricType    # LIKE, COMMENT, SHARE, REACTION, VIEW, SAVE, CLICK
    value: int
    source_platform: str
    original_metric: str       # e.g., "retweet_count", "reaction_count"
    timestamp: datetime

class NormalizedPost:
    """Platform-normalized post representation."""
    platform_post_id: str
    platform_id: str
    content: str
    caption: str
    media_type: MediaType
    posted_at: datetime
    engagement: NormalizedEngagement
    engagement_score: float    # Platform-aware engagement score
```

---

## 5. AI Engine Architecture

### 5.1 Engine Interface
```python
class BaseAIEngine(ABC):
    """Base interface for all AI engines."""
    
    @abstractmethod
    async def predict(self, input_data: NormalizedInput) -> PredictionResult
    
    @abstractmethod
    async def train(self, training_data: TrainingDataset) -> ModelArtifact
    
    @abstractmethod
    def get_model_version(self) -> str
    
    @abstractmethod
    def get_model_metadata(self) -> ModelMetadata
```

### 5.2 Engine Specifications

| Engine | Input | Output | Model | Config |
|--------|-------|--------|-------|--------|
| **Scheduling** | Historical posts, engagement, time features | Optimal posting times per platform | RandomForest + XGBoost (hard voting) | scheduler_config |
| **Sentiment (Pre)** | UniversalContent | SentimentScore (-1 to 1) + Label | VADER + k-NN (k=5) | sentiment_config |
| **Sentiment (Post)** | NormalizedComment[] | TemporalSentiment + Aggregation | VADER + k-NN + TemporalAnalyzer | sentiment_config |
| **Engagement Prediction** | Post features + platform + time | Predicted engagement score | RandomForest Regressor | engagement_config |
| **Growth** | Platform account metrics history | Follower growth prediction (R²) | RandomForest Regressor (per platform) | growth_config |
| **Auto-Reply** | NormalizedComment | ReplyResponse + Confidence | TF-IDF + LogisticRegression | reply_config |
| **Caption** | UniversalContent + platform | Optimized caption + quality score | Statistical/Template (LLM-ready) | caption_config |
| **Hashtag** | Post content + platform + history | Top-K hashtags + performance | Frequency + ML (embedding-ready) | hashtag_config |
| **Recommendation** | All engine outputs | Recommendation[] with reason/confidence | Ensemble of all engines | recommendation_config |

### 5.3 Model Registry
```python
class ModelRegistry:
    """Versioned model management with lifecycle states."""
    
    # Model lifecycle: DEVELOPMENT → STAGING → PRODUCTION → DEPRECATED
    def register(model: ModelArtifact, version: str, stage: ModelStage) -> ModelRecord
    def get_production(model_type: str, platform: Optional[str]) -> ModelArtifact
    def promote(version: str, from_stage: ModelStage, to_stage: ModelStage) -> bool
    def record_performance(model_id: str, metrics: Dict, dataset_version: str) -> None
    def detect_drift(model_id: str, current_metrics: Dict) -> DriftReport
```

---

## 6. Database Architecture

### 6.1 Entity Relationship Diagram
```
┌─────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    User     │───────│  SocialAccount   │───────│  PostPublication │
└─────────────┘       └──────────────────┘       └──────────────────┘
                              │                           │
                              │                           │
                    ┌─────────┴─────────┐       ┌────────┴────────┐
                    │                   │       │                 │
              ┌─────────┐         ┌─────────┐ ┌─────────┐   ┌─────────┐
              │ Platform│         │ Platform│ │ Platform│   │ Platform│
              │Capabilities     │   │  Config   │   │Analytics    │
              └─────────┘         └─────────┘ └─────────┘   └─────────┘

┌─────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    Post     │───────│    MediaItem     │       │  PostVariation   │
└─────────────┘       └──────────────────┘       └──────────────────┘
                              │                           │
                              │                           │
                    ┌─────────┴─────────┐       ┌────────┴────────┐
                    │                   │       │                 │
              ┌─────────┐         ┌─────────┐ ┌─────────┐   ┌─────────┐
              │Normalized│        │  Raw     │   │  AI      │   │ Schedule│
              │Comment   │        │  Platform │   │  Results │   │ Record  │
              │          │        │  Data     │   │          │   │         │
              └─────────┘         └─────────┘ └─────────┘   └─────────┘

┌─────────────┐       ┌──────────────────┐
│  Schedule   │───────│  Notification    │
└─────────────┘       └──────────────────┘
```

### 6.2 Key Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Social Accounts
CREATE TABLE social_accounts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    platform_id VARCHAR(50) NOT NULL,
    platform_account_id VARCHAR(255) NOT NULL,
    account_name VARCHAR(255),
    account_username VARCHAR(255),
    access_token_ref VARCHAR(500),  -- Encrypted reference
    refresh_token_ref VARCHAR(500), -- Encrypted reference
    status VARCHAR(50) DEFAULT 'CONNECTED',
    capabilities JSONB,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, platform_id, platform_account_id)
);

-- Posts (Universal)
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    caption TEXT,
    status VARCHAR(50) DEFAULT 'DRAFT',
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    media JSONB,           -- Array of media items
    metadata JSONB,        -- Platform-specific customizations
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Post Publications (Per-platform)
CREATE TABLE post_publications (
    id UUID PRIMARY KEY,
    post_id UUID REFERENCES posts(id),
    social_account_id UUID REFERENCES social_accounts(id),
    platform_id VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'PENDING',
    platform_payload JSONB,
    error_message TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Normalized Metrics
CREATE TABLE normalized_metrics (
    id UUID PRIMARY KEY,
    social_account_id UUID REFERENCES social_accounts(id),
    post_publication_id UUID REFERENCES post_publications(id),
    metric_type VARCHAR(50) NOT NULL,  -- LIKE, COMMENT, SHARE, REACTION, VIEW, SAVE, CLICK
    value BIGINT NOT NULL,
    source_platform VARCHAR(50) NOT NULL,
    original_metric VARCHAR(100),      -- Platform-native metric name
    timestamp TIMESTAMP NOT NULL
);

-- Normalized Comments
CREATE TABLE normalized_comments (
    id UUID PRIMARY KEY,
    social_account_id UUID REFERENCES social_accounts(id),
    post_publication_id UUID REFERENCES post_publications(id),
    platform_comment_id VARCHAR(255),
    author_username VARCHAR(255),
    author_id VARCHAR(255),
    text TEXT NOT NULL,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(50),
    parent_comment_id UUID,  -- For replies
    created_at TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP DEFAULT NOW()
);

-- AI Model Registry
CREATE TABLE model_registry (
    id UUID PRIMARY KEY,
    model_type VARCHAR(50) NOT NULL,  -- scheduling, sentiment, growth, etc.
    platform_id VARCHAR(50),          -- NULL for universal models
    version VARCHAR(50) NOT NULL,
    stage VARCHAR(50) NOT NULL,       -- DEVELOPMENT, STAGING, PRODUCTION, DEPRECATED
    model_path VARCHAR(500),          -- Path to serialized model
    dataset_version VARCHAR(50),
    feature_version VARCHAR(50),
    training_date TIMESTAMP,
    metrics JSONB,                    -- Accuracy, R², RMSE, etc.
    hyperparameters JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Schedules
CREATE TABLE schedules (
    id UUID PRIMARY KEY,
    post_id UUID REFERENCES posts(id),
    social_account_id UUID REFERENCES social_accounts(id),
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',  -- PENDING, TRIGGERED, PUBLISHED, FAILED, CANCELLED
    retry_count INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Events (Event sourcing / audit log)
CREATE TABLE events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,  -- Post ID, Account ID, etc.
    aggregate_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 7. Event Architecture

### 7.1 Normalized Internal Events
```python
class EventType(Enum):
    # Post lifecycle
    POST_CREATED = "post_created"
    POST_UPDATED = "post_updated"
    POST_DELETED = "post_deleted"
    POST_PUBLISHED = "post_published"
    POST_SCHEDULED = "post_scheduled"
    POST_PUBLISH_FAILED = "post_publish_failed"
    
    # Scheduling
    SCHEDULE_CREATED = "schedule_created"
    SCHEDULE_TRIGGERED = "schedule_triggered"
    SCHEDULE_CANCELLED = "schedule_cancelled"
    
    # Engagement
    COMMENT_RECEIVED = "comment_received"
    REPLY_RECEIVED = "reply_received"
    ENGAGEMENT_UPDATED = "engagement_updated"
    
    # AI
    SENTIMENT_CALCULATED = "sentiment_calculated"
    PREDICTION_GENERATED = "prediction_generated"
    RECOMMENDATION_CREATED = "recommendation_created"
    
    # Platform
    PLATFORM_CONNECTED = "platform_connected"
    PLATFORM_DISCONNECTED = "platform_disconnected"
    TOKEN_EXPIRING = "token_expiring"
    PLATFORM_ERROR = "platform_error"
    
    # Alerts
    HIGH_ENGAGEMENT = "high_engagement"
    LOW_ENGAGEMENT = "low_engagement"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    REPLY_REQUIRED = "reply_required"
    GROWTH_ALERT = "growth_alert"
    MODEL_ALERT = "model_alert"

class NormalizedEvent:
    event_type: EventType
    aggregate_id: UUID
    aggregate_type: str
    payload: Dict
    metadata: Dict
    timestamp: datetime
    source_platform: Optional[str]
```

### 7.2 Event Bus
```python
class EventBus:
    """In-memory / distributed event bus for decoupled communication."""
    
    def publish(event: NormalizedEvent) -> None
    def subscribe(event_type: EventType, handler: Callable) -> Subscription
    def unsubscribe(subscription: Subscription) -> None
    
    # Handlers are async, errors logged but don't block other handlers
```

---

## 8. Frontend Architecture

### 8.1 Component Hierarchy
```
App
├── Layout
│   ├── Header (PlatformSelector, UserMenu, Notifications)
│   ├── Sidebar (Navigation: Overview, Platforms, Create, Calendar, Analytics, Settings)
│   └── Main Content Area
│
├── Pages
│   ├── DashboardOverview
│   ├── PlatformsPage (Connection status, capabilities grid)
│   ├── CreatePostPage
│   │   ├── PostComposer
│   │   │   ├── CaptionEditor (with AI suggestions)
│   │   │   ├── HashtagSelector (with AI recommendations)
│   │   │   ├── MediaUploader (drag-drop, preview)
│   │   │   └── PlatformSelector (checkboxes, capability-aware)
│   │   ├── PlatformCustomizationTabs (per-platform preview)
│   │   └── SchedulePicker (Immediate | Scheduled | AI Recommended | AI + Constraints)
│   │
│   ├── CalendarPage (Month/Week/Day view with scheduled posts)
│   ├── ScheduledPostsPage (List with filters, actions)
│   ├── PublishedPostsPage (List with engagement preview)
│   ├── CommentsPage (Unified comment inbox with sentiment badges)
│   ├── AutoReplyPage (Rules, confidence thresholds, approval queue)
│   ├── SentimentPage (Pre/Post sentiment trends, temporal analysis)
│   ├── AnalyticsPage
│   │   ├── OverviewTab
│   │   ├── ContentTab
│   │   ├── TimeTab
│   │   ├── SentimentTab
│   │   ├── GrowthTab
│   │   └── ComparisonTab
│   ├── GrowthPredictionPage (Charts: actual vs predicted per platform)
│   ├── AIRecommendationsPage (Priority cards with reasons)
│   ├── NotificationsPage (In-app notification center)
│   ├── ModelsPage (Model registry, performance, drift)
│   └── SettingsPage (Account, Platforms, AI Config, Notifications)
│
└── Shared Components (Capability-driven rendering)
    ├── PlatformSelector
    ├── PostComposer
    ├── MediaUploader
    ├── CaptionEditor
    ├── HashtagSelector
    ├── SchedulePicker
    ├── SentimentPanel
    ├── AnalyticsPanel
    ├── CommentPanel
    ├── ReplyPanel
    ├── GrowthChart
    ├── RecommendationPanel
    └── PlatformStatus
```

### 8.2 Dynamic UI via Capabilities
```typescript
// Frontend queries backend for platform capabilities
interface PlatformCapabilities {
  publishing: boolean;
  scheduling: boolean;
  text_post: boolean;
  image_post: boolean;
  video_post: boolean;
  carousel_post: boolean;
  stories: boolean;
  short_video: boolean;
  comments: boolean;
  replies: boolean;
  analytics: boolean;
  audience_metrics: boolean;
  webhooks: boolean;
  direct_messages: boolean;
  hashtags: boolean;
  mentions: boolean;
  limits: {
    text_length: number;
    hashtag_count: number;
    media_count: number;
    video_duration_seconds: number;
  };
}

// UI renders conditionally:
function PostComposer({ platformId }) {
  const caps = useCapabilities(platformId);
  
  return (
    <div>
      {caps.text_post && <CaptionEditor />}
      {caps.hashtags && <HashtagSelector />}
      {caps.image_post && <MediaUploader accept="image/*" />}
      {caps.video_post && <MediaUploader accept="video/*" />}
      {caps.carousel_post && <CarouselBuilder />}
      {caps.scheduling && <SchedulePicker />}
      {!caps.scheduling && <SchedulerUnavailableNotice />}
    </div>
  );
}
```

---

## 9. Security Architecture

### 9.1 Authentication & Authorization
```
┌────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                      │
│                                                             │
│  User → Login (email/password) → JWT Access + Refresh     │
│         │                                                   │
│         ▼                                                   │
│  Platform OAuth → Platform Auth Server → Auth Code         │
│         │                                                   │
│         ▼                                                   │
│  Token Exchange → Access Token + Refresh Token             │
│         │                                                   │
│         ▼                                                   │
│  Secure Credential Store (Encrypted)                       │
│         │                                                   │
│         ▼                                                   │
│  Platform Adapter uses tokens from secure store            │
└────────────────────────────────────────────────────────────┘
```

### 9.2 Security Measures
| Layer | Measure |
|-------|---------|
| **Transport** | TLS 1.3 everywhere, HSTS, secure cookies |
| **Auth** | JWT with short expiry (15min), refresh token rotation, OAuth 2.0 PKCE |
| **Secrets** | Encrypted at rest (AES-256), never in logs, env vars for config |
| **API** | Rate limiting per user/IP, input validation, CORS policy |
| **Database** | Parameterized queries, row-level security, audit logging |
| **Platform Tokens** | Encrypted storage, automatic refresh, scope minimization |
| **Audit** | All admin actions, token access, config changes logged |

---

## 10. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION                                │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   CDN/      │    │   Load      │    │   WAF       │         │
│  │   Edge      │───►│   Balancer  │───►│   (Rate     │         │
│  │   Cache     │    │   (ALB)     │    │   Limit)    │         │
│  └─────────────┘    └──────┬──────┘    └─────────────┘         │
│                            │                                      │
│         ┌──────────────────┼──────────────────┐                  │
│         ▼                  ▼                  ▼                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Frontend   │    │   API       │    │  Worker     │         │
│  │  (Static)   │    │  (FastAPI/  │    │  (Celery/   │         │
│  │  S3+Cloud   │    │   Express)  │    │   Dramatiq) │         │
│  └─────────────┘    └──────┬──────┘    └─────────────┘         │
│                            │                                      │
│         ┌──────────────────┼──────────────────┐                  │
│         ▼                  ▼                  ▼                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ PostgreSQL  │    │   Redis     │    │  Object     │         │
│  │  (Primary)  │    │  (Cache/    │    │  Storage    │         │
│  │  + Replica  │    │   Queue)    │    │  (Media)    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   MLflow    │    │ Prometheus  │    │   Grafana   │         │
│  │  (Models)   │    │  (Metrics)  │    │  (Dashboards)│         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Configuration Architecture

```yaml
# config/platforms.yaml
platforms:
  instagram:
    enabled: true
    api_version: "v18.0"
    auth:
      type: "oauth2"
      scopes: ["instagram_basic", "instagram_content_publish", "pages_show_list"]
    capabilities:
      publishing: true
      scheduling: true
      text_post: true
      image_post: true
      video_post: true
      carousel_post: true
      stories: true
      short_video: true
      comments: true
      replies: true
      analytics: true
      audience_metrics: true
      webhooks: true
      hashtags: true
      mentions: true
    limits:
      text_length: 2200
      hashtag_count: 30
      media_count: 10
      video_duration_seconds: 3600
    rate_limits:
      requests_per_hour: 200
      burst: 50
  
  linkedin:
    enabled: true
    api_version: "v2"
    auth:
      type: "oauth2"
      scopes: ["w_member_social", "r_organization_social"]
    capabilities:
      publishing: true
      scheduling: false  # Native scheduling not available
      text_post: true
      image_post: true
      video_post: true
      carousel_post: false
      stories: false
      short_video: false
      comments: true
      replies: true
      analytics: true
      audience_metrics: true
      webhooks: false
      hashtags: true
      mentions: true
    limits:
      text_length: 3000
      hashtag_count: 10
      media_count: 9
    rate_limits:
      requests_per_day: 100000
```

---

## 12. Technology Stack Recommendations

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | React 18 + TypeScript + Vite | Modern, typed, great ecosystem |
| **UI Library** | Radix UI + Tailwind CSS | Accessible, customizable, capability-driven |
| **State** | TanStack Query + Zustand | Server state + client state |
| **Backend** | FastAPI (Python) | Async, type hints, OpenAPI, ML ecosystem |
| **Database** | PostgreSQL 15+ | JSONB, full-text, ACID, mature |
| **ORM** | SQLAlchemy 2.0 + Alembic | Async, typed, migrations |
| **Cache/Queue** | Redis + Celery | Distributed task queue, caching |
| **ML** | scikit-learn + XGBoost + MLflow | Research-aligned, versioned models |
| **Auth** | python-jose + passlib + OAuthlib | JWT, OAuth 2.0, secure |
| **Monitoring** | Prometheus + Grafana + Sentry | Metrics, dashboards, error tracking |
| **Deploy** | Docker + Kubernetes (or Fly.io/Railway) | Containerized, scalable |
| **CI/CD** | GitHub Actions | Integrated, free for public |

---

## 13. Architecture Decision Records (ADRs)

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Platform-agnostic adapter pattern | ✅ Accepted |
| ADR-002 | Capability-based platform system | ✅ Accepted |
| ADR-003 | Universal data models with platform-specific publications | ✅ Accepted |
| ADR-004 | AI engines consume normalized data only | ✅ Accepted |
| ADR-005 | Event-driven architecture for post-posting intelligence | ✅ Accepted |
| ADR-006 | Configuration-driven platform definitions | ✅ Accepted |
| ADR-007 | Model registry with lifecycle stages | ✅ Accepted |
| ADR-008 | Mock platform adapter for testing | ✅ Accepted |
| ADR-009 | Frontend renders dynamically from capabilities | ✅ Accepted |
| ADR-010 | Secure credential store for platform tokens | ✅ Accepted |

---

## 14. Next Steps

1. **Review & Approve** this architecture design
2. **Phase 3** — Core Foundation Implementation:
   - Configuration system
   - Database models & migrations
   - Authentication system
   - Logging & error handling
   - Platform registry & base adapter
   - Capability system
   - Universal data models
3. **Phase 4** — First Platform (Instagram) Implementation

---

*Document Version: 1.0*  
*Created: 2026-08-25*  
*Status: DRAFT — Awaiting Review*
