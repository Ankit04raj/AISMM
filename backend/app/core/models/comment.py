"""Comment model."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import Base


class Comment(Base):
    """Comment on a post publication."""

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("post_publications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform_comment_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    parent_comment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    author_id: Mapped[str] = mapped_column(String(255), nullable=False)  # Platform user ID
    author_username: Mapped[str] = mapped_column(String(255), nullable=False)
    author_name: Mapped[str] = mapped_column(String(255), nullable=True)
    author_avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    platform_created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # Raw platform response
    sentiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sentiment_analyses.id", ondelete="SET NULL"), nullable=True
    )
    is_replied: Mapped[bool] = mapped_column(default=False)
    replied_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reply_content: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    publication: Mapped["PostPublication"] = relationship("PostPublication", back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship("Comment", remote_side=[id], backref="replies")
    sentiment: Mapped[Optional["SentimentAnalysis"]] = relationship("SentimentAnalysis")

    # Indexes
    __table_args__ = (
        Index("ix_comments_publication_platform", "publication_id", "platform_comment_id", unique=True),
        Index("ix_comments_parent", "parent_comment_id"),
    )

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, publication_id={self.publication_id}, author={self.author_username})>"