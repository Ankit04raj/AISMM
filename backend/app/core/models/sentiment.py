"""Sentiment analysis model."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON, Enum as SQLEnum, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import Base


class SentimentPhase(str, enum.Enum):
    """Sentiment analysis phase."""
    PRE_POST = "pre_post"
    POST_POST = "post_post"
    AGGREGATED = "aggregated"


class SentimentLabel(str, enum.Enum):
    """Sentiment label."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class SentimentAnalysis(Base):
    """Sentiment analysis result for a post or comment."""

    __tablename__ = "sentiment_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # post, comment
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    phase: Mapped[SentimentPhase] = mapped_column(SQLEnum(SentimentPhase), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # -1.0 to 1.0
    label: Mapped[SentimentLabel] = mapped_column(SQLEnum(SentimentLabel), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 to 1.0
    method: Mapped[str] = mapped_column(String(50), nullable=False)  # vader, vader_knn, comment_aggregation
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # VADER scores, k-NN neighbors, etc.
    model_version: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("ix_sentiment_target", "target_type", "target_id"),
        Index("ix_sentiment_phase_score", "phase", "score"),
    )

    def __repr__(self) -> str:
        return f"<SentimentAnalysis(target={self.target_type}:{self.target_id}, phase={self.phase}, label={self.label}, score={self.score:.2f})>"