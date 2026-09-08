"""Facebook Post Publisher."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
import httpx

from ...errors import PublishingError, ValidationError
from ...normalization import UniversalContent, UniversalMedia, MediaType


@dataclass
class FacebookPublishResult:
    """Result of a Facebook publishing action."""
    platform: str
    post_id: str
    permalink: Optional[str]
    published_at: str
    media_type: str


class FacebookPublisher:
    """Handles publishing text, images, videos, and links to Facebook Page feed."""

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def publish(self, content: UniversalContent, options: Optional[Dict[str, Any]] = None) -> FacebookPublishResult:
        options = options or {}
        client = await self.adapter._get_client()
        page_id = self.adapter.page_id or "me"

        # 1. Video post
        if content.media and any(m.type == MediaType.VIDEO for m in content.media):
            video = next(m for m in content.media if m.type == MediaType.VIDEO)
            data = {
                "description": content.caption or content.text or "",
                "file_url": video.url,
            }
            if options.get("scheduled_at"):
                data["published"] = "false"
                data["scheduled_publish_time"] = int(options["scheduled_at"].timestamp())

            resp = await client.post(f"/{page_id}/videos", data=data)
            if resp.status_code != 200:
                raise PublishingError(f"Facebook video publish failed: {resp.text}", platform="facebook")
            res_data = resp.json()
            return FacebookPublishResult(
                platform="facebook",
                post_id=res_data.get("id", ""),
                permalink=f"https://facebook.com/{res_data.get('id')}",
                published_at=datetime.now(timezone.utc).isoformat(),
                media_type="VIDEO",
            )

        # 2. Photo post
        elif content.media and len(content.media) == 1 and content.media[0].type == MediaType.IMAGE:
            photo = content.media[0]
            data = {
                "caption": content.caption or content.text or "",
                "url": photo.url,
            }
            if options.get("scheduled_at"):
                data["published"] = "false"
                data["scheduled_publish_time"] = int(options["scheduled_at"].timestamp())

            resp = await client.post(f"/{page_id}/photos", data=data)
            if resp.status_code != 200:
                raise PublishingError(f"Facebook photo publish failed: {resp.text}", platform="facebook")
            res_data = resp.json()
            return FacebookPublishResult(
                platform="facebook",
                post_id=res_data.get("post_id", res_data.get("id", "")),
                permalink=f"https://facebook.com/{res_data.get('id')}",
                published_at=datetime.now(timezone.utc).isoformat(),
                media_type="IMAGE",
            )

        # 3. Standard text / multi-photo / feed post
        else:
            data = {
                "message": content.caption or content.text or "",
            }
            if options.get("link"):
                data["link"] = options["link"]

            if options.get("scheduled_at"):
                data["published"] = "false"
                data["scheduled_publish_time"] = int(options["scheduled_at"].timestamp())

            resp = await client.post(f"/{page_id}/feed", data=data)
            if resp.status_code != 200:
                raise PublishingError(f"Facebook feed publish failed: {resp.text}", platform="facebook")
            res_data = resp.json()
            return FacebookPublishResult(
                platform="facebook",
                post_id=res_data.get("id", ""),
                permalink=f"https://facebook.com/{res_data.get('id')}",
                published_at=datetime.now(timezone.utc).isoformat(),
                media_type="STATUS",
            )
