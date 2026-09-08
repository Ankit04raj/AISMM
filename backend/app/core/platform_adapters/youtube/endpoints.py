"""YouTube Data API v3 & YouTube Analytics Endpoint Constants."""

from enum import Enum


class YouTubeEndpoint(str, Enum):
    """YouTube API endpoints."""

    BASE = "https://www.googleapis.com/youtube/v3"
    UPLOAD_BASE = "https://www.googleapis.com/upload/youtube/v3"
    AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"
    ACCESS_TOKEN = "https://oauth2.googleapis.com/token"
    REVOKE_TOKEN = "https://oauth2.googleapis.com/revoke"

    # Channels & Profile
    CHANNELS = "/channels"

    # Videos & Uploads
    VIDEOS = "/videos"
    VIDEOS_UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    THUMBNAILS = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"

    # Comment Threads & Comments
    COMMENT_THREADS = "/commentThreads"
    COMMENTS = "/comments"

    # Playlists
    PLAYLISTS = "/playlists"
    PLAYLIST_ITEMS = "/playlistItems"

    # YouTube Analytics API
    ANALYTICS_REPORTS = "https://youtubeanalytics.googleapis.com/v2/reports"


class YouTubeFields(str, Enum):
    """Field sets for YouTube API requests."""

    VIDEO_BASIC = "snippet,status,statistics"
    CHANNEL_BASIC = "snippet,statistics,contentDetails"
    COMMENT_BASIC = "snippet,replies"


class YouTubeInsightMetric(str, Enum):
    """YouTube video & channel metrics."""

    VIEWS = "views"
    ESTIMATED_MINUTES_WATCHED = "estimatedMinutesWatched"
    AVERAGE_VIEW_DURATION = "averageViewDuration"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SUBSCRIBERS_GAINED = "subscribersGained"
    SUBSCRIBERS_LOST = "subscribersLost"
