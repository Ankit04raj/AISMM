"""Pydantic schemas for Phase 9 Post-Posting Intelligence."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from backend.app.core.schemas.ai import SentimentAnalyzeResponse


class CommentSyncRequest(BaseModel):
    """Request to sync comments for a post or account."""
    limit_per_platform: int = Field(default=50, ge=1, le=200)


class SyncedCommentItem(BaseModel):
    """Single synced comment details."""
    id: str
    platform: str
    platform_comment_id: str
    author_name: str
    text: str
    sentiment_label: str
    sentiment_score: float
    created_at: datetime


class CommentSyncResponse(BaseModel):
    """Response after synchronizing comments."""
    post_id: str
    total_synced: int
    new_comments_added: int
    synced_comments: List[SyncedCommentItem]
    timestamp: datetime


class TemporalSentimentPoint(BaseModel):
    """Sentiment metric at a specific time window."""
    time_window: str  # e.g., "0-1h", "1-6h", "6-24h", "24-72h", ">72h"
    comment_count: int
    avg_sentiment_score: float
    sentiment_distribution: Dict[str, int]


class TemporalSentimentResponse(BaseModel):
    """Post sentiment trajectory over time."""
    post_id: str
    overall_sentiment_label: str
    overall_sentiment_score: float
    total_comments_analyzed: int
    trajectory_trend: str  # "improving", "declining", "stable", "insufficient_data"
    time_series: List[TemporalSentimentPoint]


class IntelligenceAlert(BaseModel):
    """Alert for viral spikes, negative sentiment waves, or unhandled comments."""
    alert_type: str  # "HIGH_ENGAGEMENT_SPIKE", "NEGATIVE_SENTIMENT_SURGE", "REPLY_REQUIRED"
    severity: str  # "low", "medium", "high", "critical"
    platform: str
    message: str
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    created_at: datetime


class IntelligenceAlertsResponse(BaseModel):
    """Alerts list for a post."""
    post_id: str
    active_alerts: List[IntelligenceAlert]
    alert_count: int


class PostIntelligenceReportResponse(BaseModel):
    """Comprehensive post intelligence report combining analytics, comments, and sentiment trajectory."""
    post_id: str
    platforms: List[str]
    total_impressions: int
    total_engagements: int
    engagement_rate: float
    total_comments: int
    sentiment: TemporalSentimentResponse
    alerts: List[IntelligenceAlert]
    generated_at: datetime
