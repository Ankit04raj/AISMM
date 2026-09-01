"""Comprehensive test suite for Phase 13 AI Strategy Engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai.strategy.engine import AIStrategyEngine
from backend.app.services.strategy_service import StrategyService
from backend.app.core.schemas.strategy import (
    RecommendationPriority,
    RecommendationCategory,
    ComprehensiveStrategyResponse,
    ContentDraftStrategyRequest,
    ContentStrategyPlan,
    PlatformStrategyAdvice,
    StrategyFeedbackRequest,
)


class TestAIStrategyEngine:
    """Test unit behavior of the AIStrategyEngine synthesizing multi-model signals."""

    def test_engine_initialization_and_sub_engines(self):
        engine = AIStrategyEngine()
        assert engine.sentiment_engine is not None
        assert engine.caption_engine is not None
        assert engine.hashtag_engine is not None
        assert engine.scheduling_engine is not None
        assert engine.growth_engine is not None

    def test_generate_comprehensive_strategy_recommendations(self):
        engine = AIStrategyEngine()
        response = engine.generate_comprehensive_strategy(
            connected_platforms=["instagram", "facebook"],
            recent_sentiment_score=0.55,
            average_engagement_rate=4.8,
            posting_frequency_weekly=3.0,
            total_followers=12000,
        )

        assert isinstance(response, ComprehensiveStrategyResponse)
        assert len(response.active_recommendations) >= 3
        assert len(response.platform_profiles) == 2
        assert response.overall_strategy_health_score > 50

        # Check for timing recommendation
        timing_recs = [r for r in response.active_recommendations if r.category == RecommendationCategory.TIMING]
        assert len(timing_recs) == 1
        assert timing_recs[0].priority == RecommendationPriority.HIGH
        assert timing_recs[0].confidence_score >= 0.85

        # Check for growth cadence recommendation due to frequency < 4.0
        growth_recs = [r for r in response.active_recommendations if r.category == RecommendationCategory.GROWTH_VELOCITY]
        assert len(growth_recs) == 1

        # Check platform profiles
        ig_profile = next((p for p in response.platform_profiles if p.platform == "instagram"), None)
        assert ig_profile is not None
        assert ig_profile.best_media_format == "carousel"
        assert ig_profile.expected_engagement_rate_target > 4.0

    def test_negative_sentiment_triggers_mood_recommendation(self):
        engine = AIStrategyEngine()
        response = engine.generate_comprehensive_strategy(
            connected_platforms=["instagram"],
            recent_sentiment_score=0.25,  # Low sentiment
            average_engagement_rate=3.0,
            posting_frequency_weekly=5.0,
            total_followers=5000,
        )

        sentiment_recs = [r for r in response.active_recommendations if r.category == RecommendationCategory.AUDIENCE_SENTIMENT]
        assert len(sentiment_recs) == 1
        assert sentiment_recs[0].priority == RecommendationPriority.HIGH

    def test_synthesize_content_strategy_plan(self):
        engine = AIStrategyEngine()
        plan = engine.synthesize_content_strategy(
            draft_caption="Announcing our revolutionary AI algorithms for creators and businesses! #tech",
            target_platforms=["instagram", "facebook"],
            media_type="carousel",
            content_category="tech",
            current_followers=15000,
        )

        assert isinstance(plan, ContentStrategyPlan)
        assert "instagram" in plan.optimized_caption_by_platform
        assert "facebook" in plan.optimized_caption_by_platform
        assert len(plan.recommended_hashtags) > 0
        assert plan.projected_engagement_rate >= 4.5
        assert len(plan.strategic_tips) >= 2


class TestStrategyService:
    """Test service layer workflows and database interactions."""

    @pytest.mark.asyncio
    async def test_get_strategy_dashboard_service(self):
        mock_db = AsyncMock()

        # Mock connected accounts
        mock_acc = MagicMock()
        mock_acc.platform = "instagram"
        mock_acc.account_metadata = {"followers_count": 8500}

        mock_db.execute = AsyncMock(side_effect=[
            MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_acc])))),
            MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[MagicMock(), MagicMock()])))),
            MagicMock(scalar=MagicMock(return_value=0.58)),
        ])

        service = StrategyService(mock_db)
        dashboard = await service.get_strategy_dashboard(UUID("00000000-0000-0000-0000-000000000001"))

        assert isinstance(dashboard, ComprehensiveStrategyResponse)
        assert len(dashboard.active_recommendations) > 0
        assert len(dashboard.platform_profiles) > 0

    @pytest.mark.asyncio
    async def test_generate_content_plan_service_persists_prediction(self):
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        service = StrategyService(mock_db)
        req = ContentDraftStrategyRequest(
            draft_caption="Building future tech with AI and scalable cloud systems.",
            target_platforms=["instagram"],
            media_type="video",
            content_category="tech",
            current_followers=10000,
        )

        plan = await service.generate_content_plan(UUID("00000000-0000-0000-0000-000000000001"), req)

        assert isinstance(plan, ContentStrategyPlan)
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_get_platform_advice_and_feedback(self):
        mock_db = AsyncMock()
        service = StrategyService(mock_db)

        advice = await service.get_platform_advice(
            UUID("00000000-0000-0000-0000-000000000001"), platform="linkedin"
        )
        assert isinstance(advice, PlatformStrategyAdvice)
        assert advice.platform == "linkedin"
        assert advice.recommended_weekly_frequency > 0

        feedback = await service.record_feedback(
            UUID("00000000-0000-0000-0000-000000000001"),
            StrategyFeedbackRequest(recommendation_id="rec-123", applied=True, feedback_notes="Applied timing slot"),
        )
        assert feedback["status"] == "recorded"
        assert feedback["applied"] is True


class TestStrategyAPIEndpoints:
    """Test FastAPI REST endpoints for AI Strategy Engine."""

    def test_get_strategy_dashboard_endpoint(self):
        client = TestClient(app)
        with patch(
            "backend.app.services.strategy_service.StrategyService.get_strategy_dashboard",
            new_callable=AsyncMock,
        ) as mock_dash:
            mock_dash.return_value = ComprehensiveStrategyResponse(
                active_recommendations=[],
                platform_profiles=[
                    PlatformStrategyAdvice(
                        platform="instagram",
                        recommended_weekly_frequency=5.0,
                        optimal_time_window="18:00 - 21:00 UTC",
                        best_media_format="carousel",
                        caption_style_guidance="Engaging hook",
                        hashtag_density_recommendation="4-6 targeted hashtags",
                        expected_monthly_reach_growth=4200,
                        expected_engagement_rate_target=5.2,
                    )
                ],
                key_strategic_focus="Align posting with peak windows",
                overall_strategy_health_score=82,
                generated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            )
            # Populate a recommendation after construction so Pydantic validation stays intact
            engine = AIStrategyEngine()
            mock_dash.return_value = engine.generate_comprehensive_strategy(
                connected_platforms=["instagram", "facebook"],
                recent_sentiment_score=0.55,
                average_engagement_rate=4.8,
                posting_frequency_weekly=3.0,
                total_followers=12000,
            )
            response = client.get("/api/v1/strategy/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "active_recommendations" in data
        assert "platform_profiles" in data
        assert len(data["active_recommendations"]) > 0

    def test_generate_content_plan_endpoint(self):
        client = TestClient(app)
        payload = {
            "draft_caption": "Testing our new AI Strategy Engine integration!",
            "target_platforms": ["instagram", "facebook"],
            "media_type": "carousel",
            "content_category": "tech",
            "current_followers": 12000,
        }
        engine = AIStrategyEngine()
        plan = engine.synthesize_content_strategy(
            draft_caption=payload["draft_caption"],
            target_platforms=payload["target_platforms"],
            media_type=payload["media_type"],
            content_category=payload["content_category"],
            current_followers=payload["current_followers"],
        )
        with patch(
            "backend.app.services.strategy_service.StrategyService.generate_content_plan",
            new_callable=AsyncMock,
        ) as mock_plan:
            mock_plan.return_value = plan
            response = client.post("/api/v1/strategy/content-plan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "optimized_caption_by_platform" in data
        assert "recommended_hashtags" in data
        assert "best_publishing_time" in data
        assert data["projected_engagement_rate"] > 0

    def test_get_platform_advice_endpoint(self):
        client = TestClient(app)
        response = client.get("/api/v1/strategy/platform-advice/instagram")
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "instagram"
        assert data["best_media_format"] == "carousel"

    def test_record_feedback_endpoint(self):
        client = TestClient(app)
        payload = {
            "recommendation_id": "rec-test-001",
            "applied": True,
            "feedback_notes": "Implemented carousel format suggestion",
        }
        response = client.post("/api/v1/strategy/feedback", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "recorded"
        assert data["applied"] is True
