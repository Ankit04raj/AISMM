"""Post-related Pydantic schemas for API contracts."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class MediaItem(BaseModel):
    """Media item for posts."""
    type: str = Field(..., description="Media type (image, video, reel, story)")
    url: str = Field(..., description="Media URL (must be publicly accessible)")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL for videos")
    duration_seconds: Optional[int] = Field(None, ge=1, description="Video duration in seconds")
    width: Optional[int] = Field(None, ge=1, description="Media width in pixels")
    height: Optional[int] = Field(None, ge=1, description="Media height in pixels")
    title: Optional[str] = Field(None, max_length=500, description="Media title")
    caption: Optional[str] = Field(None, max_length=2200, description="Media caption")
    alt_text: Optional[str] = Field(None, max_length=1000, description="Accessibility alt text")


class CreatePostRequest(BaseModel):
    """Request schema for creating a post."""
    platform: str = Field(..., description="Target platform")
    content_type: str = Field(
        default="post",
        description="Content type (post, reel, story, carousel)"
    )
    text: Optional[str] = Field(None, max_length=65000, description="Post text content")
    caption: Optional[str] = Field(None, max_length=2200, description="Post caption")
    media: List[MediaItem] = Field(default=[], description="Media items")
    hashtags: Optional[List[str]] = Field(default=[], description="Hashtags")
    mentions: Optional[List[str]] = Field(default=[], description="User mentions")
    location_id: Optional[str] = Field(None, description="Location ID")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publish time")
    publish_now: bool = Field(default=True, description="Publish immediately")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Platform-specific options")

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        valid_types = ["post", "reel", "story", "carousel", "image", "video", "status"]
        if v.lower() not in valid_types:
            raise ValueError(f"content_type must be one of: {valid_types}")
        return v.lower()


class PlatformCustomization(BaseModel):
    """Platform-specific override for a post."""
    caption: Optional[str] = None
    text: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    media: Optional[List[MediaItem]] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MultiPlatformPostRequest(BaseModel):
    """Request schema for composing and publishing across multiple platforms."""
    platforms: List[str] = Field(..., min_length=1, description="Target platforms")
    content_type: str = Field(default="post", description="Content type")
    text: Optional[str] = Field(None, description="Base text content")
    caption: Optional[str] = Field(None, description="Base caption")
    media: List[MediaItem] = Field(default_factory=list, description="Base media items")
    hashtags: List[str] = Field(default_factory=list, description="Base hashtags")
    mentions: List[str] = Field(default_factory=list, description="Base mentions")
    customizations: Dict[str, PlatformCustomization] = Field(
        default_factory=dict,
        description="Platform-specific overrides"
    )
    scheduled_at: Optional[datetime] = None
    publish_now: bool = True


class PostResponse(BaseModel):
    """Response schema for post creation."""
    id: str = Field(..., description="Platform post ID or Internal ID")
    platform: str = Field(..., description="Platform name")
    permalink: Optional[str] = Field(None, description="Post permalink")
    media_type: Optional[str] = Field(None, description="Media type")
    published_at: Optional[datetime] = Field(None, description="Published timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled timestamp")
    status: str = Field(default="published", description="Post status")
    platform_data: Optional[Dict[str, Any]] = Field(default={}, description="Raw platform data")


class MultiPlatformPostResponse(BaseModel):
    """Response schema for multi-platform post creation."""
    post_id: str
    overall_status: str
    results: Dict[str, PostResponse]
    created_at: datetime


class ContentPreviewRequest(BaseModel):
    """Request schema for previewing content on target platforms."""
    platforms: List[str] = Field(..., min_length=1)
    content_type: str = "post"
    text: Optional[str] = None
    caption: Optional[str] = None
    media: List[MediaItem] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    customizations: Dict[str, PlatformCustomization] = Field(default_factory=dict)


class ContentPreviewResponse(BaseModel):
    """Native preview data for platforms."""
    previews: Dict[str, Dict[str, Any]]
    warnings: Dict[str, List[str]]


class ContentValidationRequest(BaseModel):
    """Request schema to validate content against platform rules."""
    platforms: List[str] = Field(..., min_length=1)
    content_type: str = "post"
    text: Optional[str] = None
    caption: Optional[str] = None
    media: List[MediaItem] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    customizations: Dict[str, PlatformCustomization] = Field(default_factory=dict)


class ContentValidationResponse(BaseModel):
    """Validation response with platform warnings and errors."""
    valid: bool
    platform_warnings: Dict[str, List[str]]
    platform_errors: Dict[str, List[str]]


class PostListResponse(BaseModel):
    """Response schema for post listing."""
    posts: List[PostResponse] = Field(..., description="List of posts")
    total: int = Field(..., ge=0, description="Total post count")
    page: int = Field(default=1, ge=1, description="Current page")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")
    has_next: bool = Field(default=False, description="Has next page")


class UpdatePostRequest(BaseModel):
    """Request schema for updating a post."""
    caption: Optional[str] = Field(None, max_length=2200, description="New caption")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Platform-specific options")


class DeletePostResponse(BaseModel):
    """Response schema for post deletion."""
    id: str = Field(..., description="Deleted post ID")
    deleted: bool = Field(default=True)
    platform: str = Field(..., description="Platform name")


class SchedulePostRequest(BaseModel):
    """Request schema for scheduling a post."""
    post_id: str = Field(..., description="Post container ID to schedule")
    scheduled_at: datetime = Field(..., description="Scheduled publish time")
    timezone: str = Field(default="UTC", description="Timezone for scheduling")


class PostMetrics(BaseModel):
    """Post engagement metrics."""
    post_id: str
    platform: str
    impressions: Optional[int] = None
    reach: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    video_views: Optional[int] = None
    engagement_rate: Optional[float] = Field(None, ge=0, le=100, description="Engagement rate %")
    fetched_at: Optional[datetime] = None


class CommentResponse(BaseModel):
    """Comment response schema."""
    id: str
    post_id: str
    text: Optional[str] = None
    username: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    likes: Optional[int] = None
    replies_count: Optional[int] = None


class ReplyToCommentRequest(BaseModel):
    """Request to reply to a comment."""
    text: str = Field(..., max_length=2200, description="Reply text")


class WebhookEvent(BaseModel):
    """Webhook event schema."""
    event_type: str
    object_type: str
    object_id: str
    timestamp: datetime
    data: Dict[str, Any]


class WebhookSubscriptionRequest(BaseModel):
    """Request to subscribe to webhooks."""
    callback_url: str = Field(..., description="Webhook callback URL")
    verify_token: str = Field(..., description="Verification token")
    fields: List[str] = Field(
        default=["comments", "mentions"],
        description="Webhook fields to subscribe"
    )


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    data: List[Dict[str, Any]]
    paging: Optional[Dict[str, Any]] = None
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
