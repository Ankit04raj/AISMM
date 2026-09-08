"""Pydantic schemas for Phase 10 Auto-Reply Engine."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CommentClassifyRequest(BaseModel):
    """Request to classify comment intent."""
    text: str = Field(..., min_length=1, description="Comment text to classify")


class CommentClassifyResponse(BaseModel):
    """Classification response with probabilities and detected keywords."""
    intent: str
    confidence: float
    all_probabilities: Dict[str, float]
    keywords_detected: List[str]
    baseline_accuracy: float = 88.00


class ReplySuggestRequest(BaseModel):
    """Request to generate reply suggestion and routing action."""
    comment_text: str = Field(..., min_length=1)
    comment_id: Optional[str] = ""
    platform: str = "instagram"
    automation_mode: Optional[str] = "automatic"


class ReplySuggestResponse(BaseModel):
    """Reply suggestion and routing response."""
    comment_id: str
    comment_text: str
    intent: str
    suggested_reply: str
    confidence: float
    routing_action: str  # "automatic", "approval_required", "manual", "ignore_spam"
    requires_human_review: bool
    template_used: str


class ProcessCommentRequest(BaseModel):
    """Request to process an incoming comment through auto-reply pipeline."""
    platform: str
    comment_id: str
    comment_text: str
    post_id: Optional[str] = ""
    author_name: Optional[str] = ""
    author_id: Optional[str] = ""


class ProcessCommentResponse(BaseModel):
    """Outcome of processing an incoming comment."""
    comment_id: str
    intent: str
    confidence: float
    action_taken: str  # "REPLY_SENT_AUTOMATICALLY", "QUEUED_FOR_APPROVAL", "ROUTED_TO_MANUAL", "SPAM_IGNORED"
    reply_text: Optional[str] = None
    reply_id: Optional[str] = None
    timestamp: datetime


class ApproveReplyRequest(BaseModel):
    """Request to approve or edit a pending auto-reply suggestion."""
    platform: str
    comment_id: str
    reply_text: str
    post_id: Optional[str] = ""


class ApproveReplyResponse(BaseModel):
    """Result of executing an approved reply."""
    comment_id: str
    reply_id: str
    reply_text: str
    status: str = "sent"
    timestamp: datetime
