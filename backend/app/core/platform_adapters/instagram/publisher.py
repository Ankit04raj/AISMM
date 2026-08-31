"""Instagram Post/Story/Reel Publisher."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

import httpx

from .adapter import InstagramAdapter
from .endpoints import InstagramMediaType, get_media_metrics
from ...errors import PublishingError, ValidationError
from ...normalization import UniversalContent, UniversalMedia


@dataclass
class PublishResult:
    """Result of a publish operation."""
    platform: str
    post_id: str
    container_id: str
    permalink: Optional[str]
    published_at: str
    media_type: str
    media_urls: List[str]


@dataclass
class ScheduledPublishResult:
    """Result of a scheduled publish."""
    platform: str
    container_id: str
    scheduled_at: str
    status: str  # "scheduled", "published", "failed"


class InstagramPublisher:
    """Handles publishing posts, stories, reels, and carousels to Instagram."""

    def __init__(self, adapter: InstagramAdapter):
        self.adapter = adapter
        self._client = adapter._http_client

    async def publish_image(
        self,
        content: UniversalContent,
        media: UniversalMedia,
        caption: Optional[str] = None,
        location_id: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
    ) -> PublishResult:
        """Publish a single image post."""
        return await self._publish_media(
            content=content,
            media_items=[media],
            media_type=InstagramMediaType.IMAGE,
            caption=caption,
            location_id=location_id,
            scheduled_at=scheduled_at,
        )

    async def publish_carousel(
        self,
        content: UniversalContent,
        media_items: List[UniversalMedia],
        caption: Optional[str] = None,
        location_id: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
    ) -> PublishResult:
        """Publish a carousel post (multiple images/videos)."""
        if len(media_items) < 2:
            raise ValidationError("Carousel requires at least 2 media items", platform="instagram")
        if len(media_items) > 10:
            raise ValidationError("Carousel cannot exceed 10 media items", platform="instagram")

        return await self._publish_media(
            content=content,
            media_items=media_items,
            media_type=InstagramMediaType.CAROUSEL,
            caption=caption,
            location_id=location_id,
            scheduled_at=scheduled_at,
        )

    async def publish_reel(
        self,
        content: UniversalContent,
        media: UniversalMedia,
        caption: Optional[str] = None,
        location_id: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        cover_url: Optional[str] = None,
        share_to_feed: bool = True,
    ) -> PublishResult:
        """Publish a Reel (video)."""
        result = await self._publish_media(
            content=content,
            media_items=[media],
            media_type=InstagramMediaType.REELS,
            caption=caption,
            location_id=location_id,
            scheduled_at=scheduled_at,
            extra_params={
                "share_to_feed": str(share_to_feed).lower(),
            }
        )

        # Set cover image if provided
        if cover_url and result.post_id:
            await self._set_reel_cover(result.post_id, cover_url)

        return result

    async def publish_story(
        self,
        content: UniversalContent,
        media: UniversalMedia,
        caption: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        sticker_data: Optional[Dict[str, Any]] = None,
    ) -> PublishResult:
        """Publish a Story (image/video, 24h expiry)."""
        return await self._publish_media(
            content=content,
            media_items=[media],
            media_type=InstagramMediaType.STORIES,
            caption=caption,
            scheduled_at=scheduled_at,
            extra_params={"sticker_data": sticker_data} if sticker_data else None,
        )

    async def _publish_media(
        self,
        content: UniversalContent,
        media_items: List[UniversalMedia],
        media_type: str,
        caption: Optional[str] = None,
        location_id: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> PublishResult:
        """Internal method to publish media (2-phase process)."""
        client = self.adapter._http_client or await self.adapter._get_client()

        # Phase 1: Upload all media and get media IDs
        media_ids = []
        media_urls = []

        for media in media_items:
            if media.type == "video" and media_type in (InstagramMediaType.IMAGE, InstagramMediaType.CAROUSEL):
                raise ValidationError(f"Video media not supported for {media_type}", platform="instagram")

            # For now, use media.url as the media URL (must be publicly accessible)
            # In production, use InstagramMediaUploader for actual file uploads
            if not media.url:
                raise ValidationError("Media URL required for publishing", platform="instagram")

            media_ids.append(media.url)
            media_urls.append(media.url)

        # Phase 2: Create container(s)
        if media_type == InstagramMediaType.CAROUSEL:
            container_id = await self._create_carousel_container(media_ids, caption, scheduled_at)
        else:
            container_id = await self._create_single_container(
                media_ids[0], media_type, caption, location_id, scheduled_at, extra_params
            )

        # Phase 3: Publish container
        if scheduled_at:
            # Scheduled - container is created but not published yet
            return ScheduledPublishResult(
                platform="instagram",
                container_id=container_id,
                scheduled_at=scheduled_at.isoformat(),
                status="scheduled",
            )

        publish_result = await self._publish_container(container_id)

        return PublishResult(
            platform="instagram",
            post_id=publish_result.get("id", ""),
            container_id=container_id,
            permalink=publish_result.get("permalink"),
            published_at=datetime.utcnow().isoformat(),
            media_type=media_type,
            media_urls=media_urls,
        )

    async def _create_single_container(
        self,
        media_url: str,
        media_type: str,
        caption: Optional[str],
        location_id: Optional[str],
        scheduled_at: Optional[datetime],
        extra_params: Optional[Dict],
    ) -> str:
        """Create a single media container."""
        data = {
            "media_type": media_type,
        }

        if media_type == InstagramMediaType.VIDEO or media_type == InstagramMediaType.REELS:
            data["video_url"] = media_url
        elif media_type == InstagramMediaType.STORIES:
            data["media_url"] = media_url
        else:
            data["image_url"] = media_url

        if caption:
            data["caption"] = caption

        if location_id:
            data["location_id"] = location_id

        if scheduled_at:
            data["scheduled_publish_time"] = int(scheduled_at.timestamp())

        if extra_params:
            data.update(extra_params)

        response = await client.post(f"/{self.adapter.ig_user_id}/media", data=data)

        if response.status_code != 200:
            raise PublishingError(
                f"Container creation failed: {response.text}",
                platform="instagram",
                status_code=response.status_code,
            )

        return response.json()["id"]

    async def _create_carousel_container(
        self,
        media_urls: List[str],
        caption: Optional[str],
        scheduled_at: Optional[datetime],
    ) -> str:
        """Create carousel container from media URLs."""
        # First, create child containers for each media
        child_ids = []
        for url in media_urls:
            # Determine if image or video
            is_video = url.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
            child_data = {
                "media_type": "VIDEO" if is_video else "IMAGE",
                "is_carousel_item": "true",
            }
            if is_video:
                child_data["video_url"] = url
            else:
                child_data["image_url"] = url

            response = await client.post(f"/{self.adapter.ig_user_id}/media", data=child_data)
            if response.status_code != 200:
                raise PublishingError(
                    f"Carousel child creation failed: {response.text}",
                    platform="instagram",
                )
            child_ids.append(response.json()["id"])

        # Create parent carousel container
        data = {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
        }

        if caption:
            data["caption"] = caption

        if scheduled_at:
            data["scheduled_publish_time"] = int(scheduled_at.timestamp())

        response = await client.post(f"/{self.adapter.ig_user_id}/media", data=data)

        if response.status_code != 200:
            raise PublishingError(
                f"Carousel container creation failed: {response.text}",
                platform="instagram",
            )

        return response.json()["id"]

    async def _publish_container(self, container_id: str) -> Dict[str, Any]:
        """Publish a media container."""
        response = await client.post(
            f"/{self.adapter.ig_user_id}/media_publish",
            data={"creation_id": container_id}
        )

        if response.status_code != 200:
            raise PublishingError(
                f"Media publish failed: {response.text}",
                platform="instagram",
                status_code=response.status_code,
            )

        return response.json()

    async def _set_reel_cover(self, reel_id: str, cover_url: str):
        """Set custom cover image for a Reel."""
        response = await client.post(f"/{reel_id}", data={"cover_url": cover_url})
        if response.status_code != 200:
            # Non-fatal, just log
            pass

    async def schedule_post(
        self,
        content: UniversalContent,
        media_items: List[UniversalMedia],
        scheduled_at: datetime,
        media_type: str = "IMAGE",
    ) -> ScheduledPublishResult:
        """Schedule a post for future publishing."""
        if scheduled_at <= datetime.utcnow():
            raise ValidationError("Scheduled time must be in the future", platform="instagram")

        # Create container with scheduled_publish_time
        await self._publish_media(
            content=content,
            media_items=media_items,
            media_type=media_type,
            scheduled_at=scheduled_at,
        )

        # Return container info (container_id would be returned from _publish_media)
        return ScheduledPublishResult(
            platform="instagram",
            container_id="",  # Would be filled by _publish_media
            scheduled_at=scheduled_at.isoformat(),
            status="scheduled",
        )

    async def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Get all scheduled posts."""
        response = await client.get(
            f"/{self.adapter.ig_user_id}/media",
            params={"fields": "id,media_type,timestamp,caption,scheduled_publish_time"}
        )
        if response.status_code != 200:
            return []
        return response.json().get("data", [])

    async def cancel_scheduled_post(self, container_id: str) -> bool:
        """Cancel a scheduled post."""
        response = await client.delete(f"/{container_id}")
        return response.status_code == 200