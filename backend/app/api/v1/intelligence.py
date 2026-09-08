"""Post-Posting Intelligence API router."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.intelligence_service import IntelligenceService
from backend.app.core.schemas.intelligence import (
    CommentSyncRequest,
    CommentSyncResponse,
    TemporalSentimentResponse,
    IntelligenceAlertsResponse,
    PostIntelligenceReportResponse,
)

router = APIRouter(prefix="/intelligence", tags=["Post Intelligence"])


@router.post("/posts/{post_id}/sync-comments", response_model=CommentSyncResponse)
async def sync_post_comments(
    post_id: str,
    request: CommentSyncRequest = CommentSyncRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Synchronize comments across all connected platforms for a post and run sentiment analysis."""
    service = IntelligenceService(db)
    return await service.sync_comments_for_post(
        post_id=UUID(post_id),
        user_id=current_user.id,
        limit_per_platform=request.limit_per_platform,
    )


@router.get("/posts/{post_id}/sentiment-trajectory", response_model=TemporalSentimentResponse)
async def get_sentiment_trajectory(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve temporal sentiment evolution across the post's lifetime windows."""
    service = IntelligenceService(db)
    return await service.get_temporal_sentiment_trajectory(
        post_id=UUID(post_id),
        user_id=current_user.id,
    )


@router.get("/posts/{post_id}/alerts", response_model=IntelligenceAlertsResponse)
async def get_post_alerts(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active engagement spikes, negative sentiment waves, or unhandled inquiry alerts."""
    service = IntelligenceService(db)
    return await service.get_post_alerts(
        post_id=UUID(post_id),
        user_id=current_user.id,
    )


@router.get("/posts/{post_id}/report", response_model=PostIntelligenceReportResponse)
async def get_full_post_intelligence_report(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate comprehensive intelligence report combining metrics, sentiment trajectory, and alerts."""
    service = IntelligenceService(db)
    return await service.get_full_intelligence_report(
        post_id=UUID(post_id),
        user_id=current_user.id,
    )
