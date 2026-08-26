"""
Platform Registry

Central registry for platform adapter discovery and management.
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass

from .adapter import BasePlatformAdapter
from .capabilities import PlatformCapabilities, Capability


@dataclass
class PlatformMetadata:
    """Platform metadata for discovery."""
    platform_id: str
    name: str
    description: str
    version: str
    capabilities: List[str]  # Capability names
    status: str  # "implemented", "planned", "deprecated"


class PlatformRegistry:
    """
    Central platform registry.
    
    Responsibilities:
    - Register adapters
    - Discover available platforms
    - Load platform capabilities
    - Return the correct adapter instance
    - Validate platform support
    - Provide platform metadata
    """
    
    _adapters: Dict[str, Type[BasePlatformAdapter]] = {}
    _metadata: Dict[str, PlatformMetadata] = {}
    _instances: Dict[str, BasePlatformAdapter] = {}  # Cached instances
    
    @classmethod
    def register(cls, platform_id: str, adapter_class: Type[BasePlatformAdapter],
                 metadata: Optional[PlatformMetadata] = None) -> None:
        """Register a platform adapter."""
        if platform_id in cls._adapters:
            raise ValueError(f"Platform {platform_id} already registered")
        
        cls._adapters[platform_id] = adapter_class
        
        if metadata:
            cls._metadata[platform_id] = metadata
        else:
            # Create minimal metadata from adapter
            instance = adapter_class()
            cls._metadata[platform_id] = PlatformMetadata(
                platform_id=platform_id,
                name=getattr(adapter_class, 'PLATFORM_NAME', platform_id.title()),
                description=getattr(adapter_class, 'PLATFORM_DESCRIPTION', ''),
                version=getattr(adapter_class, 'PLATFORM_VERSION', '1.0.0'),
                capabilities=instance.get_capabilities().get_supported(),
                status="implemented"
            )
    
    @classmethod
    def get(cls, platform_id: str, account_id: str = None, 
            credentials: Dict = None) -> BasePlatformAdapter:
        """Get adapter instance for a platform."""
        if platform_id not in cls._adapters:
            raise ValueError(f"Platform {platform_id} not registered")
        
        # Create new instance with account context if provided
        adapter_class = cls._adapters[platform_id]
        instance = adapter_class(account_id=account_id, credentials=credentials)
        
        # Cache instance
        cache_key = f"{platform_id}:{account_id or 'default'}"
        cls._instances[cache_key] = instance
        
        return instance
    
    @classmethod
    def get_cached(cls, platform_id: str, account_id: str = None) -> Optional[BasePlatformAdapter]:
        """Get cached adapter instance."""
        cache_key = f"{platform_id}:{account_id or 'default'}"
        return cls._instances.get(cache_key)
    
    @classmethod
    def get_all(cls) -> List[BasePlatformAdapter]:
        """Get all registered adapter instances (default config)."""
        return [cls.get(pid) for pid in cls._adapters.keys()]
    
    @classmethod
    def get_capabilities(cls, platform_id: str) -> PlatformCapabilities:
        """Get platform capabilities."""
        if platform_id not in cls._adapters:
            raise ValueError(f"Platform {platform_id} not registered")
        
        # Use cached or create temporary instance
        instance = cls.get_cached(platform_id) or cls.get(platform_id)
        return instance.get_capabilities()
    
    @classmethod
    def supports(cls, platform_id: str, capability: str) -> bool:
        """Check if platform supports a capability."""
        try:
            caps = cls.get_capabilities(platform_id)
            return caps.supports(capability)
        except ValueError:
            return False
    
    @classmethod
    def get_metadata(cls, platform_id: str) -> Optional[PlatformMetadata]:
        """Get platform metadata."""
        return cls._metadata.get(platform_id)
    
    @classmethod
    def get_all_metadata(cls) -> List[PlatformMetadata]:
        """Get metadata for all registered platforms."""
        return list(cls._metadata.values())
    
    @classmethod
    def get_enabled_platforms(cls) -> List[str]:
        """Get list of enabled platform IDs."""
        from aismm.config.platforms import get_enabled_platforms
        configs = get_enabled_platforms()
        return [c.platform_id for c in configs if c.platform_id in cls._adapters]
    
    @classmethod
    def is_registered(cls, platform_id: str) -> bool:
        """Check if platform is registered."""
        return platform_id in cls._adapters
    
    @classmethod
    def unregister(cls, platform_id: str) -> bool:
        """Unregister a platform (for testing/plugin removal)."""
        if platform_id in cls._adapters:
            del cls._adapters[platform_id]
            cls._metadata.pop(platform_id, None)
            # Clear cached instances
            keys_to_remove = [k for k in cls._instances if k.startswith(f"{platform_id}:")]
            for k in keys_to_remove:
                del cls._instances[k]
            return True
        return False
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached instances."""
        cls._instances.clear()
