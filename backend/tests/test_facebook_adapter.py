"""Tests for Facebook Platform Adapter (Phase 5 Architectural Validation)."""

import pytest
import hmac
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.app.core.platform_adapters.facebook.adapter import FacebookAdapter
from backend.app.core.platform_adapters.facebook.auth import FacebookAuth, FacebookAuthConfig
from backend.app.core.platform_adapters.facebook.config import FacebookConfig, FacebookAuthConfig as CfgAuth
from backend.app.core.platform_adapters.facebook.webhook import FacebookWebhookHandler, FacebookWebhookEventType
from backend.app.core.platform_adapters.capabilities import PlatformCapability
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType


class TestFacebookAdapter:
    """Test FacebookAdapter contract and capabilities."""

    @pytest.fixture
    def adapter(self):
        return FacebookAdapter({
            "client_id": "test_fb_id",
            "client_secret": "test_fb_secret",
            "redirect_uri": "http://localhost:8000/callback",
            "access_token": "test_fb_token",
            "page_id": "123456789",
        })

    def test_adapter_initialization(self, adapter):
        assert adapter.PLATFORM_NAME == "facebook"
        assert adapter.platform_name == "facebook"
        assert adapter.page_id == "123456789"

    @pytest.mark.asyncio
    async def test_supported_capabilities(self, adapter):
        caps = await adapter.get_capabilities()
        assert PlatformCapability.POST_TEXT in caps
        assert PlatformCapability.POST_IMAGE in caps
        assert PlatformCapability.POST_VIDEO in caps
        assert PlatformCapability.SCHEDULE_POST in caps
        assert PlatformCapability.GET_INSIGHTS in caps
        assert PlatformCapability.REPLY_COMMENT in caps

    @pytest.mark.asyncio
    async def test_publish_text_status(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"id": "fb_post_1001"}
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            content = UniversalContent(
                content_type=ContentType.POST,
                text="Facebook status update from AISMM!",
            )

            result = await adapter.publish_post(content)
            assert result.platform_post_id == "fb_post_1001"
            assert result.status == "published"
            assert "https://facebook.com/fb_post_1001" in result.url

    @pytest.mark.asyncio
    async def test_publish_photo(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"id": "fb_photo_2002", "post_id": "fb_post_2002"}
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            content = UniversalContent(
                content_type=ContentType.POST,
                text="Photo caption",
                media=[UniversalMedia(type=MediaType.IMAGE, url="https://example.com/pic.jpg")],
            )

            result = await adapter.publish_post(content)
            assert result.platform_post_id == "fb_post_2002"
            assert result.status == "published"

    @pytest.mark.asyncio
    async def test_get_post_analytics(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "data": [
                    {"name": "post_impressions", "values": [{"value": 5400}]},
                    {"name": "post_impressions_unique", "values": [{"value": 4200}]},
                    {"name": "post_reactions_like_total", "values": [{"value": 310}]},
                ]
            }
            mock_client.return_value.get = AsyncMock(return_value=mock_resp)

            analytics = await adapter.get_post_analytics("fb_post_1001")
            assert analytics.post_id == "fb_post_1001"
            assert analytics.impressions == 5400
            assert analytics.reach == 4200
            assert analytics.likes == 310


class TestFacebookAuth:
    """Test Facebook OAuth and token exchange."""

    @pytest.fixture
    def auth(self):
        return FacebookAuth(
            FacebookAuthConfig(
                client_id="fb_app_id",
                client_secret="fb_app_secret",
                redirect_uri="http://localhost:8000/callback",
            )
        )

    def test_authorization_url(self, auth):
        url, state = auth.get_authorization_url()
        assert "facebook.com" in url
        assert "client_id=fb_app_id" in url
        assert auth.validate_state(state) is True
        assert auth.validate_state("non_existent_state") is False

    @pytest.mark.asyncio
    async def test_get_page_access_token(self, auth):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "data": [{
                    "id": "page_999",
                    "name": "My Business Page",
                    "access_token": "page_token_abc",
                    "category": "Company",
                }]
            }
            mock_get.return_value = mock_resp

            page_info = await auth.get_page_access_token("user_token_xyz")
            assert page_info["page_id"] == "page_999"
            assert page_info["page_access_token"] == "page_token_abc"


class TestFacebookWebhook:
    """Test Facebook webhook signature and event ingestion."""

    @pytest.fixture
    def handler(self):
        return FacebookWebhookHandler(app_secret="fb_app_secret", verify_token="fb_token_123")

    def test_verify_challenge(self, handler):
        assert handler.verify_challenge("subscribe", "ch_123", "fb_token_123") == "ch_123"
        assert handler.verify_challenge("subscribe", "ch_123", "wrong_token") is None

    def test_verify_signature(self, handler):
        body = b'{"object": "page"}'
        sig = "sha256=" + hmac.new(b"fb_app_secret", body, hashlib.sha256).hexdigest()
        assert handler.verify_signature(body, sig) is True
        assert handler.verify_signature(body, "sha256=invalid") is False

    def test_parse_comment_event(self, handler):
        payload = {
            "entry": [{
                "id": "page_999",
                "time": 1725148800,
                "changes": [{
                    "field": "feed",
                    "value": {
                        "item": "comment",
                        "verb": "add",
                        "comment_id": "c_555",
                        "post_id": "p_111",
                        "message": "Great announcement!",
                        "sender_name": "Fan One",
                    }
                }]
            }]
        }
        events = handler.parse_event(payload)
        assert len(events) == 1
        assert events[0].event_type == FacebookWebhookEventType.FEED_COMMENT.value
        assert events[0].data["comment_id"] == "c_555"
        assert events[0].data["message"] == "Great announcement!"
