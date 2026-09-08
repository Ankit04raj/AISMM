"""YouTube Platform Adapter package."""

from .adapter import YouTubeAdapter
from .auth import YouTubeAuth, YouTubeAuthConfig
from .config import YouTubeConfig, YouTubeConfigPresets
from .endpoints import YouTubeEndpoint, YouTubeFields, YouTubeInsightMetric
from .publisher import YouTubePublisher, YouTubePublishResult
from .insights import YouTubeInsights
from .webhook import YouTubeWebhookHandler, YouTubeWebhookEvent, YouTubeWebhookEventType

__all__ = [
    "YouTubeAdapter",
    "YouTubeAuth",
    "YouTubeAuthConfig",
    "YouTubeConfig",
    "YouTubeConfigPresets",
    "YouTubeEndpoint",
    "YouTubeFields",
    "YouTubeInsightMetric",
    "YouTubePublisher",
    "YouTubePublishResult",
    "YouTubeInsights",
    "YouTubeWebhookHandler",
    "YouTubeWebhookEvent",
    "YouTubeWebhookEventType",
]
