# AISMM Platform Adapter Architecture
**Phase 2 — Architecture Design**  
**Version:** 1.0  
**Date:** 2026-08-25  
**Status:** DESIGN — AWAITING APPROVAL

---

## 1. Platform Adapter Contract

Every platform adapter MUST implement the `BasePlatformAdapter` interface. This is the single most important architectural contract.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, AsyncIterator
from enum import Enum
import asyncio

class PlatformCapability(Enum):
    # Publishing
    PUBLISHING = "publishing"
    SCHEDULING = "scheduling"
    TEXT_POST = "text_post"
    IMAGE_POST = "image_post"
    VIDEO_POST = "video_post"
    CAROUSEL_POST = "carousel_post"
    STORIES = "stories"
    SHORT_VIDEO = "short_video"
    
    # Engagement
    COMMENTS = "comments"
    REPLIES = "replies"
    DIRECT_MESSAGES = "direct_messages"
    
    # Analytics
    ANALYTICS = "analytics"
    AUDIENCE_METRICS = "audience_metrics"
    POST_ANALYTICS = "post_analytics"
    ENGAGEMENT_METRICS = "engagement_metrics"
    
    # Events
    WEBHOOKS = "webhooks"
    
    # Content features
    HASHTAGS = "hashtags"
    MENTIONS = "mentions"
    LOCATION = "location"
    POLL = "poll"

@dataclass
class PlatformConfig:
    name: str
    display_name: str
    capabilities: List[PlatformCapability]
    limits: Dict[str, Any]
    supported_media: List[str]
    api_version: str
    rate_limit: "RateLimitConfig"
    auth_type: str  # "oauth2", "oauth1", "api_key"

@dataclass
class RateLimitConfig:
    requests_per_window: int
    window_seconds: int
    retry_policy: str  # "exponential", "linear", "fixed"
    max_retries: int
    backoff_base: float = 1.0

class AuthenticationResult:
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    error: Optional[str] = None

class PublishResult:
    success: bool
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    raw_response: Optional[Dict] = None
    error: Optional[str] = None

class MediaUploadResult:
    success: bool
    media_id: Optional[str] = None
    media_url: Optional[str] = None
    error: Optional[str] = None

class NormalizedPost:
    id: str
    platform: str
    platform_post_id: str
    content: str
    caption: Optional[str]
    media: List[Dict]
    hashtags: List[str]
    mentions: List[str]
    location: Optional[str]
    published_at: datetime
    engagement: Dict[str, int]
    raw_data: Dict

class NormalizedComment:
    id: str
    platform: str
    platform_comment_id: str
    post_id: str
    author: Dict
    content: str
    created_at: datetime
    sentiment: Optional[Dict] = None
    raw_data: Dict

class NormalizedMetrics:
    post_id: str
    platform: str
    metrics: Dict[str, int]  # normalized metric types
    original_metrics: Dict[str, int]  # platform-specific
    timestamp: datetime

class BasePlatformAdapter(ABC):
    """Abstract base class for all platform adapters."""
    
    # Platform identifier (e.g., "instagram", "facebook", "x")
    PLATFORM_ID: str
    
    # Platform display name
    PLATFORM_NAME: str
    
    # Required configuration keys
    REQUIRED_CONFIG_KEYS: List[str] = []
    
    def __init__(self, config: PlatformConfig, credentials: Optional[Dict] = None):
        self.config = config
        self.credentials = credentials or {}
        self._rate_limiter = RateLimiter(config.rate_limit)
    
    @abstractmethod
    async def authenticate(self, auth_code: Optional[str] = None) -> AuthenticationResult:
        """Authenticate with platform. If auth_code provided, exchange for tokens."""
        pass
    
    @abstractmethod
    async def refresh_tokens(self) -> AuthenticationResult:
        """Refresh expired access token using refresh token."""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate current credentials are valid."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect/revoke platform connection."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[PlatformCapability]:
        """Return list of supported capabilities."""
        pass
    
    @abstractmethod
    def supports(self, capability: PlatformCapability) -> bool:
        """Check if platform supports a specific capability."""
        pass
    
    # === PUBLISHING ===
    
    @abstractmethod
    async def validate_content(self, content: "UniversalContent") -> "ValidationResult":
        """Validate content against platform limits and requirements."""
        pass
    
    @abstractmethod
    async def upload_media(self, media: "UniversalMedia") -> MediaUploadResult:
        """Upload media to platform."""
        pass
    
    @abstractmethod
    async def publish_post(self, content: "UniversalContent") -> PublishResult:
        """Publish content immediately."""
        pass
    
    async def schedule_post(self, content: "UniversalContent", 
                           scheduled_at: datetime) -> PublishResult:
        """Schedule post for future. Default raises UnsupportedCapabilityError."""
        raise UnsupportedCapabilityError(f"{self.PLATFORM_ID} does not support scheduling")
    
    async def update_post(self, platform_post_id: str, 
                         content: "UniversalContent") -> PublishResult:
        """Update existing post. Default raises UnsupportedCapabilityError."""
        raise UnsupportedCapabilityError(f"{self.PLATFORM_ID} does not support post updates")
    
    async def delete_post(self, platform_post_id: str) -> bool:
        """Delete post. Default raises UnsupportedCapabilityError."""
        raise UnsupportedCapabilityError(f"{self.PLATFORM_ID} does not support post deletion")
    
    # === CONTENT FETCHING ===
    
    @abstractmethod
    async def fetch_posts(self, account_id: str, 
                         since: Optional[datetime] = None,
                         limit: int = 50) -> AsyncIterator[NormalizedPost]:
        """Fetch posts from platform."""
        pass
    
    @abstractmethod
    async def fetch_comments(self, platform_post_id: str,
                            since: Optional[datetime] = None,
                            limit: int = 100) -> AsyncIterator[NormalizedComment]:
        """Fetch comments for a post."""
        pass
    
    async def fetch_replies(self, platform_comment_id: str,
                           limit: int = 50) -> AsyncIterator[NormalizedComment]:
        """Fetch replies to a comment. Default raises UnsupportedCapabilityError."""
        raise UnsupportedCapabilityError(f"{self.PLATFORM_ID} does not support reply fetching")
    
    # === ENGAGEMENT ===
    
    async def reply_to_comment(self, platform_comment_id: str, 
                              reply_text: str) -> PublishResult:
        """Reply to a comment. Default raises UnsupportedCapabilityError."""
        raise UnsupportedCapabilityError(f"{self.PLATFORM_ID} does not support replies")
    
    # === ANALYTICS ===
    
    @abstractmethod
    async def fetch_account_metrics(self, account_id: str,
                                   since: Optional[datetime] = None,
                                   until: Optional[datetime] = None) -> NormalizedMetrics:
        """Fetch account-level metrics."""
        pass
    
    @abstractmethod
    async def fetch_post_analytics(self, platform_post_id: str) -> NormalizedMetrics:
        """Fetch post-level analytics."""
        pass
    
    async def fetch_audience_metrics(self, account_id: str) -> Dict:
        """Fetch audience demographics. Default returns empty."""
        return {}
    
    # === WEBHOOKS ===
    
    @abstractmethod
    async def register_webhook(self, callback_url: str, events: List[str]) -> bool:
        """Register webhook with platform. Default raises UnsupportedCapabilityError."""
        raise UnsupportedCapabilityError(f"{self.PLATFORM_ID} does not support webhooks")
    
    @abstractmethod
    async def handle_webhook(self, payload: Dict, headers: Dict) -> List["AISMEvent"]:
        """Normalize webhook payload to internal events."""
        pass
    
    # === UTILITY ===
    
    @abstractmethod
    def get_rate_limit_status(self) -> Dict:
        """Return current rate limit status."""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """Return connected account info (username, followers, etc.)."""
        pass
```

---

## 2. Capability System

### Dynamic Capability Declaration

```python
class PlatformCapabilities:
    """Runtime capability checker."""
    
    def __init__(self, adapter: BasePlatformAdapter):
        self.adapter = adapter
    
    def supports(self, capability: PlatformCapability) -> bool:
        return capability in self.adapter.get_capabilities()
    
    def get_publishing_options(self) -> Dict[str, bool]:
        return {
            "immediate": self.supports(PlatformCapability.PUBLISHING),
            "scheduled": self.supports(PlatformCapability.SCHEDULING),
            "text": self.supports(PlatformCapability.TEXT_POST),
            "image": self.supports(PlatformCapability.IMAGE_POST),
            "video": self.supports(PlatformCapability.VIDEO_POST),
            "carousel": self.supports(PlatformCapability.CAROUSEL_POST),
            "stories": self.supports(PlatformCapability.STORIES),
            "short_video": self.supports(PlatformCapability.SHORT_VIDEO),
        }
    
    def get_engagement_options(self) -> Dict[str, bool]:
        return {
            "comments": self.supports(PlatformCapability.COMMENTS),
            "replies": self.supports(PlatformCapability.REPLIES),
            "direct_messages": self.supports(PlatformCapability.DIRECT_MESSAGES),
        }
    
    def get_analytics_options(self) -> Dict[str, bool]:
        return {
            "account": self.supports(PlatformCapability.ANALYTICS),
            "audience": self.supports(PlatformCapability.AUDIENCE_METRICS),
            "post": self.supports(PlatformCapability.POST_ANALYTICS),
            "engagement": self.supports(PlatformCapability.ENGAGEMENT_METRICS),
        }
```

### Frontend Integration

The frontend queries `/api/v1/platforms/{platform}/capabilities` and receives:

```json
{
  "platform": "instagram",
  "publishing": {
    "immediate": true,
    "scheduled": true,
    "text": true,
    "image": true,
    "video": true,
    "carousel": true,
    "stories": true,
    "short_video": true
  },
  "engagement": {
    "comments": true,
    "replies": true,
    "direct_messages": true
  },
  "analytics": {
    "account": true,
    "audience": true,
    "post": true,
    "engagement": true
  },
  "events": {
    "webhooks": true
  },
  "limits": {
    "caption_max_length": 2200,
    "hashtag_max_count": 30,
    "media_max_count": 10
  }
}
```

---

## 3. Directory Structure (Platform Adapters)

```
backend/app/platforms/
├── base/
│   ├── __init__.py
│   ├── adapter.py              # BasePlatformAdapter ABC
│   ├── capabilities.py         # PlatformCapability enum, PlatformConfig
│   ├── models.py               # Data classes (NormalizedPost, etc.)
│   ├── rate_limit.py           # RateLimiter class
│   ├── errors.py               # Platform-specific exceptions
│   └── normalizer.py           # Base normalization logic
│
├── instagram/
│   ├── __init__.py
│   ├── adapter.py              # InstagramAdapter
│   ├── auth.py                 # OAuth2 flow
│   ├── publisher.py            # Publishing logic
│   ├── analytics.py            # Insights API
│   ├── comments.py             # Comment handling
│   ├── webhooks.py             # Webhook verification
│   ├── mapper.py               # UniversalContent → Instagram payload
│   ├── normalizer.py           # Instagram API → NormalizedPost
│   └── config.yaml             # Platform-specific config
│
├── facebook/
│   ├── __init__.py
│   ├── adapter.py
│   ├── auth.py
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── webhooks.py
│   ├── mapper.py
│   ├── normalizer.py
│   └── config.yaml
│
├── x/                          # X (Twitter)
│   ├── __init__.py
│   ├── adapter.py
│   ├── auth.py
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── webhooks.py
│   ├── mapper.py
│   ├── normalizer.py
│   └── config.yaml
│
├── linkedin/
│   ├── __init__.py
│   ├── adapter.py
│   ├── auth.py
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── mapper.py
│   ├── normalizer.py
│   └── config.yaml
│
├── youtube/
│   ├── __init__.py
│   ├── adapter.py
│   ├── auth.py
│   ├── publisher.py
│   ├── analytics.py
│   ├── comments.py
│   ├── webhooks.py
│   ├── mapper.py
│   ├── normalizer.py
│   └── config.yaml
│
└── mock/
    ├── __init__.py
    ├── adapter.py              # MockPlatformAdapter for testing
    ├── publisher.py
    ├── analytics.py
    ├── comments.py
    └── normalizer.py
```

---

## 4. Content Normalization (Mapper)

### Universal Content Model

```python
@dataclass
class UniversalContent:
    text: str
    caption: Optional[str] = None
    title: Optional[str] = None  # For YouTube, LinkedIn articles
    media: List["UniversalMedia"] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    location: Optional[str] = None
    language: str = "en"
    content_type: str = "post"  # post, story, reel, short, article
    metadata: Dict = field(default_factory=dict)

@dataclass
class UniversalMedia:
    type: str  # image, video, carousel_item, document
    data: bytes = None
    url: str = None
    filename: str = None
    mime_type: str = None
    alt_text: str = None
    duration_seconds: float = None
    width: int = None
    height: int = None
```

### Mapper Interface

```python
class ContentMapper(ABC):
    """Maps UniversalContent to PlatformSpecificPayload."""
    
    @abstractmethod
    def to_platform_payload(self, content: UniversalContent) -> Dict:
        """Convert to platform-specific API payload."""
        pass
    
    @abstractmethod
    def from_platform_response(self, response: Dict) -> NormalizedPost:
        """Convert platform response to normalized post."""
        pass
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        return re.findall(r'#(\w+)', text)
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        return re.findall(r'@(\w+)', text)
    
    def sanitize_text(self, text: str, max_length: int) -> str:
        """Truncate text to platform limit."""
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text
```

### Instagram Mapper Example

```python
class InstagramMapper(ContentMapper):
    def to_platform_payload(self, content: UniversalContent) -> Dict:
        payload = {
            "caption": content.caption or content.text,
        }
        
        # Handle media
        if len(content.media) == 1:
            media = content.media[0]
            if media.type == "image":
                payload["image_url"] = media.url
            elif media.type == "video":
                payload["video_url"] = media.url
                if media.duration_seconds:
                    payload["media_type"] = "VIDEO"
        elif len(content.media) > 1:
            payload["media_type"] = "CAROUSEL"
            payload["children"] = [
                {"image_url": m.url} if m.type == "image" 
                else {"video_url": m.url} 
                for m in content.media
            ]
        
        # Location
        if content.location:
            payload["location_id"] = self._resolve_location(content.location)
        
        # Hashtags are in caption
        return payload
    
    def from_platform_response(self, response: Dict) -> NormalizedPost:
        return NormalizedPost(
            id=response["id"],
            platform="instagram",
            platform_post_id=response["id"],
            content=response.get("caption", ""),
            caption=response.get("caption"),
            media=[{"type": m["media_type"], "url": m.get("media_url")} 
                   for m in response.get("media", [])],
            hashtags=self.extract_hashtags(response.get("caption", "")),
            mentions=self.extract_mentions(response.get("caption", "")),
            location=response.get("location", {}).get("name"),
            published_at=parse_datetime(response["timestamp"]),
            engagement={
                "likes": response.get("like_count", 0),
                "comments": response.get("comments_count", 0),
                "shares": response.get("share_count", 0),
                "saves": response.get("saved_count", 0),
            },
            raw_data=response
        )
```

---

## 5. Error Translation

### Platform Error Hierarchy

```python
class PlatformError(Exception):
    """Base exception for all platform errors."""
    def __init__(self, message: str, platform: str, original_error: Exception = None):
        self.platform = platform
        self.original_error = original_error
        super().__init__(message)

class AuthenticationError(PlatformError):
    """Authentication/authorization failure."""
    pass

class TokenExpiredError(AuthenticationError):
    """Access token has expired."""
    pass

class RateLimitError(PlatformError):
    """Platform rate limit exceeded."""
    def __init__(self, message: str, platform: str, 
                 retry_after: int = None, original_error: Exception = None):
        self.retry_after = retry_after
        super().__init__(message, platform, original_error)

class ValidationError(PlatformError):
    """Content validation failed."""
    def __init__(self, message: str, platform: str, 
                 field_errors: Dict[str, str] = None, original_error: Exception = None):
        self.field_errors = field_errors or {}
        super().__init__(message, platform, original_error)

class PublishingError(PlatformError):
    """Post publishing failed."""
    pass

class MediaUploadError(PlatformError):
    """Media upload failed."""
    pass

class AnalyticsError(PlatformError):
    """Analytics fetch failed."""
    pass

class UnsupportedCapabilityError(PlatformError):
    """Platform doesn't support requested capability."""
    pass

class PlatformUnavailableError(PlatformError):
    """Platform API is down/unreachable."""
    pass
```

### Translation in Adapters

```python
class InstagramAdapter(BasePlatformAdapter):
    async def publish_post(self, content: UniversalContent) -> PublishResult:
        try:
            payload = self.mapper.to_platform_payload(content)
            response = await self._api_post("/media_publish", payload)
            return PublishResult(
                success=True,
                platform_post_id=response["id"],
                platform_url=f"https://instagram.com/p/{response['id']}",
                raw_response=response
            )
        except InstagramAPIError as e:
            if e.code == "RATE_LIMIT":
                raise RateLimitError("Instagram rate limit", "instagram", 
                                    retry_after=e.retry_after, original_error=e)
            elif e.code == "TOKEN_EXPIRED":
                raise TokenExpiredError("Instagram token expired", "instagram", original_error=e)
            elif e.code == "VALIDATION":
                raise ValidationError("Content validation failed", "instagram",
                                     field_errors=e.field_errors, original_error=e)
            else:
                raise PublishingError(f"Instagram publish failed: {e}", "instagram", original_error=e)
```

---

## 6. Rate Limit Management

### Rate Limiter Implementation

```python
import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional

@dataclass
class RateLimitConfig:
    requests_per_window: int
    window_seconds: int
    retry_policy: str = "exponential"
    max_retries: int = 3
    backoff_base: float = 1.0

class RateLimiter:
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._requests = deque()  # timestamps
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        async with self._lock:
            now = time.time()
            # Remove old requests outside window
            while self._requests and self._requests[0] < now - self.config.window_seconds:
                self._requests.popleft()
            
            if len(self._requests) >= self.config.requests_per_window:
                # Wait until oldest request expires
                wait_time = self._requests[0] + self.config.window_seconds - now
                await asyncio.sleep(wait_time)
                return await self.acquire()
            
            self._requests.append(now)
    
    def get_status(self) -> Dict:
        now = time.time()
        valid_requests = [r for r in self._requests if r > now - self.config.window_seconds]
        return {
            "used": len(valid_requests),
            "limit": self.config.requests_per_window,
            "remaining": max(0, self.config.requests_per_window - len(valid_requests)),
            "reset_at": (self._requests[0] + self.config.window_seconds) if self._requests else None
        }

# Usage in adapter
async def _api_request(self, method: str, path: str, **kwargs):
    await self._rate_limiter.acquire()
    
    for attempt in range(self.config.rate_limit.max_retries + 1):
        try:
            response = await self._http_client.request(method, path, **kwargs)
            return response
        except RateLimitError as e:
            if attempt == self.config.rate_limit.max_retries:
                raise
            wait = self._calculate_backoff(attempt, e.retry_after)
            await asyncio.sleep(wait)
        except Exception:
            if attempt == self.config.rate_limit.max_retries:
                raise
            wait = self._calculate_backoff(attempt)
            await asyncio.sleep(wait)
    
    def _calculate_backoff(self, attempt: int, retry_after: int = None) -> float:
        if retry_after:
            return retry_after
        if self.config.retry_policy == "exponential":
            return self.config.backoff_base * (2 ** attempt)
        elif self.config.retry_policy == "linear":
            return self.config.backoff_base * (attempt + 1)
        return self.config.backoff_base
```

---

## 7. Platform Registry

### Registry Implementation

```python
from typing import Dict, Type, Optional
from importlib import import_module
import pkgutil

class PlatformRegistry:
    """Central platform adapter registry."""
    
    def __init__(self):
        self._adapters: Dict[str, Type[BasePlatformAdapter]] = {}
        self._configs: Dict[str, PlatformConfig] = {}
        self._instances: Dict[str, BasePlatformAdapter] = {}
    
    def register(self, platform_id: str, adapter_class: Type[BasePlatformAdapter],
                 config: PlatformConfig) -> None:
        """Register a platform adapter."""
        self._adapters[platform_id] = adapter_class
        self._configs[platform_id] = config
    
    def get_adapter_class(self, platform_id: str) -> Optional[Type[BasePlatformAdapter]]:
        return self._adapters.get(platform_id)
    
    def get_config(self, platform_id: str) -> Optional[PlatformConfig]:
        return self._configs.get(platform_id)
    
    def get_adapter(self, platform_id: str, credentials: Dict = None) -> BasePlatformAdapter:
        """Get or create adapter instance."""
        if platform_id not in self._instances:
            adapter_class = self._adapters.get(platform_id)
            config = self._configs.get(platform_id)
            if not adapter_class or not config:
                raise ValueError(f"Platform {platform_id} not registered")
            self._instances[platform_id] = adapter_class(config, credentials)
        elif credentials:
            self._instances[platform_id].credentials = credentials
        return self._instances[platform_id]
    
    def list_platforms(self) -> List[Dict]:
        """List all registered platforms with metadata."""
        return [
            {
                "id": pid,
                "name": config.display_name,
                "capabilities": [c.value for c in config.capabilities],
                "limits": config.limits,
                "status": "connected" if pid in self._instances else "disconnected"
            }
            for pid, config in self._configs.items()
        ]
    
    def discover_plugins(self, package: str = "app.platforms") -> None:
        """Auto-discover platform adapters."""
        for _, name, _ in pkgutil.iter_modules([package.replace(".", "/")]):
            if name == "base":
                continue
            try:
                module = import_module(f"{package}.{name}.adapter")
                # Find adapter class in module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlatformAdapter) and 
                        attr is not BasePlatformAdapter):
                        # Create config from platform module
                        config_module = import_module(f"{package}.{name}.config")
                        config = config_module.PLATFORM_CONFIG
                        self.register(name, attr, config)
            except ImportError:
                pass  # Adapter not yet implemented
```

### Auto-Registration Pattern

Each platform adapter's `__init__.py`:

```python
# backend/app/platforms/instagram/__init__.py
from .adapter import InstagramAdapter
from .config import PLATFORM_CONFIG

# Register on import
from ..registry import platform_registry
platform_registry.register("instagram", InstagramAdapter, PLATFORM_CONFIG)
```

---

## 8. Mock Platform Adapter (Testing)

```python
# backend/app/platforms/mock/adapter.py

class MockPlatformAdapter(BasePlatformAdapter):
    """Mock adapter for testing without external APIs."""
    
    PLATFORM_ID = "mock"
    PLATFORM_NAME = "Mock Platform"
    
    def __init__(self, config: PlatformConfig, credentials: Dict = None):
        super().__init__(config, credentials)
        self._posts = {}
        self._comments = {}
        self._metrics = {}
        self._connected = False
    
    def get_capabilities(self) -> List[PlatformCapability]:
        return list(PlatformCapability)  # Supports everything
    
    async def authenticate(self, auth_code: str = None) -> AuthenticationResult:
        self._connected = True
        return AuthenticationResult(
            success=True,
            access_token="mock_access_token",
            refresh_token="mock_refresh_token",
            expires_in=3600
        )
    
    async def refresh_tokens(self) -> AuthenticationResult:
        return AuthenticationResult(success=True, access_token="new_mock_token")
    
    async def validate_credentials(self) -> bool:
        return self._connected
    
    async def disconnect(self) -> bool:
        self._connected = False
        return True
    
    async def validate_content(self, content: UniversalContent) -> ValidationResult:
        return ValidationResult(valid=True)
    
    async def upload_media(self, media: UniversalMedia) -> MediaUploadResult:
        return MediaUploadResult(success=True, media_id="mock_media_123")
    
    async def publish_post(self, content: UniversalContent) -> PublishResult:
        post_id = f"mock_post_{len(self._posts) + 1}"
        self._posts[post_id] = content
        return PublishResult(success=True, platform_post_id=post_id)
    
    async def fetch_posts(self, account_id: str, since=None, limit=50):
        for post in list(self._posts.values())[:limit]:
            yield NormalizedPost(
                id=post_id,
                platform="mock",
                platform_post_id=post_id,
                content=content.text,
                caption=content.caption,
                media=content.media,
                hashtags=content.hashtags,
                mentions=content.mentions,
                published_at=datetime.utcnow(),
                engagement={"likes": 10, "comments": 2, "shares": 1},
                raw_data={}
            )
    
    async def fetch_comments(self, platform_post_id: str, since=None, limit=100):
        for i in range(5):
            yield NormalizedComment(
                id=f"mock_comment_{i}",
                platform="mock",
                platform_comment_id=f"mock_comment_{i}",
                post_id=platform_post_id,
                author={"username": f"user_{i}"},
                content=f"Comment {i}",
                created_at=datetime.utcnow(),
                raw_data={}
            )
    
    async def fetch_account_metrics(self, account_id: str, since=None, until=None):
        return NormalizedMetrics(
            post_id="account",
            platform="mock",
            metrics={"followers": 1000, "posts": 50, "engagement_rate": 0.05},
            original_metrics={},
            timestamp=datetime.utcnow()
        )
    
    async def fetch_post_analytics(self, platform_post_id: str):
        return NormalizedMetrics(
            post_id=platform_post_id,
            platform="mock",
            metrics={"likes": 10, "comments": 2, "shares": 1, "saves": 3},
            original_metrics={},
            timestamp=datetime.utcnow()
        )
    
    async def handle_webhook(self, payload: Dict, headers: Dict) -> List[AISMEvent]:
        return []
    
    def get_rate_limit_status(self) -> Dict:
        return {"used": 0, "limit": 1000, "remaining": 1000}
    
    def get_account_info(self) -> Dict:
        return {"username": "mock_user", "followers": 1000}
```

---

## 9. New Platform Onboarding Checklist

| Step | Task | Deliverable |
|------|------|-------------|
| 1 | Research official API | API docs URL, version |
| 2 | Identify capabilities | Capability matrix |
| 3 | Implement auth | OAuth2/OAuth1 flow |
| 4 | Implement publisher | Content mapping, media upload |
| 5 | Implement analytics | Metrics mapping |
| 6 | Implement comments | Fetch, reply |
| 7 | Implement webhooks | If supported |
| 8 | Create config.yaml | Limits, capabilities, rate limits |
| 9 | Write unit tests | Adapter, mapper, normalizer |
| 10 | Write integration tests | End-to-end flow |
| 11 | Register in registry | Auto-discovery |
| 12 | Update frontend | No changes needed (dynamic) |

---

## 10. Decision Records

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-011 | Single abstract base adapter | Enforces contract, enables polymorphism |
| ADR-012 | Capability enum + dynamic discovery | Frontend adapts automatically |
| ADR-013 | UniversalContent as internal format | Single source of truth for content |
| ADR-014 | Mapper per platform (not in base) | Platform-specific logic isolated |
| ADR-015 | Error translation in adapters | Core sees normalized errors only |
| ADR-016 | Rate limiter per adapter instance | Platform-specific limits respected |
| ADR-017 | Mock adapter for testing | Full testability without APIs |
| ADR-018 | Registry auto-discovers plugins | Zero-config platform addition |

---

**Status:** DESIGN — AWAITING APPROVAL  
**Next:** Upon approval, proceed to Phase 3 (Core Foundation) implementation.