"""Tests for Phase 8 Intelligent Scheduling Engine (ML Ensemble, Features, API, Service)."""

import pytest
import asyncio
import os
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from backend.app.main import app
from backend.app.db.session import Base
from backend.app.db.models import User, Schedule, Post, PostPublication, ContentTypeEnum, PostStatusEnum
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.platform_adapters.base import PostResult
from backend.app.ai.scheduling import (
    SchedulingEngine,
    SchedulingFeatureExtractor,
    TimeConstraints,
)
from backend.app.services.scheduling_service import (
    SchedulingService,
    run_scheduler_background_worker,
)
from backend.app.core.schemas.scheduling import (
    ScheduleRecommendRequest,
    AutoScheduleRequest,
)
from backend.app.core.schemas.post import MediaItem

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


class TestBackgroundScheduledExecutionProof:
    """Proof for Section 4: Scheduled post execution happens automatically in the background."""

    @pytest.mark.asyncio
    async def test_automatic_background_execution_without_manual_trigger(self):
        """Schedule a post slightly in the future (or due), do nothing else, and show it reaches published on its own."""
        db_file = f"/tmp/test_sched_{uuid4().hex}.db"
        if os.path.exists(db_file):
            os.remove(db_file)

        test_engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", echo=False)
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

        user_id = uuid4()
        post_id = uuid4()
        due_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1)

        async with session_factory() as session:
            # 1. Create User
            user = User(
                id=user_id,
                email=f"scheduler_auto_{uuid4().hex[:8]}@aismm.io",
                hashed_password="hash",
                full_name="Scheduler Test",
            )
            session.add(user)

            # 2. Create Post in DRAFT / SCHEDULED state
            post = Post(
                id=post_id,
                user_id=user_id,
                caption="Autonomous background publish proof post #automation",
                content_type=ContentTypeEnum.POST,
                status=PostStatusEnum.SCHEDULED,
            )
            session.add(post)

            # 3. Create Schedule record scheduled due in 0.2s
            schedule = Schedule(
                user_id=user_id,
                post_id=post_id,
                scheduled_at=due_time,
                status="pending",
            )
            session.add(schedule)

            pub = PostPublication(
                post_id=post_id,
                platform="instagram",
                status="pending",
            )
            session.add(pub)

            await session.commit()

        # 4. Mock platform adapter to return successful PostResult and run the background worker loop
        adapter = PlatformRegistry.get_adapter("instagram")
        mock_result = PostResult(
            platform_post_id="ig_auto_published_999",
            url="https://instagram.com/p/auto_published_999",
        )

        with patch.object(adapter, "publish_post", new_callable=AsyncMock, return_value=mock_result):
            # Start background worker task with 0.05s poll interval pointing to our test session factory
            worker_task = asyncio.create_task(run_scheduler_background_worker(interval_seconds=0.05, session_factory=session_factory))

            # Allow event loop iterations for the background worker to execute the due post
            for _ in range(10):
                await asyncio.sleep(0.1)

            # Stop the worker task
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass

        # 5. Verify the post and schedule reached PUBLISHED automatically with NO manual trigger
        async with session_factory() as session:
            sched_result = await session.execute(select(Schedule).where(Schedule.post_id == post_id))
            updated_sched = sched_result.scalar_one()

            post_result = await session.execute(select(Post).where(Post.id == post_id))
            updated_post = post_result.scalar_one()

            pub_result = await session.execute(select(PostPublication).where(PostPublication.post_id == post_id))
            updated_pub = pub_result.scalar_one()

            # Assert automatic transitions
            assert updated_sched.status == "sent", f"Expected 'sent', got '{updated_sched.status}'"
            assert updated_post.status == PostStatusEnum.PUBLISHED, f"Expected PUBLISHED, got '{updated_post.status}'"
            assert updated_post.published_at is not None
            assert updated_pub.status == "published"
            assert updated_pub.platform_post_id == "ig_auto_published_999"

        await test_engine.dispose()
        if os.path.exists(db_file):
            os.remove(db_file)
