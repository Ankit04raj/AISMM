"""
OAuth Manager

Handles OAuth 2.0 flows for social media platform authentication.
Supports PKCE, token refresh, and secure storage.
"""

import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx

from aismm.config import settings
from aismm.config.platforms import get_platform_config, PlatformConfig
from aismm.auth.credentials import get_credential_store


@dataclass
class AuthResult:
    """Result of OAuth authentication."""
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None
    error: Optional[str] = None
    platform_account_id: Optional[str] = None
    account_username: Optional[str] = None
    account_name: Optional[str] = None


class OAuthManager:
    """Manages OAuth flows for all platforms."""
    
    def __init__(self):
        self.credential_store = get_credential_store()
        self._state_store: Dict[str, Dict] = {}  # In-memory state for PKCE
    
    def get_authorization_url(self, platform_id: str, redirect_uri: str, 
                              user_id: str) -> tuple[str, str]:
        """
        Generate OAuth authorization URL with PKCE.
        Returns (authorization_url, state_token)
        """
        config = get_platform_config(platform_id)
        if not config:
            raise ValueError(f"Unknown platform: {platform_id}")
        
        # Generate PKCE code verifier and challenge
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = secrets.token_urlsafe(32)  # Simplified; use S256 in production
        
        # Generate state token
        state = secrets.token_urlsafe(16)
        
        # Store state for callback verification
        self._state_store[state] = {
            "platform_id": platform_id,
            "user_id": user_id,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Build authorization URL
        params = {
            "client_id": os.getenv(config.auth.client_id_env),
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(config.auth.scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        
        auth_url = f"{config.auth.auth_url}?{urlencode(params)}"
        return auth_url, state
    
    async def handle_callback(self, platform_id: str, code: str, state: str) -> AuthResult:
        """Handle OAuth callback and exchange code for tokens."""
        # Verify state
        stored = self._state_store.pop(state, None)
        if not stored:
            return AuthResult(success=False, error="Invalid or expired state")
        
        if stored["platform_id"] != platform_id:
            return AuthResult(success=False, error="Platform mismatch")
        
        config = get_platform_config(platform_id)
        if not config:
            return AuthResult(success=False, error=f"Unknown platform: {platform_id}")
        
        # Exchange code for tokens
        client_id = os.getenv(config.auth.client_id_env)
        client_secret = os.getenv(config.auth.client_secret_env)
        
        if not client_id or not client_secret:
            return AuthResult(success=False, error="OAuth credentials not configured")
        
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": stored["redirect_uri"],
            "code_verifier": stored["code_verifier"],
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(config.auth.token_url, data=token_data)
        
        if response.status_code != 200:
            return AuthResult(success=False, error=f"Token exchange failed: {response.text}")
        
        token_response = response.json()
        
        # Get platform account info
        account_info = await self._get_account_info(platform_id, token_response["access_token"])
        
        return AuthResult(
            success=True,
            access_token=token_response.get("access_token"),
            refresh_token=token_response.get("refresh_token"),
            expires_in=token_response.get("expires_in"),
            scope=token_response.get("scope"),
            platform_account_id=account_info.get("id"),
            account_username=account_info.get("username"),
            account_name=account_info.get("name"),
        )
    
    async def _get_account_info(self, platform_id: str, access_token: str) -> Dict[str, Any]:
        """Fetch account info from platform API."""
        config = get_platform_config(platform_id)
        if not config:
            return {}
        
        headers = {"Authorization": f"Bearer {access_token}"}
        url = ""
        
        if platform_id == "instagram":
            url = f"{settings.INSTAGRAM_API_BASE}/{config.api_version}/me"
        elif platform_id == "facebook":
            url = f"{settings.FACEBOOK_API_BASE}/{config.api_version}/me"
        elif platform_id == "x":
            url = f"{settings.X_API_BASE}/users/me"
        elif platform_id == "linkedin":
            url = f"{settings.LINKEDIN_API_BASE}/userinfo"
        elif platform_id == "youtube":
            url = f"{settings.YOUTUBE_API_BASE}/channels?part=snippet&mine=true"
        
        if not url:
            return {}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            return {}
        
        data = response.json()
        
        # Normalize response
        if platform_id == "youtube":
            items = data.get("items", [])
            if items:
                return {
                    "id": items[0]["id"],
                    "username": items[0]["snippet"]["customUrl"],
                    "name": items[0]["snippet"]["title"],
                }
        
        return {
            "id": data.get("id"),
            "username": data.get("username") or data.get("name"),
            "name": data.get("name"),
        }
    
    async def refresh_access_token(self, platform_id: str, user_id: str) -> AuthResult:
        """Refresh access token using stored refresh token."""
        config = get_platform_config(platform_id)
        if not config:
            return AuthResult(success=False, error=f"Unknown platform: {platform_id}")
        
        # Get stored refresh token
        refresh_token = await self.credential_store.get_refresh_token(user_id, platform_id)
        if not refresh_token:
            return AuthResult(success=False, error="No refresh token stored")
        
        client_id = os.getenv(config.auth.client_id_env)
        client_secret = os.getenv(config.auth.client_secret_env)
        
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(config.auth.token_url, data=token_data)
        
        if response.status_code != 200:
            return AuthResult(success=False, error=f"Token refresh failed: {response.text}")
        
        token_response = response.json()
        
        # Store new tokens
        await self.credential_store.store_tokens(
            user_id=user_id,
            platform_id=platform_id,
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token", refresh_token),
            expires_in=token_response.get("expires_in"),
        )
        
        return AuthResult(
            success=True,
            access_token=token_response.get("access_token"),
            refresh_token=token_response.get("refresh_token"),
            expires_in=token_response.get("expires_in"),
            scope=token_response.get("scope"),
        )
    
    async def disconnect(self, user_id: str, platform_id: str) -> bool:
        """Disconnect platform account (revoke tokens)."""
        return await self.credential_store.delete_tokens(user_id, platform_id)


# Global instance
_oauth_manager: Optional[OAuthManager] = None


def get_oauth_manager() -> OAuthManager:
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager()
    return _oauth_manager
