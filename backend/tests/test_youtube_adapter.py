"""Tests for YouTube Platform Adapter (Phase 14 Multi-Platform Expansion)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.app.core.platform_adapters.youtube.adapter import YouTubeAdapter
from backend.app.core.platform_adapters.youtube.auth import YouTubeAuth, YouTubeAuthConfig
from backend.app.core.platform_adapters.youtube.config import YouTubeConfig, YouTubeAuthConfig as CfgAuth
from backend.app.core.platform_adapters.youtube.webhook import YouTubeWebhookHandler, YouTubeWebhookEventType
from backend.app.core.platform_adapters.capabilities import PlatformCapability
from backend.app.core.normalization import UniversalContent, UniversalMedia, ContentType, MediaType


class TestYouTubeAdapter:
    """Test YouTubeAdapter contract, video operations, and lifecycle."""

    @pytest.fixture
    def adapter(self):
        return YouTubeAdapter({
            "client_id": "test_yt_client_id",
            "client_secret": "test_yt_client_secret",
            "redirect_uri": "http://localhost:8000/callback",
            "access_token": "test_yt_access_token",
            "channel_id": "UC_1234567890",
        })

    def test_adapter_initialization(self, adapter):
        assert adapter.PLATFORM_NAME == "youtube"
        assert adapter.platform_name == "youtube"
        assert adapter.channel_id == "UC_1234567890"

    @pytest.mark.asyncio
    async def test_supported_capabilities(self, adapter):
        caps = await adapter.get_capabilities()
        assert PlatformCapability.POST_VIDEO in caps
        assert PlatformCapability.DELETE_POST in caps
        assert PlatformCapability.GET_POST in caps
        assert PlatformCapability.GET_INSIGHTS in caps
        assert PlatformCapability.REPLY_COMMENT in caps
        assert PlatformCapability.DELETE_COMMENT in caps

    @pytest.mark.asyncio
    async def test_publish_video(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "id": "yt_vid_999",
                "snippet": {
                    "title": "AISMM AI Engine Tutorial",
                }
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            content = UniversalContent(
                content_type=ContentType.VIDEO,
                text="In this video we demonstrate autonomous social media optimization.",
                caption="In this video we demonstrate autonomous social media optimization.",
                hashtags=["AISMM", "AI"],
                media=[UniversalMedia(type=MediaType.VIDEO, url="https://example.com/video.mp4")],
            )

            result = await adapter.publish_post(content)
            assert result.platform_post_id == "yt_vid_999"
            assert result.status == "published"
            assert "https://www.youtube.com/watch?v=fyt_vid_999" in result.url

    @pytest.mark.asyncio
    async def test_get_video_analytics(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "items": [{
                    "id": "yt_vid_999",
                    "statistics": {
                        "viewCount": "45200",
                        "likeCount": "2850",
                        "commentCount": "194",
                    }
                }]
            }
            mock_client.return_value.get = AsyncMock(return_value=mock_resp)

            analytics = await adapter.get_post_analytics("yt_vid_999")
            assert analytics.post_id == "yt_vid_999"
            assert analytics.impressions == 45200
            assert analytics.reach == 45200
            assert analytics.likes == 2850
            assert analytics.comments == 194
            assert analytics.video_views == 45200

    @pytest.mark.asyncio
    async def test_reply_to_comment(self, adapter):
        with patch.object(adapter, "_get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "id": "yt_comment_reply_888",
            }
            mock_client.return_value.post = AsyncMock(return_value=mock_resp)

            comment = await adapter.reply_to_comment("yt_thread_123", "Thanks for watching!")
            assert comment.id == "yt_comment_reply_888"
            assert comment.post_id == "yt_thread_123"
            assert comment.text == "Thanks for watching!"


class TestYouTubeAuth:
    """Test Google / YouTube OAuth 2.0 flow."""

    @pytest.fixture
    def auth(self):
        return YouTubeAuth(
            YouTubeAuthConfig(
                client_id="test_yt_id",
                client_secret="test_yt_secret",
                redirect_uri="http://localhost:8000/callback",
            )
        )

    def test_authorization_url(self, auth):
        url, state = auth.get_authorization_url()
        assert "accounts.google.com/o/oauth2/v2/auth" in url
        assert "client_id=test_yt_id" in url
        assert auth.validate_state(state) is True
        assert auth.validate_state("invalid_state") is False

    @pytest.mark.asyncio
    async def test_exchange_code(self, auth):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "access_token": "mock_yt_access_token",
                "refresh_token": "mock_yt_refresh_token",
                "expires_in": 3600,
                "token_type": "Bearer",
            }
            mock_post.return_value = mock_resp

            tokens = await auth.exchange_code("auth_code_yt")
            assert tokens["access_token"] == "mock_yt_access_token"
            assert tokens["refresh_token"] == "mock_yt_refresh_token"


class TestYouTubeWebhook:
    """Test YouTube WebSub challenge verification and Atom feed parsing."""

    @pytest.fixture
    def handler(self):
        return YouTubeWebhookHandler()

    def test_verify_challenge(self, handler):
        res = handler.verify_challenge("subscribe", "challenge_code_123", "https://youtube.com/feed")
        assert res == "challenge_code_123"

    def test_parse_atom_feed(self, handler):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns:atom="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
            <entry>
                <id>yt:video:dQw4w9WgXcQ</id>
                <yt:videoId>dQw4w9WgXcQ</yt:videoId>
                <yt:channelId>UCuAXFkgsw1L7xaCfnd5JJOw</yt:channelId>
                <title>AI Revolution in 2026</title>
                <published>2026-09-02T12:00:00+00:00</published>
            </entry>
        </feed>"""
        events = handler.parse_atom_feed(xml)
        assert len(events) == 1
        assert events[0].video_id == "dQw4w9WgXcQ"
        assert events[0].title == "AI Revolution in 2026"
