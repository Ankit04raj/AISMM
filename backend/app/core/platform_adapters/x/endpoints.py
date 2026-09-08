"""X (Twitter) API v2 Endpoint Constants."""

from enum import Enum


class XEndpoint(str, Enum):
    """X (Twitter) API v2 endpoints."""

    BASE = "https://api.twitter.com/2"
    UPLOAD_BASE = "https://upload.twitter.com/1.1"
    AUTHORIZE = "https://twitter.com/i/oauth2/authorize"
    ACCESS_TOKEN = "https://api.twitter.com/2/oauth2/token"

    # User & Account
    ME = "/users/me"
    USER_BY_ID = "/users/{id}"
    USER_BY_USERNAME = "/users/by/username/{username}"

    # Tweets & Publishing
    TWEETS = "/tweets"
    TWEET_BY_ID = "/tweets/{id}"
    MEDIA_UPLOAD = "https://upload.twitter.com/1.1/media/upload.json"

    # Engagement & Comments (Replies)
    TWEET_SEARCH = "/tweets/search/recent"
    TWEET_REPLY = "/tweets"
    TWEET_LIKES = "/users/{id}/likes"
    TWEET_RETWEETS = "/users/{id}/retweets"

    # Webhooks & Account Activity API (v1.1)
    ACCOUNT_ACTIVITY = "https://api.twitter.com/1.1/account_activity/all/{env_name}/webhooks.json"
    ACCOUNT_ACTIVITY_SUBSCRIPTIONS = "https://api.twitter.com/1.1/account_activity/all/{env_name}/subscriptions.json"


class XFields(str, Enum):
    """Field expansions for X API requests."""

    TWEET_FIELDS = "id,text,created_at,author_id,public_metrics,entities,attachments,context_annotations"
    USER_FIELDS = "id,name,username,created_at,description,profile_image_url,public_metrics,verified"
    MEDIA_FIELDS = "media_key,type,url,preview_image_url,duration_ms,public_metrics"


class XInsightMetric(str, Enum):
    """X public & organic metrics."""

    IMPRESSION_COUNT = "impression_count"
    LIKE_COUNT = "like_count"
    REPLY_COUNT = "reply_count"
    RETWEET_COUNT = "retweet_count"
    QUOTE_COUNT = "quote_count"
    BOOKMARK_COUNT = "bookmark_count"
    URL_LINK_CLICKS = "url_link_clicks"
    USER_PROFILE_CLICKS = "user_profile_clicks"
