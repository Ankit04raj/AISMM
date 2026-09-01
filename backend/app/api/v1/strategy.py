"""AI Strategy Engine API endpoints."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.services.strategy_service import StrategyService
from backend.app.core.schemas.strategy import (
    ComprehensiveStrategyResponse,
    ContentDraftStrategyRequest,
    ContentStrategyPlan,
    PlatformStrategyAdvice,
    StrategyFeedbackRequest,
)

router = APIRouter(prefix="/strategy", tags=["AI Strategy Engine"])

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.get("/dashboard", response_model=ComprehensiveStrategyResponse)
async def get_strategy_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve synthesized strategic directives, ranked recommendations, and platform guidance."""
    service = StrategyService(db)
    return await service.get_strategy_dashboard(DEFAULT_USER_ID)


@router.post("/content-plan", response_model=ContentStrategyPlan)
async def generate_content_strategy_plan(
    request: ContentDraftStrategyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate multi-platform optimized captions, Top-K hashtags, peak timing, and projected engagement for a draft."""
    service = StrategyService(db)
    return await service.generate_content_plan(DEFAULT_USER_ID, request)


@router.get("/platform-advice/{platform}", response_model=PlatformStrategyAdvice)
async def get_platform_advice(
    platform: str,
    db: AsyncSession = Depends(get_db),
):
    """Get targeted posting frequency, format ROI, and styling guidance for a specific social network."""
    service = StrategyService(db)
    return await service.get_platform_advice(DEFAULT_USER_ID, platform=platform)


@router.post("/feedback")
async def record_strategy_feedback(
    request: StrategyFeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register user acceptance or rejection of strategic advice for automated continuous learning."""
    service = StrategyService(db)
    return await service.record_feedback(DEFAULT_USER_ID, request)
