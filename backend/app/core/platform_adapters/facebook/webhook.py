"""Facebook Page Webhooks Handler."""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from ...errors import ValidationError


class FacebookWebhookEventType(str, Enum):
    FEED_POST = "feed_post"
    FEED_COMMENT = "feed_comment"
    FEED_REACTION = "feed_reaction"


@dataclass
class FacebookWebhookEvent:
    event_type: str
    object_id: str
    timestamp: datetime
    data: Dict[str, Any]
    raw: Dict[str, Any]


class FacebookWebhookHandler:
    """Handles verification and event processing for Facebook Page webhooks."""

    def __init__(self, app_secret: str, verify_token: str):
        self.app_secret = app_secret
        self.verify_token = verify_token

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        if not signature.startswith("sha256="):
            return False
        expected = hmac.new(self.app_secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature[7:])

    def verify_challenge(self, mode: str, challenge: str, token: str) -> Optional[str]:
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None

    def parse_event(self, payload: Dict[str, Any]) -> List[FacebookWebhookEvent]:
        events = []
        for entry in payload.get("entry", []):
            entry_id = entry.get("id")
            time_val = entry.get("time")
            ts = datetime.fromtimestamp(time_val, tz=timezone.utc) if time_val else datetime.now(timezone.utc)

            for change in entry.get("changes", []):
                val = change.get("value", {})
                item = val.get("item")
                verb = val.get("verb")
                if item == "comment":
                    events.append(
                        FacebookWebhookEvent(
                            event_type=FacebookWebhookEventType.FEED_COMMENT.value,
                            object_id=entry_id,
                            timestamp=ts,
                            data={
                                "comment_id": val.get("comment_id"),
                                "post_id": val.get("post_id"),
                                "message": val.get("message"),
                                "verb": verb,
                                "sender_name": val.get("sender_name"),
                            },
                            raw=change,
                        )
                    )
                elif item in ("status", "photo", "video", "post"):
                    events.append(
                        FacebookWebhookEvent(
                            event_type=FacebookWebhookEventType.FEED_POST.value,
                            object_id=entry_id,
                            timestamp=ts,
                            data={
                                "post_id": val.get("post_id"),
                                "verb": verb,
                                "message": val.get("message"),
                            },
                            raw=change,
                        )
                    )
        return events
