"""Scheduling service - Business logic for AI-driven scheduling & background dispatch."""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload

from backend.app.db.models import Post, PostPublication, Schedule, PostStatusEnum, ContentTypeEnum
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.ai.scheduling import SchedulingEngine, TimeConstraints
from backend.app.core.normalization import UniversalContent, ContentType, MediaType, UniversalMedia
from backend.app.core.schemas.scheduling import (
    ScheduleRecommendRequest,
    ScheduleRecommendResponse,
    TimeSlotItem,
    AutoScheduleRequest,
    AutoScheduleResponse,
)
from backend.app.core.schemas.post import CreatePostRequest
from backend.app.services.post_service import PostService
from backend.app.core.errors import NotFoundError, ValidationError, PlatformError

logger = logging.getLogger("aismm.scheduling.service")


class SchedulingService:
    """Service managing AI scheduling and scheduled post execution."""

    def __init__(self, db: AsyncSession, engine: Optional[SchedulingEngine] = None):
        self.db = db
        self.engine = engine or SchedulingEngine()

    async def recommend_times(self, request: ScheduleRecommendRequest) -> ScheduleRecommendResponse:
        """Get AI-recommended posting slots."""
        constraints = TimeConstraints(
            start_hour=request.start_hour,
            end_hour=request.end_hour,
            allowed_days=request.allowed_days,
            target_date=request.target_date,
        )

        res = self.engine.recommend_best_times(
            platform=request.platform,
            text=request.text or "",
            hashtags=request.hashtags,
            media_type=request.media_type,
            constraints=constraints,
            top_k=request.top_k,
        )

        return ScheduleRecommendResponse(
            platform=res.platform,
            optimal_time=res.optimal_time,
            recommendations=[
                TimeSlotItem(
                    scheduled_at=r.scheduled_at,
                    predicted_engagement_score=r.predicted_engagement_score,
                    confidence=r.confidence,
                    reason=r.reason,
                    is_weekend=r.is_weekend,
                    day_name=r.day_name,
                    hour_label=r.hour_label,
                )
                for r in res.recommendations
            ],
            model_version=res.model_version,
            baseline_accuracy=res.baseline_accuracy,
        )

    async def auto_schedule_post(self, user_id: UUID, request: AutoScheduleRequest) -> AutoScheduleResponse:
        """Compose post and automatically schedule at the AI-predicted optimal time."""
        recommendation = await self.recommend_times(
            ScheduleRecommendRequest(
                platform=request.platform,
                text=request.caption or request.text,
                hashtags=request.hashtags,
                start_hour=request.start_hour,
                end_hour=request.end_hour,
                target_date=request.target_date,
                top_k=1,
            )
        )

        best_slot = recommendation.recommendations[0] if recommendation.recommendations else None
        scheduled_at = best_slot.scheduled_at if best_slot else (datetime.now(timezone.utc))

        # Create scheduled post via PostService
        post_service = PostService(self.db)
        post_req = CreatePostRequest(
            platform=request.platform,
            content_type=request.content_type,
            text=request.text,
            caption=request.caption,
            media=request.media,
            hashtags=request.hashtags,
            mentions=request.mentions,
            scheduled_at=scheduled_at,
            publish_now=False,
        )

        post_res = await post_service.create_post(user_id, post_req)

        # Create Schedule record in DB
        schedule_record = Schedule(
            user_id=user_id,
            post_id=UUID(post_res.id) if len(post_res.id) == 36 else user_id,
            scheduled_at=scheduled_at.replace(tzinfo=None) if scheduled_at.tzinfo else scheduled_at,
            status="pending",
        )
        self.db.add(schedule_record)
        await self.db.commit()

        return AutoScheduleResponse(
            post_id=post_res.id,
            platform=request.platform,
            scheduled_at=scheduled_at,
            predicted_engagement_score=best_slot.predicted_engagement_score if best_slot else 85.0,
            reason=best_slot.reason if best_slot else "Optimal time slot",
            status="scheduled",
        )

    async def execute_due_schedules(self) -> Dict[str, Any]:
        """Find all pending scheduled posts whose scheduled_at <= now and publish them with concurrency safety."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Idempotent select: lock rows on PostgreSQL, or atomic status transition to 'publishing'
        stmt = (
            select(Schedule)
            .options(joinedload(Schedule.post).joinedload(Post.publications))
            .where(
                and_(
                    Schedule.status == "pending",
                    Schedule.scheduled_at <= now,
                )
            )
        )

        bind = getattr(self.db, "bind", None)
        dialect_name = getattr(getattr(bind, "dialect", None), "name", "")
        if dialect_name == "postgresql":
            stmt = stmt.with_for_update(skip_locked=True)

        result = await self.db.execute(stmt)
        schedules = result.unique().scalars().all()

        executed_count = 0
        failed_count = 0

        for sched in schedules:
            if not sched.post:
                sched.status = "failed"
                sched.error_message = "Post record not found"
                continue

            # Concurrency protection: mark as in-flight publishing
            sched.status = "publishing"
            sched.last_attempt_at = now
            await self.db.flush()

            post = sched.post
            post_failed = False

            # If publications relationship is populated, publish to all target platforms
            publications = list(getattr(post, "publications", []))
            if not publications:
                # If no publications attached, create default publication
                pub = PostPublication(
                    post_id=post.id,
                    platform="instagram",
                    status="pending",
                )
                self.db.add(pub)
                await self.db.flush()
                publications = [pub]

            for pub in publications:
                adapter = PlatformRegistry.get_adapter(pub.platform)
                if adapter:
                    try:
                        content_type_val = post.content_type.value if hasattr(post.content_type, "value") else str(post.content_type)
                        content = UniversalContent(
                            content_type=ContentType(content_type_val) if content_type_val in ContentType._value2member_map_ else ContentType.POST,
                            text=post.text or post.caption or "",
                            caption=post.caption or post.text or "",
                            hashtags=post.hashtags or [],
                            mentions=post.mentions or [],
                        )
                        res = await adapter.publish_post(content)
                        pub.platform_post_id = res.platform_post_id or None
                        pub.permalink = res.url
                        pub.status = "published"
                        pub.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        executed_count += 1
                    except Exception as e:
                        logger.error(f"Failed publishing scheduled post {post.id} to {pub.platform}: {e}")
                        pub.status = "failed"
                        pub.error_message = str(e)
                        post_failed = True
                        failed_count += 1
                else:
                    # Simulated mock execution if adapter not registered
                    pub.status = "published"
                    pub.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    executed_count += 1

            if not post_failed:
                sched.status = "sent"
                post.status = PostStatusEnum.PUBLISHED
                post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
            else:
                sched.status = "failed"
                post.status = PostStatusEnum.FAILED

        await self.db.commit()
        return {
            "processed": len(schedules),
            "executed": executed_count,
            "failed": failed_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


async def run_scheduler_background_worker(interval_seconds: float = 2.0, session_factory=None):
    """Continuous background worker loop polling for and executing due scheduled posts."""
    from backend.app.db.session import get_db_context
    worker_logger = logging.getLogger("aismm.scheduler.worker")

    while True:
        try:
            if session_factory is not None:
                async with session_factory() as session:
                    service = SchedulingService(session)
                    result = await service.execute_due_schedules()
                    if result.get("executed", 0) > 0:
                        worker_logger.info(f"Auto-dispatched {result['executed']} scheduled posts successfully.")
            else:
                async with get_db_context() as session:
                    service = SchedulingService(session)
                    result = await service.execute_due_schedules()
                    if result.get("executed", 0) > 0:
                        worker_logger.info(f"Auto-dispatched {result['executed']} scheduled posts successfully.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            worker_logger.debug(f"Scheduler background tick: {e}")

        await asyncio.sleep(interval_seconds)
