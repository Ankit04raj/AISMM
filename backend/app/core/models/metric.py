"""Metric model for normalized engagement metrics."""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class Metric(Base):
    """Normalized engagement metric for a post publication."""

    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("post_publications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # LIKE, COMMENT, SHARE, REACTION, VIEW, SAVE, etc.
    value: Mapped[int] = mapped_column(Integer, default=0)
    original_metric: Mapped[str] = mapped_column(String(100), nullable=True)  # Platform-specific metric name (e.g., "retweet_count")
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    publication: Mapped["PostPublication"] = relationship("PostPublication", back_populates="metrics")

    # Indexes
    __table_args__ = (
        Index("ix_metrics_publication_type", "publication_id", "metric_type"),
        Index("ix_metrics_platform_type", "source_platform", "metric_type"),
    )

    def __repr__(self) -> str:
        return f"<Metric(publication_id={self.publication_id}, type={self.metric_type}, value={self.value})>"


class AccountMetric(Base):
    """Account-level metrics (followers, engagement rate, etc.)."""

    __tablename__ = "account_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # FOLLOWERS, ENGAGEMENT_RATE, REACH, IMPRESSIONS
    value: Mapped[int] = mapped_column(Integer, default=0)
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Indexes
    __table_args__ = (
        Index("ix_account_metrics_account_type", "account_id", "metric_type"),
        Index("ix_account_metrics_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<AccountMetric(account_id={self.account_id}, type={self.metric_type}, value={self.value})>"