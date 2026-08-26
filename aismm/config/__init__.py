"""
AISMM Configuration System

Configuration-driven architecture for platform-agnostic social media management.
"""

from .settings import settings
from .platforms import load_platform_configs, PLATFORM_CONFIGS

__all__ = ["settings", "load_platform_configs", "PLATFORM_CONFIGS"]
