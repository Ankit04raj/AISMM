"""LinkedIn UGC and REST Post Publisher."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
import httpx

from ...errors import PublishingError, ValidationError
from ...normalization import UniversalContent, UniversalMedia, MediaType


@dataclass
class LinkedInPublishResult:
    """Result of a LinkedIn post publication."""
    platform: str
    post_id: str
    permalink: Optional[str]
    published_at: str
    media_type: str


class LinkedInPublisher:
    """Handles publishing text commentary, articles, and media to LinkedIn member or organization feed."""

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def publish(self, content: UniversalContent, options: Optional[Dict[str, Any]] = None) -> LinkedInPublishResult:
        options = options or {}
        client = await self.adapter._get_client()

        author_urn = self.adapter.organization_urn or self.adapter.author_urn or f"urn:li:person:{self.adapter.author_id or 'me'}"
        text = content.caption or content.text or ""

        # Construct UGC Post payload
        media_category = "NONE"
        media_elements = []

        if content.media:
            first_media = content.media[0]
            if first_media.type == MediaType.VIDEO:
                media_category = "VIDEO"
                media_elements.append({
                    "status": "READY",
                    "description": {"text": first_media.alt_text or "Video attachment"},
                    "originalUrl": first_media.url,
                    "title": {"text": getattr(content, "title", None) or "Video Post"},
                })
            elif first_media.type in (MediaType.IMAGE, MediaType.CAROUSEL):
                media_category = "IMAGE"
                media_elements.append({
                    "status": "READY",
                    "description": {"text": first_media.alt_text or "Image attachment"},
                    "originalUrl": first_media.url,
                    "title": {"text": getattr(content, "title", None) or "Image Post"},
                })

        ugc_payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": media_category,
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": options.get("visibility", "PUBLIC")
            }
        }

        if media_elements:
            ugc_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = media_elements

        headers = {
            "X-Restli-Protocol-Version": "2.0.0",
        }

        resp = await client.post("/v2/ugcPosts", json=ugc_payload, headers=headers)
        if resp.status_code not in (200, 201):
            raise PublishingError(f"LinkedIn UGC publish failed: {resp.text}", platform="linkedin")

        res_data = resp.json()
        post_urn = res_data.get("id", "urn:li:share:unknown")

        return LinkedInPublishResult(
            platform="linkedin",
            post_id=post_urn,
            permalink=f"https://www.linkedin.com/feed/update/{post_urn}",
            published_at=datetime.now(timezone.utc).isoformat(),
            media_type=media_category,
        )
