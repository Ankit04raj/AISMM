"""Instagram OAuth2.0 Authentication Flow."""

import secrets
from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from datetime import datetime, timedelta


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
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class InstagramAuth:
    """Handles Instagram OAuth2.0 flows."""

    AUTH_BASE_URL = "https://api.instagram.com/oauth/authorize"
    TOKEN_URL = "https://api.instagram.com/oauth/access_token"
    REFRESH_URL = "https://graph.facebook.com/v19.0/oauth/access_token"

    def __init__(self, config: InstagramAuthConfig):
        self.config = config
        self._state_store: Dict[str, Dict] = {}  # In production: use Redis

    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Generate authorization URL with PKCE support."""
        if state is None:
            state = secrets.token_urlsafe(32)

        # Store state for validation
        self._state_store[state] = {
            "created_at": datetime.utcnow(),
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

        # Check expiry (10 minutes)
        entry = self._state_store[state]
        if datetime.utcnow() - entry["created_at"] > timedelta(minutes=10):
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
        import httpx

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
            return TokenResponse(**response.json())

    async def exchange_for_long_lived_token(self, short_token: str) -> TokenResponse:
        """Exchange short-lived token for long-lived (60-day) token."""
        import httpx

        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "fb_exchange_token": short_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.REFRESH_URL, params=params)
            response.raise_for_status()
            return TokenResponse(**response.json())

    async def refresh_long_lived_token(self, long_token: str) -> TokenResponse:
        """Refresh long-lived token (within 24h of expiry)."""
        return await self.exchange_for_long_lived_token(long_token)

    def get_token_expiry(self, expires_in: int) -> datetime:
        """Calculate token expiry datetime."""
        return datetime.utcnow() + timedelta(seconds=expires_in)


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
        return datetime.utcnow() >= self._token_expiry - timedelta(hours=1)  # 1h buffer

    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refresh (within 24h of expiry for long-lived)."""
        if not self._token_expiry:
            return True
        return datetime.utcnow() >= self._token_expiry - timedelta(hours=24)

    def set_token(self, token: TokenResponse):
        """Set current token and calculate expiry."""
        self._current_token = token
        self._token_expiry = self.auth.get_token_expiry(token.expires_in)

    async def ensure_valid_token(self) -> str:
        """Ensure we have a valid token, refreshing if needed."""
        if not self._current_token or self.is_expired:
            raise RuntimeError("No valid token available. Re-authenticate.")

        if self.needs_refresh:
            new_token = await self.auth.refresh_long_lived_token(self._current_token.access_token)
            self.set_token(new_token)

        return self._current_token.access_token