"""Auto-Reply API router."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Classify comment into intent categories using TF-IDF + Logistic Regression."""
    service = ReplyService(db)
    return service.classify_comment(request.text)


@router.post("/suggest", response_model=ReplySuggestResponse)
async def suggest_comment_reply(
    request: ReplySuggestRequest,
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process incoming comment event through auto-reply policy and optional execution."""
    raise HTTPException(503, 'Unattended auto-reply dispatch is not available. Review a reply in the owner-scoped inbox.')


@router.post("/approve", response_model=ApproveReplyResponse)
async def approve_and_send_reply(
    request: ApproveReplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve or edit a pending auto-reply suggestion and send to the social network."""
    from backend.app.api.v1.comments import reply_to_comment
    from backend.app.core.schemas.post import ReplyToCommentRequest
    from datetime import datetime, timezone
    reply = await reply_to_comment(request.platform, request.comment_id, ReplyToCommentRequest(text=request.reply_text), current_user, db)
    return ApproveReplyResponse(comment_id=request.comment_id, reply_id=reply['id'], reply_text=request.reply_text, status='sent', timestamp=datetime.now(timezone.utc))
