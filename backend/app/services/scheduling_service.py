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

        return AutoScheduleResponse(
            post_id=post_res.id,
            platform=request.platform,
            scheduled_at=scheduled_at,
            predicted_engagement_score=best_slot.predicted_engagement_score if best_slot else 0.0,
            reason=best_slot.reason if best_slot else "Optimal time slot",
            status="scheduled",
        )

    async def execute_due_schedules(self) -> Dict[str, Any]:
        """At-most-once dispatch claim. Interrupted claims require operator review."""
        from sqlalchemy import update
        from backend.app.services.owned_adapter import owned_adapter
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        result = await self.db.execute(select(Schedule).where(Schedule.status=='pending', Schedule.scheduled_at<=now))
        schedules = result.scalars().all()
        executed = failed = processed = 0
        for schedule in schedules:
            claim = await self.db.execute(update(Schedule).where(Schedule.id==schedule.id, Schedule.status=='pending')
                .values(status='publishing', last_attempt_at=now))
            await self.db.commit()  # claim durable before external side effects
            if claim.rowcount != 1:
                continue
            processed += 1
            post = await PostService(self.db).get_post(schedule.post_id, schedule.user_id)
            success = bool(post and post.publications)
            if post:
                for publication in post.publications:
                    if publication.status == 'published':
                        continue
                    try:
                        adapter = await owned_adapter(self.db, schedule.user_id, publication.platform)
                        payload = (publication.platform_data or {}).get('content')
                        if payload:
                            from backend.app.core.normalization import ContentNormalizer
                            payload['content_type'] = ContentType(payload['content_type'])
                            payload['media'] = [ContentNormalizer.normalize_media(m) for m in payload.get('media', [])]
                            payload['scheduled_at'] = None
                        content = UniversalContent(**payload) if payload else UniversalContent(
                            content_type=ContentType(post.content_type.value), text=post.text or post.caption or '',
                            caption=post.caption, hashtags=post.hashtags or [], mentions=post.mentions or [])
                        response = await adapter.publish_post(content)
                        if response.status != 'published' or not response.platform_post_id:
                            raise ValueError('Provider did not confirm publication')
                        publication.platform_post_id = response.platform_post_id
                        publication.permalink = response.url
                        publication.status = 'published'
                        publication.published_at = now
                        executed += 1
                    except Exception:
                        publication.status = 'failed'
                        publication.error_message = 'Publication not confirmed. Review provider before retrying.'
                        success = False
                        failed += 1
                post.status = PostStatusEnum.PUBLISHED if success else PostStatusEnum.FAILED
                if success:
                    post.published_at = now
            schedule.status = 'sent' if success else 'failed'
            await self.db.commit()
        return {'processed': processed, 'executed': executed, 'failed': failed, 'timestamp': now.isoformat()}


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
