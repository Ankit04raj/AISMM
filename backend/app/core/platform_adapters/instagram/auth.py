"""Instagram OAuth2.0 Authentication Flow."""

import secrets
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx


@dataclass
class InstagramAuthConfig:
    """Instagram OAuth configuration."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list = None

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = [
                "instagram_graph_user_profile",
                "instagram_graph_user_media",
                "instagram_manage_comments",
                "instagram_manage_insights",
                "pages_show_list",
                "pages_read_engagement",
            ]


@dataclass
class TokenResponse:
    """OAuth token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class InstagramAuth:
    """Handles Instagram OAuth2.0 flows."""

    AUTH_BASE_URL = "https://api.instagram.com/oauth/authorize"
    TOKEN_URL = "https://api.instagram.com/oauth/access_token"
    REFRESH_URL = "https://graph.facebook.com/v19.0/oauth/access_token"
    GRAPH_BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, config: InstagramAuthConfig):
        self.config = config
        self._state_store: Dict[str, Dict] = {}  # In production: use Redis

    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Generate authorization URL with PKCE support."""
        if state is None:
            state = secrets.token_urlsafe(32)

        self._state_store[state] = {
            "created_at": datetime.now(timezone.utc),
            "code_verifier": secrets.token_urlsafe(64),
        }

        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": ",".join(self.config.scopes),
            "response_type": "code",
            "state": state,
        }

        return f"{self.AUTH_BASE_URL}?{urlencode(params)}", state

    def validate_state(self, state: str) -> bool:
        """Validate OAuth state parameter."""
        if state not in self._state_store:
            return False

        entry = self._state_store[state]
        created = entry["created_at"]
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) - created > timedelta(minutes=10):
            del self._state_store[state]
            return False

        return True

    def consume_state(self, state: str) -> Optional[str]:
        """Consume and return code_verifier for PKCE."""
        if state in self._state_store:
            verifier = self._state_store[state].get("code_verifier")
            del self._state_store[state]
            return verifier
        return None

    async def exchange_code_for_token(self, code: str, code_verifier: Optional[str] = None) -> TokenResponse:
        """Exchange authorization code for access token."""
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
            "code": code,
        }

        if code_verifier:
            data["code_verifier"] = code_verifier

        async with httpx.AsyncClient() as client:
            response = await client.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            res_data = response.json()
            return TokenResponse(
                access_token=res_data.get("access_token", ""),
                token_type=res_data.get("token_type", "Bearer"),
                expires_in=res_data.get("expires_in", 3600),
                refresh_token=res_data.get("refresh_token"),
                scope=res_data.get("scope"),
            )

    async def exchange_code(self, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """Exchange code returning raw dict response for services."""
        token_res = await self.exchange_code_for_token(code)
        # Try exchange for long lived token
        try:
            long_res = await self.exchange_for_long_lived_token(token_res.access_token)
            return {
                "access_token": long_res.access_token,
                "token_type": long_res.token_type,
                "expires_in": long_res.expires_in,
                "refresh_token": long_res.refresh_token or token_res.refresh_token,
                "scope": token_res.scope,
            }
        except Exception:
            return {
                "access_token": token_res.access_token,
                "token_type": token_res.token_type,
                "expires_in": token_res.expires_in,
                "refresh_token": token_res.refresh_token,
                "scope": token_res.scope,
            }

    async def exchange_for_long_lived_token(self, short_token: str) -> TokenResponse:
        """Exchange short-lived token for long-lived (60-day) token."""
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "fb_exchange_token": short_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.REFRESH_URL, params=params)
            response.raise_for_status()
            res_data = response.json()
            return TokenResponse(
                access_token=res_data.get("access_token", ""),
                token_type=res_data.get("token_type", "Bearer"),
                expires_in=res_data.get("expires_in", 5184000),
            )

    async def refresh_long_lived_token(self, long_token: str) -> TokenResponse:
        """Refresh long-lived token (within 24h of expiry)."""
        return await self.exchange_for_long_lived_token(long_token)

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Service helper to refresh token and return dict."""
        token_res = await self.refresh_long_lived_token(refresh_token)
        return {
            "access_token": token_res.access_token,
            "expires_in": token_res.expires_in,
            "refresh_token": token_res.refresh_token,
        }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch user/business account profile using access token."""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(base_url=self.GRAPH_BASE_URL) as client:
            # First fetch /me accounts
            resp = await client.get("/me/accounts", headers=headers, params={"fields": "instagram_business_account{id,username,name,profile_picture_url}"})
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                for acc in data:
                    ig_acc = acc.get("instagram_business_account")
                    if ig_acc:
                        return {
                            "id": ig_acc.get("id"),
                            "username": ig_acc.get("username", "instagram_user"),
                            "name": ig_acc.get("name", "Instagram Business"),
                            "profile_picture_url": ig_acc.get("profile_picture_url"),
                            "account_type": "business",
                        }
            # Fallback to direct /me
            me_resp = await client.get("/me", headers=headers, params={"fields": "id,name"})
            if me_resp.status_code == 200:
                me_data = me_resp.json()
                return {
                    "id": me_data.get("id", "ig_user_unknown"),
                    "username": me_data.get("name", "instagram_user"),
                    "name": me_data.get("name"),
                    "account_type": "personal",
                }
            return {
                "id": "unknown_id",
                "username": "instagram_user",
                "name": "Instagram User",
                "account_type": "creator",
            }

    async def revoke_token(self, access_token: str) -> bool:
        """Revoke application permissions."""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(base_url=self.GRAPH_BASE_URL) as client:
            resp = await client.delete("/me/permissions", headers=headers)
            return resp.status_code == 200

    def get_token_expiry(self, expires_in: int) -> datetime:
        """Calculate token expiry datetime."""
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)


class InstagramTokenManager:
    """Manages token lifecycle for Instagram API."""

    def __init__(self, auth: InstagramAuth):
        self.auth = auth
        self._current_token: Optional[TokenResponse] = None
        self._token_expiry: Optional[datetime] = None

    @property
    def access_token(self) -> Optional[str]:
        return self._current_token.access_token if self._current_token else None

    @property
    def is_expired(self) -> bool:
        if not self._token_expiry:
            return True
        return datetime.now(timezone.utc) >= self._token_expiry - timedelta(hours=1)

    @property
    def needs_refresh(self) -> bool:
        if not self._token_expiry:
            return True
        return datetime.now(timezone.utc) >= self._token_expiry - timedelta(hours=24)

    def set_token(self, token: TokenResponse):
        self._current_token = token
        self._token_expiry = self.auth.get_token_expiry(token.expires_in)

    async def ensure_valid_token(self) -> str:
        if not self._current_token or self.is_expired:
            raise RuntimeError("No valid token available. Re-authenticate.")
        if self.needs_refresh:
            new_token = await self.auth.refresh_long_lived_token(self._current_token.access_token)
            self.set_token(new_token)
        return self._current_token.access_token
