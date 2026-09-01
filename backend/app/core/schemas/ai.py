"""Pydantic schemas for AI Content Engine API endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SentimentAnalyzeRequest(BaseModel):
    """Request for pre-posting sentiment analysis."""
    text: str = Field(..., min_length=1, description="Text to analyze")


class SentimentAnalyzeResponse(BaseModel):
    """Sentiment analysis response."""
    score: float = Field(..., description="Compound sentiment score (-1.0 to 1.0)")
    label: str = Field(..., description="Sentiment label (very_positive, positive, neutral, negative, very_negative)")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    positive_score: float = 0.0
    neutral_score: float = 0.0
    negative_score: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)


class PostSentimentRequest(BaseModel):
    """Request for post-posting audience sentiment aggregation."""
    comments: List[str] = Field(..., description="List of comment texts")


class CaptionAnalyzeRequest(BaseModel):
    """Request for caption quality analysis."""
    text: str = Field(..., min_length=1)
    platform: str = Field(default="instagram")


class CaptionFeaturesResponse(BaseModel):
    """Extracted caption features."""
    length: int
    word_count: int
    hashtag_count: int
    mention_count: int
    emoji_count: int
    question_count: int
    exclamation_count: int
    has_cta: bool
    detected_cta: Optional[str] = None


class CaptionAnalyzeResponse(BaseModel):
    """Caption quality score and recommendations."""
    score: float = Field(..., description="Quality score (0-100)")
    grade: str = Field(..., description="Quality grade")
    features: CaptionFeaturesResponse
    strengths: List[str]
    suggestions: List[str]


class CaptionOptimizeRequest(BaseModel):
    """Request for platform-tailored caption adaptation."""
    text: str = Field(..., min_length=1)
    platform: str = Field(..., description="Target platform")
    target_tone: str = Field(default="engaging")


class CaptionOptimizeResponse(BaseModel):
    """Optimized caption response."""
    original_text: str
    optimized_text: str
    platform: str
    character_count: int


class HashtagRecommendRequest(BaseModel):
    """Request for Top-K hashtag recommendations."""
    text: str = Field(..., min_length=1)
    platform: str = Field(default="instagram")
    top_k: int = Field(default=5, ge=1, le=30)


class HashtagItem(BaseModel):
    """Individual hashtag item with relevance."""
    hashtag: str
    category: str
    relevance_score: float
    is_trending: bool = False


class HashtagRecommendResponse(BaseModel):
    """Hashtag recommendation response."""
    top_k: List[str]
    recommendations: List[HashtagItem]
    platform: str
    max_recommended: int


class ContentOptimizeAllRequest(BaseModel):
    """Request for comprehensive AI content optimization."""
    text: str = Field(..., min_length=1)
    platforms: List[str] = Field(default=["instagram", "facebook", "twitter", "linkedin"])
    top_k_hashtags: int = Field(default=5, ge=1, le=20)


class PlatformVariantItem(BaseModel):
    """Adapted platform variant."""
    platform: str
    text: str
    recommended_hashtags: List[str]
    character_count: int


class ContentOptimizeAllResponse(BaseModel):
    """Unified AI optimization response."""
    sentiment: SentimentAnalyzeResponse
    caption_analysis: CaptionAnalyzeResponse
    hashtags: HashtagRecommendResponse
    platform_variants: Dict[str, PlatformVariantItem]
