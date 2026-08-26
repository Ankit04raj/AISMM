"""
Platform Configuration System

Loads platform capabilities, limits, and API configuration from YAML files.
This is the single source of truth for what each platform supports.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


class Capability(str, Enum):
    """Platform capabilities - declared per platform."""
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


@dataclass
class PlatformLimits:
    """Platform-specific content limits."""
    text_length: int = 280
    hashtag_count: int = 30
    media_count: int = 4
    video_duration_seconds: int = 140
    carousel_cards: int = 10


@dataclass
class RateLimitConfig:
    """Rate limiting configuration per platform."""
    requests_per_window: int = 100
    window_seconds: int = 60
    burst: int = 10
    backoff_base: float = 1.0
    backoff_max: float = 60.0
    max_retries: int = 5


@dataclass
class AuthConfig:
    """Authentication configuration."""
    type: str = "oauth2"  # oauth2, oauth1, api_key
    scopes: List[str] = field(default_factory=list)
    token_url: str = ""
    auth_url: str = ""
    client_id_env: str = ""
    client_secret_env: str = ""


@dataclass
class PlatformConfig:
    """Complete platform configuration loaded from YAML."""
    platform_id: str
    name: str
    enabled: bool = True
    api_version: str = "v1"
    
    auth: AuthConfig = field(default_factory=AuthConfig)
    capabilities: Dict[Capability, bool] = field(default_factory=dict)
    limits: PlatformLimits = field(default_factory=PlatformLimits)
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)
    
    # Raw config for extensibility
    raw: Dict[str, Any] = field(default_factory=dict)
    
    def supports(self, capability: str) -> bool:
        """Check if platform supports a capability."""
        try:
            cap = Capability(capability)
            return self.capabilities.get(cap, False)
        except ValueError:
            return False
    
    def get_limit(self, limit_name: str) -> Optional[int]:
        """Get a platform limit."""
        return getattr(self.limits, limit_name, None)
    
    def get_all_capabilities(self) -> Dict[str, bool]:
        """Get all capabilities as string-keyed dict."""
        return {cap.value: enabled for cap, enabled in self.capabilities.items()}


# Global registry
PLATFORM_CONFIGS: Dict[str, PlatformConfig] = {}


def load_platform_configs(config_dir: Optional[Path] = None) -> Dict[str, PlatformConfig]:
    """Load all platform configurations from YAML files."""
    global PLATFORM_CONFIGS
    
    if config_dir is None:
        config_dir = Path(__file__).parent / "platforms"
    
    if not config_dir.exists():
        return PLATFORM_CONFIGS
    
    for yaml_file in config_dir.glob("*.yaml"):
        platform_id = yaml_file.stem
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            continue
        
        # Parse capabilities
        capabilities = {}
        for cap_str, enabled in data.get("capabilities", {}).items():
            try:
                capabilities[Capability(cap_str)] = enabled
            except ValueError:
                pass  # Unknown capability, ignore
        
        # Parse limits
        limits_data = data.get("limits", {})
        limits = PlatformLimits(**limits_data)
        
        # Parse rate limits
        rl_data = data.get("rate_limits", {})
        rate_limits = RateLimitConfig(**rl_data)
        
        # Parse auth
        auth_data = data.get("auth", {})
        auth = AuthConfig(**auth_data)
        
        config = PlatformConfig(
            platform_id=platform_id,
            name=data.get("name", platform_id.title()),
            enabled=data.get("enabled", True),
            api_version=data.get("api_version", "v1"),
            auth=auth,
            capabilities=capabilities,
            limits=limits,
            rate_limits=rate_limits,
            raw=data
        )
        
        PLATFORM_CONFIGS[platform_id] = config
    
    return PLATFORM_CONFIGS


def get_platform_config(platform_id: str) -> Optional[PlatformConfig]:
    """Get platform configuration by ID."""
    return PLATFORM_CONFIGS.get(platform_id)


def get_enabled_platforms() -> List[PlatformConfig]:
    """Get all enabled platform configurations."""
    return [c for c in PLATFORM_CONFIGS.values() if c.enabled]
