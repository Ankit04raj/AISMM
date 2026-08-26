"""Instagram Insights & Metrics Fetcher."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import httpx

from .adapter import InstagramAdapter
from .endpoints import (
    InstagramInsightMetric,
    InstagramInsightPeriod,
    InstagramMediaType,
    get_media_metrics,
    get_account_metrics,
)
from ...normalization import MetricNormalizer


@dataclass
class InsightDataPoint:
    """Single insight data point."""
    name: str
    period: str
    values: List[Dict[str, Any]]
    title: str
    description: str


@dataclass
class MediaInsights:
    """Media-level insights container."""
    media_id: str
    media_type: str
    fetched_at: str
    metrics: Dict[str, Any]
    normalized: Dict[str, Any]


@dataclass
class AccountInsights:
    """Account-level insights container."""
    ig_user_id: str
    fetched_at: str
    metrics: Dict[str, Any]
    normalized: Dict[str, Any]


class InstagramInsights:
    """Fetches and processes Instagram insights."""

    def __init__(self, adapter: InstagramAdapter):
        self.adapter = adapter
        self._client = adapter._http_client

    async def get_media_insights(
        self,
        media_id: str,
        media_type: str,
        metrics: Optional[List[str]] = None,
        period: str = "lifetime",
    ) -> MediaInsights:
        """Get insights for a specific media item."""
        client = self.adapter._http_client or await self.adapter._get_client()

        # Use media-type appropriate metrics if not specified
        if metrics is None:
            metrics = get_media_metrics(media_type)

        response = await client.get(
            f"/{media_id}/insights",
            params={
                "metric": ",".join(metrics),
                "period": period,
            }
        )

        if response.status_code != 200:
            raise InsightsError(
                f"Media insights fetch failed: {response.text}",
                platform="instagram",
                status_code=response.status_code,
            )

        data = response.json()
        raw_metrics = self._parse_insights_response(data)

        # Normalize using our metric normalizer
        normalized = MetricNormalizer.normalize_metrics(raw_metrics, "instagram")

        return MediaInsights(
            media_id=media_id,
            media_type=media_type,
            fetched_at=datetime.utcnow().isoformat(),
            metrics=raw_metrics,
            normalized=normalized["normalized"],
        )

    async def get_multiple_media_insights(
        self,
        media_ids: List[str],
        media_types: Dict[str, str],
        metrics: Optional[List[str]] = None,
        period: str = "lifetime",
    ) -> List[MediaInsights]:
        """Get insights for multiple media items (batch)."""
        results = []
        for media_id in media_ids:
            media_type = media_types.get(media_id, "IMAGE")
            try:
                insights = await self.get_media_insights(media_id, media_type, metrics, period)
                results.append(insights)
            except Exception as e:
                # Continue on individual failures
                results.append(MediaInsights(
                    media_id=media_id,
                    media_type=media_type,
                    fetched_at=datetime.utcnow().isoformat(),
                    metrics={},
                    normalized={},
                ))
        return results

    async def get_account_insights(
        self,
        metrics: Optional[List[str]] = None,
        period: str = "day",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> AccountInsights:
        """Get account-level insights."""
        client = self.adapter._http_client or await self.adapter._get_client()

        if metrics is None:
            metrics = get_account_metrics()

        params = {
            "metric": ",".join(metrics),
            "period": period,
        }

        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())

        response = await client.get(
            f"/{self.adapter.ig_user_id}/insights",
            params=params
        )

        if response.status_code != 200:
            raise InsightsError(
                f"Account insights fetch failed: {response.text}",
                platform="instagram",
                status_code=response.status_code,
            )

        data = response.json()
        raw_metrics = self._parse_insights_response(data)

        normalized = MetricNormalizer.normalize_metrics(raw_metrics, "instagram")

        return AccountInsights(
            ig_user_id=self.adapter.ig_user_id,
            fetched_at=datetime.utcnow().isoformat(),
            metrics=raw_metrics,
            normalized=normalized["normalized"],
        )

    async def get_account_insights_time_series(
        self,
        metrics: Optional[List[str]] = None,
        period: str = "day",
        days: int = 30,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get account insights as time series."""
        client = self.adapter._http_client or await self.adapter._get_client()

        if metrics is None:
            metrics = get_account_metrics()

        until = datetime.utcnow()
        since = until - timedelta(days=days)

        params = {
            "metric": ",".join(metrics),
            "period": period,
            "since": int(since.timestamp()),
            "until": int(until.timestamp()),
        }

        response = await client.get(
            f"/{self.adapter.ig_user_id}/insights",
            params=params
        )

        if response.status_code != 200:
            raise InsightsError(
                f"Account time series failed: {response.text}",
                platform="instagram",
            )

        data = response.json()
        return self._parse_time_series_response(data)

    async def get_media_insights_time_series(
        self,
        media_id: str,
        media_type: str,
        metrics: Optional[List[str]] = None,
        period: str = "lifetime",
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get media insights as time series (if supported)."""
        # Note: Media insights typically only support 'lifetime' period
        # Some metrics support day/week for recent media
        client = self.adapter._http_client or await self.adapter._get_client()

        if metrics is None:
            metrics = get_media_metrics(media_type)

        # For media, only lifetime is generally supported
        params = {
            "metric": ",".join(metrics),
            "period": period,
        }

        response = await client.get(f"/{media_id}/insights", params=params)

        if response.status_code != 200:
            raise InsightsError(
                f"Media time series failed: {response.text}",
                platform="instagram",
            )

        data = response.json()
        return self._parse_time_series_response(data)

    async def get_story_insights(
        self,
        story_id: str,
        metrics: Optional[List[str]] = None,
    ) -> MediaInsights:
        """Get insights for a story."""
        story_metrics = metrics or [
            InstagramInsightMetric.IMPRESSIONS.value,
            InstagramInsightMetric.REACH.value,
            InstagramInsightMetric.EXITS.value,
            InstagramInsightMetric.REPLIES.value,
            InstagramInsightMetric.TAPS_FORWARD.value,
            InstagramInsightMetric.TAPS_BACKWARD.value,
        ]

        return await self.get_media_insights(story_id, InstagramMediaType.STORIES, story_metrics)

    async def get_reel_insights(
        self,
        reel_id: str,
        metrics: Optional[List[str]] = None,
    ) -> MediaInsights:
        """Get insights for a reel."""
        reel_metrics = metrics or [
            InstagramInsightMetric.PLAYS.value,
            InstagramInsightMetric.REACH.value,
            InstagramInsightMetric.LIKES.value,
            InstagramInsightMetric.COMMENTS.value,
            InstagramInsightMetric.SHARES.value,
            InstagramInsightMetric.SAVES.value,
            InstagramInsightMetric.TOTAL_INTERACTIONS.value,
        ]

        return await self.get_media_insights(reel_id, InstagramMediaType.REELS, reel_metrics)

    def _parse_insights_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse insights API response to flat metric dict."""
        metrics = {}
        for item in data.get("data", []):
            name = item.get("name")
            values = item.get("values", [])
            if values and name:
                # Get the latest value
                latest = values[-1] if values else {}
                value = latest.get("value", 0)
                metrics[name] = value
        return metrics

    def _parse_time_series_response(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse insights response as time series."""
        series = {}
        for item in data.get("data", []):
            name = item.get("name")
            values = item.get("values", [])
            if name and values:
                series[name] = [
                    {
                        "timestamp": v.get("end_time"),
                        "value": v.get("value"),
                    }
                    for v in values
                ]
        return series

    async def get_top_media(
        self,
        metric: str = "impressions",
        limit: int = 10,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get top performing media by metric."""
        client = self.adapter._http_client or await self.adapter._get_client()

        params = {
            "fields": f"id,caption,media_type,media_url,permalink,timestamp,{metric}",
            "limit": limit,
        }

        if since:
            params["since"] = int(since.timestamp())

        response = await client.get(f"/{self.adapter.ig_user_id}/media", params=params)

        if response.status_code != 200:
            return []

        data = response.json()
        media = data.get("data", [])

        # Sort by metric (descending)
        media.sort(key=lambda x: x.get(metric, 0), reverse=True)
        return media[:limit]

    async def get_follower_demographics(self) -> Dict[str, Any]:
        """Get follower demographics (age, gender, location)."""
        client = self.adapter._http_client or await self.adapter._get_client()

        metrics = [
            "follower_demographics",
            "follower_gender",
            "follower_age",
            "follower_locale",
            "follower_city",
            "follower_country",
        ]

        response = await client.get(
            f"/{self.adapter.ig_user_id}/insights",
            params={"metric": ",".join(metrics), "period": "lifetime"}
        )

        if response.status_code != 200:
            return {}

        data = response.json()
        return self._parse_insights_response(data)


class InsightsError(Exception):
    """Insights fetch error."""
    def __init__(self, message: str, platform: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.platform = platform
        self.status_code = status_code