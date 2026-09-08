"""Pydantic schemas for Intelligent Scheduling API endpoints."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from backend.app.core.schemas.post import MediaItem


class ScheduleRecommendRequest(BaseModel):
    """Request for optimal posting time recommendations."""
    platform: str = Field(default="instagram", description="Target platform")
    text: Optional[str] = Field(None, description="Post text/caption")
    hashtags: Optional[List[str]] = Field(default_factory=list)
    media_type: str = Field(default="image")
    start_hour: Optional[int] = Field(None, ge=0, le=23, description="Earliest allowed hour (0-23)")
    end_hour: Optional[int] = Field(None, ge=0, le=23, description="Latest allowed hour (0-23)")
    allowed_days: Optional[List[int]] = Field(None, description="Allowed weekdays (0=Mon..6=Sun)")
    target_date: Optional[datetime] = None
    top_k: int = Field(default=5, ge=1, le=20)


class TimeSlotItem(BaseModel):
    """Recommended time slot item."""
    scheduled_at: datetime
    predicted_engagement_score: float
    confidence: float
    reason: str
    is_weekend: bool
    day_name: str
    hour_label: str


class ScheduleRecommendResponse(BaseModel):
    """Response containing optimal posting slots."""
    platform: str
    optimal_time: datetime
    recommendations: List[TimeSlotItem]
    model_version: str
    baseline_accuracy: float = 88.08


class AutoScheduleRequest(BaseModel):
    """Request to compose content and let AI pick optimal posting time."""
    platform: str
    content_type: str = "post"
    text: Optional[str] = None
    caption: Optional[str] = None
    media: List[MediaItem] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    start_hour: Optional[int] = Field(None, ge=0, le=23)
    end_hour: Optional[int] = Field(None, ge=0, le=23)
    target_date: Optional[datetime] = None


class AutoScheduleResponse(BaseModel):
    """Response for AI auto-scheduled post."""
    post_id: str
    platform: str
    scheduled_at: datetime
    predicted_engagement_score: float
    reason: str
    status: str = "scheduled"
