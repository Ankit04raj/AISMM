"""AI Strategy Engine API endpoints."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.strategy_service import StrategyService
from backend.app.core.schemas.strategy import (
    ComprehensiveStrategyResponse,
    ContentDraftStrategyRequest,
    ContentStrategyPlan,
    PlatformStrategyAdvice,
    StrategyFeedbackRequest,
)

router = APIRouter(prefix="/strategy", tags=["AI Strategy Engine"])


@router.get("/dashboard", response_model=ComprehensiveStrategyResponse)
async def get_strategy_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve synthesized strategic directives, ranked recommendations, and platform guidance."""
    service = StrategyService(db)
    return await service.get_strategy_dashboard(current_user.id)


@router.post("/content-plan", response_model=ContentStrategyPlan)
async def generate_content_strategy_plan(
    request: ContentDraftStrategyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate multi-platform optimized captions, Top-K hashtags, peak timing, and projected engagement for a draft."""
    service = StrategyService(db)
    return await service.generate_content_plan(current_user.id, request)


@router.get("/platform-advice/{platform}", response_model=PlatformStrategyAdvice)
async def get_platform_advice(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get targeted posting frequency, format ROI, and styling guidance for a specific social network."""
    service = StrategyService(db)
    return await service.get_platform_advice(current_user.id, platform=platform)


@router.post("/feedback")
async def record_strategy_feedback(
    request: StrategyFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register user acceptance or rejection of strategic advice for automated continuous learning."""
    service = StrategyService(db)
    return await service.record_feedback(current_user.id, request)
