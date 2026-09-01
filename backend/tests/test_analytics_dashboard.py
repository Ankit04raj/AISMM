"""Tests for Phase 12 Universal Analytics Dashboard (Overview, Comparison, Content, Temporal, Sentiment, Growth Drift)."""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.analytics_service import AnalyticsService
from backend.app.db.models import SocialAccount, Post, PostPublication, Comment, SentimentAnalysis, ContentTypeEnum, PostStatusEnum

client = TestClient(app)


class TestAnalyticsService:
    """Test AnalyticsService business logic and aggregation."""

    @pytest.mark.asyncio
    async def test_dashboard_overview_aggregation(self):
        mock_db = AsyncMock()
        service = AnalyticsService(mock_db)
        user_id = uuid4()

        # Mock accounts
        acc1 = MagicMock(spec=SocialAccount)
        acc1.platform = "instagram"
        acc1.account_metadata = {"followers_count": 15000}

        acc2 = MagicMock(spec=SocialAccount)
        acc2.platform = "facebook"
        acc2.account_metadata = {"followers_count": 22000}

        mock_db_acc = MagicMock()
        mock_db_acc.scalars.return_value.all.return_value = [acc1, acc2]

        # Mock posts
        p1 = MagicMock(spec=Post)
        p1.publications = [MagicMock(platform="instagram")]
        p1.comments = [MagicMock(), MagicMock()]
        p1.metrics = []

        mock_db_posts = MagicMock()
        mock_db_posts.scalars.return_value.all.return_value = [p1]

        # Mock avg sentiment
        mock_db_sent = MagicMock()
        mock_db_sent.scalar.return_value = 0.62

        mock_db.execute.side_effect = [mock_db_acc, mock_db_posts, mock_db_sent]

        overview = await service.get_dashboard_overview(user_id, days=30)

        assert overview.total_connected_platforms == 2
        assert overview.total_followers == 37000
        assert overview.total_posts_published == 1
        assert overview.total_comments_received == 2
        assert overview.average_sentiment_score == 0.62

    @pytest.mark.asyncio
    async def test_platform_comparison_benchmarking(self):
        mock_db = AsyncMock()
        service = AnalyticsService(mock_db)
        user_id = uuid4()

        acc_ig = MagicMock(spec=SocialAccount)
        acc_ig.platform = "instagram"
        acc_ig.account_metadata = {"followers_count": 10000}

        acc_fb = MagicMock(spec=SocialAccount)
        acc_fb.platform = "facebook"
        acc_fb.account_metadata = {"followers_count": 8000}

        mock_db_acc = MagicMock()
        mock_db_acc.scalars.return_value.all.return_value = [acc_ig, acc_fb]

        pub1 = MagicMock(spec=PostPublication)
        pub2 = MagicMock(spec=PostPublication)
        mock_db_pubs_ig = MagicMock()
        mock_db_pubs_ig.scalars.return_value.all.return_value = [pub1, pub2]

        mock_db_pubs_fb = MagicMock()
        mock_db_pubs_fb.scalars.return_value.all.return_value = [pub1]

        mock_db.execute.side_effect = [mock_db_acc, mock_db_pubs_ig, mock_db_pubs_fb]

        comparison = await service.get_platform_comparison(user_id, days=30)

        assert len(comparison.platforms) == 2
        platforms = [p.platform for p in comparison.platforms]
        assert "instagram" in platforms
        assert "facebook" in platforms
        assert comparison.strongest_platform_by_reach in ("instagram", "facebook")

    @pytest.mark.asyncio
    async def test_content_performance_and_roi(self):
        mock_db = AsyncMock()
        service = AnalyticsService(mock_db)
        user_id = uuid4()

        p1 = MagicMock(spec=Post)
        p1.id = uuid4()
        p1.content_type = ContentTypeEnum.CAROUSEL
        p1.text = "Carousel high performer post"
        p1.created_at = datetime.now(timezone.utc).replace(tzinfo=None)
        pub1 = MagicMock(platform="instagram")
        p1.publications = [pub1]
        p1.comments = [MagicMock() for _ in range(10)]

        p2 = MagicMock(spec=Post)
        p2.id = uuid4()
        p2.content_type = ContentTypeEnum.POST
        p2.text = "Standard image post"
        p2.created_at = datetime.now(timezone.utc).replace(tzinfo=None)
        pub2 = MagicMock(platform="facebook")
        p2.publications = [pub2]
        p2.comments = [MagicMock()]

        mock_db_posts = MagicMock()
        mock_db_posts.scalars.return_value.all.return_value = [p1, p2]
        mock_db.execute.return_value = mock_db_posts

        res = await service.get_content_performance(user_id, days=30)

        assert len(res.top_posts) == 2
        assert res.top_posts[0].content_type == "carousel"
        assert len(res.by_content_type) == 2
        assert len(res.top_performing_hashtags) >= 1

    @pytest.mark.asyncio
    async def test_temporal_analytics_heatmap(self):
        mock_db = AsyncMock()
        service = AnalyticsService(mock_db)
        user_id = uuid4()

        res = await service.get_temporal_analytics(user_id, days=30)

        assert res.best_overall_hour == 19
        assert res.best_overall_day == "Wednesday"
        assert len(res.heatmap_slots) == 7 * 24  # Full 7-day 24h matrix
        assert res.weekday_vs_weekend_lift_percent > 0

    @pytest.mark.asyncio
    async def test_growth_accuracy_drift_report(self):
        mock_db = AsyncMock()
        service = AnalyticsService(mock_db)
        user_id = uuid4()

        res = await service.get_growth_accuracy_report(user_id, platform="instagram")

        assert res.platform == "instagram"
        assert res.r2_score >= 0.85
        assert res.drift_status == "calibrated"
        assert len(res.data_points) == 5


class TestAnalyticsAPIEndpoints:
    """Test FastAPI /api/v1/analytics endpoints."""

    def test_dashboard_overview_endpoint(self):
        with patch("backend.app.services.analytics_service.AnalyticsService.get_dashboard_overview", new_callable=AsyncMock) as mock_ov:
            mock_ov.return_value = {
                "total_connected_platforms": 2,
                "total_followers": 25000,
                "total_impressions": 54000,
                "total_reach": 42000,
                "total_engagements": 2800,
                "overall_engagement_rate": 5.18,
                "total_posts_published": 14,
                "total_comments_received": 340,
                "average_sentiment_score": 0.58,
                "time_period_days": 30,
                "generated_at": datetime.now(timezone.utc),
            }

            resp = client.get("/api/v1/analytics/dashboard?days=30")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total_followers"] == 25000
            assert data["overall_engagement_rate"] == 5.18

    def test_comparison_endpoint(self):
        with patch("backend.app.services.analytics_service.AnalyticsService.get_platform_comparison", new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = {
                "platforms": [
                    {
                        "platform": "instagram",
                        "followers": 15000,
                        "impressions": 30000,
                        "reach": 24000,
                        "engagements": 1800,
                        "engagement_rate": 6.0,
                        "posts_count": 8,
                        "avg_likes_per_post": 150.0,
                        "avg_comments_per_post": 30.0,
                        "top_performing_media_type": "carousel",
                    }
                ],
                "strongest_platform_by_reach": "instagram",
                "strongest_platform_by_engagement": "instagram",
                "time_period_days": 30,
            }

            resp = client.get("/api/v1/analytics/comparison?days=30")
            assert resp.status_code == 200
            assert resp.json()["strongest_platform_by_reach"] == "instagram"

    def test_temporal_endpoint(self):
        resp = client.get("/api/v1/analytics/temporal?days=30")
        assert resp.status_code == 200
        data = resp.json()
        assert "heatmap_slots" in data
        assert len(data["heatmap_slots"]) == 168  # 7 * 24

    def test_growth_accuracy_endpoint(self):
        resp = client.get("/api/v1/analytics/growth-accuracy?platform=instagram")
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "instagram"
        assert data["drift_status"] == "calibrated"
