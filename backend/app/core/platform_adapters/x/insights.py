"""X (Twitter) Insights and Engagement Metrics (API v2)."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from ...normalization import MetricNormalizer
from ...errors import PlatformError


class XInsights:
    """Fetches and normalizes public and non-public tweet and user metrics from X API v2."""

    TWEET_FIELDS = "id,text,created_at,public_metrics,non_public_metrics,organic_metrics"

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def get_tweet_insights(self, tweet_id: str) -> Dict[str, Any]:
        """Fetch tweet engagement metrics and normalize to AISMM canonical categories."""
        client = await self.adapter._get_client()

        resp = await client.get(
            f"/tweets/{tweet_id}",
            params={"tweet.fields": "public_metrics,non_public_metrics,organic_metrics"},
        )
        if resp.status_code != 200:
            raise PlatformError(f"X tweet insights failed: {resp.text}", platform="x")

        data = resp.json().get("data", {})
        pub_metrics = data.get("public_metrics", {})
        org_metrics = data.get("organic_metrics", {})
        non_pub_metrics = data.get("non_public_metrics", {})

        raw_metrics = {
            "like_count": pub_metrics.get("like_count", 0),
            "retweet_count": pub_metrics.get("retweet_count", 0),
            "reply_count": pub_metrics.get("reply_count", 0),
            "quote_count": pub_metrics.get("quote_count", 0),
            "bookmark_count": pub_metrics.get("bookmark_count", 0),
            "impression_count": pub_metrics.get("impression_count", 0) or org_metrics.get("impression_count", 0),
            "url_link_clicks": org_metrics.get("url_link_clicks", 0) or non_pub_metrics.get("url_link_clicks", 0),
            "user_profile_clicks": org_metrics.get("user_profile_clicks", 0),
        }

        return MetricNormalizer.normalize_metrics(raw_metrics, "x")

    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Fetch user-level audience and follower metrics."""
        client = await self.adapter._get_client()

        resp = await client.get(
            f"/users/{user_id}",
            params={"user.fields": "public_metrics"},
        )
        if resp.status_code != 200:
            raise PlatformError(f"X user insights failed: {resp.text}", platform="x")

        data = resp.json().get("data", {})
        pub = data.get("public_metrics", {})
        raw_metrics = {
            "followers_count": pub.get("followers_count", 0),
            "following_count": pub.get("following_count", 0),
            "tweet_count": pub.get("tweet_count", 0),
            "listed_count": pub.get("listed_count", 0),
        }

        return MetricNormalizer.normalize_metrics(raw_metrics, "x")
