"""Tests for Phase 10 Auto-Reply Engine (TF-IDF Classifier, Routing, Policy, API Endpoints)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai.reply import (
    TFIDFReplyEngine,
    ReplyIntent,
    ReplyAction,
    AutomationMode,
    ReplyConfig,
)
from backend.app.services.reply_service import ReplyService
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.platform_adapters.base import CommentData

client = TestClient(app)


class TestTFIDFReplyEngine:
    """Test machine learning comment classification and response suggestion."""

    def test_pricing_inquiry_classification(self):
        engine = TFIDFReplyEngine()
        res = engine.classify_comment("What is the pricing for your pro subscription?")
        assert res.intent == ReplyIntent.PRICING_INQUIRY
        assert res.confidence >= 0.70
        assert "pricing" in res.keywords_detected

    def test_compliment_praise_classification(self):
        engine = TFIDFReplyEngine()
        res = engine.classify_comment("Loving the new release, amazing work team! ❤️🔥")
        assert res.intent == ReplyIntent.COMPLIMENT_PRAISE
        assert res.confidence >= 0.75

    def test_support_issue_classification(self):
        engine = TFIDFReplyEngine()
        res = engine.classify_comment("The app crashed and threw an error when uploading media.")
        assert res.intent == ReplyIntent.SUPPORT_ISSUE
        assert "support" in res.keywords_detected

    def test_spam_detection(self):
        engine = TFIDFReplyEngine()
        res = engine.classify_comment("Check out my bio for free crypto gains and 100k followers!")
        assert res.intent == ReplyIntent.SPAM_TROLL
        assert res.confidence >= 0.90

    def test_human_in_the_loop_routing_policy(self):
        engine = TFIDFReplyEngine()

        # 1. Compliment with high confidence -> Automatic
        high_conf_sugg = engine.generate_reply("Amazing work team, love this! ❤️")
        assert high_conf_sugg.intent == ReplyIntent.COMPLIMENT_PRAISE
        assert high_conf_sugg.routing_action in (ReplyAction.AUTOMATIC, ReplyAction.APPROVAL_REQUIRED)
        assert len(high_conf_sugg.suggested_reply) > 0

        # 2. Support issue -> Approval Required (safety guardrail)
        support_sugg = engine.generate_reply("My payment failed and getting error code 400.")
        assert support_sugg.intent == ReplyIntent.SUPPORT_ISSUE
        assert support_sugg.routing_action == ReplyAction.APPROVAL_REQUIRED
        assert support_sugg.requires_human_review is True

        # 3. Spam -> Ignore
        spam_sugg = engine.generate_reply("Follow for follow back guaranteed free money!")
        assert spam_sugg.routing_action == ReplyAction.IGNORE_SPAM
        assert spam_sugg.suggested_reply == ""


class TestReplyService:
    """Test ReplyService business logic and execution."""

    @pytest.mark.asyncio
    async def test_process_comment_automatic_execution(self):
        mock_db = AsyncMock()
        service = ReplyService(mock_db)

        adapter = PlatformRegistry.get_adapter("instagram")
        with patch.object(adapter, "reply_to_comment", new_callable=AsyncMock) as mock_reply:
            mock_comment = MagicMock()
            mock_comment.id = "sent_reply_777"
            mock_reply.return_value = mock_comment

            res = await service.process_incoming_comment(
                platform="instagram",
                comment_id="c_1001",
                comment_text="Awesome launch team, loving this! 🎉",
            )

            assert res.comment_id == "c_1001"
            assert res.action_taken in ("REPLY_SENT_AUTOMATICALLY", "QUEUED_FOR_APPROVAL")
            if res.action_taken == "REPLY_SENT_AUTOMATICALLY":
                assert res.reply_id == "sent_reply_777"
                assert mock_reply.called

    @pytest.mark.asyncio
    async def test_approve_and_send_reply(self):
        mock_db = AsyncMock()
        service = ReplyService(mock_db)

        adapter = PlatformRegistry.get_adapter("instagram")
        with patch.object(adapter, "reply_to_comment", new_callable=AsyncMock) as mock_reply:
            mock_comment = MagicMock()
            mock_comment.id = "approved_sent_888"
            mock_reply.return_value = mock_comment

            resp = await service.approve_and_send_reply(
                platform="instagram",
                comment_id="c_2002",
                reply_text="Thanks for your feedback!",
            )

            assert resp.comment_id == "c_2002"
            assert resp.reply_id == "approved_sent_888"
            assert resp.status == "sent"
            assert mock_reply.called


class TestReplyAPIEndpoints:
    """Test FastAPI /api/v1/reply endpoints."""

    def test_classify_endpoint(self):
        resp = client.post("/api/v1/reply/classify", json={"text": "How much does a monthly plan cost?"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "pricing_inquiry"
        assert data["confidence"] > 0.60

    def test_suggest_endpoint(self):
        resp = client.post(
            "/api/v1/reply/suggest",
            json={"comment_text": "Love your product, super helpful!", "platform": "instagram"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "compliment_praise"
        assert len(data["suggested_reply"]) > 0
        assert data["routing_action"] in ("automatic", "approval_required")

    def test_approve_endpoint(self):
        adapter = PlatformRegistry.get_adapter("instagram")
        with patch.object(adapter, "reply_to_comment", new_callable=AsyncMock) as mock_reply:
            mock_c = MagicMock()
            mock_c.id = "reply_resp_123"
            mock_reply.return_value = mock_c

            resp = client.post(
                "/api/v1/reply/approve",
                json={
                    "platform": "instagram",
                    "comment_id": "c_505",
                    "reply_text": "Thank you for reaching out!",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["comment_id"] == "c_505"
            assert data["reply_id"] == "reply_resp_123"
            assert data["status"] == "sent"
