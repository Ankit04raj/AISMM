"""YouTube Video & Channel Analytics (Data API v3 & Analytics API)."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from ...normalization import MetricNormalizer
from ...errors import PlatformError


class YouTubeInsights:
    """Fetches and normalizes YouTube video statistics and channel performance."""

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def get_video_insights(self, video_id: str) -> Dict[str, Any]:
        """Fetch video view count, like count, and comment count from YouTube Data API."""
        client = await self.adapter._get_client()

        resp = await client.get(
            "/videos",
            params={"part": "statistics,contentDetails", "id": video_id},
        )
        if resp.status_code != 200:
            raise PlatformError(f"YouTube video statistics failed: {resp.text}", platform="youtube")

        items = resp.json().get("items", [])
        if not items:
            return MetricNormalizer.normalize_metrics({}, "youtube")

        stats = items[0].get("statistics", {})
        raw_metrics = {
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "shares": 0,
            "estimatedMinutesWatched": int(stats.get("viewCount", 0)) * 2,
        }

        return MetricNormalizer.normalize_metrics(raw_metrics, "youtube")

    async def get_channel_insights(self, channel_id: str) -> Dict[str, Any]:
        """Fetch channel subscribers, total video count, and aggregate views."""
        client = await self.adapter._get_client()

        params = {"part": "statistics"}
        if channel_id == "mine":
            params["mine"] = "true"
        else:
            params["id"] = channel_id

        resp = await client.get("/channels", params=params)
        if resp.status_code != 200:
            raise PlatformError(f"YouTube channel statistics failed: {resp.text}", platform="youtube")

        items = resp.json().get("items", [])
        if not items:
            return MetricNormalizer.normalize_metrics({}, "youtube")

        stats = items[0].get("statistics", {})
        raw_metrics = {
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "followers": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "views": int(stats.get("viewCount", 0)),
        }

        return MetricNormalizer.normalize_metrics(raw_metrics, "youtube")
