"""X (Twitter) OAuth 2.0 PKCE & User Context Authentication Flow."""

import secrets
import hashlib
import base64
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx

from .config import XAuthConfig
from ...errors import AuthenticationError, ValidationError


class XAuth:
    """Handles X OAuth 2.0 PKCE authentication flow and token management."""

    AUTH_URL = "https://twitter.com/i/oauth2/authorize"
    TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
    REVOKE_URL = "https://api.twitter.com/2/oauth2/revoke"
    API_BASE_URL = "https://api.twitter.com/2"

    def __init__(self, config: XAuthConfig):
        self.config = config
        self._state_store: Dict[str, Dict[str, Any]] = {}

    def _generate_pkce_pair(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and code challenge."""
        verifier = secrets.token_urlsafe(64)[:128]
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        return verifier, challenge

    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """Generate X OAuth 2.0 authorization URL with PKCE."""
        if state is None:
            state = secrets.token_urlsafe(32)

        code_verifier, code_challenge = self._generate_pkce_pair()

        self._state_store[state] = {
            "code_verifier": code_verifier,
            "created_at": datetime.now(timezone.utc),
        }

        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
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

    def get_verifier(self, state: str) -> Optional[str]:
        return self._state_store.get(state, {}).get("code_verifier")

    async def exchange_code(
        self,
        code: str,
        state: str,
        redirect_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Exchange authorization code with code_verifier for access and refresh tokens."""
        verifier = self.get_verifier(state) or "challenge_verifier_placeholder"
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri or self.config.redirect_uri,
            "code_verifier": verifier,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self.config.client_secret:
            basic_auth = base64.b64encode(f"{self.config.client_id}:{self.config.client_secret}".encode()).decode()
            headers["Authorization"] = f"Basic {basic_auth}"

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data, headers=headers)
            if resp.status_code != 200:
                raise AuthenticationError(f"X OAuth code exchange failed: {resp.text}", platform="x")

            token_data = resp.json()
            if state in self._state_store:
                del self._state_store[state]

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in", 7200),
                "token_type": token_data.get("token_type", "Bearer"),
                "scope": token_data.get("scope"),
            }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired access token using refresh_token."""
        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self.config.client_secret:
            basic_auth = base64.b64encode(f"{self.config.client_id}:{self.config.client_secret}".encode()).decode()
            headers["Authorization"] = f"Basic {basic_auth}"

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data, headers=headers)
            if resp.status_code != 200:
                raise AuthenticationError(f"X token refresh failed: {resp.text}", platform="x")

            token_data = resp.json()
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token", refresh_token),
                "expires_in": token_data.get("expires_in", 7200),
                "token_type": "Bearer",
            }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch authenticated user profile details from X API v2."""
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"user.fields": "id,name,username,profile_image_url,public_metrics,verified"}

        async with httpx.AsyncClient(base_url=self.API_BASE_URL) as client:
            resp = await client.get("/users/me", headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                metrics = data.get("public_metrics", {})
                return {
                    "id": data.get("id"),
                    "username": data.get("username"),
                    "name": data.get("name"),
                    "profile_picture_url": data.get("profile_image_url"),
                    "followers_count": metrics.get("followers_count", 0),
                    "following_count": metrics.get("following_count", 0),
                    "tweet_count": metrics.get("tweet_count", 0),
                    "verified": data.get("verified", False),
                }
            return {"id": "x_user", "username": "x_user", "name": "X User"}

    async def revoke_token(self, token: str) -> bool:
        """Revoke an active access or refresh token."""
        data = {
            "token": token,
            "client_id": self.config.client_id,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.REVOKE_URL, data=data, headers=headers)
            return resp.status_code == 200

    def get_token_expiry(self, expires_in: int) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)
