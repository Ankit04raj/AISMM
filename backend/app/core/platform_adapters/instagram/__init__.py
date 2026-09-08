"""Instagram Platform Adapter - Reference Implementation."""

from .adapter import InstagramAdapter
from .auth import InstagramAuth, InstagramAuthConfig, InstagramTokenManager
from .endpoints import InstagramEndpoint, InstagramFields, InstagramMediaType, InstagramInsightMetric
from .media import InstagramMediaUploader, MediaUploadResult
from .publisher import InstagramPublisher, PublishResult
from .insights import InstagramInsights, MediaInsights, AccountInsights
from .webhook import InstagramWebhookHandler, InstagramWebhookManager, InstagramWebhookField
from .config import InstagramConfig, InstagramConfigPresets

__all__ = [
    "InstagramAdapter",
    "InstagramAuth",
    "InstagramAuthConfig",
    "InstagramTokenManager",
    "InstagramEndpoint",
    "InstagramFields",
    "InstagramMediaType",
    "InstagramInsightMetric",
    "InstagramMediaUploader",
    "MediaUploadResult",
    "InstagramPublisher",
    "PublishResult",
    "InstagramInsights",
    "MediaInsights",
    "AccountInsights",
    "InstagramWebhookHandler",
    "InstagramWebhookManager",
    "InstagramWebhookField",
    "InstagramConfig",
    "InstagramConfigPresets",
]