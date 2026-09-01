"""Auto-Reply Service - Business logic for comment classification, routing, and automated reply execution."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.ai.reply import (
    TFIDFReplyEngine,
    ReplyConfig,
    ReplyAction,
    ReplyIntent,
    AutomationMode,
)
from backend.app.core.schemas.reply import (
    CommentClassifyResponse,
    ReplySuggestResponse,
    ProcessCommentResponse,
    ApproveReplyResponse,
)
from backend.app.core.errors import NotFoundError, ValidationError, PlatformError


class ReplyService:
    """Service managing auto-reply classification, human-in-the-loop approvals, and platform response execution."""

    def __init__(self, db: AsyncSession, engine: Optional[TFIDFReplyEngine] = None):
        self.db = db
        self.engine = engine or TFIDFReplyEngine()

    def classify_comment(self, text: str) -> CommentClassifyResponse:
        """Classify incoming comment intent."""
        res = self.engine.classify_comment(text)
        return CommentClassifyResponse(
            intent=res.intent.value,
            confidence=res.confidence,
            all_probabilities=res.all_probabilities,
            keywords_detected=res.keywords_detected,
            baseline_accuracy=88.00,
        )

    def suggest_reply(
        self,
        comment_text: str,
        comment_id: str = "",
        automation_mode: str = "automatic",
    ) -> ReplySuggestResponse:
        """Generate response suggestion and determine routing action."""
        mode = AutomationMode(automation_mode.lower()) if automation_mode in AutomationMode._value2member_map_ else AutomationMode.AUTOMATIC
        self.engine.config.automation_mode = mode

        suggestion = self.engine.generate_reply(comment_text, comment_id=comment_id)
        return ReplySuggestResponse(
            comment_id=suggestion.comment_id,
            comment_text=suggestion.comment_text,
            intent=suggestion.intent.value,
            suggested_reply=suggestion.suggested_reply,
            confidence=suggestion.confidence,
            routing_action=suggestion.routing_action.value,
            requires_human_review=suggestion.requires_human_review,
            template_used=suggestion.template_used,
        )

    async def process_incoming_comment(
        self,
        platform: str,
        comment_id: str,
        comment_text: str,
        post_id: str = "",
        author_name: str = "",
        author_id: str = "",
    ) -> ProcessCommentResponse:
        """Process incoming comment through classification, policy evaluation, and optional auto-execution."""
        p_key = platform.lower()
        if not PlatformRegistry.is_registered(p_key):
            raise ValidationError(f"Unsupported platform: {platform}")

        adapter = PlatformRegistry.get_adapter(p_key)
        suggestion = self.engine.generate_reply(comment_text, comment_id=comment_id)

        action_taken = "ROUTED_TO_MANUAL"
        reply_id = None
        reply_text = suggestion.suggested_reply

        # 1. Automatic execution
        if suggestion.routing_action == ReplyAction.AUTOMATIC and adapter:
            try:
                sent_reply = await adapter.reply_to_comment(comment_id, suggestion.suggested_reply)
                reply_id = sent_reply.id if hasattr(sent_reply, "id") else str(sent_reply.get("id", "auto_reply_sent"))
                action_taken = "REPLY_SENT_AUTOMATICALLY"
            except Exception as e:
                action_taken = "QUEUED_FOR_APPROVAL"

        # 2. Approval required
        elif suggestion.routing_action == ReplyAction.APPROVAL_REQUIRED:
            action_taken = "QUEUED_FOR_APPROVAL"

        # 3. Spam ignore / hide
        elif suggestion.routing_action == ReplyAction.IGNORE_SPAM:
            action_taken = "SPAM_IGNORED"
            if adapter:
                try:
                    await adapter.hide_comment(comment_id)
                except Exception:
                    pass

        return ProcessCommentResponse(
            comment_id=comment_id,
            intent=suggestion.intent.value,
            confidence=suggestion.confidence,
            action_taken=action_taken,
            reply_text=reply_text if action_taken != "SPAM_IGNORED" else None,
            reply_id=reply_id,
            timestamp=datetime.now(timezone.utc),
        )

    async def approve_and_send_reply(
        self,
        platform: str,
        comment_id: str,
        reply_text: str,
        post_id: str = "",
    ) -> ApproveReplyResponse:
        """Approve and execute a reply on the target platform."""
        p_key = platform.lower()
        if not PlatformRegistry.is_registered(p_key):
            raise ValidationError(f"Unsupported platform: {platform}")

        adapter = PlatformRegistry.get_adapter(p_key)
        if not adapter:
            raise PlatformError(f"Adapter not available for: {platform}")

        sent_res = await adapter.reply_to_comment(comment_id, reply_text)
        reply_id = sent_res.id if hasattr(sent_res, "id") else str(sent_res.get("id", "approved_reply"))

        return ApproveReplyResponse(
            comment_id=comment_id,
            reply_id=reply_id,
            reply_text=reply_text,
            status="sent",
            timestamp=datetime.now(timezone.utc),
        )
