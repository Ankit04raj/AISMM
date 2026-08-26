"""Insights-related Pydantic schemas for API contracts."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MetricNormalizer(BaseModel):
    """Normalizes insights metrics to a standard format."""
    impressions: Optional[int] = Field(None, ge=0, description="Impressions")
    reach: Optional[int] = Field(None, ge=0, description="Reach")
    likes: Optional[int] = Field(None, ge=0, description="Likes")
    comments: Optional[int] = Field(None, ge=0, description="Comments")
    saves: Optional[int] = Field(None, ge=0, description="Saves")
    shares: Optional[int] = Field(None, ge=0, description="Shares")
    video_views: Optional[int] = Field(None, ge=0, description="Video views")


class PostInsights(BaseModel):
    """Post-level insights."""
    post_id: str
    platform: str
    impressions: Optional[int] = None
    reach: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    saves: Optional[int] = None
    shares: Optional[int] = None
    video_views: Optional[int] = None
    engagement_rate: Optional[float] = Field(None, ge=0, le=100, description="Engagement rate %")
    fetched_at: Optional[datetime] = None


class MediaInsights(BaseModel):
    """Media-level insights."""
    media_id: str
    platform: str
    impressions: Optional[int] = None
    reach: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    saves: Optional[int] = None
    shares: Optional[int] = None
    video_views: Optional[int] = None
    engagement_rate: Optional[float] = Field(None, ge=0, le=100, description="Engagement rate %")
    fetched_at: Optional[datetime] = None


class AccountInsights(BaseModel):
    """Account-level insights."""
    platform: str
    account_id: str
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None
    impressions: Optional[int] = None
    reach: Optional[int] = None
    profile_views: Optional[int] = None
    website_clicks: Optional[int] = None
    email_contacts: Optional[int] = None
    phone_call_clicks: Optional[int] = None
    fetched_at: Optional[datetime] = None


class FollowerDemographics(BaseModel):
    """Follower demographics breakdown."""
    age_gender: Optional[Dict[str, Dict[str, int]]] = Field(None, description="Age/gender distribution")
    top_countries: Optional[Dict[str, int]] = Field(None, description="Top countries")
    top_cities: Optional[Dict[str, int]] = Field(None, description="Top cities")
    locales: Optional[Dict[str, int]] = Field(None, description="Language locales")


class AccountProfile(BaseModel):
    """Account profile details."""
    id: str
    platform: str
    username: str
    display_name: Optional[str] = None
    biography: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None
    account_type: Optional[str] = None
    is_verified: Optional[bool] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None