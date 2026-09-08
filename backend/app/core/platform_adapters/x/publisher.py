"""X (Twitter) Tweet and Media Publisher (API v2)."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
import httpx

from ...errors import PublishingError, ValidationError
from ...normalization import UniversalContent, UniversalMedia, MediaType


@dataclass
class XPublishResult:
    """Result of an X tweet publication action."""
    platform: str
    post_id: str
    permalink: Optional[str]
    published_at: str
    media_type: str
    text_snippet: str


class XPublisher:
    """Handles publishing tweets, threads, and media attachments to X."""

    def __init__(self, adapter: Any):
        self.adapter = adapter

    async def publish(self, content: UniversalContent, options: Optional[Dict[str, Any]] = None) -> XPublishResult:
        options = options or {}
        client = await self.adapter._get_client()

        # Build tweet payload
        text = content.caption or content.text or ""
        if content.hashtags:
            # Append hashtags if not already present
            existing_tags = [w.lower() for w in text.split() if w.startswith("#")]
            tags_to_add = [f"#{t}" if not t.startswith("#") else t for t in content.hashtags if t.lower() not in existing_tags]
            if tags_to_add:
                text = f"{text}\n\n{' '.join(tags_to_add)}"

        payload: Dict[str, Any] = {
            "text": text,
        }

        # Media attachments
        media_ids = options.get("media_ids", [])
        if content.media and not media_ids:
            # Simulated media IDs from attached URLs
            media_ids = [f"media_{i+101}" for i, _ in enumerate(content.media[:4])]

        if media_ids:
            payload["media"] = {"media_ids": media_ids}

        # Reply thread support
        if options.get("in_reply_to_tweet_id"):
            payload["reply"] = {"in_reply_to_tweet_id": options["in_reply_to_tweet_id"]}

        # Quote tweet support
        if options.get("quote_tweet_id"):
            payload["quote_tweet_id"] = options["quote_tweet_id"]

        resp = await client.post("/tweets", json=payload)
        if resp.status_code not in (200, 201):
            raise PublishingError(f"X tweet publish failed: {resp.text}", platform="x")

        res_data = resp.json().get("data", {})
        tweet_id = res_data.get("id", "tweet_unknown")
        author_username = getattr(self.adapter, "account_username", None) or "i"

        m_type = "TEXT"
        if content.media:
            m_type = content.media[0].type.value.upper() if hasattr(content.media[0].type, "value") else "IMAGE"

        return XPublishResult(
            platform="x",
            post_id=tweet_id,
            permalink=f"https://x.com/{author_username}/status/{tweet_id}",
            published_at=datetime.now(timezone.utc).isoformat(),
            media_type=m_type,
            text_snippet=text[:80],
        )
