"""LinkedIn Share & Organization Insights (API v2)."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from ...normalization import MetricNormalizer
from ...errors import PlatformError


class LinkedInInsights:
    """Fetches and normalizes LinkedIn Organizational Share Statistics and page metrics."""

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def get_share_insights(self, share_urn: str) -> Dict[str, Any]:
        """Fetch statistics for a specific share/UGC post."""
        client = await self.adapter._get_client()

        org_urn = self.adapter.organization_urn or "urn:li:organization:123456"
        params = {
            "q": "organizationalEntity",
            "organizationalEntity": org_urn,
            "shares": f"List({share_urn})",
        }
        headers = {"X-Restli-Protocol-Version": "2.0.0"}

        resp = await client.get(
            "/v2/organizationalEntityShareStatistics",
            params=params,
            headers=headers,
        )
        if resp.status_code != 200:
            raise PlatformError(f"LinkedIn share insights failed: {resp.text}", platform="linkedin")

        data = resp.json().get("elements", [])
        raw_metrics = {
            "impression_count": 0,
            "click_count": 0,
            "like_count": 0,
            "comment_count": 0,
            "share_count": 0,
            "engagement": 0.0,
        }

        if data:
            stats = data[0].get("totalShareStatistics", {})
            raw_metrics = {
                "impression_count": stats.get("impressionCount", 0),
                "click_count": stats.get("clickCount", 0),
                "like_count": stats.get("likeCount", 0),
                "comment_count": stats.get("commentCount", 0),
                "share_count": stats.get("shareCount", 0),
                "engagement": stats.get("engagement", 0.0),
                "unique_impressions_count": stats.get("uniqueImpressionsCount", 0),
            }

        return MetricNormalizer.normalize_metrics(raw_metrics, "linkedin")

    async def get_page_insights(self, organization_urn: str) -> Dict[str, Any]:
        """Fetch organization follower and page statistics."""
        client = await self.adapter._get_client()
        headers = {"X-Restli-Protocol-Version": "2.0.0"}

        resp = await client.get(
            f"/v2/networkSizes/{organization_urn}?edgeType=CompanyFollowedByMember",
            headers=headers,
        )
        followers = 0
        if resp.status_code == 200:
            followers = resp.json().get("firstDegreeSize", 0)

        raw_metrics = {
            "followers_count": followers,
        }
        return MetricNormalizer.normalize_metrics(raw_metrics, "linkedin")
