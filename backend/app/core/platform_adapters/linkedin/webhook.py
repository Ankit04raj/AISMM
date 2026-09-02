"""LinkedIn Webhooks Handler."""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from ...errors import ValidationError


class LinkedInWebhookEventType(str, Enum):
    ORGANIZATION_SHARE = "ORGANIZATION_SHARE"
    MEMBER_SHARE = "MEMBER_SHARE"
    COMMENT = "COMMENT"
    REACTION = "REACTION"


@dataclass
class LinkedInWebhookEvent:
    event_type: str
    object_urn: str
    timestamp: datetime
    data: Dict[str, Any]
    raw: Dict[str, Any]


class LinkedInWebhookHandler:
    """Handles verification and event parsing for LinkedIn Community Management webhooks."""

    def __init__(self, client_secret: str):
        self.client_secret = client_secret

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify HMAC-SHA256 signature from X-LI-Signature header."""
        if not signature:
            return False
        expected = hmac.new(self.client_secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_event(self, payload: Dict[str, Any]) -> List[LinkedInWebhookEvent]:
        events = []
        for event in payload.get("events", [payload]):
            event_type = event.get("eventType") or event.get("type", "ORGANIZATION_SHARE")
            object_urn = event.get("entityUrn") or event.get("urn", "")
            events.append(
                LinkedInWebhookEvent(
                    event_type=event_type,
                    object_urn=object_urn,
                    timestamp=datetime.now(timezone.utc),
                    data=event.get("data", event),
                    raw=event,
                )
            )
        return events
