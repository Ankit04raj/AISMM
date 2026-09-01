"""Tests for Phase 6 Content Management & Multi-Platform Publishing."""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.normalization import ContentType, MediaType
from backend.app.core.schemas.post import (
    MultiPlatformPostRequest,
    PlatformCustomization,
    ContentPreviewRequest,
    ContentValidationRequest,
    MediaItem,
)
from backend.app.services.preview_service import PreviewService
from backend.app.services.post_service import PostService
from backend.app.db.models import Post, PostPublication, PostStatusEnum, ContentTypeEnum

client = TestClient(app)


class TestPreviewService:
    """Test platform-specific preview generation."""

    def test_multi_platform_preview_rendering(self):
        req = ContentPreviewRequest(
            platforms=["instagram", "facebook", "twitter", "linkedin"],
            content_type="post",
            text="Universal announcement #ai @partner",
            caption="Universal announcement",
            hashtags=["ai", "future"],
            mentions=["partner"],
            media=[MediaItem(type="image", url="https://example.com/pic.jpg")],
            customizations={
                "twitter": PlatformCustomization(text="Short tweet variant #ai"),
                "linkedin": PlatformCustomization(caption="Professional LinkedIn article commentary"),
            },
        )

        resp = PreviewService.generate_previews(req)

        # Instagram preview check
        assert "instagram" in resp.previews
        ig = resp.previews["instagram"]
        assert ig["layout"] == "instagram_card"
        assert ig["media_type"] == "IMAGE"
        assert "#ai" in ig["caption"]
        assert "@partner" in ig["caption"]

        # Facebook preview check
        assert "facebook" in resp.previews
        fb = resp.previews["facebook"]
        assert fb["layout"] == "facebook_feed_card"
        assert "Universal announcement" in fb["message"]

        # Twitter preview check
        assert "twitter" in resp.previews
        tw = resp.previews["twitter"]
        assert tw["layout"] == "tweet_card"
        assert "Short tweet variant #ai" in tw["text"]
        assert tw["char_remaining"] > 0

        # LinkedIn preview check
        assert "linkedin" in resp.previews
        li = resp.previews["linkedin"]
        assert li["layout"] == "linkedin_share_box"
        assert "Professional LinkedIn" in li["commentary"]


class TestContentValidation:
    """Test validation of content against platform constraints."""

    def test_validation_detects_warnings_and_errors(self):
        # Twitter character limit overflow + carousel item count error
        resp = client.post(
            "/api/v1/content/validate",
            json={
                "platforms": ["twitter", "instagram"],
                "content_type": "carousel",
                "text": "A" * 350,  # exceeds Twitter 280 limit
                "media": [{"type": "image", "url": "https://example.com/1.jpg"}],  # carousel with only 1 item -> error
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert len(data["platform_warnings"]["twitter"]) > 0
        assert "Text exceeds twitter limit" in data["platform_warnings"]["twitter"][0]
        assert "Carousel format requires at least 2 media items" in data["platform_errors"]["instagram"][0]


class TestMultiPlatformPublishing:
    """Test multi-platform post composer and publishing service."""

    @pytest.mark.asyncio
    async def test_publish_to_instagram_and_facebook_simultaneously(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        service = PostService(mock_db)

        user_id = uuid4()
        req = MultiPlatformPostRequest(
            platforms=["instagram", "facebook"],
            content_type="post",
            text="Launch post across networks #launch",
            media=[MediaItem(type="image", url="https://example.com/photo.jpg")],
            customizations={
                "facebook": PlatformCustomization(text="Facebook specific message!"),
            },
            publish_now=True,
        )

        ig_adapter = PlatformRegistry.get_adapter("instagram")
        fb_adapter = PlatformRegistry.get_adapter("facebook")

        with patch.object(ig_adapter, "publish_post", new_callable=AsyncMock) as mock_ig_pub, \
             patch.object(fb_adapter, "publish_post", new_callable=AsyncMock) as mock_fb_pub:

            mock_ig_res = MagicMock()
            mock_ig_res.platform_post_id = "ig_111"
            mock_ig_res.url = "https://instagram.com/p/111"
            mock_ig_res.status = "published"
            mock_ig_res.published_at = datetime.now(timezone.utc)
            mock_ig_res.platform_data = {"container_id": "c_111", "media_type": "IMAGE"}
            mock_ig_pub.return_value = mock_ig_res

            mock_fb_res = MagicMock()
            mock_fb_res.platform_post_id = "fb_222"
            mock_fb_res.url = "https://facebook.com/222"
            mock_fb_res.status = "published"
            mock_fb_res.published_at = datetime.now(timezone.utc)
            mock_fb_res.platform_data = {"media_type": "IMAGE"}
            mock_fb_pub.return_value = mock_fb_res

            resp = await service.create_multi_platform_post(user_id, req)

            assert resp.overall_status == "published"
            assert "instagram" in resp.results
            assert "facebook" in resp.results
            assert resp.results["instagram"].id == "ig_111"
            assert resp.results["facebook"].id == "fb_222"
            assert mock_ig_pub.called
            assert mock_fb_pub.called
            assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_retry_failed_platform_publication(self):
        mock_db = AsyncMock()
        service = PostService(mock_db)

        user_id = uuid4()
        post_id = uuid4()

        # Mock existing post with 1 published IG and 1 failed FB publication
        existing_post = MagicMock(spec=Post)
        existing_post.id = post_id
        existing_post.user_id = user_id
        existing_post.content_type = ContentTypeEnum.POST
        existing_post.text = "Retry post text"
        existing_post.caption = "Retry post text"
        existing_post.hashtags = []
        existing_post.mentions = []
        existing_post.media = []

        ig_pub = MagicMock(spec=PostPublication)
        ig_pub.platform = "instagram"
        ig_pub.status = "published"

        fb_pub = MagicMock(spec=PostPublication)
        fb_pub.platform = "facebook"
        fb_pub.status = "failed"
        fb_pub.error_message = "Network timeout"

        existing_post.publications = [ig_pub, fb_pub]

        with patch.object(service, "get_post", new_callable=AsyncMock, return_value=existing_post):
            fb_adapter = PlatformRegistry.get_adapter("facebook")
            with patch.object(fb_adapter, "publish_post", new_callable=AsyncMock) as mock_fb_retry:
                mock_fb_res = MagicMock()
                mock_fb_res.platform_post_id = "fb_recovered_333"
                mock_fb_res.url = "https://facebook.com/333"
                mock_fb_res.status = "published"
                mock_fb_res.published_at = datetime.now(timezone.utc)
                mock_fb_res.platform_data = {}
                mock_fb_retry.return_value = mock_fb_res

                retry_resp = await service.retry_publication(post_id, user_id, "facebook")

                assert retry_resp.id == "fb_recovered_333"
                assert retry_resp.status == "published"
                assert fb_pub.status == "published"
                assert fb_pub.error_message is None
                assert mock_db.commit.called
