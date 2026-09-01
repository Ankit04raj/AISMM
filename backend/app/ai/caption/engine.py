"""Caption Analysis & Optimization Engine."""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class CaptionFeatures:
    """Structural and stylistic features of a caption."""
    length: int
    word_count: int
    hashtag_count: int
    mention_count: int
    emoji_count: int
    question_count: int
    exclamation_count: int
    has_cta: bool
    detected_cta: Optional[str] = None


@dataclass
class CaptionAnalysis:
    """Caption quality evaluation result."""
    score: float  # 0 to 100 quality score
    grade: str  # Excellent (85-100), Good (70-84), Fair (50-69), Needs Improvement (<50)
    features: CaptionFeatures
    strengths: List[str]
    suggestions: List[str]


class CaptionEngine:
    """Analyzes caption quality and provides platform-adapted variants."""

    CTA_PATTERNS = [
        r"\b(link in bio|click the link|tap the link|check out|learn more|sign up|swipe up)\b",
        r"\b(comment below|drop a comment|let us know|what do you think|share your thoughts)\b",
        r"\b(save this|bookmark this|share with|tag a friend|follow us|subscribe)\b",
        r"\b(dm us|send a message|get yours today|shop now|order now)\b",
    ]

    EMOJI_REGEX = re.compile(
        r"[\U00010000-\U0010ffff]|[☀-➿]|[⌀-⏿]|[⭐-⭕]",
        flags=re.UNICODE,
    )

    def extract_features(self, text: str) -> CaptionFeatures:
        clean_text = text or ""
        words = clean_text.split()
        hashtags = re.findall(r"#\w+", clean_text)
        mentions = re.findall(r"@\w+", clean_text)
        emojis = self.EMOJI_REGEX.findall(clean_text)
        questions = clean_text.count("?")
        exclamations = clean_text.count("!")

        detected_cta = None
        has_cta = False
        for pattern in self.CTA_PATTERNS:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                has_cta = True
                detected_cta = match.group(0).lower()
                break

        return CaptionFeatures(
            length=len(clean_text),
            word_count=len(words),
            hashtag_count=len(hashtags),
            mention_count=len(mentions),
            emoji_count=len(emojis),
            question_count=questions,
            exclamation_count=exclamations,
            has_cta=has_cta,
            detected_cta=detected_cta,
        )

    def analyze(self, text: str, platform: str = "instagram") -> CaptionAnalysis:
        """Evaluate caption quality and generate actionable suggestions."""
        features = self.extract_features(text)
        score = 50.0  # Base score
        strengths = []
        suggestions = []

        # 1. Word count & readability
        if 15 <= features.word_count <= 80:
            score += 15
            strengths.append("Optimal caption length for engagement")
        elif features.word_count < 5:
            score -= 15
            suggestions.append("Caption is very short; add context or tell a story")
        elif features.word_count > 150 and platform.lower() == "twitter":
            score -= 20
            suggestions.append("Text is too long for Twitter's 280-character limit")

        # 2. Call to action
        if features.has_cta:
            score += 15
            strengths.append(f"Clear call-to-action included ('{features.detected_cta}')")
        else:
            suggestions.append("Add a clear Call-To-Action (e.g. 'Link in bio', 'Drop a comment')")

        # 3. Questions / Conversational Hooks
        if features.question_count >= 1:
            score += 10
            strengths.append("Engaging question to encourage comment replies")
        else:
            suggestions.append("Ask a question at the end to boost audience comments")

        # 4. Emoji usage
        if 1 <= features.emoji_count <= 6:
            score += 10
            strengths.append("Effective emoji usage for visual appeal")
        elif features.emoji_count > 12:
            score -= 10
            suggestions.append("Too many emojis may reduce professional readability")
        elif features.emoji_count == 0 and platform.lower() in ("instagram", "tiktok"):
            suggestions.append("Add 1-3 emojis to increase visual engagement")

        # 5. Hashtags
        if platform.lower() == "instagram":
            if 3 <= features.hashtag_count <= 15:
                score += 10
                strengths.append("Well-balanced hashtag count for discovery")
            elif features.hashtag_count == 0:
                suggestions.append("Add 3-5 niche hashtags for reach")
            elif features.hashtag_count > 25:
                suggestions.append("Keep hashtags under 20 to avoid looking spammy")
        elif platform.lower() == "twitter":
            if 1 <= features.hashtag_count <= 3:
                score += 10
            elif features.hashtag_count > 4:
                score -= 10
                suggestions.append("Limit Twitter hashtags to 1-2 to maximize retweet rate")

        final_score = max(10.0, min(100.0, score))
        if final_score >= 85:
            grade = "Excellent"
        elif final_score >= 70:
            grade = "Good"
        elif final_score >= 50:
            grade = "Fair"
        else:
            grade = "Needs Improvement"

        return CaptionAnalysis(
            score=round(final_score, 1),
            grade=grade,
            features=features,
            strengths=strengths,
            suggestions=suggestions,
        )

    def optimize_for_platform(
        self,
        text: str,
        platform: str,
        target_tone: str = "engaging",
    ) -> str:
        """Transform base caption into platform-tailored variant."""
        clean = text or ""
        features = self.extract_features(clean)
        platform_key = platform.lower()

        if platform_key == "instagram":
            # Add emojis if none, ensure spacing, add CTA if missing
            out = clean
            if not features.has_cta:
                out += "\n\n👉 Link in bio for more!"
            return out

        elif platform_key == "twitter":
            # Compact text to under 280 characters
            if len(clean) > 270:
                out = clean[:260] + "..."
            else:
                out = clean
            return out

        elif platform_key == "linkedin":
            # Professional style
            return clean

        elif platform_key == "facebook":
            # Community conversation style
            return clean

        return clean
