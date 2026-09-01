"""Tests for Phase 7 AI Content Engine (Sentiment, Caption, Hashtag, API endpoints)."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai.sentiment import SentimentEngine, PrePostAnalyzer, PostPostAnalyzer
from backend.app.ai.caption import CaptionEngine
from backend.app.ai.hashtag import HashtagEngine
from backend.app.ai.content_engine import AIContentEngine

client = TestClient(app)


class TestSentimentEngine:
    """Test Dual-Phase Sentiment Analysis Engine."""

    def test_pre_post_positive_and_negative_sentiment(self):
        engine = SentimentEngine()

        pos_res = engine.analyze_pre_posting("We are thrilled to launch our new revolutionary AI product today! 🚀🎉")
        assert pos_res.score > 0.05
        assert pos_res.label in ("positive", "very_positive")
        assert pos_res.positive_score > 0

        neg_res = engine.analyze_pre_posting("This update is terrible and completely broke everything, extremely disappointed. 😡")
        assert neg_res.score < -0.05
        assert neg_res.label in ("negative", "very_negative")
        assert neg_res.negative_score > 0

        neu_res = engine.analyze_pre_posting("Meeting is scheduled for 2pm tomorrow in room 302.")
        assert neu_res.label == "neutral"

    def test_post_post_comment_aggregation(self):
        engine = SentimentEngine()
        comments = [
            "This is fantastic, great job team!",
            "Love the new design!",
            "Works like a charm, thank you! 🔥",
            "Not bad, pretty standard.",
        ]
        res = engine.analyze_post_posting(comments)
        assert res.score > 0.05
        assert res.label in ("positive", "very_positive")
        assert res.details["sample_size"] == 4
        assert res.details["sentiment_distribution"]["positive"] + res.details["sentiment_distribution"]["very_positive"] >= 2


class TestCaptionEngine:
    """Test Caption Quality Analysis and Optimization."""

    def test_caption_feature_extraction_and_scoring(self):
        engine = CaptionEngine()
        caption = "Introducing our newest automated AI assistant! 🚀 What feature are you most excited for? Link in bio to try it out #ai #tech"
        analysis = engine.analyze(caption, platform="instagram")

        assert analysis.score >= 70.0
        assert analysis.grade in ("Good", "Excellent")
        assert analysis.features.has_cta is True
        assert analysis.features.question_count >= 1
        assert analysis.features.emoji_count >= 1
        assert analysis.features.hashtag_count == 2
        assert len(analysis.strengths) >= 2

    def test_caption_platform_optimization(self):
        engine = CaptionEngine()
        base = "Announcing our startup fundraise."
        opt_ig = engine.optimize_for_platform(base, platform="instagram")
        assert "Link in bio" in opt_ig

        long_text = "Word " * 70  # ~350 chars
        opt_tw = engine.optimize_for_platform(long_text, platform="twitter")
        assert len(opt_tw) <= 280


class TestHashtagEngine:
    """Test Hashtag Extraction and Top-K Recommendation."""

    def test_hashtag_extraction_and_deduplication(self):
        engine = HashtagEngine()
        tags = engine.extract_hashtags("Loving the new #ai tool! #AI #machinelearning #Tech #ai")
        assert len(tags) == 3
        assert "ai" in tags
        assert "machinelearning" in tags
        assert "tech" in tags

    def test_top_k_recommendations_category_matching(self):
        engine = HashtagEngine()
        text = "Our software development team is building machine learning models for data science."
        res = engine.recommend_hashtags(text, platform="instagram", top_k=5)

        assert len(res.top_k) == 5
        assert any("ai" in tag.lower() or "tech" in tag.lower() or "machinelearning" in tag.lower() for tag in res.top_k)
        assert res.recommendations[0].relevance_score >= 0.70


class TestAIContentEngine:
    """Test unified AI Content Engine orchestrator."""

    def test_unified_optimization_flow(self):
        engine = AIContentEngine()
        text = "Supercharge your social media workflow with AI automation! 🚀 Check out the link in bio. What is your biggest challenge? #socialmedia"

        res = engine.optimize(text, platforms=["instagram", "twitter", "linkedin"], top_k_hashtags=5)

        assert res.sentiment.score > 0
        assert res.caption_analysis.score >= 70
        assert len(res.hashtags.top_k) == 5
        assert "instagram" in res.platform_variants
        assert "twitter" in res.platform_variants
        assert "linkedin" in res.platform_variants
        assert len(res.platform_variants["twitter"].text) <= 280


class TestAIAPIEndpoints:
    """Test FastAPI /api/v1/ai endpoints."""

    def test_sentiment_analyze_endpoint(self):
        resp = client.post("/api/v1/ai/sentiment/analyze", json={"text": "Incredible results achieved today! 🎉"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] > 0
        assert data["label"] in ("positive", "very_positive")

    def test_sentiment_comments_endpoint(self):
        resp = client.post(
            "/api/v1/ai/sentiment/comments",
            json={"comments": ["Super helpful!", "Great content", "Loved it!"]},
        )
        assert resp.status_code == 200
        assert resp.json()["score"] > 0

    def test_caption_analyze_and_optimize_endpoints(self):
        # Analyze
        resp_an = client.post(
            "/api/v1/ai/caption/analyze",
            json={"text": "New launch! Check it out.", "platform": "instagram"},
        )
        assert resp_an.status_code == 200
        assert "score" in resp_an.json()

        # Optimize
        resp_opt = client.post(
            "/api/v1/ai/caption/optimize",
            json={"text": "New launch! Check it out.", "platform": "instagram"},
        )
        assert resp_opt.status_code == 200
        assert "optimized_text" in resp_opt.json()

    def test_hashtags_recommend_endpoint(self):
        resp = client.post(
            "/api/v1/ai/hashtags/recommend",
            json={"text": "Artificial intelligence and deep learning tools", "platform": "instagram", "top_k": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["top_k"]) == 5

    def test_content_optimize_all_endpoint(self):
        resp = client.post(
            "/api/v1/ai/content/optimize-all",
            json={
                "text": "Revolutionize your marketing with AI tools! 🚀 What are your thoughts? Link in bio.",
                "platforms": ["instagram", "facebook", "twitter"],
                "top_k_hashtags": 5,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "sentiment" in data
        assert "caption_analysis" in data
        assert "hashtags" in data
        assert "platform_variants" in data
        assert "instagram" in data["platform_variants"]
        assert "twitter" in data["platform_variants"]
