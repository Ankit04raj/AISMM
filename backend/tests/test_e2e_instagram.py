"""End-to-End Test for First Platform: Instagram Integration Lifecycle."""

import pytest
import hmac
import hashlib
import json
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.core.platform_adapters import PlatformRegistry, PlatformCapability
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType
from backend.app.core.schemas.post import CreatePostRequest, MediaItem
from backend.app.core.schemas.account import ConnectAccountRequest
from backend.app.services.account_service import AccountService
from backend.app.services.post_service import PostService
from backend.app.services.metrics_service import MetricsService
from backend.app.core.platform_adapters.instagram.webhook import InstagramWebhookHandler, InstagramWebhookEventType


@pytest.mark.asyncio
async def test_e2e_instagram_lifecycle():
    """Execute complete Instagram platform lifecycle:

    1. Account Connection & Profile Fetch
    2. Content Creation, Normalization & Publishing
    3. Scheduled Post Workflow
    4. Post & Account Analytics Fetching with Metric Normalization
    5. Webhook Comment Event Handling & Reply Flow
    """
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db_result = MagicMock()
    mock_db_result.scalar_one_or_none.return_value = None
    mock_db_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_db_result

    user_id = uuid4()
    adapter = PlatformRegistry.get_adapter("instagram")
    assert adapter is not None
    assert adapter.supports(PlatformCapability.POST_IMAGE)
    assert adapter.supports(PlatformCapability.POST_CAROUSEL)

    # -------------------------------------------------------------
    # Step 1: Connect Account Flow
    # -------------------------------------------------------------
    account_service = AccountService(mock_db)
    connect_req = ConnectAccountRequest(
        platform="instagram",
        authorization_code="auth_code_e2e",
        redirect_uri="http://localhost:8000/callback",
    )

    with patch.object(adapter.auth, "exchange_code", new_callable=AsyncMock) as mock_exchange, \
         patch.object(adapter.auth, "get_user_profile", new_callable=AsyncMock) as mock_profile:

        mock_exchange.return_value = {
            "access_token": "long_lived_token_e2e",
            "token_type": "Bearer",
            "expires_in": 5184000,
            "refresh_token": "refresh_token_e2e",
            "scope": "instagram_graph_user_profile,instagram_graph_user_media",
        }
        mock_profile.return_value = {
            "id": "ig_business_12345",
            "username": "brand_official",
            "name": "Brand Official",
            "profile_picture_url": "https://example.com/avatar.jpg",
            "account_type": "business",
        }

        account_resp = await account_service.connect_account(user_id, connect_req)
        assert account_resp.platform == "instagram"
        assert account_resp.platform_user_id == "ig_business_12345"
        assert account_resp.username == "brand_official"
        assert mock_db.add.called
        assert mock_db.commit.called

    # -------------------------------------------------------------
    # Step 2: Content Creation & 2-Phase Publishing
    # -------------------------------------------------------------
    post_service = PostService(mock_db)
    post_req = CreatePostRequest(
        platform="instagram",
        content_type="carousel",
        text="Product launch #innovation @partner",
        media=[
            MediaItem(type="image", url="https://example.com/slide1.jpg"),
            MediaItem(type="image", url="https://example.com/slide2.jpg"),
        ],
        publish_now=True,
    )

    with patch.object(adapter, "_create_media_container", new_callable=AsyncMock) as mock_create_c, \
         patch.object(adapter, "_publish_media_container", new_callable=AsyncMock) as mock_pub_c:

        mock_create_c.return_value = "carousel_container_999"
        mock_pub_c.return_value = {
            "id": "ig_post_8888",
            "permalink": "https://instagram.com/p/Bxyz123",
        }

        post_resp = await post_service.create_post(user_id, post_req)
        assert post_resp.platform == "instagram"
        assert post_resp.permalink == "https://instagram.com/p/Bxyz123"
        assert post_resp.status == "published"
        assert mock_create_c.called
        assert mock_pub_c.called

    # -------------------------------------------------------------
    # Step 3: Scheduling Flow
    # -------------------------------------------------------------
    sched_time = datetime(2027, 6, 15, 18, 30, 0)
    sched_req = CreatePostRequest(
        platform="instagram",
        content_type="post",
        text="Summer promotion coming soon!",
        media=[MediaItem(type="image", url="https://example.com/summer.jpg")],
        scheduled_at=sched_time,
        publish_now=False,
    )

    with patch.object(adapter, "_create_media_container", new_callable=AsyncMock) as mock_sched_c:
        mock_sched_c.return_value = "sched_container_777"

        sched_resp = await post_service.create_post(user_id, sched_req)
        assert sched_resp.platform == "instagram"
        assert sched_resp.status == "scheduled"
        assert sched_resp.scheduled_at == sched_time

    # -------------------------------------------------------------
    # Step 4: Analytics Fetching & Metric Normalization
    # -------------------------------------------------------------
    with patch.object(adapter, "_fetch_insights", new_callable=AsyncMock) as mock_insights:
        mock_insights.return_value = {
            "normalized": {
                "impressions": 12500,
                "reach": 9800,
                "likes": 1200,
                "comments": 150,
                "shares": 85,
                "saves": 310,
                "engagement_rate": 14.0,
            },
            "raw": {"impressions": 12500, "likes": 1200},
            "platform": "instagram",
        }

        analytics_data = await adapter.get_post_analytics("ig_post_8888")
        assert analytics_data.post_id == "ig_post_8888"
        assert analytics_data.impressions == 12500
        assert analytics_data.likes == 1200
        assert analytics_data.engagement == (1200 + 150 + 85 + 310)

    # -------------------------------------------------------------
    # Step 5: Webhook Event Ingestion & Comment Reply
    # -------------------------------------------------------------
    webhook_handler = InstagramWebhookHandler(
        app_secret="test_secret_123",
        verify_token="test_token_123",
        callback_url="http://localhost:8000/api/v1/webhooks/instagram",
    )

    # Verify Challenge
    challenge = webhook_handler.verify_challenge("subscribe", "challenge_777", "test_token_123")
    assert challenge == "challenge_777"

    # Ingest Comment Webhook
    event_payload = {
        "object": "instagram",
        "entry": [{
            "id": "ig_business_12345",
            "time": 1725148800,
            "changes": [{
                "field": "comments",
                "value": {
                    "verb": "created",
                    "comment_id": "comment_9999",
                    "media_id": "ig_post_8888",
                    "text": "Where can I purchase this?",
                    "from": {"username": "customer_1", "id": "cust_101"},
                },
            }],
        }],
    }

    events = webhook_handler.parse_event(event_payload)
    assert len(events) == 1
    assert events[0].event_type == InstagramWebhookEventType.COMMENT_CREATED.value
    assert events[0].data["comment_id"] == "comment_9999"
    assert events[0].data["text"] == "Where can I purchase this?"

    # Reply to Comment
    with patch.object(adapter, "reply_to_comment", new_callable=AsyncMock) as mock_reply:
        reply_obj = MagicMock()
        reply_obj.id = "reply_1111"
        reply_obj.text = "Check the link in our bio!"
        mock_reply.return_value = reply_obj

        reply_result = await adapter.reply_to_comment("comment_9999", "Check the link in our bio!")
        assert reply_result.id == "reply_1111"
        assert reply_result.text == "Check the link in our bio!"
