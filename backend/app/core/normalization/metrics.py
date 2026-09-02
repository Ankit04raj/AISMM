"""Metrics normalization utilities for cross-platform analytics."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .content import UniversalMetrics


@dataclass
class NormalizedMetric:
    """Platform-neutral metric record used by analytics and scheduling."""
    metric_type: str
    value: float
    source_platform: str
    original_metric: str = ""
    timestamp: Optional[str] = None


class MetricNormalizer:
    """Normalizes platform-specific metrics to universal format."""

    METRIC_TYPE_MAP = {
        "like_count": "LIKE",
        "likes": "LIKE",
        "retweet_count": "SHARE",
        "retweets": "SHARE",
        "share_count": "SHARE",
        "shares": "SHARE",
        "view_count": "VIEW",
        "views": "VIEW",
        "reaction_count": "REACTION",
        "reactions": "REACTION",
        "comment_count": "COMMENT",
        "comments": "COMMENT",
        "save_count": "SAVE",
        "saves": "SAVE",
        "click_count": "CLICK",
        "clicks": "CLICK",
        "impression_count": "IMPRESSION",
        "impressions": "IMPRESSION",
    }

    @classmethod
    def normalize_metric(cls, metric: Dict[str, Any]) -> NormalizedMetric:
        """Convert a raw metric into the platform-neutral metric representation."""
        raw_metric_name = str(metric.get("metric_type") or metric.get("original_metric") or "").lower()
        metric_key = raw_metric_name.replace("_count", "").replace("_total", "")
        normalized_type = cls.METRIC_TYPE_MAP.get(raw_metric_name, cls.METRIC_TYPE_MAP.get(metric_key, "UNKNOWN"))
        if normalized_type == "UNKNOWN":
            normalized_type = str(metric.get("metric_type", "UNKNOWN")).upper()

        return NormalizedMetric(
            metric_type=normalized_type,
            value=float(metric.get("value", 0) or 0),
            source_platform=str(metric.get("source_platform") or metric.get("platform") or "unknown"),
            original_metric=str(metric.get("original_metric") or metric.get("metric_type") or ""),
            timestamp=metric.get("timestamp"),
        )

    # Platform-specific metric mappings to universal metrics
    PLATFORM_METRIC_MAP = {
        "instagram": {
            "impressions": "impressions",
            "reach": "reach",
            "likes": "likes",
            "comments": "comments",
            "shares": "shares",
            "saved": "saves",
            "video_views": "video_views",
            "profile_visits": "profile_visits",
            "follows": "followers_gained",
            "email_contacts": "clicks",
            "phone_call_clicks": "clicks",
            "text_message_clicks": "clicks",
            "get_directions_clicks": "clicks",
            "website_clicks": "clicks",
        },
        "twitter": {
            "impression_count": "impressions",
            "retweet_count": "shares",
            "reply_count": "comments",
            "like_count": "likes",
            "quote_count": "shares",
            "bookmark_count": "saves",
            "video_view_count": "video_views",
            "url_link_clicks": "clicks",
            "user_profile_clicks": "profile_visits",
        },
        "x": {
            "impression_count": "impressions",
            "retweet_count": "shares",
            "reply_count": "comments",
            "like_count": "likes",
            "quote_count": "shares",
            "bookmark_count": "saves",
            "video_view_count": "video_views",
            "url_link_clicks": "clicks",
            "user_profile_clicks": "profile_visits",
        },
        "linkedin": {
            "impression_count": "impressions",
            "impressions": "impressions",
            "click_count": "clicks",
            "clicks": "clicks",
            "like_count": "likes",
            "likes": "likes",
            "comment_count": "comments",
            "comments": "comments",
            "share_count": "shares",
            "shares": "shares",
            "engagement": "engagements",
        },
        "youtube": {
            "views": "impressions",
            "view_count": "impressions",
            "likes": "likes",
            "like_count": "likes",
            "comments": "comments",
            "comment_count": "comments",
            "shares": "shares",
            "estimatedminuteswatched": "video_watch_time",
        },
        "facebook": {
            "post_impressions": "impressions",
            "post_impressions_unique": "reach",
            "post_engaged_users": "engagements",
            "post_reactions_like_total": "likes",
            "post_comments": "comments",
            "post_shares": "shares",
            "post_video_views": "video_views",
            "post_video_complete_views_30s": "video_views",
        },
        "tiktok": {
            "impressions": "impressions",
            "reach": "reach",
            "likes": "likes",
            "comments": "comments",
            "shares": "shares",
            "saves": "saves",
            "video_views": "video_views",
            "total_play_time": "engagements",
            "average_watch_time": "engagements",
        },
    }

    # Metrics that are engagement actions
    ENGAGEMENT_METRICS = {
        "likes", "comments", "shares", "saves", "clicks",
        "retweets", "replies", "quotes", "bookmarks",
        "reactions", "video_views",
    }

    @classmethod
    def normalize_metrics(
        cls,
        raw_metrics: Dict[str, Any],
        platform: str,
    ) -> Dict[str, Any]:
        """Normalize raw platform metrics to universal format."""
        mapping = cls.PLATFORM_METRIC_MAP.get(platform.lower(), {})

        normalized = {}
        for raw_key, value in raw_metrics.items():
            universal_key = mapping.get(raw_key.lower())
            if universal_key:
                if universal_key in normalized:
                    # Sum duplicate metrics (e.g., multiple click types)
                    if isinstance(normalized[universal_key], (int, float)) and isinstance(value, (int, float)):
                        normalized[universal_key] += value
                else:
                    normalized[universal_key] = value

        # Calculate engagement rate if we have impressions
        if "impressions" in normalized and normalized["impressions"] > 0:
            engagements = sum(
                normalized.get(k, 0)
                for k in cls.ENGAGEMENT_METRICS
                if k in normalized
            )
            normalized["engagement_rate"] = round((engagements / normalized["impressions"]) * 100, 2)

        return {
            "normalized": normalized,
            "raw": raw_metrics,
            "platform": platform,
            "mapped_fields": list(mapping.keys()),
        }

    @classmethod
    def normalize_time_series(
        cls,
        time_series: Dict[str, List[Dict[str, Any]]],
        platform: str,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Normalize time series metrics."""
        mapping = cls.PLATFORM_METRIC_MAP.get(platform.lower(), {})

        normalized = {}
        for raw_key, data_points in time_series.items():
            universal_key = mapping.get(raw_key.lower())
            if universal_key:
                if universal_key not in normalized:
                    normalized[universal_key] = []
                for point in data_points:
                    # Ensure timestamp format
                    timestamp = point.get("end_time") or point.get("timestamp")
                    value = point.get("value")
                    if timestamp and value is not None:
                        normalized[universal_key].append({
                            "timestamp": timestamp,
                            "value": value,
                        })

        return normalized

    @classmethod
    def aggregate_metrics(
        cls,
        metrics_list: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Aggregate multiple metric sets (e.g., cross-platform totals)."""
        aggregated = {}

        for metrics in metrics_list:
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    aggregated[key] = aggregated.get(key, 0) + value

        # Recalculate engagement rate
        if "impressions" in aggregated and aggregated["impressions"] > 0:
            engagements = sum(
                aggregated.get(k, 0)
                for k in cls.ENGAGEMENT_METRICS
                if k in aggregated
            )
            aggregated["engagement_rate"] = round((engagements / aggregated["impressions"]) * 100, 2)

        return aggregated

    @classmethod
    def calculate_growth(
        cls,
        current: Dict[str, Any],
        previous: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate growth rates between two metric sets."""
        growth = {}

        for key in set(current.keys()) | set(previous.keys()):
            curr_val = current.get(key, 0)
            prev_val = previous.get(key, 0)

            if isinstance(curr_val, (int, float)) and isinstance(prev_val, (int, float)):
                if prev_val > 0:
                    growth[key] = round(((curr_val - prev_val) / prev_val) * 100, 2)
                elif curr_val > 0:
                    growth[key] = 100.0
                else:
                    growth[key] = 0.0

        return growth

    @classmethod
    def get_top_metrics(
        cls,
        metrics: Dict[str, Any],
        top_n: int = 5,
        exclude: Optional[List[str]] = None,
    ) -> List[tuple]:
        """Get top N metrics by value."""
        exclude = exclude or ["engagement_rate", "fetched_at", "period", "raw_data"]

        sorted_metrics = sorted(
            [(k, v) for k, v in metrics.items() if k not in exclude and isinstance(v, (int, float))],
            key=lambda x: x[1],
            reverse=True,
        )

        return sorted_metrics[:top_n]


@dataclass
class MetricSummary:
    """Summary of metrics for reporting."""
    platform: str
    entity_id: str
    entity_type: str
    period: str
    total_impressions: int = 0
    total_reach: int = 0
    total_engagements: int = 0
    engagement_rate: float = 0.0
    top_metrics: List[tuple] = field(default_factory=list)
    growth: Dict[str, float] = field(default_factory=dict)
    fetched_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "period": self.period,
            "total_impressions": self.total_impressions,
            "total_reach": self.total_reach,
            "total_engagements": self.total_engagements,
            "engagement_rate": self.engagement_rate,
            "top_metrics": self.top_metrics,
            "growth": self.growth,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }

    @classmethod
    def from_normalized(cls, normalized: Dict[str, Any], platform: str, entity_id: str, entity_type: str) -> "MetricSummary":
        """Create summary from normalized metrics."""
        summary = cls(
            platform=platform,
            entity_id=entity_id,
            entity_type=entity_type,
            period=normalized.get("period", "lifetime"),
            fetched_at=datetime.fromisoformat(normalized["fetched_at"]) if normalized.get("fetched_at") else None,
        )

        summary.total_impressions = normalized.get("impressions", 0)
        summary.total_reach = normalized.get("reach", 0)
        summary.engagement_rate = normalized.get("engagement_rate", 0.0)

        # Calculate total engagements
        engagement_keys = ["likes", "comments", "shares", "saves", "clicks", "video_views"]
        summary.total_engagements = sum(normalized.get(k, 0) for k in engagement_keys)

        # Top metrics
        summary.top_metrics = MetricNormalizer.get_top_metrics(normalized)

        return summary