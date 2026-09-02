"""Tests for LinkedIn Platform Adapter (Phase 14 Multi-Platform Expansion)."""

import pytest
import hmac
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.app.core.platform_adapters.linkedin.adapter import LinkedInAdapter
from backend.app.core.platform_adapters.linkedin.auth import LinkedInAuth, LinkedInAuthConfig
from backend.app.core.platform_adapters.linkedin.config import LinkedInConfig, LinkedInAuthConfig as CfgAuth
from backend.app.core.platform_adapters.linkedin.webhook import LinkedInWebhookHandler, LinkedInWebhookEventType
from backend.app.core.platform_adapters.capabilities import PlatformCapability
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType


class TestLinkedInAdapter:
    """Test LinkedInAdapter contract, capabilities, and lifecycle."""

    @pytest.fixture
    def adapter(self):
        return LinkedInAdapter({
            "client_id": "test_li_client_id",
            "client_secret": "test_li_client_secret",
            "redirect_uri": "http://localhost:8000/callback",
            "access_token": "test_li_access_token",
            "organization_urn": "urn:li:organization:12345678",
            "author_urn": "urn:li:organization:12345678",
        })

    def test_adapter_initialization(self, adapter):
        assert adapter.PLATFORM_NAME == "linkedin"
        assert adapter.platform_name == "linkedin"
        assert adapter.organization_urn == "urn:li:organization:12345678"

    @pytest.mark.asyncio
    async def test_supported_capabilities(self, adapter):
        caps = await adapter.get_capabilities()
        assert PlatformCapability.POST_TEXT in caps
        assert PlatformCapability.POST_IMAGE in caps
        assert PlatformCapability.POST_VIDEO in caps
        assert PlatformCapability.GET_POST in caps
        assert PlatformCapability.GET_INSIGHTS in caps
        assert PlatformCapability.REPLY_COMMENT in caps

    @pytest.mark.asyncio
    async def test_publish_text_ugc_post(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "id": "urn:li:share:1001",
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            content = UniversalContent(
                content_type=ContentType.POST,
                text="Excited to announce our new corporate AI roadmap! #leadership",
                hashtags=["leadership"],
            )

            result = await adapter.publish_post(content)
            assert result.platform_post_id == "urn:li:share:1001"
            assert result.status == "published"
            assert "https://www.linkedin.com/feed/update/urn:li:share:1001" in result.url

    @pytest.mark.asyncio
    async def test_publish_media_ugc_post(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "id": "urn:li:ugcPost:2002",
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            content = UniversalContent(
                content_type=ContentType.POST,
                text="Visual presentation deck",
                media=[UniversalMedia(type=MediaType.IMAGE, url="https://example.com/slide.png", alt_text="Slide 1")],
            )

            result = await adapter.publish_post(content)
            assert result.platform_post_id == "urn:li:ugcPost:2002"
            assert result.status == "published"

    @pytest.mark.asyncio
    async def test_get_share_analytics(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "elements": [{
                    "totalShareStatistics": {
                        "impressionCount": 12400,
                        "uniqueImpressionsCount": 9800,
                        "clickCount": 650,
                        "likeCount": 380,
                        "commentCount": 42,
                        "shareCount": 58,
                        "engagement": 0.091,
                    }
                }]
            }
            mock_client.return_value.get = AsyncMock(return_value=mock_resp)

            analytics = await adapter.get_post_analytics("urn:li:share:1001")
            assert analytics.post_id == "urn:li:share:1001"
            assert analytics.impressions == 12400
            assert analytics.reach == 12400
            assert analytics.likes == 380
            assert analytics.comments == 42
            assert analytics.shares == 58
            assert analytics.clicks == 650

    @pytest.mark.asyncio
    async def test_reply_to_comment(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "id": "urn:li:comment:999",
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            comment = await adapter.reply_to_comment("urn:li:comment:555", "Thank you for the insightful question!")
            assert comment.id == "urn:li:comment:999"
            assert comment.post_id == "urn:li:comment:555"
            assert comment.text == "Thank you for the insightful question!"


class TestLinkedInAuth:
    """Test LinkedIn 3-legged OAuth 2.0 flow."""

    @pytest.fixture
    def auth(self):
        return LinkedInAuth(
            LinkedInAuthConfig(
                client_id="test_li_id",
                client_secret="test_li_secret",
                redirect_uri="http://localhost:8000/callback",
            )
        )

    def test_authorization_url(self, auth):
        url, state = auth.get_authorization_url()
        assert "linkedin.com/oauth/v2/authorization" in url
        assert "client_id=test_li_id" in url
        assert auth.validate_state(state) is True
        assert auth.validate_state("non_existent") is False

    @pytest.mark.asyncio
    async def test_exchange_code(self, auth):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "access_token": "mock_li_token",
                "expires_in": 5184000,
                "scope": "r_organization_social w_organization_social",
            }
            mock_post.return_value = mock_resp

            tokens = await auth.exchange_code("auth_code_li")
            assert tokens["access_token"] == "mock_li_token"
            assert tokens["expires_in"] == 5184000


class TestLinkedInWebhook:
    """Test LinkedIn signature verification and event parsing."""

    @pytest.fixture
    def handler(self):
        return LinkedInWebhookHandler(client_secret="linkedin_secret_xyz")

    def test_verify_signature(self, handler):
        body = b'{"eventType": "ORGANIZATION_SHARE"}'
        sig = hmac.new(b"linkedin_secret_xyz", body, hashlib.sha256).hexdigest()
        assert handler.verify_signature(body, sig) is True
        assert handler.verify_signature(body, "invalid_sig") is False

    def test_parse_event(self, handler):
        payload = {
            "events": [{
                "eventType": "COMMENT",
                "entityUrn": "urn:li:comment:123",
                "data": {"text": "Great update!"},
            }]
        }
        events = handler.parse_event(payload)
        assert len(events) == 1
        assert events[0].event_type == "COMMENT"
        assert events[0].object_urn == "urn:li:comment:123"
