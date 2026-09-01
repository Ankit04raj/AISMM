"""Temporal & Contextual Feature Extraction for Scheduling Engine."""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class SchedulingFeatures:
    """Extracted feature vector for post engagement time prediction."""
    hour: int
    day_of_week: int  # 0=Monday, 6=Sunday
    is_weekend: int  # 0 or 1
    sin_hour: float
    cos_hour: float
    sin_dow: float
    cos_dow: float
    caption_length: int
    word_count: int
    hashtag_count: int
    mention_count: int
    has_media: int
    media_type_code: int  # 0=text, 1=image, 2=video, 3=carousel, 4=reel/story
    platform_code: int  # 0=instagram, 1=facebook, 2=twitter, 3=linkedin, 4=other
    follower_count: int = 1000
    historical_avg_engagement: float = 3.5

    def to_vector(self) -> List[float]:
        """Convert features to numeric vector for ML models."""
        return [
            float(self.hour),
            float(self.day_of_week),
            float(self.is_weekend),
            self.sin_hour,
            self.cos_hour,
            self.sin_dow,
            self.cos_dow,
            float(self.caption_length),
            float(self.word_count),
            float(self.hashtag_count),
            float(self.mention_count),
            float(self.has_media),
            float(self.media_type_code),
            float(self.platform_code),
            float(self.follower_count),
            float(self.historical_avg_engagement),
        ]


class SchedulingFeatureExtractor:
    """Extracts ML-ready features from timestamps and content payloads."""

    PLATFORM_MAP = {
        "instagram": 0,
        "facebook": 1,
        "twitter": 2,
        "linkedin": 3,
        "tiktok": 4,
    }

    MEDIA_TYPE_MAP = {
        "text": 0,
        "status": 0,
        "image": 1,
        "photo": 1,
        "video": 2,
        "carousel": 3,
        "reel": 4,
        "story": 4,
    }

    @classmethod
    def extract(
        cls,
        dt: datetime,
        platform: str,
        text: str = "",
        hashtags: Optional[List[str]] = None,
        mentions: Optional[List[str]] = None,
        media_type: str = "image",
        has_media: bool = True,
        follower_count: int = 1000,
        historical_avg_engagement: float = 3.5,
    ) -> SchedulingFeatures:
        """Extract full temporal and contextual feature set."""
        hour = dt.hour
        dow = dt.weekday()
        is_weekend = 1 if dow >= 5 else 0

        # Cyclical temporal encoding for continuous periodic transitions
        sin_hour = math.sin(2 * math.pi * hour / 24.0)
        cos_hour = math.cos(2 * math.pi * hour / 24.0)
        sin_dow = math.sin(2 * math.pi * dow / 7.0)
        cos_dow = math.cos(2 * math.pi * dow / 7.0)

        clean_text = text or ""
        words = clean_text.split()
        tag_count = len(hashtags) if hashtags is not None else clean_text.count("#")
        mention_count = len(mentions) if mentions is not None else clean_text.count("@")

        p_code = cls.PLATFORM_MAP.get(platform.lower(), 0)
        m_code = cls.MEDIA_TYPE_MAP.get(media_type.lower(), 1)

        return SchedulingFeatures(
            hour=hour,
            day_of_week=dow,
            is_weekend=is_weekend,
            sin_hour=round(sin_hour, 4),
            cos_hour=round(cos_hour, 4),
            sin_dow=round(sin_dow, 4),
            cos_dow=round(cos_dow, 4),
            caption_length=len(clean_text),
            word_count=len(words),
            hashtag_count=tag_count,
            mention_count=mention_count,
            has_media=1 if has_media else 0,
            media_type_code=m_code,
            platform_code=p_code,
            follower_count=follower_count,
            historical_avg_engagement=historical_avg_engagement,
        )
