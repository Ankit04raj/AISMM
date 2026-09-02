"""YouTube / Google OAuth 2.0 Flow and Channel Authorization."""

import secrets
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx

from .config import YouTubeAuthConfig
from ...errors import AuthenticationError, ValidationError


class YouTubeAuth:
    """Handles Google/YouTube OAuth 2.0 authorization, token exchange, and refresh."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    REVOKE_URL = "https://oauth2.googleapis.com/revoke"
    DATA_BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, config: YouTubeAuthConfig):
        self.config = config
        self._state_store: Dict[str, Dict[str, Any]] = {}

    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """Generate Google OAuth 2.0 authorization URL."""
        if state is None:
            state = secrets.token_urlsafe(32)

        self._state_store[state] = {
            "created_at": datetime.now(timezone.utc),
        }

        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        return f"{self.AUTH_URL}?{urlencode(params)}", state

    def validate_state(self, state: str) -> bool:
        if state not in self._state_store:
            return False
        entry = self._state_store[state]
        created = entry["created_at"]
        if datetime.now(timezone.utc) - created > timedelta(minutes=15):
            del self._state_store[state]
            return False
        return True

    async def exchange_code(self, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        data = {
            "code": code,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": redirect_uri or self.config.redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data)
            if resp.status_code != 200:
                raise AuthenticationError(f"YouTube token exchange failed: {resp.text}", platform="youtube")

            token_data = resp.json()
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in", 3600),
                "token_type": token_data.get("token_type", "Bearer"),
                "scope": token_data.get("scope"),
            }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired Google access token."""
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data)
            if resp.status_code != 200:
                raise AuthenticationError(f"YouTube token refresh failed: {resp.text}", platform="youtube")

            token_data = resp.json()
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token", refresh_token),
                "expires_in": token_data.get("expires_in", 3600),
                "token_type": "Bearer",
            }

    async def get_channel_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch YouTube channel details for the authenticated user."""
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"part": "snippet,statistics,contentDetails", "mine": "true"}

        async with httpx.AsyncClient(base_url=self.DATA_BASE_URL) as client:
            resp = await client.get("/channels", headers=headers, params=params)
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    ch = items[0]
                    snippet = ch.get("snippet", {})
                    stats = ch.get("statistics", {})
                    return {
                        "id": ch.get("id"),
                        "title": snippet.get("title"),
                        "name": snippet.get("title"),
                        "username": snippet.get("customUrl", snippet.get("title")),
                        "description": snippet.get("description"),
                        "profile_picture_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                        "subscriber_count": int(stats.get("subscriberCount", 0)),
                        "video_count": int(stats.get("videoCount", 0)),
                        "view_count": int(stats.get("viewCount", 0)),
                    }
            return {"id": "youtube_channel", "name": "YouTube Channel", "title": "YouTube Channel"}

    async def revoke_token(self, token: str) -> bool:
        """Revoke OAuth token."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.REVOKE_URL, params={"token": token})
            return resp.status_code == 200

    def get_token_expiry(self, expires_in: int) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)
