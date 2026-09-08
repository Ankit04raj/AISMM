"""Instagram Graph API Endpoint Constants."""

from enum import Enum


class InstagramEndpoint(str, Enum):
    """Instagram Graph API endpoints."""

    # Base
    BASE = "https://graph.facebook.com/v19.0"

    # OAuth
    AUTHORIZE = "https://api.instagram.com/oauth/authorize"
    ACCESS_TOKEN = "https://api.instagram.com/oauth/access_token"
    REFRESH_TOKEN = "https://graph.facebook.com/v19.0/oauth/access_token"

    # User/Account
    ME = "/me"
    ME_ACCOUNTS = "/me/accounts"
    IG_USER = "/{ig_user_id}"

    # Media Publishing (2-phase)
    MEDIA_CONTAINER = "/{ig_user_id}/media"
    MEDIA_PUBLISH = "/{ig_user_id}/media_publish"
    MEDIA_STATUS = "/{container_id}"
    MEDIA_UPLOAD = "/{ig_user_id}/media_upload"  # Resumable upload

    # Media Management
    MEDIA = "/{media_id}"
    MEDIA_CHILDREN = "/{media_id}/children"
    MEDIA_INSIGHTS = "/{media_id}/insights"
    MEDIA_COMMENTS = "/{media_id}/comments"
    COMMENT_REPLIES = "/{comment_id}/replies"
    COMMENT_HIDE = "/{comment_id}"

    # Account Insights
    ACCOUNT_INSIGHTS = "/{ig_user_id}/insights"

    # Webhooks
    SUBSCRIBED_APPS = "/{ig_user_id}/subscribed_apps"

    # Stories
    STORIES = "/{ig_user_id}/stories"
    STORY_INSIGHTS = "/{story_id}/insights"

    # Reels
    REELS = "/{ig_user_id}/reels"
    REEL_INSIGHTS = "/{reel_id}/insights"


class InstagramFields(str, Enum):
    """Common field sets for API requests."""

    # Media fields
    MEDIA_BASIC = "id,caption,media_type,media_url,permalink,timestamp"
    MEDIA_EXTENDED = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,is_comment_enabled"
    MEDIA_FULL = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,is_comment_enabled,owner,thumbnail_url,children{id,media_url,media_type}"

    # Insights fields
    INSIGHTS_BASIC = "impressions,reach,likes,comments,shares,saves"
    INSIGHTS_VIDEO = "video_views,video_play_retention,video_avg_time_watched"
    INSIGHTS_STORY = "exits,replies,taps_forward,taps_backward"
    INSIGHTS_REEL = "plays,reach,likes,comments,shares,saves,total_interactions"
    INSIGHTS_ACCOUNT = "followers_count,impressions,reach,profile_views,website_clicks"

    # Comment fields
    COMMENT_BASIC = "id,text,timestamp,username,like_count"
    COMMENT_FULL = "id,text,timestamp,username,like_count,hidden,replies{id,text,timestamp,username,like_count}"

    # Account fields
    ACCOUNT_BASIC = "id,username,account_type,media_count,profile_picture_url"
    ACCOUNT_EXTENDED = "id,username,account_type,media_count,profile_picture_url,biography,website,ig_id"


class InstagramMediaType(str, Enum):
    """Instagram media types."""
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL = "CAROUSEL"
    REELS = "REELS"
    STORIES = "STORIES"


class InstagramInsightPeriod(str, Enum):
    """Insight periods."""
    LIFETIME = "lifetime"
    DAY = "day"
    DAYS_28 = "days_28"
    WEEK = "week"
    MONTH = "month"


class InstagramInsightMetric(str, Enum):
    """Insight metrics."""

    # Media metrics
    IMPRESSIONS = "impressions"
    REACH = "reach"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    VIDEO_VIEWS = "video_views"
    VIDEO_PLAY_RETENTION = "video_play_retention"
    VIDEO_AVG_TIME_WATCHED = "video_avg_time_watched"

    # Story metrics
    EXITS = "exits"
    REPLIES = "replies"
    TAPS_FORWARD = "taps_forward"
    TAPS_BACKWARD = "taps_backward"

    # Reel metrics
    PLAYS = "plays"
    TOTAL_INTERACTIONS = "total_interactions"

    # Account metrics
    FOLLOWERS_COUNT = "followers_count"
    PROFILE_VIEWS = "profile_views"
    WEBSITE_CLICKS = "website_clicks"
    EMAIL_CONTACTS = "email_contacts"
    PHONE_CALL_CLICKS = "phone_call_clicks"
    GET_DIRECTIONS_CLICKS = "get_directions_clicks"
    TEXT_MESSAGE_CLICKS = "text_message_clicks"


# Media metric groups by media type
MEDIA_METRICS_MAP = {
    InstagramMediaType.IMAGE: [
        InstagramInsightMetric.IMPRESSIONS,
        InstagramInsightMetric.REACH,
        InstagramInsightMetric.LIKES,
        InstagramInsightMetric.COMMENTS,
        InstagramInsightMetric.SHARES,
        InstagramInsightMetric.SAVES,
    ],
    InstagramMediaType.VIDEO: [
        InstagramInsightMetric.IMPRESSIONS,
        InstagramInsightMetric.REACH,
        InstagramInsightMetric.LIKES,
        InstagramInsightMetric.COMMENTS,
        InstagramInsightMetric.SHARES,
        InstagramInsightMetric.SAVES,
        InstagramInsightMetric.VIDEO_VIEWS,
        InstagramInsightMetric.VIDEO_PLAY_RETENTION,
        InstagramInsightMetric.VIDEO_AVG_TIME_WATCHED,
    ],
    InstagramMediaType.CAROUSEL: [
        InstagramInsightMetric.IMPRESSIONS,
        InstagramInsightMetric.REACH,
        InstagramInsightMetric.LIKES,
        InstagramInsightMetric.COMMENTS,
        InstagramInsightMetric.SHARES,
        InstagramInsightMetric.SAVES,
    ],
    InstagramMediaType.REELS: [
        InstagramInsightMetric.PLAYS,
        InstagramInsightMetric.REACH,
        InstagramInsightMetric.LIKES,
        InstagramInsightMetric.COMMENTS,
        InstagramInsightMetric.SHARES,
        InstagramInsightMetric.SAVES,
        InstagramInsightMetric.TOTAL_INTERACTIONS,
    ],
    InstagramMediaType.STORIES: [
        InstagramInsightMetric.IMPRESSIONS,
        InstagramInsightMetric.REACH,
        InstagramInsightMetric.EXITS,
        InstagramInsightMetric.REPLIES,
        InstagramInsightMetric.TAPS_FORWARD,
        InstagramInsightMetric.TAPS_BACKWARD,
    ],
}

# Account metrics
ACCOUNT_METRICS = [
    InstagramInsightMetric.FOLLOWERS_COUNT,
    InstagramInsightMetric.IMPRESSIONS,
    InstagramInsightMetric.REACH,
    InstagramInsightMetric.PROFILE_VIEWS,
    InstagramInsightMetric.WEBSITE_CLICKS,
    InstagramInsightMetric.EMAIL_CONTACTS,
    InstagramInsightMetric.PHONE_CALL_CLICKS,
    InstagramInsightMetric.GET_DIRECTIONS_CLICKS,
    InstagramInsightMetric.TEXT_MESSAGE_CLICKS,
]


def get_media_metrics(media_type: str) -> list:
    """Get appropriate metrics for media type."""
    try:
        mtype = InstagramMediaType(media_type.upper())
        return [m.value for m in MEDIA_METRICS_MAP.get(mtype, [])]
    except ValueError:
        return [m.value for m in MEDIA_METRICS_MAP[InstagramMediaType.IMAGE]]


def get_account_metrics() -> list:
    """Get account-level metrics."""
    return [m.value for m in ACCOUNT_METRICS]