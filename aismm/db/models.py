"""
AISMM Database Models

Universal, platform-agnostic data models following the architecture:
- User: Core user entity
- SocialAccount: Connected platform accounts
- Post: Universal post content
- PostPublication: Per-platform publication records
- NormalizedMetric: Unified engagement metrics
- NormalizedComment: Unified comments/replies
- Schedule: Post scheduling records
- ModelRegistry: ML model versioning
- Event: Event sourcing / audit log
"""

import enum
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum,
    JSON, BigInteger, Index, UniqueConstraint, Boolean, Integer
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AccountStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TOKEN_EXPIRED = "token_expired"
    PENDING = "pending"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PublicationStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class ScheduleStatus(str, enum.Enum):
    PENDING = "pending"
    TRIGGERED = "triggered"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricType(str, enum.Enum):
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    REACTION = "reaction"
    VIEW = "view"
    SAVE = "save"
    CLICK = "click"
    IMPRESSION = "impression"
    REACH = "reach"
    FOLLOWER = "follower"
    WATCH_TIME = "watch_time"


class ContentType(str, enum.Enum):
    POST = "post"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    ARTICLE = "article"
    VIDEO = "video"
    CAROUSEL = "carousel"


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"
    DOCUMENT = "document"
    AUDIO = "audio"


class ModelStage(str, enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


class User(Base):
    """Core user entity."""
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class SocialAccount(Base):
    """Connected social media account."""
    __tablename__ = "social_accounts"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_id = Column(String(50), nullable=False, index=True)  # instagram, facebook, x, linkedin, youtube
    platform_account_id = Column(String(255), nullable=False, index=True)
    account_name = Column(String(255))
    account_username = Column(String(255), index=True)
    access_token_ref = Column(String(500))  # Encrypted reference to credential store
    refresh_token_ref = Column(String(500))  # Encrypted reference to credential store
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.PENDING, nullable=False)
    capabilities = Column(JSON, default=dict)  # Platform capabilities snapshot
    platform_config = Column(JSON, default=dict)  # Platform-specific config
    last_synced_at = Column(DateTime)
    last_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="social_accounts")
    post_publications = relationship("PostPublication", back_populates="social_account", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="social_account", cascade="all, delete-orphan")
    metrics = relationship("NormalizedMetric", back_populates="social_account", cascade="all, delete-orphan")
    comments = relationship("NormalizedComment", back_populates="social_account", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("user_id", "platform_id", "platform_account_id", name="uq_user_platform_account"),
        Index("ix_social_accounts_user_platform", "user_id", "platform_id"),
    )
    
    def __repr__(self):
        return f"<SocialAccount(id={self.id}, platform={self.platform_id}, username={self.account_username})>"


class Post(Base):
    """Universal post content - platform-neutral."""
    __tablename__ = "posts"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Main text content
    caption = Column(Text)  # AI-optimized caption
    status = Column(SQLEnum(PostStatus), default=PostStatus.DRAFT, nullable=False, index=True)
    scheduled_at = Column(DateTime, index=True)
    published_at = Column(DateTime)
    content_type = Column(SQLEnum(ContentType), default=ContentType.POST)
    media = Column(JSON, default=list)  # List of media items
    metadata = Column(JSON, default=dict)  # Platform-specific customizations
    ai_analysis = Column(JSON, default=dict)  # AI engine results (sentiment, hashtags, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    publications = relationship("PostPublication", back_populates="post", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="post", cascade="all, delete-orphan")
    variations = relationship("PostVariation", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post(id={self.id}, status={self.status}, content_preview={self.content[:50]})>"


class PostPublication(Base):
    """Per-platform publication record."""
    __tablename__ = "post_publications"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    post_id = Column(PG_UUID(as_uuid=False), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    social_account_id = Column(PG_UUID(as_uuid=False), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_id = Column(String(50), nullable=False, index=True)
    platform_post_id = Column(String(255), index=True)
    status = Column(SQLEnum(PublicationStatus), default=PublicationStatus.PENDING, nullable=False)
    platform_payload = Column(JSON, default=dict)  # Exact payload sent to platform
    platform_response = Column(JSON, default=dict)  # Raw platform API response
    error_message = Column(Text)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="publications")
    social_account = relationship("SocialAccount", back_populates="post_publications")
    metrics = relationship("NormalizedMetric", back_populates="publication", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("social_account_id", "platform_post_id", name="uq_account_platform_post"),
    )
    
    def __repr__(self):
        return f"<PostPublication(id={self.id}, platform={self.platform_id}, status={self.status})>"


class PostVariation(Base):
    """Platform-specific post variation for cross-platform customization."""
    __tablename__ = "post_variations"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    post_id = Column(PG_UUID(as_uuid=False), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_id = Column(String(50), nullable=False, index=True)
    content = Column(Text)
    caption = Column(Text)
    hashtags = Column(JSON, default=list)
    media = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="variations")
    
    __table_args__ = (
        UniqueConstraint("post_id", "platform_id", name="uq_post_platform_variation"),
    )
    
    def __repr__(self):
        return f"<PostVariation(post_id={self.post_id}, platform={self.platform_id})>"


class MediaItem(Base):
    """Media attached to posts."""
    __tablename__ = "media_items"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    post_id = Column(PG_UUID(as_uuid=False), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(SQLEnum(MediaType), nullable=False)
    file_path = Column(String(500))  # Local path or S3 key
    url = Column(String(1000))  # Public URL after upload
    thumbnail_url = Column(String(1000))
    width = Column(Integer)
    height = Column(Integer)
    duration_seconds = Column(Integer)  # For video
    file_size_bytes = Column(BigInteger)
    mime_type = Column(String(100))
    platform_media_ids = Column(JSON, default=dict)  # Platform-specific media IDs after upload
    alt_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MediaItem(id={self.id}, type={self.media_type}, post_id={self.post_id})>"


class NormalizedMetric(Base):
    """Platform-normalized engagement metric."""
    __tablename__ = "normalized_metrics"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    social_account_id = Column(PG_UUID(as_uuid=False), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    publication_id = Column(PG_UUID(as_uuid=False), ForeignKey("post_publications.id", ondelete="SET NULL"), index=True)
    metric_type = Column(SQLEnum(MetricType), nullable=False, index=True)
    value = Column(BigInteger, nullable=False)
    source_platform = Column(String(50), nullable=False)
    original_metric = Column(String(100))  # Platform-native metric name (e.g., "retweet_count")
    period_start = Column(DateTime)  # For aggregated metrics
    period_end = Column(DateTime)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    social_account = relationship("SocialAccount", back_populates="metrics")
    publication = relationship("PostPublication", back_populates="metrics")
    
    __table_args__ = (
        Index("ix_metrics_account_type_time", "social_account_id", "metric_type", "timestamp"),
        Index("ix_metrics_publication_type", "publication_id", "metric_type"),
    )
    
    def __repr__(self):
        return f"<NormalizedMetric(type={self.metric_type}, value={self.value}, platform={self.source_platform})>"


class NormalizedComment(Base):
    """Platform-normalized comment/reply."""
    __tablename__ = "normalized_comments"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    social_account_id = Column(PG_UUID(as_uuid=False), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    publication_id = Column(PG_UUID(as_uuid=False), ForeignKey("post_publications.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_comment_id = Column(String(255), nullable=False, index=True)
    parent_comment_id = Column(PG_UUID(as_uuid=False), ForeignKey("normalized_comments.id"), index=True)
    author_username = Column(String(255))
    author_id = Column(String(255))
    author_avatar_url = Column(String(500))
    text = Column(Text, nullable=False)
    sentiment_score = Column(Integer)  # -100 to 100 (VADER * 100)
    sentiment_label = Column(String(50))  # very_positive, positive, neutral, negative, very_negative
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    is_reply = Column(Boolean, default=False)
    platform_created_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    replied_at = Column(DateTime)  # When we replied
    reply_text = Column(Text)  # Our reply text
    
    # Relationships
    social_account = relationship("SocialAccount", back_populates="comments")
    publication = relationship("PostPublication", backref="comments")
    replies = relationship("NormalizedComment", backref="parent", remote_side=[id])
    
    __table_args__ = (
        UniqueConstraint("social_account_id", "platform_comment_id", name="uq_account_platform_comment"),
        Index("ix_comments_publication_sentiment", "publication_id", "sentiment_label"),
    )
    
    def __repr__(self):
        return f"<NormalizedComment(id={self.id}, platform={self.social_account.platform_id}, sentiment={self.sentiment_label})>"


class Schedule(Base):
    """Post scheduling record."""
    __tablename__ = "schedules"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    post_id = Column(PG_UUID(as_uuid=False), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    social_account_id = Column(PG_UUID(as_uuid=False), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(SQLEnum(ScheduleStatus), default=ScheduleStatus.PENDING, nullable=False)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    triggered_at = Column(DateTime)
    published_at = Column(DateTime)
    platform_schedule_id = Column(String(255))  # Platform's native schedule ID
    metadata = Column(JSON, default=dict)  # AI recommendation, user constraints, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="schedules")
    social_account = relationship("SocialAccount", back_populates="schedules")
    
    __table_args__ = (
        Index("ix_schedules_account_status_time", "social_account_id", "status", "scheduled_at"),
    )
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, post_id={self.post_id}, scheduled_at={self.scheduled_at}, status={self.status})>"


class ModelRegistry(Base):
    """ML model version registry."""
    __tablename__ = "model_registry"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    engine_type = Column(String(50), nullable=False, index=True)  # scheduling, sentiment, growth, etc.
    platform = Column(String(50), index=True)  # NULL for universal models
    version = Column(String(50), nullable=False)
    stage = Column(SQLEnum(ModelStage), default=ModelStage.DEVELOPMENT, nullable=False)
    model_path = Column(String(500))  # Path to serialized model
    dataset_version = Column(String(50))
    feature_version = Column(String(50))
    training_date = Column(DateTime)
    metrics = Column(JSON, default=dict)  # accuracy, R², RMSE, F1, etc.
    hyperparameters = Column(JSON, default=dict)
    description = Column(Text)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    promoted_at = Column(DateTime)
    deprecated_at = Column(DateTime)
    
    __table_args__ = (
        UniqueConstraint("engine_type", "platform", "version", name="uq_model_version"),
        Index("ix_model_registry_engine_stage", "engine_type", "stage"),
    )
    
    def __repr__(self):
        return f"<ModelRegistry({self.engine_type}/{self.platform}:{self.version} [{self.stage}])>"


class Event(Base):
    """Event sourcing / audit log for all significant actions."""
    __tablename__ = "events"
    
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    event_type = Column(String(100), nullable=False, index=True)
    aggregate_id = Column(PG_UUID(as_uuid=False), nullable=False, index=True)  # Post ID, Account ID, etc.
    aggregate_type = Column(String(50), nullable=False)  # post, social_account, schedule, etc.
    payload = Column(JSON, nullable=False)  # Event data
    metadata = Column(JSON, default=dict)  # Correlation ID, causation ID, user ID, etc.
    source_platform = Column(String(50))  # Platform that originated the event
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index("ix_events_aggregate", "aggregate_type", "aggregate_id"),
        Index("ix_events_type_time", "event_type", "created_at"),
    )
    
    def __repr__(self):
        return f"<Event({self.event_type} on {self.aggregate_type}:{self.aggregate_id})>"
