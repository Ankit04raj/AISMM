"""Tests for X (Twitter) Platform Adapter (Phase 14 Multi-Platform Expansion)."""

import pytest
import hmac
import hashlib
import base64
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.app.core.platform_adapters.x.adapter import XAdapter
from backend.app.core.platform_adapters.x.auth import XAuth, XAuthConfig
from backend.app.core.platform_adapters.x.config import XConfig, XAuthConfig as CfgAuth
from backend.app.core.platform_adapters.x.webhook import XWebhookHandler, XWebhookEventType
from backend.app.core.platform_adapters.capabilities import PlatformCapability
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType


class TestXAdapter:
    """Test XAdapter contract, capabilities, and lifecycle."""

    @pytest.fixture
    def adapter(self):
        return XAdapter({
            "client_id": "test_x_client_id",
            "client_secret": "test_x_client_secret",
            "redirect_uri": "http://localhost:8000/callback",
            "access_token": "test_x_bearer_token",
            "account_user_id": "987654321",
            "account_username": "AISMM_Official",
        })

    def test_adapter_initialization(self, adapter):
        assert adapter.PLATFORM_NAME == "x"
        assert adapter.platform_name == "x"
        assert adapter.account_user_id == "987654321"

    @pytest.mark.asyncio
    async def test_supported_capabilities(self, adapter):
        caps = await adapter.get_capabilities()
        assert PlatformCapability.POST_TEXT in caps
        assert PlatformCapability.POST_IMAGE in caps
        assert PlatformCapability.POST_VIDEO in caps
        assert PlatformCapability.DELETE_POST in caps
        assert PlatformCapability.GET_POST in caps
        assert PlatformCapability.GET_INSIGHTS in caps
        assert PlatformCapability.REPLY_COMMENT in caps

    @pytest.mark.asyncio
    async def test_publish_text_tweet(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "data": {
                    "id": "tweet_1001",
                    "text": "Hello world from AISMM X Adapter! #ai",
                }
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            content = UniversalContent(
                content_type=ContentType.POST,
                text="Hello world from AISMM X Adapter!",
                hashtags=["ai"],
            )

            result = await adapter.publish_post(content)
            assert result.platform_post_id == "tweet_1001"
            assert result.status == "published"
            assert "https://x.com/AISMM_Official/status/tweet_1001" in result.url

    @pytest.mark.asyncio
    async def test_publish_media_tweet(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "data": {
                    "id": "tweet_1002",
                    "text": "Check out this visual!",
                }
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            content = UniversalContent(
                content_type=ContentType.POST,
                text="Check out this visual!",
                media=[UniversalMedia(type=MediaType.IMAGE, url="https://example.com/chart.png")],
            )

            result = await adapter.publish_post(content)
            assert result.platform_post_id == "tweet_1002"
            assert result.status == "published"

    @pytest.mark.asyncio
    async def test_get_tweet_analytics(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "data": {
                    "id": "tweet_1001",
                    "public_metrics": {
                        "impression_count": 8500,
                        "like_count": 420,
                        "retweet_count": 95,
                        "reply_count": 32,
                        "quote_count": 14,
                        "bookmark_count": 55,
                    },
                    "organic_metrics": {
                        "url_link_clicks": 180,
                        "user_profile_clicks": 65,
                    }
                }
            }
            mock_client.return_value.get = AsyncMock(return_value=mock_resp)

            analytics = await adapter.get_post_analytics("tweet_1001")
            assert analytics.post_id == "tweet_1001"
            assert analytics.impressions == 8500
            assert analytics.likes == 420
            assert analytics.shares == 109  # 95 retweets + 14 quotes
            assert analytics.comments == 32
            assert analytics.clicks == 180

    @pytest.mark.asyncio
    async def test_reply_to_tweet(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 201
            mock_resp.json.return_value = {
                "data": {
                    "id": "reply_999",
                    "text": "Thanks for the feedback!",
                }
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            comment = await adapter.reply_to_comment("tweet_1001", "Thanks for the feedback!")
            assert comment.id == "reply_999"
            assert comment.post_id == "tweet_1001"
            assert comment.text == "Thanks for the feedback!"


class TestXAuth:
    """Test X OAuth 2.0 PKCE authentication flow."""

    @pytest.fixture
    def auth(self):
        return XAuth(
            XAuthConfig(
                client_id="test_client_id",
                client_secret="test_client_secret",
                redirect_uri="http://localhost:8000/callback",
            )
        )

    def test_authorization_url_pkce(self, auth):
        url, state = auth.get_authorization_url()
        assert "twitter.com/i/oauth2/authorize" in url
        assert "code_challenge=" in url
        assert "code_challenge_method=S256" in url
        assert auth.validate_state(state) is True
        assert auth.get_verifier(state) is not None

    @pytest.mark.asyncio
    async def test_exchange_code(self, auth):
        url, state = auth.get_authorization_url()
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "access_token": "mock_x_access_token",
                "refresh_token": "mock_x_refresh_token",
                "expires_in": 7200,
                "token_type": "Bearer",
                "scope": "tweet.read tweet.write users.read",
            }
            mock_post.return_value = mock_resp

            tokens = await auth.exchange_code("auth_code_123", state=state)
            assert tokens["access_token"] == "mock_x_access_token"
            assert tokens["refresh_token"] == "mock_x_refresh_token"


class TestXWebhook:
    """Test X CRC challenge verification and event parsing."""

    @pytest.fixture
    def handler(self):
        return XWebhookHandler(consumer_secret="twitter_secret_key_123")

    def test_generate_crc_response(self, handler):
        resp = handler.generate_crc_response("crc_token_abc")
        assert "response_token" in resp
        assert resp["response_token"].startswith("sha256=")

    def test_parse_tweet_create_event(self, handler):
        payload = {
            "for_user_id": "12345",
            "tweet_create_events": [{
                "id_str": "tweet_888",
                "id": 888,
                "text": "Great insights on AI!",
                "user": {
                    "id_str": "user_777",
                    "screen_name": "tech_lead",
                },
                "in_reply_to_status_id_str": "tweet_1001",
            }]
        }
        events = handler.parse_event(payload)
        assert len(events) == 1
        assert events[0].event_type == XWebhookEventType.TWEET_CREATE.value
        assert events[0].data["tweet_id"] == "tweet_888"
        assert events[0].data["author_screen_name"] == "tech_lead"
