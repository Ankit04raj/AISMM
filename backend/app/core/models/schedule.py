"""Schedule model for post scheduling."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, JSON, Enum as SQLEnum, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import Base


class ScheduleStatus(str, enum.Enum):
    """Schedule status."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleType(str, enum.Enum):
    """Schedule type."""
    IMMEDIATE = "immediate"
    SPECIFIC_TIME = "specific_time"
    AI_RECOMMENDED = "ai_recommended"
    AI_CONSTRAINED = "ai_constrained"  # AI within user-specified window


class Schedule(Base):
    """Post schedule."""

    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schedule_type: Mapped[ScheduleType] = mapped_column(SQLEnum(ScheduleType), nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(
        SQLEnum(ScheduleStatus), default=ScheduleStatus.PENDING, nullable=False, index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # For AI constrained
    window_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=True)  # Specific platform or None for all
    ai_confidence: Mapped[float] = mapped_column(nullable=True)  # AI confidence score
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=True)  # Why this time was chosen
    executed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    post: Mapped["Post"] = relationship("Post", back_populates="schedules")
    user: Mapped["User"] = relationship("User", back_populates="schedules")

    # Indexes
    __table_args__ = (
        Index("ix_schedules_user_status_time", "user_id", "status", "scheduled_at"),
        Index("ix_schedules_post", "post_id"),
    )

    def __repr__(self) -> str:
        return f"<Schedule(id={self.id}, post_id={self.post_id}, type={self.schedule_type}, status={self.status})>"