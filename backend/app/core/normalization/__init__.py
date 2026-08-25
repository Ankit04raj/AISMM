"""Normalization utilities for platform-native content and metrics."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class NormalizedContent:
    """Platform-neutral representation of content."""

    text: str = ""
    caption: str = ""
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    content_type: str = "post"
    location: Optional[str] = None
    language: str = "en"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedMetric:
    """Platform-neutral representation of an engagement metric."""

    metric_type: str
    value: float | int
    source_platform: str
    original_metric: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    raw_data: Dict[str, Any] = field(default_factory=dict)


class ContentNormalizer:
    """Normalizes raw platform content into AISMM internal structures."""

    @staticmethod
    def normalize_content(raw: Dict[str, Any]) -> NormalizedContent:
        text = str(raw.get("text") or raw.get("content") or raw.get("caption") or "")
        caption = str(raw.get("caption") or raw.get("title") or "")

        hashtags = ContentNormalizer._extract_hashtags(text or caption)
        mentions = ContentNormalizer._extract_mentions(text or caption)
        links = ContentNormalizer._extract_links(text or caption)

        return NormalizedContent(
            text=text,
            caption=caption,
            hashtags=hashtags,
            mentions=mentions,
            links=links,
            content_type=str(raw.get("content_type") or raw.get("type") or "post"),
            location=raw.get("location"),
            language=str(raw.get("language") or "en"),
            metadata={k: v for k, v in raw.items() if k not in {"text", "content", "caption", "title", "location", "language", "content_type", "type"}},
        )

    @staticmethod
    def _extract_hashtags(value: str) -> List[str]:
        found = re.findall(r"#([A-Za-z0-9_]+)", value or "")
        return list(dict.fromkeys(tag.lower() for tag in found))

    @staticmethod
    def _extract_mentions(value: str) -> List[str]:
        found = re.findall(r"@([A-Za-z0-9_]+)", value or "")
        return list(dict.fromkeys(tag.lower() for tag in found))

    @staticmethod
    def _extract_links(value: str) -> List[str]:
        found = re.findall(r"https?://\S+|www\.\S+", value or "")
        return found


class MetricNormalizer:
    """Normalizes platform-specific metric names into common AISMM metrics."""

    _NORM_MAP = {
        "like": "LIKE",
        "likes": "LIKE",
        "love": "LIKE",
        "heart": "LIKE",
        "reaction": "REACTION",
        "reactions": "REACTION",
        "comment": "COMMENT",
        "comments": "COMMENT",
        "share": "SHARE",
        "shares": "SHARE",
        "retweet": "SHARE",
        "retweets": "SHARE",
        "repost": "SHARE",
        "reposts": "SHARE",
        "view": "VIEW",
        "views": "VIEW",
        "save": "SAVE",
        "saves": "SAVE",
        "impression": "IMPRESSION",
        "impressions": "IMPRESSION",
        "reach": "REACH",
        "followers": "FOLLOWER",
        "follower": "FOLLOWER",
        "click": "CLICK",
        "clicks": "CLICK",
        "watch": "VIEW",
    }

    @staticmethod
    def normalize_metric(raw: Dict[str, Any]) -> NormalizedMetric:
        metric_name = str(raw.get("metric_type") or raw.get("name") or raw.get("type") or "unknown")
        source_platform = str(raw.get("source_platform") or raw.get("platform") or "unknown").lower()
        value = raw.get("value", raw.get("count", 0))
        original_metric = raw.get("original_metric") or metric_name

        metric_type = MetricNormalizer._normalize_metric_name(metric_name)

        return NormalizedMetric(
            metric_type=metric_type,
            value=value,
            source_platform=source_platform,
            original_metric=str(original_metric),
            raw_data=dict(raw),
        )

    @staticmethod
    def normalize_metrics(raw_metrics: Iterable[Dict[str, Any]]) -> List[NormalizedMetric]:
        return [MetricNormalizer.normalize_metric(metric) for metric in raw_metrics]

    @staticmethod
    def _normalize_metric_name(metric_name: str) -> str:
        key = metric_name.lower().replace("-", "_").replace(" ", "_")
        for alias, normalized in MetricNormalizer._NORM_MAP.items():
            if alias in key:
                return normalized
        return key.upper()


__all__ = [
    "NormalizedContent",
    "NormalizedMetric",
    "ContentNormalizer",
    "MetricNormalizer",
]
