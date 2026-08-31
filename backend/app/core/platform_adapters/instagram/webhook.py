"""Instagram Webhook Handler - Real-time Events."""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ...errors import ValidationError, PlatformError


class InstagramWebhookField(str, Enum):
    """Instagram webhook subscription fields."""
    COMMENTS = "comments"
    MENTIONS = "mentions"
    STORY_REPLIES = "story_replies"
    MESSAGES = "messages"
    MESSAGING_POSTBACKS = "messaging_postbacks"
    MESSAGING_REFERRALS = "messaging_referrals"
    STORY_INSIGHTS = "story_insights"


class InstagramWebhookEventType(str, Enum):
    """Webhook event types."""
    # Comment events
    COMMENT_CREATED = "comment_created"
    COMMENT_DELETED = "comment_deleted"
    COMMENT_HIDDEN = "comment_hidden"
    COMMENT_REPLY_CREATED = "comment_reply_created"

    # Mention events
    MENTION_CREATED = "mention_created"

    # Story events
    STORY_REPLY_CREATED = "story_reply_created"
    STORY_INSIGHTS = "story_insights"

    # Message events
    MESSAGE_CREATED = "message_created"
    MESSAGE_DELETED = "message_deleted"

    # Account events
    ACCOUNT_UPDATED = "account_updated"


@dataclass
class WebhookEvent:
    """Parsed webhook event."""
    event_type: str
    object_type: str  # "instagram", "page"
    object_id: str
    timestamp: datetime
    data: Dict[str, Any]
    raw: Dict[str, Any]


class InstagramWebhookHandler:
    """Handles Instagram webhook verification and event processing."""

    def __init__(
        self,
        app_secret: str,
        verify_token: str,
        callback_url: str
    ):
        self.app_secret = app_secret
        self.verify_token = verify_token
        self.callback_url = callback_url
        self._event_handlers: Dict[str, List[Callable]] = {}

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify X-Hub-Signature-256 header."""
        if not signature.startswith("sha256="):
            return False

        expected_signature = hmac.new(
            self.app_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        provided_signature = signature[7:]  # Remove "sha256="
        return hmac.compare_digest(expected_signature, provided_signature)

    def verify_challenge(self, mode: str, challenge: str, token: str) -> Optional[str]:
        """Verify webhook subscription challenge (GET request)."""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None

    def parse_event(self, payload: Dict[str, Any]) -> List[WebhookEvent]:
        """Parse incoming webhook payload into events."""
        events = []

        object_type = payload.get("object")
        entry_list = payload.get("entry", [])

        for entry in entry_list:
            entry_id = entry.get("id")
            time = entry.get("time")
            timestamp = datetime.fromtimestamp(time) if time else datetime.utcnow()

            changes = entry.get("changes", [])
            for change in changes:
                field = change.get("field")
                value = change.get("value", {})

                event = self._parse_change(field, value, object_type, entry_id, timestamp)
                if event:
                    event.raw = change
                    events.append(event)

        return events

    def _parse_change(
        self,
        field: str,
        value: Dict[str, Any],
        object_type: str,
        object_id: str,
        timestamp: datetime
    ) -> Optional[WebhookEvent]:
        """Parse a single change into a webhook event."""
        event_type_map = {
            InstagramWebhookField.COMMENTS.value: self._parse_comment_event,
            InstagramWebhookField.MENTIONS.value: self._parse_mention_event,
            InstagramWebhookField.STORY_REPLIES.value: self._parse_story_reply_event,
            InstagramWebhookField.STORY_INSIGHTS.value: self._parse_story_insights_event,
        }

        parser = event_type_map.get(field)
        if parser:
            return parser(value, object_type, object_id, timestamp)

        return None

    def _parse_comment_event(
        self,
        value: Dict,
        object_type: str,
        object_id: str,
        timestamp: datetime
    ) -> WebhookEvent:
        """Parse comment-related event."""
        verb = value.get("verb", "created")

        event_type_map = {
            "created": InstagramWebhookEventType.COMMENT_CREATED,
            "deleted": InstagramWebhookEventType.COMMENT_DELETED,
            "hidden": InstagramWebhookEventType.COMMENT_HIDDEN,
        }

        event_type = event_type_map.get(verb, InstagramWebhookEventType.COMMENT_CREATED)

        return WebhookEvent(
            event_type=event_type.value,
            object_type=object_type,
            object_id=object_id,
            timestamp=timestamp,
            raw=value,
            data={
                "comment_id": value.get("comment_id"),
                "media_id": value.get("media_id"),
                "text": value.get("text"),
                "username": value.get("from", {}).get("username"),
                "user_id": value.get("from", {}).get("id"),
            }
        )

    def _parse_mention_event(
        self,
        value: Dict,
        object_type: str,
        object_id: str,
        timestamp: datetime
    ) -> WebhookEvent:
        """Parse mention event."""
        return WebhookEvent(
            event_type=InstagramWebhookEventType.MENTION_CREATED.value,
            object_type=object_type,
            object_id=object_id,
            timestamp=timestamp,
            raw=value,
            data={
                "mention_id": value.get("mention_id"),
                "media_id": value.get("media_id"),
                "username": value.get("username"),
                "media_type": value.get("media_type"),
            }
        )

    def _parse_story_reply_event(
        self,
        value: Dict,
        object_type: str,
        object_id: str,
        timestamp: datetime
    ) -> WebhookEvent:
        """Parse story reply event."""
        return WebhookEvent(
            event_type=InstagramWebhookEventType.STORY_REPLY_CREATED.value,
            object_type=object_type,
            object_id=object_id,
            timestamp=timestamp,
            raw=value,
            data={
                "story_id": value.get("story_id"),
                "reply_id": value.get("reply_id"),
                "text": value.get("text"),
                "username": value.get("from", {}).get("username"),
                "user_id": value.get("from", {}).get("id"),
            }
        )

    def _parse_story_insights_event(
        self,
        value: Dict,
        object_type: str,
        object_id: str,
        timestamp: datetime
    ) -> WebhookEvent:
        """Parse story insights event."""
        return WebhookEvent(
            event_type=InstagramWebhookEventType.STORY_INSIGHTS.value,
            object_type=object_type,
            object_id=object_id,
            timestamp=timestamp,
            raw=value,
            data={
                "story_id": value.get("story_id"),
                "metrics": value.get("metrics", {}),
            }
        )

    def register_handler(self, event_type: str, handler: Callable):
        """Register an event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def register_handlers(self, handlers: Dict[str, Callable]):
        """Register multiple handlers at once."""
        for event_type, handler in handlers.items():
            self.register_handler(event_type, handler)

    async def process_event(self, event: WebhookEvent) -> List[Any]:
        """Process a webhook event through registered handlers."""
        results = []
        handlers = self._event_handlers.get(event.event_type, [])

        # Also check for wildcard handlers
        wildcard_handlers = self._event_handlers.get("*", [])

        all_handlers = handlers + wildcard_handlers

        for handler in all_handlers:
            try:
                if hasattr(handler, "__call__"):
                    result = await handler(event) if callable(handler) else handler(event)
                    results.append(result)
            except Exception as e:
                # Log error but continue processing other handlers
                results.append({"error": str(e), "handler": handler.__name__})

        return results

    async def handle_webhook_request(
        self,
        method: str,
        query_params: Dict[str, str],
        headers: Dict[str, str],
        body: bytes
    ) -> Dict[str, Any]:
        """Main entry point for webhook requests."""
        if method == "GET":
            # Verification request
            mode = query_params.get("hub.mode")
            challenge = query_params.get("hub.challenge")
            token = query_params.get("hub.verify_token")

            response = self.verify_challenge(mode, challenge, token)
            if response:
                return {"status": "verified", "challenge": response}
            else:
                raise ValidationError("Webhook verification failed", platform="instagram")

        elif method == "POST":
            # Event notification
            signature = headers.get("x-hub-signature-256", "")

            if not self.verify_signature(body, signature):
                raise ValidationError("Invalid webhook signature", platform="instagram")

            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON payload", platform="instagram")

            events = self.parse_event(payload)

            # Process all events
            all_results = []
            for event in events:
                results = await self.process_event(event)
                all_results.extend(results)

            return {
                "status": "processed",
                "events_received": len(events),
                "results": all_results,
            }

        else:
            raise ValidationError(f"Unsupported method: {method}", platform="instagram")


class InstagramWebhookManager:
    """Manages webhook subscriptions for Instagram."""

    def __init__(self, adapter: "InstagramAdapter"):
        self.adapter = adapter

    async def subscribe(
        self,
        callback_url: str,
        verify_token: str,
        fields: List[str]
    ) -> Dict[str, Any]:
        """Subscribe to webhook fields."""
        client = self.adapter._http_client or await self.adapter._get_client()

        response = await client.post(
            f"/{self.adapter.ig_user_id}/subscribed_apps",
            data={
                "subscribed_fields": ",".join(fields),
                "callback_url": callback_url,
                "verify_token": verify_token,
            }
        )

        if response.status_code != 200:
            raise PlatformError(
                f"Webhook subscribe failed: {response.text}",
                platform="instagram",
                status_code=response.status_code,
            )

        return response.json()

    async def unsubscribe(self) -> bool:
        """Unsubscribe from all webhooks."""
        client = self.adapter._http_client or await self.adapter._get_client()

        response = await client.delete(f"/{self.adapter.ig_user_id}/subscribed_apps")
        return response.status_code == 200

    async def get_subscriptions(self) -> Dict[str, Any]:
        """Get current webhook subscriptions."""
        client = self.adapter._http_client or await self.adapter._get_client()

        response = await client.get(f"/{self.adapter.ig_user_id}/subscribed_apps")

        if response.status_code != 200:
            return {}

        return response.json()

    async def verify_webhook_health(self) -> Dict[str, Any]:
        """Verify webhook endpoint is healthy."""
        # This would typically make a test call to the callback URL
        # For now, return subscription status
        subs = await self.get_subscriptions()
        return {
            "active": bool(subs),
            "subscriptions": subs,
        }