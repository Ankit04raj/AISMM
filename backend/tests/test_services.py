"""Tests for service layer with adapter and normalization wiring."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from backend.app.core.platform_adapters import PlatformRegistry, BasePlatformAdapter, PlatformCapability
from backend.app.core.platform_adapters.base import PostContent, PostResult
from backend.app.core.normalization import ContentNormalizer, MetricNormalizer, UniversalContent, ContentType, MediaType
from backend.app.core.schemas.post import CreatePostRequest, MediaItem
from backend.app.services.post_service import PostService
from backend.app.services.user_service import UserService


class MockServiceAdapter(BasePlatformAdapter):
    """Mock adapter for testing service layer integration."""

    PLATFORM_NAME = "mock_service"
    SUPPORTED_CAPABILITIES = {
        PlatformCapability.POST_IMAGE,
        PlatformCapability.SCHEDULE_POST,
        PlatformCapability.DELETE_POST,
    }

    @property
    def platform_name(self) -> str:
        return self.PLATFORM_NAME

    async def authenticate(self, credentials):
        return True

    async def refresh_token(self):
        return True

    async def validate_connection(self):
        return True

    async def publish_post(self, content):
        return PostResult(
            platform_post_id="mock_post_123",
            url="https://example.com/mock_post_123",
            status="published",
            published_at=datetime.now(timezone.utc),
            platform_data={"container_id": "c_123", "media_type": "IMAGE"},
        )

    async def schedule_post(self, content, scheduled_at):
        return PostResult(
            platform_post_id="mock_container_123",
            url=None,
            status="scheduled",
            published_at=None,
            platform_data={"container_id": "mock_container_123", "media_type": "IMAGE"},
        )

    async def delete_post(self, post_id):
        return True

    async def get_post(self, post_id):
        return {"id": post_id}

    async def get_post_analytics(self, post_id):
        pass

    async def get_account_analytics(self, since, until):
        return {}

    async def get_comments(self, post_id, limit=50):
        return []

    async def reply_to_comment(self, comment_id, text):
        pass

    async def delete_comment(self, comment_id):
        return True

    async def hide_comment(self, comment_id):
        return True

    async def get_profile(self):
        return {}

    async def update_profile(self, data):
        return True

    async def upload_media(self, media):
        return "mock_media_id"


@pytest.fixture(autouse=True)
def register_mock_service():
    PlatformRegistry.register("mock_service", MockServiceAdapter)
    yield
    PlatformRegistry.clear()


def test_registry_registration_and_lookup():
    """Verify registry discovers and returns adapter instances."""
    assert PlatformRegistry.is_registered("mock_service")
    adapter = PlatformRegistry.get_adapter("mock_service")
    assert adapter is not None
    assert adapter.platform_name == "mock_service"
    assert "mock_service" in PlatformRegistry.list_platforms()


def test_content_normalizer_service_wiring():
    """Verify ContentNormalizer correctly prepares UniversalMedia from raw input."""
    raw_media = {
        "type": "image",
        "url": "https://example.com/test.jpg",
        "alt_text": "Sample image",
    }
    media = ContentNormalizer.normalize_media(raw_media)
    assert media.type == MediaType.IMAGE
    assert media.url == "https://example.com/test.jpg"
    assert media.alt_text == "Sample image"


@pytest.mark.asyncio
async def test_post_service_create_and_publish_flow():
    """Verify PostService normalizes content and calls adapter publish."""
    mock_db = AsyncMock()
    service = PostService(mock_db)

    user_id = uuid4()
    req = CreatePostRequest(
        platform="mock_service",
        content_type="post",
        text="Test content #aismm @user",
        media=[MediaItem(type="image", url="https://example.com/test.jpg")],
        publish_now=True,
    )

    resp = await service.create_post(user_id, req)

    assert resp.platform == "mock_service"
    assert resp.permalink == "https://example.com/mock_post_123"
    assert resp.status == "published"
    assert resp.id == "mock_post_123"
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_post_service_schedule_flow():
    """Verify PostService normalizes content and schedules through adapter."""
    mock_db = AsyncMock()
    service = PostService(mock_db)

    user_id = uuid4()
    sched_time = datetime(2027, 1, 1, 12, 0, 0)
    req = CreatePostRequest(
        platform="mock_service",
        content_type="post",
        text="Scheduled post",
        media=[],
        scheduled_at=sched_time,
        publish_now=False,
    )

    resp = await service.create_post(user_id, req)

    assert resp.platform == "mock_service"
    assert resp.status == "scheduled"
    assert resp.scheduled_at == sched_time
    assert mock_db.commit.called
