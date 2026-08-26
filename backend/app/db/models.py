"""Database models for AISMM."""

import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Boolean,
    JSON,
    Enum as SQLEnum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, declared_attr

from backend.app.db.session import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class SocialAccount(Base):
    """Social media account connection."""

    __tablename__ = "social_accounts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    platform_user_id = Column(String(100), nullable=False, index=True)
    username = Column(String(100), nullable=True)
    display_name = Column(String(200), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    account_type = Column(String(50), nullable=True)  # personal, business, creator
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    permissions = Column(JSON, nullable=True, default=list)
    account_metadata = Column(JSON, nullable=True, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    connected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="social_accounts")

    # Constraints
    __table_args__ = (
        UniqueConstraint("platform", "platform_user_id", name="uq_platform_user"),
        Index("ix_social_accounts_user_platform", "user_id", "platform"),
    )

    def __repr__(self):
        return f"<SocialAccount(platform={self.platform}, username={self.username})>"


class ContentTypeEnum(enum.Enum):
    """Content type enumeration."""
    POST = "post"
    REEL = "reel"
    STORY = "story"
    CAROUSEL = "carousel"


class PostStatusEnum(enum.Enum):
    """Post status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELETED = "deleted"


class Post(Base):
    """Post model."""

    __tablename__ = "posts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(SQLEnum(ContentTypeEnum), default=ContentTypeEnum.POST, nullable=False)
    text = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True, default=list)
    mentions = Column(JSON, nullable=True, default=list)
    status = Column(SQLEnum(PostStatusEnum), default=PostStatusEnum.DRAFT, nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=True, index=True)
    published_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
    platform_data = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="posts")
    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan")
    publications = relationship("PostPublication", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="post", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_posts_user_status", "user_id", "status"),
        Index("ix_posts_user_scheduled", "user_id", "scheduled_at"),
    )

    def __repr__(self):
        return f"<Post(id={self.id}, status={self.status.value})>"


class PostMedia(Base):
    """Post media attachments."""

    __tablename__ = "post_media"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(String(20), nullable=False)  # image, video, reel
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    title = Column(String(500), nullable=True)
    caption = Column(Text, nullable=True)
    alt_text = Column(String(1000), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    post = relationship("Post", back_populates="media")

    def __repr__(self):
        return f"<PostMedia(id={self.id}, type={self.media_type})>"


class PostPublication(Base):
    """Post publication record on a platform."""

    __tablename__ = "post_publications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    platform_post_id = Column(String(100), nullable=True, index=True)
    platform_container_id = Column(String(100), nullable=True)  # For scheduled posts
    permalink = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    platform_data = Column(JSON, nullable=True, default=dict)
    status = Column(String(50), default="pending", nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    post = relationship("Post", back_populates="publications")

    # Indexes
    __table_args__ = (
        Index("ix_post_publications_platform_post", "platform", "platform_post_id"),
        UniqueConstraint("post_id", "platform", name="uq_post_platform"),
    )

    def __repr__(self):
        return f"<PostPublication(platform={self.platform}, post_id={self.platform_post_id})>"


class Comment(Base):
    """Post comments."""

    __tablename__ = "comments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    platform_comment_id = Column(String(100), nullable=True)
    parent_comment_id = Column(PG_UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    text = Column(Text, nullable=True)
    username = Column(String(100), nullable=True)
    user_id = Column(String(100), nullable=True)
    like_count = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    post = relationship("Post", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Comment(id={self.id}, platform={self.platform})>"


class Metric(Base):
    """Aggregated metrics storage."""

    __tablename__ = "metrics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(20), nullable=False)  # post, account, media
    metrics = Column(JSON, nullable=False, default=dict)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    period = Column(String(20), nullable=True)  # lifetime, day, week, month

    # Relationships
    post = relationship("Post", back_populates="metrics")

    # Indexes
    __table_args__ = (
        Index("ix_metrics_platform_entity", "platform", "entity_id", "entity_type"),
        Index("ix_metrics_post_fetched", "post_id", "fetched_at"),
    )

    def __repr__(self):
        return f"<Metric(platform={self.platform}, entity={self.entity_id})>"


class Schedule(Base):
    """Post scheduling."""

    __tablename__ = "schedules"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending, sent, failed, cancelled
    retry_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    next_attempt_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="schedules")
    post = relationship("Post")

    # Indexes
    __table_args__ = (
        Index("ix_schedules_user_scheduled", "user_id", "scheduled_at"),
        Index("ix_schedules_status_next", "status", "next_attempt_at"),
    )

    def __repr__(self):
        return f"<Schedule(id={self.id}, scheduled_at={self.scheduled_at})>"


class MLModel(Base):
    """ML model registry."""

    __tablename__ = "ml_models"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # classification, regression, generation
    framework = Column(String(50), nullable=True)  # sklearn, pytorch, tensorflow, etc.
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True, default=dict)
    metrics = Column(JSON, nullable=True, default=dict)
    artifact_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    is_production = Column(Boolean, default=False, nullable=False)
    trained_at = Column(DateTime, nullable=True)
    deployed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    predictions = relationship("ModelPrediction", back_populates="model")

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_model_version"),
    )

    def __repr__(self):
        return f"<MLModel(name={self.name}, version={self.version})>"


class ModelPrediction(Base):
    """ML model predictions."""

    __tablename__ = "model_predictions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey("ml_models.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(20), nullable=False)  # post, account, user
    input_data = Column(JSON, nullable=False, default=dict)
    prediction = Column(JSON, nullable=False, default=dict)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    model = relationship("MLModel", back_populates="predictions")

    # Indexes
    __table_args__ = (
        Index("ix_predictions_model_entity", "model_id", "entity_id", "entity_type"),
        Index("ix_predictions_created", "created_at"),
    )

    def __repr__(self):
        return f"<ModelPrediction(model={self.model_id}, entity={self.entity_id})>"


class SentimentAnalysis(Base):
    """Sentiment analysis results."""

    __tablename__ = "sentiment_analyses"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=False)  # positive, negative, neutral
    confidence = Column(Float, nullable=False)
    scores = Column(JSON, nullable=True, default=dict)  # positive, negative, neutral scores
    entities = Column(JSON, nullable=True, default=list)
    keywords = Column(JSON, nullable=True, default=list)
    language = Column(String(10), nullable=True)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SentimentAnalysis(post={self.post_id}, sentiment={self.sentiment})>"