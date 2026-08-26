"""Post models - Universal content and platform-specific publications."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Integer, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import Base


class PostStatus(str, enum.Enum):
    """Post lifecycle status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class Post(Base):
    """Universal post - platform-independent content."""

    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Main content text
    caption: Mapped[str] = mapped_column(Text, nullable=True)  # Optional caption
    hashtags: Mapped[List[str]] = mapped_column(JSON, default=list)  # Normalized hashtags
    mentions: Mapped[List[str]] = mapped_column(JSON, default=list)  # Normalized mentions
    links: Mapped[List[str]] = mapped_column(JSON, default=list)  # URLs
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    content_type: Mapped[str] = mapped_column(String(50), default="post")  # post, story, reel, short, article
    status: Mapped[PostStatus] = mapped_column(
        SQLEnum(PostStatus), default=PostStatus.DRAFT, nullable=False, index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # Flexible metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="posts")
    publications: Mapped[list["PostPublication"]] = relationship(
        "PostPublication", back_populates="post", cascade="all, delete-orphan"
    )
    media: Mapped[list["PostMedia"]] = relationship(
        "PostMedia", back_populates="post", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_posts_user_status", "user_id", "status"),
        Index("ix_posts_scheduled", "scheduled_at", "status"),
    )

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, user_id={self.user_id}, status={self.status})>"


class PostPublication(Base):
    """Platform-specific publication of a universal post."""

    __tablename__ = "post_publications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    platform_post_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)  # ID from platform API
    platform_url: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[PostStatus] = mapped_column(
        SQLEnum(PostStatus), default=PostStatus.DRAFT, nullable=False, index=True
    )
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    platform_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # What was sent to platform
    platform_response: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # Raw platform response
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    engagement_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    post: Mapped["Post"] = relationship("Post", back_populates="publications")
    account: Mapped["SocialAccount"] = relationship("SocialAccount", back_populates="publications")
    metrics: Mapped[list["Metric"]] = relationship(
        "Metric", back_populates="publication", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="publication", cascade="all, delete-orphan"
    )

    # Unique constraint: one publication per post per account
    __table_args__ = (
        Index("ix_publications_post_account", "post_id", "account_id", unique=True),
        Index("ix_publications_platform_status", "platform", "status"),
    )

    def __repr__(self) -> str:
        return f"<PostPublication(id={self.id}, post_id={self.post_id}, platform={self.platform}, status={self.status})>"


class PostMedia(Base):
    """Media attached to a post."""

    __tablename__ = "post_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # image, video, carousel_item, document
    url: Mapped[str] = mapped_column(String(500), nullable=True)  # Public URL after upload
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)  # Local storage path
    filename: Mapped[str] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float] = mapped_column(nullable=True)  # For video
    alt_text: Mapped[str] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)  # For carousel ordering
    platform_media_ids: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)  # Platform-specific media IDs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    post: Mapped["Post"] = relationship("Post", back_populates="media")

    def __repr__(self) -> str:
        return f"<PostMedia(id={self.id}, post_id={self.post_id}, type={self.type})>"