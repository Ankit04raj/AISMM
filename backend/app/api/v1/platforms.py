"""Platforms API router."""

from fastapi import APIRouter, HTTPException, Depends
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.oauth_service import get_platform_oauth_status

router = APIRouter(prefix="/platforms", tags=["Platforms"])


@router.get("")
async def list_platforms(
    current_user: User = Depends(get_current_user),
):
    """List all supported platforms and their OAuth configuration readiness."""
    return {
        "platforms": PlatformRegistry.list_platforms(),
        "oauth_status": get_platform_oauth_status(),
    }


@router.get("/{platform}/capabilities")
async def get_platform_capabilities(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Get capabilities for a specific platform."""
    if not PlatformRegistry.is_registered(platform):
        raise HTTPException(status_code=404, detail=f"Platform not found: {platform}")

    adapter = PlatformRegistry.get_adapter(platform)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Adapter not available for: {platform}")

    caps = await adapter.get_capabilities()
    return {
        "platform": platform,
        "capabilities": [c.value if hasattr(c, "value") else str(c) for c in caps],
    }
