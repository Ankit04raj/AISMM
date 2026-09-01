"""Authentication API router."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.schemas.auth import (
    OAuthInitRequest,
    OAuthInitResponse,
    OAuthCallbackRequest,
    OAuthTokenResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/oauth/init", response_model=OAuthInitResponse)
async def oauth_init(request: OAuthInitRequest):
    """Initiate OAuth flow for a social media platform."""
    if not PlatformRegistry.is_registered(request.platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

    adapter = PlatformRegistry.get_adapter(request.platform)
    if not adapter or not hasattr(adapter, "auth"):
        raise HTTPException(status_code=400, detail=f"OAuth not supported for: {request.platform}")

    auth_url, state = adapter.auth.get_authorization_url(state=request.state)
    return OAuthInitResponse(
        authorization_url=auth_url,
        state=state,
        expires_at=adapter.auth.get_token_expiry(600),
    )


@router.post("/oauth/callback", response_model=OAuthTokenResponse)
async def oauth_callback(request: OAuthCallbackRequest):
    """Handle OAuth callback and code exchange."""
    if not PlatformRegistry.is_registered(request.platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

    adapter = PlatformRegistry.get_adapter(request.platform)
    if not adapter or not hasattr(adapter, "auth"):
        raise HTTPException(status_code=400, detail=f"OAuth not supported for: {request.platform}")

    token_response = await adapter.auth.exchange_code(
        code=request.code,
        redirect_uri=request.redirect_uri,
    )
    return OAuthTokenResponse(
        access_token=token_response["access_token"],
        token_type=token_response.get("token_type", "Bearer"),
        expires_in=token_response.get("expires_in", 3600),
        refresh_token=token_response.get("refresh_token"),
        scope=token_response.get("scope"),
    )


@router.post("/oauth/refresh")
async def oauth_refresh(request: RefreshTokenRequest):
    """Refresh platform access token."""
    if not PlatformRegistry.is_registered(request.platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

    adapter = PlatformRegistry.get_adapter(request.platform)
    if not adapter or not hasattr(adapter, "auth"):
        raise HTTPException(status_code=400, detail=f"OAuth refresh not supported for: {request.platform}")

    refreshed = await adapter.auth.refresh_access_token(request.refresh_token)
    return refreshed
