"""
Base Platform Adapter

Abstract base class that all platform adapters must implement.
This is the contract between AISMM core and platform-specific implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .capabilities import PlatformCapabilities, Capability
from .models import (
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
from .errors import (
    PlatformError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    PublishingError,
    UnsupportedCapabilityError,
)


class BasePlatformAdapter(ABC):
    """
    Abstract base class for all platform adapters.
    
    Every platform integration must implement this interface.
    The AISMM core interacts ONLY with this interface.
    """
    
    # Class attributes for metadata
    PLATFORM_NAME: str = ""
    PLATFORM_DESCRIPTION: str = ""
    PLATFORM_VERSION: str = "1.0.0"
    
    def __init__(self, account_id: Optional[str] = None, credentials: Optional[Dict] = None):
        self.account_id = account_id
        self.credentials = credentials or {}
        self._capabilities: Optional[PlatformCapabilities] = None
    
    # ── Identity ──────────────────────────────────────────────────────
    
    @property
    @abstractmethod
    def platform_id(self) -> str:
        """Unique platform identifier (e.g., 'instagram', 'facebook', 'x')."""
        pass
    
    # ── Capabilities ─────────────────────────────────────────────────
    
    @abstractmethod
    def get_capabilities(self) -> PlatformCapabilities:
        """Return the complete capability set for this platform."""
        pass
    
    def supports(self, capability: str) -> bool:
        """Check if platform supports a capability."""
        caps = self.get_capabilities()
        return caps.supports(capability)
    
    def require_capability(self, capability: str) -> None:
        """Raise UnsupportedCapabilityError if not supported."""
        if not self.supports(capability):
            raise UnsupportedCapabilityError(capability, self.platform_id)
    
    # ── Authentication ───────────────────────────────────────────────
    
    @abstractmethod
    async def authenticate(self, credentials: Dict) -> AuthResult:
        """
        Authenticate with platform using provided credentials.
        Returns AuthResult with tokens on success.
        """
        pass
    
    @abstractmethod
    async def refresh_token(self) -> AuthResult:
        """Refresh access token using stored refresh token."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect/revoke tokens. Returns True on success."""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate current credentials are still valid."""
        pass
    
    # ── Publishing ───────────────────────────────────────────────────
    
    @abstractmethod
    async def validate_content(self, content: UniversalContent) -> ValidationResult:
        """
        Validate content against platform requirements.
        Returns ValidationResult with errors/warnings/adjustments.
        """
        pass
    
    @abstractmethod
    async def upload_media(self, media: MediaItem) -> MediaUploadResult:
        """
        Upload media to platform.
        Returns MediaUploadResult with platform media ID.
        """
        pass
    
    @abstractmethod
    async def publish_post(self, payload: PlatformSpecificPayload) -> PublishResult:
        """
        Publish post immediately.
        Returns PublishResult with platform post ID.
        """
        pass
    
    @abstractmethod
    async def schedule_post(self, payload: PlatformSpecificPayload,
                           scheduled_at: datetime) -> ScheduleResult:
        """
        Schedule post for future publishing.
        Returns ScheduleResult with platform schedule ID.
        """
        pass
    
    @abstractmethod
    async def update_post(self, publication_id: str,
                         payload: PlatformSpecificPayload) -> bool:
        """Update an already published post."""
        pass
    
    @abstractmethod
    async def delete_post(self, publication_id: str) -> bool:
        """Delete a published post."""
        pass
    
    # ── Content Fetching ─────────────────────────────────────────────
    
    @abstractmethod
    async def fetch_posts(self, account_id: str, limit: int = 50) -> List[NormalizedPost]:
        """Fetch recent posts for an account."""
        pass
    
    @abstractmethod
    async def fetch_comments(self, publication_id: str) -> List[NormalizedComment]:
        """Fetch comments for a publication."""
        pass
    
    @abstractmethod
    async def fetch_replies(self, comment_id: str) -> List[NormalizedComment]:
        """Fetch replies to a comment."""
        pass
    
    # ── Engagement ───────────────────────────────────────────────────
    
    @abstractmethod
    async def reply_to_comment(self, comment_id: str, text: str) -> ReplyResult:
        """Reply to a comment."""
        pass
    
    @abstractmethod
    async def fetch_engagement(self, publication_id: str) -> NormalizedEngagement:
        """Fetch engagement metrics for a publication."""
        pass
    
    @abstractmethod
    async def fetch_account_metrics(self, account_id: str) -> NormalizedAccountMetrics:
        """Fetch account-level metrics."""
        pass
    
    @abstractmethod
    async def fetch_post_analytics(self, publication_id: str) -> NormalizedPostAnalytics:
        """Fetch detailed post analytics."""
        pass
    
    # ── Webhooks / Events ────────────────────────────────────────────
    
    @abstractmethod
    async def register_webhook(self, url: str, events: List[str]) -> WebhookRegistration:
        """Register webhook endpoint for real-time events."""
        pass
    
    @abstractmethod
    async def handle_webhook(self, payload: Dict, signature: str) -> List[Dict]:
        """
        Handle incoming webhook payload.
        Returns list of normalized events.
        """
        pass
    
    # ── Utility Methods ──────────────────────────────────────────────
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Any:
        """Make HTTP request with rate limiting and error handling. To be implemented by subclasses."""
        raise NotImplementedError
    
    def _translate_error(self, error: Exception, status_code: int = None) -> PlatformError:
        """Translate platform-specific error to normalized AISMM error."""
        from .errors import translate_error
        return translate_error(self.platform_id, str(error), status_code)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(platform={self.platform_id}, account={self.account_id})>"
