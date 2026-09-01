"""Pydantic schemas for Phase 13 AI Strategy Engine."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RecommendationPriority(str, Enum):
    """Priority level for strategic AI recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationCategory(str, Enum):
    """Category classification of recommendation."""
    TIMING = "timing"
    CONTENT_FORMAT = "content_format"
    CAPTION_OPTIMIZATION = "caption_optimization"
    HASHTAG_STRATEGY = "hashtag_strategy"
    AUDIENCE_SENTIMENT = "audience_sentiment"
    GROWTH_VELOCITY = "growth_velocity"
    CROSS_PLATFORM_SYNERGY = "cross_platform_synergy"


class StrategyRecommendationItem(BaseModel):
    """Individual actionable AI strategy recommendation."""
    recommendation_id: str
    category: RecommendationCategory
    priority: RecommendationPriority
    title: str
    action_text: str
    target_platform: Optional[str] = None  # None indicates cross-platform / global
    reasoning: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    expected_impact_percent: float
    metric_targeted: str  # e.g., "reach", "engagement_rate", "follower_growth", "sentiment_ratio"


class PlatformStrategyAdvice(BaseModel):
    """Platform-tailored strategy profile."""
    platform: str
    recommended_weekly_frequency: float
    optimal_time_window: str
    best_media_format: str
    caption_style_guidance: str
    hashtag_density_recommendation: str
    expected_monthly_reach_growth: int
    expected_engagement_rate_target: float


class ContentDraftStrategyRequest(BaseModel):
    """Request payload to generate a complete multi-model strategic plan for a planned post or campaign."""
    draft_caption: Optional[str] = None
    target_platforms: List[str] = Field(default_factory=lambda: ["instagram", "facebook"])
    media_type: str = "image"
    content_category: Optional[str] = "tech"
    current_followers: Optional[int] = 10000


class ContentStrategyPlan(BaseModel):
    """Synthesized strategic optimization plan for a specific piece of content."""
    optimized_caption_by_platform: Dict[str, str]
    recommended_hashtags: List[str]
    best_publishing_time: str
    best_publishing_day: str
    projected_engagement_rate: float
    sentiment_prediction_compound: float
    strategic_tips: List[str]


class ComprehensiveStrategyResponse(BaseModel):
    """Master AI strategic dashboard response aggregating high-level directives."""
    active_recommendations: List[StrategyRecommendationItem]
    platform_profiles: List[PlatformStrategyAdvice]
    key_strategic_focus: str
    overall_strategy_health_score: int  # 0-100
    generated_at: datetime


class StrategyFeedbackRequest(BaseModel):
    """User feedback payload acknowledging or rejecting a strategic recommendation."""
    recommendation_id: str
    applied: bool
    feedback_notes: Optional[str] = None
