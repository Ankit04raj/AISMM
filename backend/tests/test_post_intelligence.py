"""Tests for Phase 9 Post-Posting Intelligence (Comment Sync, Temporal Sentiment, Alerts, APIs)."""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.intelligence_service import IntelligenceService
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.platform_adapters.base import CommentData
from backend.app.db.models import Post, PostPublication, Comment, PostStatusEnum, ContentTypeEnum

client = TestClient(app)


class TestIntelligenceService:
    """Test IntelligenceService methods."""

    @pytest.mark.asyncio
    async def test_sync_comments_and_sentiment_analysis(self):
        mock_db = AsyncMock()
        service = IntelligenceService(mock_db)

        user_id = uuid4()
        post_id = uuid4()

        mock_post = MagicMock(spec=Post)
        mock_post.id = post_id
        mock_post.user_id = user_id
        mock_post.created_at = datetime.now(timezone.utc).replace(tzinfo=None)
        mock_post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)

        pub = MagicMock(spec=PostPublication)
        pub.platform = "instagram"
        pub.platform_post_id = "ig_12345"
        mock_post.publications = [pub]

        # 1. Mock post lookup
        mock_db_post_res = MagicMock()
        mock_db_post_res.scalar_one_or_none.return_value = mock_post

        # 2. Mock comment existing lookup (return None -> new comment)
        mock_db_comm_res = MagicMock()
        mock_db_comm_res.scalar_one_or_none.return_value = None

        mock_db.execute.side_effect = [mock_db_post_res, mock_db_comm_res]

        adapter = PlatformRegistry.get_adapter("instagram")
        with patch.object(adapter, "get_comments", new_callable=AsyncMock) as mock_get_c:
            mock_get_c.return_value = [
                CommentData(
                    id="comm_901",
                    post_id="ig_12345",
                    author_id="user_1",
                    author_name="fan_alex",
                    text="This new release is unbelievable! Absolutely love it! 🚀",
                    created_at=datetime.now(timezone.utc),
                    platform_data={},
                )
            ]

            sync_res = await service.sync_comments_for_post(post_id, user_id)

            assert sync_res.total_synced == 1
            assert sync_res.new_comments_added == 1
            assert sync_res.synced_comments[0].sentiment_label in ("positive", "very_positive")
            assert mock_db.add.called
            assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_temporal_sentiment_trajectory(self):
        mock_db = AsyncMock()
        service = IntelligenceService(mock_db)

        user_id = uuid4()
        post_id = uuid4()

        pub_time = datetime(2026, 9, 1, 10, 0, 0)
        mock_post = MagicMock(spec=Post)
        mock_post.id = post_id
        mock_post.user_id = user_id
        mock_post.published_at = pub_time

        # Create comments in different time windows
        # Window 0-1h: Positive
        c1 = MagicMock(spec=Comment)
        c1.text = "Great start! Very happy with this."
        c1.created_at = pub_time + timedelta(minutes=30)

        # Window 1-6h: Positive
        c2 = MagicMock(spec=Comment)
        c2.text = "Super awesome features!"
        c2.created_at = pub_time + timedelta(hours=3)

        # Window 6-24h: Mixed
        c3 = MagicMock(spec=Comment)
        c3.text = "It is okay, normal update."
        c3.created_at = pub_time + timedelta(hours=12)

        mock_db_post = MagicMock()
        mock_db_post.scalar_one_or_none.return_value = mock_post

        mock_db_comms = MagicMock()
        mock_db_comms.scalars.return_value.all.return_value = [c1, c2, c3]

        mock_db.execute.side_effect = [mock_db_post, mock_db_comms]

        trajectory = await service.get_temporal_sentiment_trajectory(post_id, user_id)

        assert trajectory.total_comments_analyzed == 3
        assert trajectory.overall_sentiment_score > 0
        assert len(trajectory.time_series) >= 2
        assert trajectory.time_series[0].time_window == "0-1h"
        assert trajectory.time_series[0].comment_count == 1

    @pytest.mark.asyncio
    async def test_post_alerts_detection(self):
        mock_db = AsyncMock()
        service = IntelligenceService(mock_db)

        user_id = uuid4()
        post_id = uuid4()

        mock_post = MagicMock(spec=Post)
        mock_post.id = post_id
        mock_post.user_id = user_id
        pub = MagicMock(spec=PostPublication)
        pub.platform = "instagram"
        mock_post.publications = [pub]

        # 3 negative comments + 2 questions -> should trigger Negative Sentiment Surge and Reply Required
        c1 = MagicMock(spec=Comment)
        c1.text = "This is broken and terrible! 😡"
        c2 = MagicMock(spec=Comment)
        c2.text = "Completely disappointed, worst update ever."
        c3 = MagicMock(spec=Comment)
        c3.text = "How do I fix this error? Does anyone know?"
        c4 = MagicMock(spec=Comment)
        c4.text = "Where is the customer support link?"

        mock_post.comments = [c1, c2, c3, c4]

        mock_db_post = MagicMock()
        mock_db_post.scalar_one_or_none.return_value = mock_post
        mock_db.execute.return_value = mock_db_post

        alerts_res = await service.get_post_alerts(post_id, user_id)

        assert alerts_res.alert_count >= 1
        alert_types = [a.alert_type for a in alerts_res.active_alerts]
        assert "NEGATIVE_SENTIMENT_SURGE" in alert_types
        assert "REPLY_REQUIRED" in alert_types


class TestIntelligenceAPIEndpoints:
    """Test FastAPI /api/v1/intelligence endpoints."""

    def test_sync_comments_endpoint(self):
        with patch("backend.app.services.intelligence_service.IntelligenceService.sync_comments_for_post", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = {
                "post_id": str(uuid4()),
                "total_synced": 3,
                "new_comments_added": 3,
                "synced_comments": [],
                "timestamp": datetime.now(timezone.utc),
            }

            resp = client.post(f"/api/v1/intelligence/posts/{uuid4()}/sync-comments", json={"limit_per_platform": 20})
            assert resp.status_code == 200
            assert resp.json()["total_synced"] == 3

    def test_sentiment_trajectory_endpoint(self):
        with patch("backend.app.services.intelligence_service.IntelligenceService.get_temporal_sentiment_trajectory", new_callable=AsyncMock) as mock_traj:
            mock_traj.return_value = {
                "post_id": str(uuid4()),
                "overall_sentiment_label": "positive",
                "overall_sentiment_score": 0.65,
                "total_comments_analyzed": 5,
                "trajectory_trend": "stable",
                "time_series": [
                    {
                        "time_window": "0-1h",
                        "comment_count": 2,
                        "avg_sentiment_score": 0.70,
                        "sentiment_distribution": {"positive": 2},
                    }
                ],
            }

            resp = client.get(f"/api/v1/intelligence/posts/{uuid4()}/sentiment-trajectory")
            assert resp.status_code == 200
            assert resp.json()["overall_sentiment_label"] == "positive"

    def test_post_alerts_endpoint(self):
        with patch("backend.app.services.intelligence_service.IntelligenceService.get_post_alerts", new_callable=AsyncMock) as mock_alerts:
            mock_alerts.return_value = {
                "post_id": str(uuid4()),
                "active_alerts": [
                    {
                        "alert_type": "HIGH_ENGAGEMENT_SPIKE",
                        "severity": "medium",
                        "platform": "instagram",
                        "message": "High engagement wave",
                        "metric_value": 25.0,
                        "threshold": 20.0,
                        "created_at": datetime.now(timezone.utc),
                    }
                ],
                "alert_count": 1,
            }

            resp = client.get(f"/api/v1/intelligence/posts/{uuid4()}/alerts")
            assert resp.status_code == 200
            assert resp.json()["alert_count"] == 1
            assert resp.json()["active_alerts"][0]["alert_type"] == "HIGH_ENGAGEMENT_SPIKE"
