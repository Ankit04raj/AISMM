"""Hashtag Extraction & Recommendation Engine (Research Baseline: Top-K evaluation)."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class HashtagRecommendation:
    """Recommended hashtag with category and confidence/relevance score."""
    hashtag: str
    category: str
    relevance_score: float
    is_trending: bool = False


@dataclass
class HashtagSuggestionResponse:
    """Response containing Top-K and category-grouped recommendations."""
    top_k: List[str]
    recommendations: List[HashtagRecommendation]
    platform: str
    max_recommended: int


class HashtagEngine:
    """Extracts, categorizes, and recommends relevant hashtags."""

    CATEGORY_KEYWORDS = {
        "ai_tech": {
            "keywords": ["ai", "artificial intelligence", "ml", "machine learning", "tech", "technology", "software", "code", "coding", "data", "deep learning", "automation"],
            "hashtags": ["ai", "tech", "artificialintelligence", "machinelearning", "automation", "datascience", "technology", "softwareengineering", "deeplearning", "futureofwork"],
        },
        "business_marketing": {
            "keywords": ["business", "marketing", "growth", "startup", "founder", "sales", "entrepreneur", "strategy", "brand", "branding", "agency", "product"],
            "hashtags": ["business", "marketing", "entrepreneurship", "startuplife", "growthhacking", "digitalmarketing", "businessgrowth", "branding", "leadership", "success"],
        },
        "social_media": {
            "keywords": ["social media", "instagram", "facebook", "twitter", "content", "creator", "post", "audience", "followers", "engagement", "reach"],
            "hashtags": ["socialmediamanagement", "contentcreator", "socialmediastrategy", "digitalmarketingtips", "instatips", "contentmarketing", "socialgrowth", "engagement"],
        },
        "design_creative": {
            "keywords": ["design", "creative", "ui", "ux", "art", "visual", "video", "photo", "photography", "graphic", "illustration"],
            "hashtags": ["design", "creativity", "uidesign", "uxdesign", "visualart", "graphicdesign", "creativeagency", "contentcreation", "artdirection", "designer"],
        },
        "lifestyle_general": {
            "keywords": ["life", "lifestyle", "daily", "motivation", "inspiration", "mindset", "productivity", "community", "learn"],
            "hashtags": ["motivation", "productivity", "mindset", "successmindset", "inspiration", "dailygrind", "growthmindset", "goals", "focus", "learnings"],
        },
    }

    PLATFORM_LIMITS = {
        "instagram": 30,
        "facebook": 30,
        "twitter": 4,
        "linkedin": 5,
        "tiktok": 20,
    }

    def extract_hashtags(self, text: str) -> List[str]:
        """Extract and deduplicate hashtags from text."""
        if not text:
            return []
        tags = re.findall(r"#([A-Za-z0-9_]+)", text)
        seen = set()
        out = []
        for t in tags:
            norm = t.lower()
            if norm not in seen:
                seen.add(norm)
                out.append(norm)
        return out

    def recommend_hashtags(
        self,
        text: str,
        platform: str = "instagram",
        top_k: int = 5,
    ) -> HashtagSuggestionResponse:
        """Generate Top-K hashtag recommendations based on content text."""
        clean_text = (text or "").lower()
        existing_tags = set(self.extract_hashtags(clean_text))

        category_scores: Dict[str, float] = {}
        for cat, data in self.CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in data["keywords"] if re.search(r"\b" + re.escape(kw) + r"\b", clean_text))
            if matches > 0:
                category_scores[cat] = matches

        # If no specific keyword matched, default to general categories
        if not category_scores:
            category_scores["social_media"] = 1
            category_scores["lifestyle_general"] = 1

        recommendations: List[HashtagRecommendation] = []
        seen_tags = set(existing_tags)

        # Sort categories by match intensity
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

        for cat, score in sorted_categories:
            cat_data = self.CATEGORY_KEYWORDS[cat]
            relevance = min(0.99, 0.70 + (0.05 * score))

            for tag in cat_data["hashtags"]:
                if tag not in seen_tags:
                    seen_tags.add(tag)
                    recommendations.append(
                        HashtagRecommendation(
                            hashtag=f"#{tag}",
                            category=cat,
                            relevance_score=round(relevance, 2),
                            is_trending=relevance > 0.85,
                        )
                    )

        # Sort recommendations by relevance score
        recommendations.sort(key=lambda r: r.relevance_score, reverse=True)

        platform_limit = self.PLATFORM_LIMITS.get(platform.lower(), 10)
        selected_top_k = [r.hashtag for r in recommendations[:min(top_k, platform_limit)]]

        return HashtagSuggestionResponse(
            top_k=selected_top_k,
            recommendations=recommendations[:platform_limit],
            platform=platform,
            max_recommended=platform_limit,
        )
