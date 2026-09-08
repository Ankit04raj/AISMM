"""YouTube Video Publisher and Metadata Manager."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
import httpx

from ...errors import PublishingError, ValidationError
from ...normalization import UniversalContent, UniversalMedia, MediaType


@dataclass
class YouTubePublishResult:
    """Result of a YouTube video upload / publishing action."""
    platform: str
    post_id: str
    permalink: Optional[str]
    published_at: str
    media_type: str
    title: str


class YouTubePublisher:
    """Handles publishing and inserting videos via YouTube Data API v3."""

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def publish(self, content: UniversalContent, options: Optional[Dict[str, Any]] = None) -> YouTubePublishResult:
        options = options or {}
        client = await self.adapter._get_client()

        title = getattr(content, "title", None) or (content.caption[:60] if content.caption else "New Video Upload")
        description = content.caption or content.text or ""
        tags = content.hashtags or ["AISMM", "Video"]
        privacy_status = options.get("privacy_status", "public")

        video_payload = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": options.get("category_id", "28"),  # Science & Technology
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            }
        }

        resp = await client.post(
            "/videos?part=snippet,status",
            json=video_payload,
        )
        if resp.status_code not in (200, 201):
            raise PublishingError(f"YouTube video insert failed: {resp.text}", platform="youtube")

        res_data = resp.json()
        video_id = res_data.get("id", "yt_unknown")

        return YouTubePublishResult(
            platform="youtube",
            post_id=video_id,
            permalink=f"https://www.youtube.com/watch?v=f{video_id}",
            published_at=datetime.now(timezone.utc).isoformat(),
            media_type="VIDEO",
            title=title,
        )
