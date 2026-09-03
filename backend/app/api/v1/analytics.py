"""Universal Analytics Dashboard API router."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.analytics_service import AnalyticsService
from backend.app.core.schemas.analytics import (
    OverviewMetrics,
    PlatformComparisonResponse,
    ContentPerformanceResponse,
    TemporalAnalyticsResponse,
    SentimentTrendSummary,
    GrowthAccuracyReportResponse,
)

router = APIRouter(prefix="/analytics", tags=["Universal Analytics Dashboard"])


@router.get("/dashboard", response_model=OverviewMetrics)
async def get_dashboard_overview(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated multi-platform metrics (reach, impressions, engagement rate, posts, sentiment)."""
    service = AnalyticsService(db)
    return await service.get_dashboard_overview(current_user.id, days=days)


@router.get("/comparison", response_model=PlatformComparisonResponse)
async def get_platform_comparison(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Comparative performance benchmarking across active social platforms."""
    service = AnalyticsService(db)
    return await service.get_platform_comparison(current_user.id, days=days)


@router.get("/content", response_model=ContentPerformanceResponse)
async def get_content_performance(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rank top/bottom posts, evaluate content format ROI, and identify top hashtags."""
    service = AnalyticsService(db)
    return await service.get_content_performance(current_user.id, days=days)


@router.get("/temporal", response_model=TemporalAnalyticsResponse)
async def get_temporal_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Temporal heatmaps, peak engagement hours, and weekday vs weekend lift."""
    service = AnalyticsService(db)
    return await service.get_temporal_analytics(current_user.id, days=days)


@router.get("/sentiment-trends", response_model=SentimentTrendSummary)
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Historical sentiment trend distributions and audience mood health status."""
    service = AnalyticsService(db)
    return await service.get_sentiment_trends(current_user.id, days=days)


@router.get("/growth-accuracy", response_model=GrowthAccuracyReportResponse)
async def get_growth_accuracy_report(
    platform: str = Query("instagram"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Model evaluation comparing actual audience growth against ML predictions for drift monitoring."""
    service = AnalyticsService(db)
    return await service.get_growth_accuracy_report(current_user.id, platform=platform)
