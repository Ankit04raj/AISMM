"""Tests for Phase 8 Intelligent Scheduling Engine (ML Ensemble, Features, API, Service)."""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai.scheduling import (
    SchedulingEngine,
    SchedulingFeatureExtractor,
    TimeConstraints,
)
from backend.app.services.scheduling_service import SchedulingService
from backend.app.core.schemas.scheduling import (
    ScheduleRecommendRequest,
    AutoScheduleRequest,
)
from backend.app.core.schemas.post import MediaItem
from backend.app.db.models import Schedule, Post, PostPublication

client = TestClient(app)


class TestFeatureExtractor:
    """Test temporal and contextual feature extraction."""

    def test_cyclical_and_context_features(self):
        dt = datetime(2026, 9, 2, 19, 30, 0)  # Wednesday 7:30 PM
        feat = SchedulingFeatureExtractor.extract(
            dt=dt,
            platform="instagram",
            text="Big launch event today! #launch #tech",
            hashtags=["launch", "tech"],
            has_media=True,
            media_type="image",
        )

        assert feat.hour == 19
        assert feat.day_of_week == 2  # Wednesday
        assert feat.is_weekend == 0
        assert feat.hashtag_count == 2
        assert feat.has_media == 1
        assert feat.platform_code == 0
        assert len(feat.to_vector()) == 16


class TestSchedulingEngine:
    """Test ML model training, prediction, and constraint filtering."""

    def test_engine_initialization_and_scoring(self):
        engine = SchedulingEngine()
        assert engine._is_trained is True

        dt_peak = datetime(2026, 9, 2, 19, 0, 0)  # Wednesday 7 PM (Instagram peak)
        feat_peak = SchedulingFeatureExtractor.extract(dt=dt_peak, platform="instagram")
        score_peak = engine.score_slot(feat_peak)

        dt_off = datetime(2026, 9, 2, 3, 0, 0)  # Wednesday 3 AM (Off-peak)
        feat_off = SchedulingFeatureExtractor.extract(dt=dt_off, platform="instagram")
        score_off = engine.score_slot(feat_off)

        assert score_peak > score_off

    def test_platform_specific_recommendation_differences(self):
        engine = SchedulingEngine()

        ig_res = engine.recommend_best_times(platform="instagram", top_k=3)
        li_res = engine.recommend_best_times(platform="linkedin", top_k=3)

        assert len(ig_res.recommendations) == 3
        assert len(li_res.recommendations) == 3
        assert ig_res.baseline_accuracy == 88.08
        # Instagram optimal hours are in evening (18-21), LinkedIn in morning (8-14)
        assert any(r.scheduled_at.hour in [18, 19, 20, 21] for r in ig_res.recommendations)
        assert any(r.scheduled_at.hour in [8, 9, 10, 11, 14] for r in li_res.recommendations)

    def test_user_time_constraints_filtering(self):
        engine = SchedulingEngine()
        constraints = TimeConstraints(
            start_hour=14,
            end_hour=16,
            allowed_days=[0, 1, 2],  # Mon-Wed
        )

        res = engine.recommend_best_times(
            platform="instagram",
            constraints=constraints,
            top_k=5,
        )

        for rec in res.recommendations:
            assert 14 <= rec.scheduled_at.hour <= 16
            assert rec.scheduled_at.weekday() in [0, 1, 2]


class TestSchedulingService:
    """Test SchedulingService database and workflow integration."""

    @pytest.mark.asyncio
    async def test_recommend_and_auto_schedule(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        service = SchedulingService(mock_db)

        # 1. Recommend
        rec_req = ScheduleRecommendRequest(
            platform="instagram",
            text="Exciting news coming soon!",
            top_k=3,
        )
        rec_res = await service.recommend_times(rec_req)
        assert rec_res.platform == "instagram"
        assert len(rec_res.recommendations) == 3

        # 2. Auto-schedule
        user_id = uuid4()
        auto_req = AutoScheduleRequest(
            platform="instagram",
            content_type="post",
            text="Automated post at optimal time #ai",
            media=[MediaItem(type="image", url="https://example.com/pic.jpg")],
            start_hour=18,
            end_hour=21,
        )

        with patch("backend.app.services.post_service.PostService.create_post", new_callable=AsyncMock) as mock_create:
            mock_post_res = MagicMock()
            mock_post_res.id = str(uuid4())
            mock_create.return_value = mock_post_res

            auto_res = await service.auto_schedule_post(user_id, auto_req)

            assert auto_res.platform == "instagram"
            assert auto_res.status == "scheduled"
            assert 18 <= auto_res.scheduled_at.hour <= 21
            assert mock_db.add.called
            assert mock_db.commit.called


class TestSchedulingAPIEndpoints:
    """Test FastAPI /api/v1/scheduling endpoints."""

    def test_recommend_times_endpoint(self):
        resp = client.post(
            "/api/v1/scheduling/recommend-times",
            json={
                "platform": "instagram",
                "text": "Upcoming product drop!",
                "top_k": 3,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "instagram"
        assert len(data["recommendations"]) == 3
        assert "predicted_engagement_score" in data["recommendations"][0]

    def test_trigger_due_endpoint(self):
        with patch("backend.app.services.scheduling_service.SchedulingService.execute_due_schedules", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"processed": 2, "executed": 2, "failed": 0}
            resp = client.post("/api/v1/scheduling/trigger-due")
            assert resp.status_code == 200
            assert resp.json()["processed"] == 2
