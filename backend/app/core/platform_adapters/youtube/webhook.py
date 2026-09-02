"""YouTube WebSub (PubSubHubbub) Webhook Handler."""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from ...errors import ValidationError


class YouTubeWebhookEventType(str, Enum):
    VIDEO_UPLOAD = "VIDEO_UPLOAD"
    VIDEO_UPDATE = "VIDEO_UPDATE"
    VIDEO_DELETE = "VIDEO_DELETE"


@dataclass
class YouTubeWebhookEvent:
    event_type: str
    video_id: str
    channel_id: str
    title: str
    published_at: datetime
    raw: Dict[str, Any]


class YouTubeWebhookHandler:
    """Handles verification and event parsing for YouTube WebSub push notifications."""

    def __init__(self, secret: Optional[str] = None):
        self.secret = secret

    def verify_challenge(self, mode: str, challenge: str, topic: str) -> Optional[str]:
        """Verify WebSub hub.challenge response."""
        if mode in ("subscribe", "unsubscribe") and challenge:
            return challenge
        return None

    def parse_atom_feed(self, xml_payload: str) -> List[YouTubeWebhookEvent]:
        """Parse Atom XML payload from YouTube WebSub notifications."""
        events = []
        try:
            root = ET.fromstring(xml_payload.strip())
            # Find all entries (support default namespace or atom prefix)
            entries = root.findall("{http://www.w3.org/2005/Atom}entry") or root.findall("entry") or root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//entry")

            for entry in entries:
                # Search videoId and channelId
                vid = "unknown"
                chid = "unknown"
                title = "New Video"

                for child in entry:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if tag in ("videoId", "yt:videoId"):
                        vid = child.text or "unknown"
                    elif tag in ("channelId", "yt:channelId"):
                        chid = child.text or "unknown"
                    elif tag == "title":
                        title = child.text or "New Video"

                events.append(
                    YouTubeWebhookEvent(
                        event_type=YouTubeWebhookEventType.VIDEO_UPLOAD.value,
                        video_id=vid,
                        channel_id=chid,
                        title=title,
                        published_at=datetime.now(timezone.utc),
                        raw={"video_id": vid, "channel_id": chid, "title": title},
                    )
                )
        except Exception:
            pass

        return events
