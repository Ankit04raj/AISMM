"""Growth Feature Extraction for Predictive Growth Engine."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class AccountGrowthFeatures:
    """Feature vector for predicting audience and follower growth trajectory."""
    current_followers: int
    posting_frequency_weekly: float  # posts per week
    avg_engagement_rate: float  # percentage, e.g. 4.5%
    follower_velocity_7d: float  # net followers gained in past 7 days
    follower_velocity_30d: float  # net followers gained in past 30 days
    video_ratio: float  # percentage of content that is video/reel
    carousel_ratio: float  # percentage of content that is carousel
    avg_sentiment_score: float  # -1.0 to 1.0 compound sentiment
    follower_following_ratio: float
    platform_code: int  # 0=instagram, 1=facebook, 2=twitter, 3=linkedin, 4=tiktok

    def to_vector(self) -> List[float]:
        """Convert features to numeric list for regression model."""
        return [
            float(self.current_followers),
            float(self.posting_frequency_weekly),
            float(self.avg_engagement_rate),
            float(self.follower_velocity_7d),
            float(self.follower_velocity_30d),
            float(self.video_ratio),
            float(self.carousel_ratio),
            float(self.avg_sentiment_score),
            float(self.follower_following_ratio),
            float(self.platform_code),
        ]


class GrowthFeatureExtractor:
    """Extracts ML growth features from account profiles, metrics, and content stats."""

    PLATFORM_CODES = {
        "instagram": 0,
        "facebook": 1,
        "twitter": 2,
        "linkedin": 3,
        "tiktok": 4,
    }

    @classmethod
    def extract(
        cls,
        platform: str,
        current_followers: int,
        following_count: int = 100,
        posts_last_30_days: int = 12,
        avg_engagement_rate: float = 4.2,
        followers_gained_7d: Optional[int] = None,
        followers_gained_30d: Optional[int] = None,
        video_count: int = 4,
        carousel_count: int = 3,
        total_posts: int = 12,
        avg_sentiment_score: float = 0.35,
    ) -> AccountGrowthFeatures:
        """Extract structured growth features."""
        p_code = cls.PLATFORM_CODES.get(platform.lower(), 0)

        weekly_freq = round((posts_last_30_days / 30.0) * 7.0, 2)
        v_ratio = round(video_count / max(1, total_posts), 2)
        c_ratio = round(carousel_count / max(1, total_posts), 2)
        ff_ratio = round(current_followers / max(1, following_count), 2)

        # Default velocity approximations if not tracked yet
        vel_30d = float(followers_gained_30d) if followers_gained_30d is not None else round(current_followers * 0.035, 1)
        vel_7d = float(followers_gained_7d) if followers_gained_7d is not None else round(vel_30d / 4.0, 1)

        return AccountGrowthFeatures(
            current_followers=current_followers,
            posting_frequency_weekly=weekly_freq,
            avg_engagement_rate=avg_engagement_rate,
            follower_velocity_7d=vel_7d,
            follower_velocity_30d=vel_30d,
            video_ratio=v_ratio,
            carousel_ratio=c_ratio,
            avg_sentiment_score=avg_sentiment_score,
            follower_following_ratio=ff_ratio,
            platform_code=p_code,
        )
