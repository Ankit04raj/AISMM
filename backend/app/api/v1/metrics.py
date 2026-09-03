"""Metrics and Analytics API router."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.metrics_service import MetricsService
from backend.app.core.schemas.insights import PostInsights, AccountInsights

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/overview")
async def get_overview(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated metrics overview for user."""
    service = MetricsService(db)
    return await service.get_user_overview(current_user.id, days)


@router.get("/top-posts")
async def get_top_posts(
    metric: str = "impressions",
    limit: int = 10,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get top performing posts."""
    service = MetricsService(db)
    return await service.get_top_posts(current_user.id, metric, limit, days)


@router.get("/engagement-trends")
async def get_engagement_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get engagement trends over time."""
    service = MetricsService(db)
    return await service.get_engagement_trends(current_user.id, days)


@router.get("/posts/{post_id}", response_model=PostInsights)
async def get_post_insights(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics and insights for a specific post."""
    service = MetricsService(db)
    insights = await service.get_post_insights(UUID(post_id), current_user.id)
    if not insights:
        raise HTTPException(status_code=404, detail="Insights not found for post")
    return insights
