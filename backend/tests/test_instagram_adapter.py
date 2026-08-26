"""Tests for Instagram Platform Adapter."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from backend.app.core.platform_adapters.instagram.adapter import InstagramAdapter
from backend.app.core.platform_adapters.instagram.auth import InstagramAuth, InstagramAuthConfig
from backend.app.core.platform_adapters.instagram.config import (
    InstagramConfig,
    InstagramAuthConfig as ConfigAuthConfig,
    InstagramRateLimitConfig,
)
from backend.app.core.platform_adapters.capabilities import PlatformCapability as Cap
from backend.app.core.platform_adapters.errors import (
    AuthenticationError,
    ValidationError,
    MediaUploadError,
    PublishingError,
)


class TestInstagramAdapter:
    """Test InstagramAdapter core functionality."""

    @pytest.fixture
    def config(self):
        return {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "http://localhost:8000/callback",
            "access_token": "test_access_token",
            "ig_user_id": "123456789",
        }

    @pytest.fixture
    def adapter(self, config):
        return InstagramAdapter(config)

    @pytest.mark.asyncio
    async def test_adapter_initialization(self, adapter):
        assert adapter.PLATFORM_NAME == "instagram"
        assert adapter.BASE_URL == "https://graph.facebook.com/v19.0"
        assert adapter.client_id == "test_client_id"
        assert adapter.client_secret == "test_client_secret"

    @pytest.mark.asyncio
    async def test_supported_capabilities(self, adapter):
        caps = await adapter.get_capabilities()
        expected = {
            Cap.POST_IMAGE,
            Cap.POST_CAROUSEL,
            Cap.POST_REEL,
            Cap.POST_STORY,
            Cap.SCHEDULE_POST,
            Cap.FETCH_INSIGHTS,
            Cap.WEBHOOK_SUBSCRIBE,
            Cap.MANAGE_COMMENTS,
            Cap.GET_PROFILE,
        }
        assert caps == expected

    @pytest.mark.asyncio
    async def test_health_check(self, adapter):
        with patch.object(adapter, 'validate_token', return_value=True):
            health = await adapter.health_check()
            assert health["platform"] == "instagram"
            assert health["status"] == "healthy"
            assert health["token_valid"] is True
            assert health["ig_user_id"] == "123456789"

    @pytest.mark.asyncio
    async def test_determine_media_type(self, adapter):
        from backend.app.core.normalization import UniversalContent, UniversalMedia

        # Image
        content = UniversalContent(
            text="Test",
            media=[UniversalMedia(type="image", url="http://example.com/img.jpg")]
        )
        assert adapter._determine_media_type(content) == "IMAGE"

        # Carousel
        content = UniversalContent(
            text="Test",
            media=[
                UniversalMedia(type="image", url="http://example.com/img1.jpg"),
                UniversalMedia(type="image", url="http://example.com/img2.jpg"),
            ]
        )
        assert adapter._determine_media_type(content) == "CAROUSEL"

        # Reel (video)
        content = UniversalContent(
            text="Test",
            media=[UniversalMedia(type="video", url="http://example.com/video.mp4")],
            content_type="reel"
        )
        assert adapter._determine_media_type(content) == "REELS"

        # Story
        content = UniversalContent(
            text="Test",
            media=[UniversalMedia(type="image", url="http://example.com/img.jpg")],
            content_type="story"
        )
        assert adapter._determine_media_type(content) == "STORIES"


class TestInstagramAuth:
    """Test Instagram OAuth authentication flow."""

    @pytest.fixture
    def auth_config(self):
        return InstagramAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback",
        )

    @pytest.fixture
    def auth(self, auth_config):
        return InstagramAuth(auth_config)

    def test_get_authorization_url(self, auth):
        url, state = auth.get_authorization_url()
        assert "api.instagram.com/oauth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback" in url
        assert state in auth._state_store

    def test_validate_state(self, auth):
        url, state = auth.get_authorization_url()
        assert auth.validate_state(state) is True
        assert auth.validate_state("invalid_state") is False

    def test_consume_state(self, auth):
        url, state = auth.get_authorization_url()
        verifier = auth.consume_state(state)
        assert verifier is not None
        assert state not in auth._state_store

    def test_token_expiry_calculation(self, auth):
        expiry = auth.get_token_expiry(3600)
        assert isinstance(expiry, datetime)
        assert expiry > datetime.utcnow()


class TestInstagramConfig:
    """Test Instagram configuration validation."""

    def test_valid_config(self):
        config = InstagramConfig(
            auth=ConfigAuthConfig(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="http://localhost/callback",
            )
        )
        assert config.auth.client_id == "test_id"
        assert config.rate_limits.calls_per_hour == 200

    def test_invalid_auth_config(self):
        with pytest.raises(ValueError, match="client_id and client_secret are required"):
            InstagramConfig(
                auth=ConfigAuthConfig(
                    client_id="",
                    client_secret="test_secret",
                    redirect_uri="http://localhost/callback",
                )
            )

    def test_webhook_validation(self):
        # Should fail without required fields when webhooks enabled
        with pytest.raises(ValueError, match="Webhook config requires"):
            InstagramConfig(
                auth=ConfigAuthConfig(
                    client_id="test_id",
                    client_secret="test_secret",
                    redirect_uri="http://localhost/callback",
                ),
                enable_webhooks=True,
                webhook=None,
            )

    def test_presets(self):
        dev = InstagramConfig.presets.development()
        assert dev.rate_limits.calls_per_hour == 50

        prod = InstagramConfig.presets.production()
        assert prod.rate_limits.calls_per_hour == 200

    def test_to_adapter_config(self):
        config = InstagramConfig(
            auth=ConfigAuthConfig(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="http://localhost/callback",
            )
        )
        adapter_config = config.to_adapter_config()
        assert adapter_config["client_id"] == "test_id"
        assert adapter_config["rate_limit_calls"] == 200


class TestInstagramPublisher:
    """Test Instagram publishing logic."""

    @pytest.fixture
    def mock_adapter(self):
        adapter = MagicMock(spec=InstagramAdapter)
        adapter.ig_user_id = "123456789"
        adapter._http_client = AsyncMock()
        return adapter

    @pytest.fixture
    def publisher(self, mock_adapter):
        from backend.app.core.platform_adapters.instagram.publisher import InstagramPublisher
        return InstagramPublisher(mock_adapter)

    @pytest.mark.asyncio
    async def test_publish_image_validation(self, publisher):
        from backend.app.core.normalization import UniversalContent, UniversalMedia

        content = UniversalContent(text="Test")
        media = UniversalMedia(type="image", url="http://example.com/img.jpg")

        # Should fail without media URL
        media_no_url = UniversalMedia(type="image", url="")
        with pytest.raises(ValidationError, match="Media URL required"):
            await publisher.publish_image(content, media_no_url)


class TestInstagramInsights:
    """Test Instagram insights fetching."""

    @pytest.fixture
    def mock_adapter(self):
        adapter = MagicMock(spec=InstagramAdapter)
        adapter.ig_user_id = "123456789"
        adapter._http_client = AsyncMock()
        return adapter

    @pytest.fixture
    def insights(self, mock_adapter):
        from backend.app.core.platform_adapters.instagram.insights import InstagramInsights
        return InstagramInsights(mock_adapter)

    @pytest.mark.asyncio
    async def test_get_media_metrics_mapping(self):
        from backend.app.core.platform_adapters.instagram.endpoints import get_media_metrics

        image_metrics = get_media_metrics("IMAGE")
        assert "impressions" in image_metrics
        assert "reach" in image_metrics

        reel_metrics = get_media_metrics("REELS")
        assert "plays" in reel_metrics
        assert "total_interactions" in reel_metrics

        story_metrics = get_media_metrics("STORIES")
        assert "exits" in story_metrics
        assert "replies" in story_metrics


class TestInstagramWebhook:
    """Test Instagram webhook handling."""

    @pytest.fixture
    def handler(self):
        from backend.app.core.platform_adapters.instagram.webhook import InstagramWebhookHandler
        return InstagramWebhookHandler(
            app_secret="test_app_secret",
            verify_token="test_verify_token",
            callback_url="http://localhost/webhook"
        )

    def test_verify_challenge(self, handler):
        challenge = "test_challenge_123"
        result = handler.verify_challenge("subscribe", challenge, "test_verify_token")
        assert result == challenge

        # Wrong token
        result = handler.verify_challenge("subscribe", challenge, "wrong_token")
        assert result is None

    def test_verify_signature(self, handler):
        payload = b'{"test": "data"}'
        signature = "sha256=" + hmac.new(
            b"test_app_secret",
            payload,
            hashlib.sha256
        ).hexdigest()

        import hmac
        import hashlib
        assert handler.verify_signature(payload, signature) is True

        # Invalid signature
        assert handler.verify_signature(payload, "sha256=invalid") is False

    def test_parse_comment_event(self, handler):
        from backend.app.core.platform_adapters.instagram.webhook import (
            InstagramWebhookEventType,
            InstagramWebhookField,
        )

        payload = {
            "object": "instagram",
            "entry": [{
                "id": "123456789",
                "time": int(datetime.utcnow().timestamp()),
                "changes": [{
                    "field": "comments",
                    "value": {
                        "verb": "created",
                        "comment_id": "comment_123",
                        "media_id": "media_456",
                        "text": "Great post!",
                        "from": {"username": "user1", "id": "user_123"}
                    }
                }]
            }]
        }

        events = handler.parse_event(payload)
        assert len(events) == 1
        assert events[0].event_type == InstagramWebhookEventType.COMMENT_CREATED.value
        assert events[0].data["comment_id"] == "comment_123"
        assert events[0].data["text"] == "Great post!"


class TestInstagramEndpoints:
    """Test Instagram endpoint constants."""

    def test_endpoint_constants(self):
        from backend.app.core.platform_adapters.instagram.endpoints import InstagramEndpoint

        assert InstagramEndpoint.MEDIA_CONTAINER == "/{ig_user_id}/media"
        assert InstagramEndpoint.MEDIA_PUBLISH == "/{ig_user_id}/media_publish"

    def test_media_type_enum(self):
        from backend.app.core.platform_adapters.instagram.endpoints import InstagramMediaType

        assert InstagramMediaType.IMAGE == "IMAGE"
        assert InstagramMediaType.REELS == "REELS"
        assert InstagramMediaType.CAROUSEL == "CAROUSEL"

    def test_insight_metrics(self):
        from backend.app.core.platform_adapters.instagram.endpoints import InstagramInsightMetric

        assert InstagramInsightMetric.IMPRESSIONS == "impressions"
        assert InstagramInsightMetric.VIDEO_VIEWS == "video_views"


class TestInstagramMediaUploader:
    """Test media upload functionality."""

    @pytest.fixture
    def uploader(self):
        from backend.app.core.platform_adapters.instagram.media import InstagramMediaUploader
        return InstagramMediaUploader(
            access_token="test_token",
            ig_user_id="123456789",
        )

    def test_chunk_size_constant(self):
        from backend.app.core.platform_adapters.instagram.media import InstagramMediaUploader

        assert InstagramMediaUploader.CHUNK_SIZE == 4 * 1024 * 1024  # 4MB
        assert InstagramMediaUploader.MAX_SINGLE_UPLOAD == 100 * 1024 * 1024  # 100MB


# Integration-style tests (mocked HTTP)
class TestInstagramAdapterIntegration:
    """Integration tests with mocked HTTP responses."""

    @pytest.fixture
    def adapter(self):
        config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "http://localhost/callback",
            "access_token": "test_token",
            "ig_user_id": "123456789",
        }
        return InstagramAdapter(config)

    @pytest.mark.asyncio
    async def test_authenticate_flow(self, adapter):
        with patch.object(adapter, '_get_client') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "short_token",
                "expires_in": 3600,
            }
            mock_client.return_value.post.return_value = mock_response

            # Mock long-lived token exchange
            mock_response_long = AsyncMock()
            mock_response_long.status_code = 200
            mock_response_long.json.return_value = {
                "access_token": "long_token",
                "expires_in": 5184000,
            }
            mock_client.return_value.get.return_value = mock_response_long

            # Mock get IG user ID
            mock_response_accounts = AsyncMock()
            mock_response_accounts.status_code = 200
            mock_response_accounts.json.return_value = {
                "data": [{
                    "instagram_business_account": {"id": "987654321"}
                }]
            }
            mock_client.return_value.get.return_value = mock_response_accounts

            result = await adapter.authenticate({"code": "auth_code_123"})

            assert result["access_token"] == "long_token"
            assert adapter.ig_user_id == "987654321"

    @pytest.mark.asyncio
    async def test_publish_post_flow(self, adapter):
        from backend.app.core.normalization import UniversalContent, UniversalMedia

        with patch.object(adapter, '_get_client') as mock_client:
            # Mock media upload
            mock_upload = AsyncMock()
            mock_upload.status_code = 200
            mock_upload.json.return_value = {"id": "media_container_123"}
            mock_client.return_value.post.return_value = mock_upload

            # Mock publish
            mock_publish = AsyncMock()
            mock_publish.status_code = 200
            mock_publish.json.return_value = {
                "id": "post_456",
                "permalink": "https://instagram.com/p/abc123"
            }

            # Need to mock the second call
            call_count = [0]
            async def mock_post(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return mock_upload
                return mock_publish

            mock_client.return_value.post.side_effect = mock_post

            content = UniversalContent(
                text="Test post",
                media=[UniversalMedia(type="image", url="http://example.com/img.jpg")]
            )

            result = await adapter.publish_post(content)

            assert result["platform"] == "instagram"
            assert result["post_id"] == "post_456"
            assert result["container_id"] == "media_container_123"
            assert result["media_type"] == "IMAGE"

    @pytest.mark.asyncio
    async def test_fetch_insights(self, adapter):
        with patch.object(adapter, '_get_client') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"name": "impressions", "values": [{"value": 1000}]},
                    {"name": "reach", "values": [{"value": 800}]},
                    {"name": "likes", "values": [{"value": 150}]},
                ]
            }
            mock_client.return_value.get.return_value = mock_response

            result = await adapter.fetch_insights("post_123")

            assert "normalized" in result
            assert result["normalized"]["impressions"] == 1000
            assert result["normalized"]["reach"] == 800


# Pytest configuration
pytest_plugins = ["pytest_asyncio"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])