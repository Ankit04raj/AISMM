"""X (Twitter) Account Activity Webhooks Handler."""

import hmac
import hashlib
import base64
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from ...errors import ValidationError


class XWebhookEventType(str, Enum):
    TWEET_CREATE = "tweet_create"
    FAVORITE = "favorite"
    FOLLOW = "follow"
    RETWEET = "retweet"
    DIRECT_MESSAGE = "direct_message"


@dataclass
class XWebhookEvent:
    event_type: str
    object_id: str
    timestamp: datetime
    data: Dict[str, Any]
    raw: Dict[str, Any]


class XWebhookHandler:
    """Handles verification (CRC challenge) and event parsing for X Account Activity API."""

    def __init__(self, consumer_secret: str):
        self.consumer_secret = consumer_secret

    def generate_crc_response(self, crc_token: str) -> Dict[str, str]:
        """Generate challenge-response check (CRC) token response."""
        sha256_hash_digest = hmac.new(
            self.consumer_secret.encode("utf-8"),
            msg=crc_token.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        response_token = "sha256=" + base64.b64encode(sha256_hash_digest).decode("utf-8")
        return {"response_token": response_token}

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify X signature on incoming webhook payload."""
        if not signature.startswith("sha256="):
            return False
        expected_digest = hmac.new(
            self.consumer_secret.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha256,
        ).digest()
        expected_sig = "sha256=" + base64.b64encode(expected_digest).decode("utf-8")
        return hmac.compare_digest(expected_sig, signature)

    def parse_event(self, payload: Dict[str, Any]) -> List[XWebhookEvent]:
        """Parse normalized webhook events from Account Activity payload."""
        events = []
        user_id = payload.get("for_user_id", "")

        # 1. Tweet create events (including mentions and replies)
        for tweet in payload.get("tweet_create_events", []):
            created_at_str = tweet.get("created_at")
            events.append(
                XWebhookEvent(
                    event_type=XWebhookEventType.TWEET_CREATE.value,
                    object_id=tweet.get("id_str", tweet.get("id", "")),
                    timestamp=datetime.now(timezone.utc),
                    data={
                        "tweet_id": tweet.get("id_str", str(tweet.get("id"))),
                        "text": tweet.get("text"),
                        "author_id": tweet.get("user", {}).get("id_str"),
                        "author_screen_name": tweet.get("user", {}).get("screen_name"),
                        "in_reply_to_status_id": tweet.get("in_reply_to_status_id_str"),
                    },
                    raw=tweet,
                )
            )

        # 2. Favorite events (likes)
        for fav in payload.get("favorite_events", []):
            events.append(
                XWebhookEvent(
                    event_type=XWebhookEventType.FAVORITE.value,
                    object_id=fav.get("id", ""),
                    timestamp=datetime.now(timezone.utc),
                    data={
                        "favorited_status_id": fav.get("favorited_status", {}).get("id_str"),
                        "user_id": fav.get("user", {}).get("id_str"),
                    },
                    raw=fav,
                )
            )

        return events
