"""Facebook Insights and Analytics fetcher."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from ...normalization import MetricNormalizer
from ...errors import PlatformError


class FacebookInsights:
    """Fetches and normalizes Facebook Page and Post insights."""

    DEFAULT_POST_METRICS = [
        "post_impressions",
        "post_impressions_unique",
        "post_engaged_users",
        "post_reactions_like_total",
        "post_clicks",
        "post_video_views",
    ]

    DEFAULT_PAGE_METRICS = [
        "page_impressions",
        "page_engaged_users",
        "page_fans",
        "page_post_engagements",
    ]

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def get_post_insights(self, post_id: str, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch post insights and normalize."""
        client = await self.adapter._get_client()
        metric_list = metrics or self.DEFAULT_POST_METRICS

        resp = await client.get(
            f"/{post_id}/insights",
            params={"metric": ",".join(metric_list)},
        )
        if resp.status_code != 200:
            raise PlatformError(f"Facebook insights failed: {resp.text}", platform="facebook")

        data = resp.json()
        raw_metrics = {}
        for item in data.get("data", []):
            name = item.get("name")
            values = item.get("values", [])
            if name and values:
                raw_metrics[name] = values[-1].get("value", 0)

        return MetricNormalizer.normalize_metrics(raw_metrics, "facebook")

    async def get_page_insights(self, metrics: Optional[List[str]] = None, period: str = "day") -> Dict[str, Any]:
        """Fetch page-level insights."""
        client = await self.adapter._get_client()
        page_id = self.adapter.page_id or "me"
        metric_list = metrics or self.DEFAULT_PAGE_METRICS

        resp = await client.get(
            f"/{page_id}/insights",
            params={"metric": ",".join(metric_list), "period": period},
        )
        if resp.status_code != 200:
            raise PlatformError(f"Facebook page insights failed: {resp.text}", platform="facebook")

        data = resp.json()
        raw_metrics = {}
        for item in data.get("data", []):
            name = item.get("name")
            values = item.get("values", [])
            if name and values:
                raw_metrics[name] = values[-1].get("value", 0)

        return MetricNormalizer.normalize_metrics(raw_metrics, "facebook")
