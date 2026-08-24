# Platform Adapter Architecture

## Overview
The platform adapter layer is the boundary between AISMM's platform-agnostic core and external social media APIs. Each platform implements the same `BasePlatformAdapter` contract, exposing only the capabilities it actually supports.

---

## 1. Adapter Directory Structure

```
platforms/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── adapter.py          # BasePlatformAdapter (ABC)
│   ├── capabilities.py      # PlatformCapabilities enum + helper
│   ├── models.py            # UniversalContent, PlatformSpecificPayload, normalized entities
│   ├── errors.py            # PlatformError hierarchy
│   └── registry.py         # PlatformRegistry
│
├── instagram/
│   ├── __init__.py
│   ├── config.yaml         # Capabilities, limits, API version
│   ├── adapter.py          # InstagramAdapter(BasePlatformAdapter)
│   ├── auth.py             # OAuth flow, token management
│   ├── publisher.py        # create_post, publish, schedule, media upload
│   ├── analytics.py        # fetch metrics, account analytics
│   ├── comments.py         # fetch comments, reply
│   ├── mapper.py           # UniversalContent -> Instagram payload
│   └── client.py           # Graph API HTTP client with rate limiting
│
├── facebook/
│   ├── __init__.py
│   ├── config.yaml
│   ├── adapter.py
│   ├── auth.py
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── mapper.py
│   └── client.py
│
├── x/
│   ├── __init__.py
│   ├── config.yaml
│   ├── adapter.py
│   ├── auth.py             # OAuth 1.0a / 2.0
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── mapper.py
│   └── client.py
│
├── linkedin/
│   ├── __init__.py
│   ├── config.yaml
│   ├── adapter.py
│   ├── auth.py
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── mapper.py
│   └── client.py
│
├── youtube/
│   ├── __init__.py
│   ├── config.yaml
│   ├── adapter.py
│   ├── auth.py
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── mapper.py
│   └── client.py
│
└── mock/
    ├── __init__.py
    └── adapter.py          # MockPlatformAdapter for testing
```

---

## 2. Base Adapter Contract (interface)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class BasePlatformAdapter(ABC):
    """Every platform must implement this contract exactly."""

    # ── Identity ──────────────────────────────────────────────────────
    @property
    @abstractmethod
    def platform_id(self) -> str:
        """e.g. 'instagram', 'facebook', 'x', 'linkedin', 'youtube'"""

    # ── Authentication ───────────────────────────────────────────────
    @abstractmethod
    async def authenticate(self, credentials: Dict) -> AuthResult: ...

    @abstractmethod
    async def refresh_token(self) -> AuthResult: ...

    @abstractmethod
    async def disconnect(self) -> bool: ...

    @abstractmethod
    async def validate_credentials(self) -> bool: ...

    # ── Publishing ───────────────────────────────────────────────────
    @abstractmethod
    async def validate_content(self, content: UniversalContent) -> ValidationResult: ...

    @abstractmethod
    async def upload_media(self, media: MediaItem) -> MediaUploadResult: ...

    @abstractmethod
    async def publish_post(self, payload: PlatformSpecificPayload) -> PublishResult: ...

    @abstractmethod
    async def schedule_post(self, payload: PlatformSpecificPayload,
                           scheduled_at: datetime) -> ScheduleResult: ...

    @abstractmethod
    async def update_post(self, publication_id: str,
                         payload: PlatformSpecificPayload) -> bool: ...

    @abstractmethod
    async def delete_post(self, publication_id: str) -> bool: ...

    # ── Content Fetching ─────────────────────────────────────────────
    @abstractmethod
    async def fetch_posts(self, account_id: str, limit: int = 50) -> List[NormalizedPost]: ...

    @abstractmethod
    async def fetch_comments(self, publication_id: str) -> List[NormalizedComment]: ...

    @abstractmethod
    async def fetch_replies(self, comment_id: str) -> List[NormalizedComment]: ...

    # ── Engagement ───────────────────────────────────────────────────
    @abstractmethod
    async def reply_to_comment(self, comment_id: str, text: str) -> ReplyResult: ...

    @abstractmethod
    async def fetch_engagement(self, publication_id: str) -> NormalizedEngagement: ...

    @abstractmethod
    async def fetch_account_metrics(self, account_id: str) -> NormalizedAccountMetrics: ...

    @abstractmethod
    async def fetch_post_analytics(self, publication_id: str) -> NormalizedPostAnalytics: ...

    # ── Webhooks / Events ────────────────────────────────────────────
    @abstractmethod
    async def register_webhook(self, url: str, events: List[str]) -> WebhookRegistration: ...

    @abstractmethod
    async def handle_webhook(self, payload: Dict, signature: str) -> List[NormalizedEvent]: ...

    # ── Capabilities ─────────────────────────────────────────────────
    @abstractmethod
    def get_capabilities(self) -> PlatformCapabilities: ...

    @abstractmethod
    def supports(self, capability: str) -> bool: ...
```

---

## 3. Capability System

```python
from enum import Enum

class Capability(str, Enum):
    PUBLISHING = "publishing"
    SCHEDULING = "scheduling"
    TEXT_POST = "text_post"
    IMAGE_POST = "image_post"
    VIDEO_POST = "video_post"
    CAROUSEL_POST = "carousel_post"
    STORIES = "stories"
    SHORT_VIDEO = "short_video"
    COMMENTS = "comments"
    REPLIES = "replies"
    ANALYTICS = "analytics"
    AUDIENCE_METRICS = "audience_metrics"
    WEBHOOKS = "webhooks"
    DIRECT_MESSAGES = "direct_messages"
    HASHTAGS = "hashtags"
    MENTIONS = "mentions"

class PlatformCapabilities:
    """Immutable capability set loaded from config."""
    def __init__(self, capabilities: Dict[Capability, bool], limits: Dict):
        self._caps = capabilities
        self._limits = limits

    def supports(self, capability: str) -> bool:
        return self._caps.get(Capability(capability), False)

    def get_limit(self, limit_name: str) -> Optional[int]:
        return self._limits.get(limit_name)
```

---

## 4. Content Normalization (Mapper)

```python
class BaseMapper(ABC):
    """Maps UniversalContent <-> PlatformSpecificPayload."""

    @abstractmethod
    def to_platform(self, content: UniversalContent,
                    account_caps: PlatformCapabilities) -> PlatformSpecificPayload:
        """Convert universal content to platform-specific payload.
        Applies platform limits (text length, hashtag count, media count)."""

    @abstractmethod
    def from_platform(self, raw_post: Dict) -> NormalizedPost:
        """Convert platform API response to normalized post."""

    @abstractmethod
    def to_normalized_comment(self, raw_comment: Dict) -> NormalizedComment: ...

    @abstractmethod
    def to_normalized_engagement(self, raw_metrics: Dict,
                                 original_metric_names: Dict) -> NormalizedEngagement: ...
```

### Example: Instagram Mapper
```python
class InstagramMapper(BaseMapper):
    def to_platform(self, content, caps):
        # Apply Instagram limits
        max_text = caps.get_limit("text_length")  # 2200
        max_tags = caps.get_limit("hashtag_count")  # 30

        caption = content.caption or content.text
        if len(caption) > max_text:
            caption = caption[:max_text]

        hashtags = (content.hashtags or [])[:max_tags]
        caption_with_tags = f"{caption}\n\n" + " ".join(f"#{t}" for t in hashtags)

        return PlatformSpecificPayload(
            platform="instagram",
            text=caption_with_tags,
            media_ids=[m.platform_media_id for m in content.media],
            media_type=self._resolve_media_type(content.media),
        )
```

---

## 5. Error Translation

Each adapter translates platform-specific errors into normalized AISMM errors:

```python
class PlatformError(Exception): pass
class AuthenticationError(PlatformError): pass
class RateLimitError(PlatformError): pass
class ValidationError(PlatformError): pass
class PublishingError(PlatformError): pass
class AnalyticsError(PlatformError): pass
class UnsupportedCapabilityError(PlatformError): pass

# Adapter example:
def _translate_error(self, api_error: Dict) -> PlatformError:
    code = api_error.get("error", {}).get("code")
    if code == 190:
        return AuthenticationError("Token expired")
    elif code == 4:
        return RateLimitError("Rate limit reached")
    elif code == 100:
        return ValidationError(api_error["error"]["message"])
    else:
        return PlatformError(f"Unknown error: {api_error}")
```

---

## 6. Rate Limit & Retry Management

```python
class RateLimitPolicy:
    requests_per_hour: int
    burst: int
    backoff_base: float = 1.0
    backoff_max: float = 60.0
    max_retries: int = 5

    def backoff_seconds(self, attempt: int) -> float:
        return min(self.backoff_base * (2 ** attempt), self.backoff_max)
```

---

## 7. Platform Registry

```python
class PlatformRegistry:
    _adapters: Dict[str, Type[BasePlatformAdapter]] = {}

    @classmethod
    def register(cls, platform_id: str, adapter_class: Type[BasePlatformAdapter]):
        cls._adapters[platform_id] = adapter_class

    @classmethod
    def get(cls, platform_id: str, account=None) -> BasePlatformAdapter:
        if platform_id not in cls._adapters:
            raise UnsupportedCapabilityError(f"Platform {platform_id} not registered")
        return cls._adapters[platform_id](account=account)

    @classmethod
    def get_all_capabilities(cls) -> Dict[str, PlatformCapabilities]:
        return {pid: cls.get(pid).get_capabilities()
                for pid in cls._adapters}

    @classmethod
    def register_from_config(cls, config_path: str):
        """Auto-discover and register adapters from config."""
```

---

## 8. Mock Adapter (for testing)

```python
class MockPlatformAdapter(BasePlatformAdapter):
    """Simulates a platform without external API calls.
    Configurable to simulate: publishing, comments, analytics,
    errors, rate limits, unsupported features."""

    def __init__(self, config: Dict = None):
        self._config = config or {}
        self._posts = []
        self._comments = []
        self._should_fail = self._config.get("simulate_error", False)
        self._rate_limit = self._config.get("simulate_rate_limit", False)

    async def publish_post(self, payload):
        if self._should_fail:
            raise PublishingError("Simulated failure")
        if self._rate_limit:
            raise RateLimitError("Simulated rate limit")
        post_id = f"mock_{uuid4()}"
        self._posts.append(post_id)
        return PublishResult(post_id=post_id, status="published")
```

---

## 9. Adapter Lifecycle

```
Config Load → Registry.register(platform_id, AdapterClass)
     │
     ▼
User Connects → Adapter.authenticate(credentials)
     │
     ▼
Store Encrypted Tokens → SocialAccount record (status=CONNECTED)
     │
     ▼
Runtime: Registry.get(platform_id, account) → Adapter instance
     │
     ▼
Operation: adapter.publish_post(payload)
     │
     ├─► mapper.to_platform()
     ├─► client.request() with rate limiting & retries
     ├─► error translation
     └─► normalized result
     │
     ▼
Store PostPublication + metrics
```

---

*Document Version: 1.0 — Phase 2 Architecture Design*
