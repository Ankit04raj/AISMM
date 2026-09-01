"""Platform registry."""

from typing import Dict, Type, Optional, List, Any
from .base import BasePlatformAdapter


class PlatformRegistry:
    """Central platform adapter registry."""

    _adapters: Dict[str, Type[BasePlatformAdapter]] = {}
    _instances: Dict[str, BasePlatformAdapter] = {}

    @classmethod
    def register(cls, platform_id: str, adapter_class: Type[BasePlatformAdapter]) -> None:
        """Register a platform adapter class."""
        cls._adapters[platform_id.lower()] = adapter_class

    @classmethod
    def get_adapter_class(cls, platform_id: str) -> Optional[Type[BasePlatformAdapter]]:
        """Get the registered adapter class for a platform."""
        return cls._adapters.get(platform_id.lower())

    @classmethod
    def get_adapter(
        cls,
        platform_id: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[BasePlatformAdapter]:
        """Get or instantiate an adapter for a platform."""
        key = platform_id.lower()
        if config is not None:
            adapter_cls = cls.get_adapter_class(key)
            if adapter_cls:
                return adapter_cls(config)
            return None

        if key not in cls._instances:
            adapter_cls = cls.get_adapter_class(key)
            if adapter_cls:
                cls._instances[key] = adapter_cls({})
        return cls._instances.get(key)

    @classmethod
    def list_platforms(cls) -> List[str]:
        """List all registered platforms."""
        return list(cls._adapters.keys())

    @classmethod
    def is_registered(cls, platform_id: str) -> bool:
        """Check if a platform adapter is registered."""
        return platform_id.lower() in cls._adapters

    @classmethod
    def clear(cls) -> None:
        """Clear registered instances (useful for testing)."""
        cls._instances.clear()
