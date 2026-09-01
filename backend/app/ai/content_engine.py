"""Unified AI Content Engine for Multi-Platform Social Media Optimization."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from backend.app.ai.sentiment import SentimentEngine, SentimentResult
from backend.app.ai.caption import CaptionEngine, CaptionAnalysis
from backend.app.ai.hashtag import HashtagEngine, HashtagSuggestionResponse


@dataclass
class OptimizedContentVariant:
    """Platform-adapted content variant."""
    platform: str
    text: str
    recommended_hashtags: List[str]
    character_count: int


@dataclass
class AIContentOptimizationResult:
    """Comprehensive AI optimization output."""
    sentiment: SentimentResult
    caption_analysis: CaptionAnalysis
    hashtags: HashtagSuggestionResponse
    platform_variants: Dict[str, OptimizedContentVariant]


class AIContentEngine:
    """Master AI engine for content optimization before publication."""

    def __init__(
        self,
        sentiment_engine: Optional[SentimentEngine] = None,
        caption_engine: Optional[CaptionEngine] = None,
        hashtag_engine: Optional[HashtagEngine] = None,
    ):
        self.sentiment = sentiment_engine or SentimentEngine()
        self.caption = caption_engine or CaptionEngine()
        self.hashtag = hashtag_engine or HashtagEngine()

    def optimize(
        self,
        text: str,
        platforms: Optional[List[str]] = None,
        top_k_hashtags: int = 5,
    ) -> AIContentOptimizationResult:
        """Run all AI models over content to produce optimization suggestions and variants."""
        target_platforms = platforms or ["instagram", "facebook", "twitter", "linkedin"]

        # 1. Dual-phase pre-post sentiment
        sentiment_res = self.sentiment.analyze_pre_posting(text)

        # 2. Caption quality analysis
        primary_platform = target_platforms[0] if target_platforms else "instagram"
        caption_res = self.caption.analyze(text, platform=primary_platform)

        # 3. Top-K Hashtag recommendations
        hashtag_res = self.hashtag.recommend_hashtags(text, platform=primary_platform, top_k=top_k_hashtags)

        # 4. Generate platform-adapted variants
        variants: Dict[str, OptimizedContentVariant] = {}
        for p in target_platforms:
            p_key = p.lower()
            adapted_text = self.caption.optimize_for_platform(text, platform=p_key)
            p_tags = self.hashtag.recommend_hashtags(text, platform=p_key, top_k=top_k_hashtags).top_k
            variants[p_key] = OptimizedContentVariant(
                platform=p_key,
                text=adapted_text,
                recommended_hashtags=p_tags,
                character_count=len(adapted_text),
            )

        return AIContentOptimizationResult(
            sentiment=sentiment_res,
            caption_analysis=caption_res,
            hashtags=hashtag_res,
            platform_variants=variants,
        )
