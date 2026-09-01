"""Facebook Graph API Endpoint Constants."""

from enum import Enum


class FacebookEndpoint(str, Enum):
    """Facebook Graph API endpoints."""

    BASE = "https://graph.facebook.com/v19.0"
    AUTHORIZE = "https://www.facebook.com/v19.0/dialog/oauth"
    ACCESS_TOKEN = "https://graph.facebook.com/v19.0/oauth/access_token"

    # User & Pages
    ME = "/me"
    ME_ACCOUNTS = "/me/accounts"
    PAGE = "/{page_id}"

    # Feed Publishing & Management
    FEED = "/{page_id}/feed"
    PHOTOS = "/{page_id}/photos"
    VIDEOS = "/{page_id}/videos"
    POST = "/{post_id}"

    # Insights
    POST_INSIGHTS = "/{post_id}/insights"
    PAGE_INSIGHTS = "/{page_id}/insights"

    # Comments
    COMMENTS = "/{post_id}/comments"
    COMMENT = "/{comment_id}"
    COMMENT_REPLIES = "/{comment_id}/comments"

    # Webhooks
    SUBSCRIBED_APPS = "/{page_id}/subscribed_apps"


class FacebookFields(str, Enum):
    """Common field sets for Facebook API requests."""

    POST_BASIC = "id,message,created_time,permalink_url,shares"
    POST_FULL = "id,message,created_time,permalink_url,shares,reactions.summary(total_count),comments.summary(total_count),attachments"
    PAGE_BASIC = "id,name,category,link,picture,fan_count"
    PAGE_FULL = "id,name,category,link,picture,fan_count,followers_count,about,website,phone,emails"
    COMMENT_BASIC = "id,message,created_time,from,like_count,comment_count"
    COMMENT_FULL = "id,message,created_time,from,like_count,comment_count,is_hidden,parent"


class FacebookInsightMetric(str, Enum):
    """Facebook insight metrics."""

    POST_IMPRESSIONS = "post_impressions"
    POST_IMPRESSIONS_UNIQUE = "post_impressions_unique"
    POST_ENGAGED_USERS = "post_engaged_users"
    POST_REACTIONS_LIKE_TOTAL = "post_reactions_like_total"
    POST_CLICKS = "post_clicks"
    POST_VIDEO_VIEWS = "post_video_views"
    PAGE_FANS = "page_fans"
    PAGE_IMPRESSIONS = "page_impressions"
    PAGE_ENGAGED_USERS = "page_engaged_users"
    PAGE_POST_ENGAGEMENTS = "page_post_engagements"
