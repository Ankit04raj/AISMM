"""Platform registry."""

from typing import Dict, Type, Optional, List
from .base import BasePlatformAdapter


class PlatformRegistry:
    """Central platform adapter registry."""

    _adapters: Dict[str, Type[BasePlatformAdapter]] = {}

    @classmethod
    def register(cls, platform_id: str, adapter_class: Type[BasePlatformAdapter]) -> None:
        """Register a platform adapter."""
        cls._adapters[platform_id] = adapter_class

    @classmethod
    def get_adapter_class(cls, platform_id: str) -> Optional[Type[BasePlatformAdapter]]:
        return cls._adapters.get(platform_id)

    @classmethod
    def list_platforms(cls) -> List[str]:
        """List all registered platforms."""
        return list(cls._adapters.keys())