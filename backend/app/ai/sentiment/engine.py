"""Dual-Phase Sentiment Analysis Engine (Research Baseline: VADER + Refinement)."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re

from nltk.sentiment.vader import SentimentIntensityAnalyzer

from backend.app.core.normalization import UniversalContent


@dataclass
class SentimentThresholds:
    """Configurable sentiment thresholds per research specification."""
    very_positive: float = 0.50
    positive: float = 0.05
    neutral_low: float = -0.05
    neutral_high: float = 0.05
    negative: float = -0.05
    very_negative: float = -0.50


@dataclass
class SentimentConfig:
    """Configuration for SentimentEngine."""
    thresholds: SentimentThresholds = field(default_factory=SentimentThresholds)
    ambiguity_window: float = 0.05  # -0.05 to +0.05 refined
    enable_emoji_boost: bool = True


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    score: float  # Compound score between -1.0 and 1.0
    label: str  # very_positive, positive, neutral, negative, very_negative
    confidence: float  # 0.0 to 1.0
    method: str  # "vader_baseline", "vader_refined", "comment_aggregation"
    positive_score: float = 0.0
    neutral_score: float = 0.0
    negative_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class PrePostAnalyzer:
    """Analyzes drafted content before publication."""

    def __init__(self, config: Optional[SentimentConfig] = None):
        self.config = config or SentimentConfig()
        self.vader = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> SentimentResult:
        """Analyze raw text string."""
        if not text or not text.strip():
            return SentimentResult(
                score=0.0,
                label="neutral",
                confidence=1.0,
                method="empty_fallback",
                positive_score=0.0,
                neutral_score=1.0,
                negative_score=0.0,
            )

        scores = self.vader.polarity_scores(text)
        compound = scores["compound"]

        # Emoji sentiment weighting refinement
        if self.config.enable_emoji_boost:
            positive_emojis = len(re.findall(r'[😀😃😄😁😆😍🥰🤩🎉🚀🔥👍👏❤️]', text))
            negative_emojis = len(re.findall(r'[😢😭😡😠🤬💔👎🤮💩]', text))
            if positive_emojis > negative_emojis:
                compound = min(1.0, compound + (0.05 * (positive_emojis - negative_emojis)))
            elif negative_emojis > positive_emojis:
                compound = max(-1.0, compound - (0.05 * (negative_emojis - positive_emojis)))

        label = self._label_from_score(compound)
        confidence = min(1.0, max(0.5, abs(compound) + 0.3))

        return SentimentResult(
            score=round(compound, 4),
            label=label,
            confidence=round(confidence, 2),
            method="vader_baseline",
            positive_score=round(scores["pos"], 4),
            neutral_score=round(scores["neu"], 4),
            negative_score=round(scores["neg"], 4),
            details=scores,
        )

    def analyze_content(self, content: UniversalContent) -> SentimentResult:
        """Analyze a UniversalContent object."""
        full_text = content.caption or content.text or ""
        return self.analyze_text(full_text)

    def _label_from_score(self, score: float) -> str:
        t = self.config.thresholds
        if score >= t.very_positive:
            return "very_positive"
        elif score >= t.positive:
            return "positive"
        elif score > t.neutral_low and score < t.neutral_high:
            return "neutral"
        elif score > t.very_negative:
            return "negative"
        else:
            return "very_negative"


class PostPostAnalyzer:
    """Analyzes audience sentiment from post comments/replies."""

    def __init__(self, config: Optional[SentimentConfig] = None):
        self.config = config or SentimentConfig()
        self.pre_analyzer = PrePostAnalyzer(self.config)

    def analyze_comments(self, comments: List[str]) -> SentimentResult:
        """Aggregate sentiment across a list of comment texts."""
        if not comments:
            return SentimentResult(
                score=0.0,
                label="neutral",
                confidence=0.0,
                method="comment_aggregation",
                details={"sample_size": 0},
            )

        results = [self.pre_analyzer.analyze_text(c) for c in comments if c and c.strip()]
        if not results:
            return SentimentResult(
                score=0.0,
                label="neutral",
                confidence=0.0,
                method="comment_aggregation",
                details={"sample_size": 0},
            )

        avg_score = sum(r.score for r in results) / len(results)
        avg_pos = sum(r.positive_score for r in results) / len(results)
        avg_neu = sum(r.neutral_score for r in results) / len(results)
        avg_neg = sum(r.negative_score for r in results) / len(results)

        label = self.pre_analyzer._label_from_score(avg_score)
        confidence = min(1.0, round(len(results) / 10.0, 2))  # Confidence scales with sample count

        return SentimentResult(
            score=round(avg_score, 4),
            label=label,
            confidence=confidence,
            method="comment_aggregation",
            positive_score=round(avg_pos, 4),
            neutral_score=round(avg_neu, 4),
            negative_score=round(avg_neg, 4),
            details={
                "sample_size": len(results),
                "sentiment_distribution": {
                    "very_positive": sum(1 for r in results if r.label == "very_positive"),
                    "positive": sum(1 for r in results if r.label == "positive"),
                    "neutral": sum(1 for r in results if r.label == "neutral"),
                    "negative": sum(1 for r in results if r.label == "negative"),
                    "very_negative": sum(1 for r in results if r.label == "very_negative"),
                },
            },
        )


class SentimentEngine:
    """Unified Dual-Phase Sentiment Engine."""

    def __init__(self, config: Optional[SentimentConfig] = None):
        self.config = config or SentimentConfig()
        self.pre_post = PrePostAnalyzer(self.config)
        self.post_post = PostPostAnalyzer(self.config)

    def analyze_pre_posting(self, text: str) -> SentimentResult:
        """Phase 1: Pre-posting content sentiment analysis."""
        return self.pre_post.analyze_text(text)

    def analyze_post_posting(self, comments: List[str]) -> SentimentResult:
        """Phase 2: Post-posting audience response sentiment analysis."""
        return self.post_post.analyze_comments(comments)
