"""Intelligent Scheduling API router."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.services.scheduling_service import SchedulingService
from backend.app.core.schemas.scheduling import (
    ScheduleRecommendRequest,
    ScheduleRecommendResponse,
    AutoScheduleRequest,
    AutoScheduleResponse,
)

router = APIRouter(prefix="/scheduling", tags=["Intelligent Scheduling"])

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("/recommend-times", response_model=ScheduleRecommendResponse)
async def get_recommended_posting_times(
    request: ScheduleRecommendRequest,
    db: AsyncSession = Depends(get_db),
):
    """Predict optimal posting times for highest audience engagement using ML ensemble."""
    service = SchedulingService(db)
    return await service.recommend_times(request)


@router.post("/auto-schedule", response_model=AutoScheduleResponse, status_code=status.HTTP_201_CREATED)
async def auto_schedule_post(
    request: AutoScheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    """Automatically schedule a post at the AI-predicted optimal time slot."""
    service = SchedulingService(db)
    return await service.auto_schedule_post(DEFAULT_USER_ID, request)


@router.post("/trigger-due")
async def trigger_due_scheduled_posts(
    db: AsyncSession = Depends(get_db),
):
    """Background worker endpoint to trigger publishing of due scheduled posts."""
    service = SchedulingService(db)
    return await service.execute_due_schedules()
