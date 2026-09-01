"""Pydantic schemas for Phase 12 Universal Analytics Dashboard."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OverviewMetrics(BaseModel):
    """Aggregated multi-platform overview metrics."""
    total_connected_platforms: int
    total_followers: int
    total_impressions: int
    total_reach: int
    total_engagements: int
    overall_engagement_rate: float
    total_posts_published: int
    total_comments_received: int
    average_sentiment_score: float
    time_period_days: int
    generated_at: datetime


class PlatformComparisonItem(BaseModel):
    """Normalized performance metrics for a single platform."""
    platform: str
    followers: int
    impressions: int
    reach: int
    engagements: int
    engagement_rate: float
    posts_count: int
    avg_likes_per_post: float
    avg_comments_per_post: float
    top_performing_media_type: str


class PlatformComparisonResponse(BaseModel):
    """Comparative benchmarking across all active social platforms."""
    platforms: List[PlatformComparisonItem]
    strongest_platform_by_reach: str
    strongest_platform_by_engagement: str
    time_period_days: int


class ContentTypePerformanceItem(BaseModel):
    """Performance breakdown by media/content format (image, video, carousel, etc.)."""
    content_type: str
    total_posts: int
    avg_impressions: float
    avg_engagements: float
    avg_engagement_rate: float


class PostRankingItem(BaseModel):
    """Ranked post item in top/bottom performance tables."""
    post_id: str
    platform: str
    content_type: str
    text_snippet: Optional[str] = None
    created_at: datetime
    impressions: int
    engagements: int
    engagement_rate: float


class ContentPerformanceResponse(BaseModel):
    """Content performance analytics."""
    top_posts: List[PostRankingItem]
    bottom_posts: List[PostRankingItem]
    by_content_type: List[ContentTypePerformanceItem]
    top_performing_hashtags: List[Dict[str, Any]]
    optimal_caption_length_range: str


class TemporalHeatmapSlot(BaseModel):
    """Engagement score for a specific day and hour slot."""
    day_of_week: int  # 0=Monday .. 6=Sunday
    day_name: str
    hour: int  # 0-23
    avg_engagement_score: float
    sample_posts: int


class TemporalAnalyticsResponse(BaseModel):
    """Temporal engagement heatmaps and peak activity timing."""
    best_overall_hour: int
    best_overall_day: str
    weekday_avg_engagement: float
    weekend_avg_engagement: float
    weekday_vs_weekend_lift_percent: float
    heatmap_slots: List[TemporalHeatmapSlot]


class SentimentTrendSummary(BaseModel):
    """Historical sentiment trend analytics."""
    overall_sentiment_label: str
    average_compound_score: float
    positive_comments_count: int
    neutral_comments_count: int
    negative_comments_count: int
    positive_ratio_percent: float
    negative_ratio_percent: float
    sentiment_health_status: str  # "excellent", "healthy", "concerning", "critical"


class GrowthDriftPoint(BaseModel):
    """Comparison between actual vs predicted followers at a specific date."""
    date: str
    actual_followers: int
    predicted_followers: int
    absolute_error: int
    error_percentage: float


class GrowthAccuracyReportResponse(BaseModel):
    """Report evaluating growth model prediction accuracy against actual data."""
    platform: str
    model_version: str
    r2_score: float
    rmse: float
    mean_absolute_percentage_error: float
    drift_status: str  # "calibrated", "mild_drift", "retraining_recommended"
    data_points: List[GrowthDriftPoint]
