"""LinkedIn API v2 & REST Endpoint Constants."""

from enum import Enum


class LinkedInEndpoint(str, Enum):
    """LinkedIn REST & Community Management endpoints."""

    BASE = "https://api.linkedin.com"
    AUTHORIZE = "https://www.linkedin.com/oauth/v2/authorization"
    ACCESS_TOKEN = "https://api.linkedin.com/oauth/v2/accessToken"

    # Profile & Organizations
    USERINFO = "https://api.linkedin.com/v2/userinfo"
    ME = "https://api.linkedin.com/v2/me"
    ORGANIZATION_ACLS = "https://api.linkedin.com/v2/organizationalEntityAcls"
    ORGANIZATION = "https://api.linkedin.com/v2/organizations/{id}"

    # Posts & UGC
    UGC_POSTS = "https://api.linkedin.com/v2/ugcPosts"
    REST_POSTS = "https://api.linkedin.com/rest/posts"
    SHARES = "https://api.linkedin.com/v2/shares"
    POST_BY_ID = "https://api.linkedin.com/rest/posts/{id}"

    # Media Upload (Assets API)
    ASSETS = "https://api.linkedin.com/v2/assets?action=registerUpload"
    IMAGES = "https://api.linkedin.com/rest/images?action=initializeUpload"

    # Analytics & Insights
    SHARE_STATISTICS = "https://api.linkedin.com/v2/organizationalEntityShareStatistics"
    PAGE_STATISTICS = "https://api.linkedin.com/v2/organizationPageStatistics"

    # Social Actions & Comments
    SOCIAL_ACTIONS = "https://api.linkedin.com/v2/socialActions/{entity_urn}"
    COMMENTS = "https://api.linkedin.com/v2/socialActions/{entity_urn}/comments"
    COMMENT_BY_ID = "https://api.linkedin.com/v2/socialActions/{entity_urn}/comments/{comment_urn}"


class LinkedInFields(str, Enum):
    """Field projections for LinkedIn API requests."""

    ORGANIZATION_PROJECTION = "(id,localizedName,vanityName,logoV2)"
    POST_PROJECTION = "(id,author,commentary,createdAt,publishedAt,lifecycleState)"
    SHARE_STATS_PROJECTION = "(elements*(organizationalEntity,totalShareStatistics*(shareCount,clickCount,engagement,likeCount,commentCount,impressionCount)))"


class LinkedInInsightMetric(str, Enum):
    """LinkedIn organizational share statistics."""

    IMPRESSION_COUNT = "impressionCount"
    CLICK_COUNT = "clickCount"
    ENGAGEMENT = "engagement"
    LIKE_COUNT = "likeCount"
    COMMENT_COUNT = "commentCount"
    SHARE_COUNT = "shareCount"
    UNIQUE_IMPRESSIONS_COUNT = "uniqueImpressionsCount"
