"""Auto-Reply API router."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.services.reply_service import ReplyService
from backend.app.core.schemas.reply import (
    CommentClassifyRequest,
    CommentClassifyResponse,
    ReplySuggestRequest,
    ReplySuggestResponse,
    ProcessCommentRequest,
    ProcessCommentResponse,
    ApproveReplyRequest,
    ApproveReplyResponse,
)

router = APIRouter(prefix="/reply", tags=["Auto-Reply Engine"])


@router.post("/classify", response_model=CommentClassifyResponse)
async def classify_comment_intent(
    request: CommentClassifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Classify comment into intent categories using TF-IDF + Logistic Regression."""
    service = ReplyService(db)
    return service.classify_comment(request.text)


@router.post("/suggest", response_model=ReplySuggestResponse)
async def suggest_comment_reply(
    request: ReplySuggestRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate reply suggestion and determine policy routing (automatic, approval, manual, spam)."""
    service = ReplyService(db)
    return service.suggest_reply(
        comment_text=request.comment_text,
        comment_id=request.comment_id or "",
        automation_mode=request.automation_mode or "automatic",
    )


@router.post("/process-comment", response_model=ProcessCommentResponse)
async def process_incoming_comment(
    request: ProcessCommentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Process incoming comment event through auto-reply policy and optional execution."""
    service = ReplyService(db)
    return await service.process_incoming_comment(
        platform=request.platform,
        comment_id=request.comment_id,
        comment_text=request.comment_text,
        post_id=request.post_id or "",
        author_name=request.author_name or "",
        author_id=request.author_id or "",
    )


@router.post("/approve", response_model=ApproveReplyResponse)
async def approve_and_send_reply(
    request: ApproveReplyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Approve or edit a pending auto-reply suggestion and send to the social network."""
    service = ReplyService(db)
    return await service.approve_and_send_reply(
        platform=request.platform,
        comment_id=request.comment_id,
        reply_text=request.reply_text,
        post_id=request.post_id or "",
    )
