"""Metrics and Analytics API router."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.services.metrics_service import MetricsService
from backend.app.core.schemas.insights import PostInsights, AccountInsights

router = APIRouter(prefix="/metrics", tags=["Metrics"])

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.get("/overview")
async def get_overview(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated metrics overview for user."""
    service = MetricsService(db)
    return await service.get_user_overview(DEFAULT_USER_ID, days)


@router.get("/top-posts")
async def get_top_posts(
    metric: str = "impressions",
    limit: int = 10,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Get top performing posts."""
    service = MetricsService(db)
    return await service.get_top_posts(DEFAULT_USER_ID, metric, limit, days)


@router.get("/engagement-trends")
async def get_engagement_trends(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Get engagement trends over time."""
    service = MetricsService(db)
    return await service.get_engagement_trends(DEFAULT_USER_ID, days)


@router.get("/posts/{post_id}", response_model=PostInsights)
async def get_post_insights(
    post_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get analytics and insights for a specific post."""
    service = MetricsService(db)
    insights = await service.get_post_insights(UUID(post_id), DEFAULT_USER_ID)
    if not insights:
        raise HTTPException(status_code=404, detail="Insights not found for post")
    return insights
