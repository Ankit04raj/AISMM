"""Platform registry."""

from typing import Dict, Type, Optional, List
from .base import BasePlatformAdapter

class PlatformRegistry:
    """Central platform adapter registry."""

    def __init__(self):
        self._adapters: Dict[str, Type[BasePlatformAdapter]] = {}

    def register(self, platform_id: str, adapter_class: Type[BasePlatformAdapter]) -> None:
        """Register a platform adapter."""
        self._adapters[platform_id] = adapter_class

    def get_adapter_class(self, platform_id: str) -> Optional[Type[BasePlatformAdapter]]:
        return self._adapters.get(platform_id)

    def list_platforms(self) -> List[str]:
        """List all registered platforms."""
        return list(self._adapters.keys())

# Global registry instance
platform_registry = PlatformRegistry()