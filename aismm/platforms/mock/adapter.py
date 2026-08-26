"""
Mock Platform Adapter

Simulates a social media platform for testing without external API dependencies.
Configurable to simulate: publishing, comments, analytics, errors, rate limits,
authentication, unsupported features, and webhook events.
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from ..base.adapter import BasePlatformAdapter
from ..base.capabilities import PlatformCapabilities, Capability, PlatformLimits, RateLimitConfig
from ..base.models import (
    UniversalContent,
    PlatformSpecificPayload,
    NormalizedPost,
    NormalizedComment,
    NormalizedEngagement,
    NormalizedAccountMetrics,
    NormalizedPostAnalytics,
    MediaItem,
    ValidationResult,
    PublishResult,
    ScheduleResult,
    MediaUploadResult,
    ReplyResult,
    WebhookRegistration,
    AuthResult,
)
from ..base.errors import (
    PlatformError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    PublishingError,
    UnsupportedCapabilityError,
)


@dataclass
class MockConfig:
    """Configuration for mock adapter behavior."""
    # Success/failure simulation
    simulate_error: bool = False
    simulate_rate_limit: bool = False
    simulate_auth_failure: bool = False
    
    # Error probabilities
    error_probability: float = 0.0
    rate_limit_probability: float = 0.0
    
    # Delays
    request_delay_ms: int = 0
    
    # Capabilities override
    custom_capabilities: Dict[Capability, bool] = field(default_factory=dict)
    custom_limits: Dict[str, int] = field(default_factory=dict)
    
    # Data
    mock_accounts: List[Dict] = field(default_factory=list)
    mock_posts: List[Dict] = field(default_factory=list)
    mock_comments: Dict[str, List[Dict]] = field(default_factory=dict)  # publication_id -> comments
    mock_metrics: Dict[str, Dict] = field(default_factory=dict)  # publication_id -> metrics


class MockPlatformAdapter(BasePlatformAdapter):
    """
    Mock platform adapter for testing.
    
    Simulates all platform operations without external API calls.
    Fully configurable to test success, error, and edge cases.
    """
    
    PLATFORM_NAME = "Mock Platform"
    PLATFORM_DESCRIPTION = "Mock adapter for testing"
    PLATFORM_VERSION = "1.0.0"
    
    def __init__(
        self, 
        account_id: Optional[str] = None, 
        credentials: Optional[Dict] = None,
        config: Optional[MockConfig] = None
    ):
        super().__init__(account_id, credentials)
        self.config = config or MockConfig()
        self._posts: List[Dict] = []
        self._comments: Dict[str, List[Dict]] = {}
        self._schedules: Dict[str, Dict] = {}
        self._webhooks: List[Dict] = []
        self._authenticated = False
        self._tokens = {"access": "mock_access_token", "refresh": "mock_refresh_token"}
        self._request_count = 0
        self._rate_limit_window_start = datetime.utcnow()
    
    @property
    def platform_id(self) -> str:
        return "mock"
    
    def get_capabilities(self) -> PlatformCapabilities:
        """Return mock capabilities (configurable)."""
        if self._capabilities is None:
            # Default capabilities - all true for testing
            capabilities = {cap: True for cap in Capability}
            
            # Override with custom capabilities
            capabilities.update(self.config.custom_capabilities)
            
            limits = PlatformLimits(**{
                "text_length": 2000,
                "hashtag_count": 20,
                "media_count": 5,
                "video_duration_seconds": 300,
                **self.config.custom_limits
            })
            
            rate_limits = RateLimitConfig(
                requests_per_window=1000,
                window_seconds=60,
                burst=100,
            )
            
            self._capabilities = PlatformCapabilities(
                platform_id=self.platform_id,
                capabilities=capabilities,
                limits=limits,
                rate_limits=rate_limits
            )
        return self._capabilities
    
    # ── Authentication ───────────────────────────────────────────────
    
    async def authenticate(self, credentials: Dict) -> AuthResult:
        await self._simulate_delay()
        self._check_rate_limit()
        
        if self.config.simulate_auth_failure:
            return AuthResult(
                success=False,
                error="Simulated authentication failure",
                platform_account_id=None
            )
        
        self._authenticated = True
        platform_account_id = credentials.get("platform_account_id", f"mock_user_{uuid.uuid4().hex[:8]}")
        
        return AuthResult(
            success=True,
            access_token=self._tokens["access"],
            refresh_token=self._tokens["refresh"],
            expires_in=3600,
            scope="mock_scope",
            platform_account_id=platform_account_id,
            account_username=credentials.get("username", "mock_user"),
            account_name=credentials.get("name", "Mock User"),
        )
    
    async def refresh_token(self) -> AuthResult:
        await self._simulate_delay()
        
        if not self._authenticated:
            raise AuthenticationError("Not authenticated", platform=self.platform_id)
        
        if self.config.simulate_auth_failure:
            return AuthResult(success=False, error="Simulated token refresh failure")
        
        return AuthResult(
            success=True,
            access_token=f"mock_access_token_{uuid.uuid4().hex[:8]}",
            refresh_token=self._tokens["refresh"],
            expires_in=3600,
            scope="mock_scope",
        )
    
    async def disconnect(self) -> bool:
        await self._simulate_delay()
        self._authenticated = False
        self._tokens = {"access": "mock_access_token", "refresh": "mock_refresh_token"}
        return True
    
    async def validate_credentials(self) -> bool:
        await self._simulate_delay()
        return self._authenticated and not self.config.simulate_auth_failure
    
    # ── Publishing ───────────────────────────────────────────────────
    
    async def validate_content(self, content: UniversalContent) -> ValidationResult:
        await self._simulate_delay()
        self._check_rate_limit()
        
        errors = []
        warnings = []
        
        # Check text length
        caps = self.get_capabilities()
        max_text = caps.get_limit("text_length") or 2000
        text = content.caption or content.text
        if len(text) > max_text:
            errors.append(f"Text exceeds maximum length of {max_text} characters")
        
        # Check hashtag count
        max_tags = caps.get_limit("hashtag_count") or 20
        if len(content.hashtags) > max_tags:
            errors.append(f"Too many hashtags (max {max_tags})")
        
        # Check media count
        max_media = caps.get_limit("media_count") or 5
        if len(content.media) > max_media:
            errors.append(f"Too many media items (max {max_media})")
        
        # Check unsupported content types
        if content.content_type == ContentType.STORY and not caps.supports("stories"):
            errors.append("Stories not supported on this platform")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            platform_adjustments={"text_length_limit": max_text, "hashtag_limit": max_tags}
        )
    
    async def upload_media(self, media: MediaItem) -> MediaUploadResult:
        await self._simulate_delay()
        self._check_rate_limit()
        self._maybe_fail()
        
        if self.config.simulate_error:
            return MediaUploadResult(
                success=False,
                error="Simulated media upload failure"
            )
        
        media_id = f"mock_media_{uuid.uuid4().hex[:12]}"
        media.platform_media_ids[self.platform_id] = media_id
        
        return MediaUploadResult(
            success=True,
            platform_media_id=media_id,
            media_url=f"https://mock-platform.com/media/{media_id}",
        )
    
    async def publish_post(self, payload: PlatformSpecificPayload) -> PublishResult:
        await self._simulate_delay()
        self._check_rate_limit()
        self._maybe_fail()
        
        if self.config.simulate_error:
            return PublishResult(
                success=False,
                error="Simulated publishing failure"
            )
        
        post_id = f"mock_post_{uuid.uuid4().hex[:12]}"
        post_data = {
            "id": post_id,
            "platform_id": self.platform_id,
            "text": payload.text,
            "media_ids": payload.media_ids,
            "published_at": datetime.utcnow().isoformat(),
            "platform_payload": payload.to_dict(),
        }
        self._posts.append(post_data)
        
        return PublishResult(
            success=True,
            platform_post_id=post_id,
            platform_url=f"https://mock-platform.com/post/{post_id}",
            platform_response=post_data,
        )
    
    async def schedule_post(self, payload: PlatformSpecificPayload,
                           scheduled_at: datetime) -> ScheduleResult:
        await self._simulate_delay()
        self._check_rate_limit()
        self._maybe_fail()
        
        if not self.get_capabilities().supports("scheduling"):
            raise UnsupportedCapabilityError("scheduling", self.platform_id)
        
        if self.config.simulate_error:
            return ScheduleResult(
                success=False,
                error="Simulated scheduling failure"
            )
        
        schedule_id = f"mock_schedule_{uuid.uuid4().hex[:12]}"
        schedule_data = {
            "id": schedule_id,
            "platform_id": self.platform_id,
            "text": payload.text,
            "media_ids": payload.media_ids,
            "scheduled_at": scheduled_at.isoformat(),
            "status": "pending",
            "platform_payload": payload.to_dict(),
        }
        self._schedules[schedule_id] = schedule_data
        
        return ScheduleResult(
            success=True,
            platform_schedule_id=schedule_id,
            scheduled_at=scheduled_at,
            platform_response=schedule_data,
        )
    
    async def update_post(self, publication_id: str, payload: PlatformSpecificPayload) -> bool:
        await self._simulate_delay()
        self._check_rate_limit()
        
        for post in self._posts:
            if post["id"] == publication_id:
                post["text"] = payload.text
                post["media_ids"] = payload.media_ids
                post["platform_payload"] = payload.to_dict()
                return True
        return False
    
    async def delete_post(self, publication_id: str) -> bool:
        await self._simulate_delay()
        self._check_rate_limit()
        
        self._posts = [p for p in self._posts if p["id"] != publication_id]
        return True
    
    # ── Content Fetching ─────────────────────────────────────────────
    
    async def fetch_posts(self, account_id: str, limit: int = 50) -> List[NormalizedPost]:
        await self._simulate_delay()
        self._check_rate_limit()
        
        # Return mock posts
        posts = []
        for post_data in self._posts[-limit:]:
            posts.append(NormalizedPost(
                platform_post_id=post_data["id"],
                platform_id=self.platform_id,
                content=post_data["text"],
                caption=post_data["text"],
                media_type=MediaType.IMAGE if post_data["media_ids"] else None,
                posted_at=datetime.fromisoformat(post_data["published_at"]),
                engagement={"like": random.randint(0, 100), "comment": random.randint(0, 20)},
                engagement_score=random.uniform(0, 10),
            ))
        return posts
    
    async def fetch_comments(self, publication_id: str) -> List[NormalizedComment]:
        await self._simulate_delay()
        self._check_rate_limit()
        
        comments = self._comments.get(publication_id, [])
        result = []
        for c in comments:
            result.append(NormalizedComment(
                platform_comment_id=c["id"],
                platform_id=self.platform_id,
                publication_id=publication_id,
                author_username=c.get("author", "mock_user"),
                author_id=c.get("author_id", "mock_author"),
                author_avatar_url=None,
                text=c["text"],
                sentiment_score=c.get("sentiment", random.uniform(-1, 1)),
                sentiment_label=c.get("sentiment_label", "neutral"),
                like_count=c.get("likes", 0),
                reply_count=0,
                is_reply=False,
                platform_created_at=datetime.fromisoformat(c["created_at"]),
            ))
        return result
    
    async def fetch_replies(self, comment_id: str) -> List[NormalizedComment]:
        await self._simulate_delay()
        # Find comment and return its replies (mock: empty)
        return []
    
    # ── Engagement ───────────────────────────────────────────────────
    
    async def reply_to_comment(self, comment_id: str, text: str) -> ReplyResult:
        await self._simulate_delay()
        self._check_rate_limit()
        self._maybe_fail()
        
        if self.config.simulate_error:
            return ReplyResult(success=False, error="Simulated reply failure")
        
        reply_id = f"mock_reply_{uuid.uuid4().hex[:12]}"
        return ReplyResult(
            success=True,
            platform_reply_id=reply_id,
            platform_response={"id": reply_id, "text": text},
        )
    
    async def fetch_engagement(self, publication_id: str) -> NormalizedEngagement:
        await self._simulate_delay()
        self._check_rate_limit()
        
        metrics = self._mock_metrics.get(publication_id, {})
        
        return NormalizedEngagement(
            metric_type=MetricType.LIKE,
            value=metrics.get("likes", random.randint(10, 500)),
            source_platform=self.platform_id,
            original_metric="like_count",
        )
    
    async def fetch_account_metrics(self, account_id: str) -> NormalizedAccountMetrics:
        await self._simulate_delay()
        self._check_rate_limit()
        
        return NormalizedAccountMetrics(
            platform_id=self.platform_id,
            platform_account_id=account_id,
            followers=random.randint(1000, 100000),
            following=random.randint(100, 5000),
            posts_count=len(self._posts),
            total_engagement=random.randint(500, 10000),
            avg_engagement_rate=random.uniform(1.0, 10.0),
        )
    
    async def fetch_post_analytics(self, publication_id: str) -> NormalizedPostAnalytics:
        await self._simulate_delay()
        self._check_rate_limit()
        
        return NormalizedPostAnalytics(
            platform_post_id=publication_id,
            platform_id=self.platform_id,
            impressions=random.randint(1000, 50000),
            reach=random.randint(500, 30000),
            engagement={"like": random.randint(10, 500), "comment": random.randint(5, 50)},
            video_views=random.randint(0, 10000),
            video_watch_time_seconds=random.randint(0, 50000),
        )
    
    # ── Webhooks ─────────────────────────────────────────────────────
    
    async def register_webhook(self, url: str, events: List[str]) -> WebhookRegistration:
        await self._simulate_delay()
        
        webhook_id = f"mock_webhook_{uuid.uuid4().hex[:12]}"
        webhook = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._webhooks.append(webhook)
        
        return WebhookRegistration(
            success=True,
            webhook_id=webhook_id,
            webhook_url=url,
            events=events,
            expires_at=datetime.utcnow() + timedelta(days=365),
        )
    
    async def handle_webhook(self, payload: Dict, signature: str) -> List[Dict]:
        await self._simulate_delay()
        
        # Normalize webhook payload to internal events
        events = []
        event_type = payload.get("event_type", "unknown")
        
        events.append({
            "event_type": event_type,
            "platform": self.platform_id,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return events
    
    # ── Helper Methods ───────────────────────────────────────────────
    
    async def _simulate_delay(self):
        if self.config.request_delay_ms > 0:
            await asyncio.sleep(self.config.request_delay_ms / 1000)
    
    def _check_rate_limit(self):
        self._request_count += 1
        window = self.get_capabilities().rate_limits.window_seconds
        
        if (datetime.utcnow() - self._rate_limit_window_start).seconds > window:
            self._request_count = 0
            self._rate_limit_window_start = datetime.utcnow()
        
        if self._request_count > self.get_capabilities().rate_limits.requests_per_window:
            if self.config.simulate_rate_limit:
                raise RateLimitError("Rate limit exceeded", platform=self.platform_id, retry_after=60)
    
    def _maybe_fail(self):
        if self.config.error_probability > 0 and random.random() < self.config.error_probability:
            raise PublishingError("Simulated random failure", platform=self.platform_id)
    
    # ── Test Utilities ───────────────────────────────────────────────
    
    def add_mock_comment(self, publication_id: str, text: str, 
                         author: str = "mock_user", sentiment: float = 0.0):
        """Add a mock comment for testing."""
        if publication_id not in self._comments:
            self._comments[publication_id] = []
        
        self._comments[publication_id].append({
            "id": f"mock_comment_{uuid.uuid4().hex[:8]}",
            "text": text,
            "author": author,
            "author_id": f"author_{uuid.uuid4().hex[:8]}",
            "sentiment": sentiment,
            "sentiment_label": self._sentiment_label(sentiment),
            "likes": random.randint(0, 10),
            "created_at": datetime.utcnow().isoformat(),
        })
    
    def add_mock_post(self, text: str, media_ids: List[str] = None):
        """Add a mock post for testing."""
        post_id = f"mock_post_{uuid.uuid4().hex[:12]}"
        self._posts.append({
            "id": post_id,
            "text": text,
            "media_ids": media_ids or [],
            "published_at": datetime.utcnow().isoformat(),
        })
        return post_id
    
    def set_mock_metrics(self, publication_id: str, metrics: Dict):
        """Set mock metrics for a publication."""
        self._mock_metrics[publication_id] = metrics
    
    @property
    def _mock_metrics(self) -> Dict:
        if not hasattr(self, '_mock_metrics_store'):
            self._mock_metrics_store = {}
        return self._mock_metrics_store
    
    def _sentiment_label(self, score: float) -> str:
        if score >= 0.5:
            return "very_positive"
        elif score >= 0.05:
            return "positive"
        elif score > -0.05:
            return "neutral"
        elif score > -0.5:
            return "negative"
        else:
            return "very_negative"
    
    def get_posts(self) -> List[Dict]:
        """Get all mock posts (for testing)."""
        return self._posts.copy()
    
    def get_schedules(self) -> Dict:
        """Get all mock schedules (for testing)."""
        return self._schedules.copy()
    
    def reset(self):
        """Reset mock state."""
        self._posts.clear()
        self._comments.clear()
        self._schedules.clear()
        self._webhooks.clear()
        self._authenticated = False
        self._request_count = 0
        self._rate_limit_window_start = datetime.utcnow()
