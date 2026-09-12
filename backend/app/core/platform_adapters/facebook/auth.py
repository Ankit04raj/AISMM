"""Facebook OAuth2.0 Authentication Flow for Pages."""

import secrets
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx

from .config import FacebookAuthConfig
from ...errors import AuthenticationError, ValidationError


class FacebookAuth:
    """Handles Facebook OAuth2.0 and Page Access Token flows."""

    API_VERSION = "v20.0"
    AUTH_URL = f"https://www.facebook.com/{API_VERSION}/dialog/oauth"
    TOKEN_URL = f"https://graph.facebook.com/{API_VERSION}/oauth/access_token"
    GRAPH_BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

    def __init__(self, config: FacebookAuthConfig):
        self.config = config
        self._state_store: Dict[str, Dict[str, Any]] = {}

    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Generate Facebook OAuth authorization URL."""
        if state is None:
            state = secrets.token_urlsafe(32)

        self._state_store[state] = {
            "created_at": datetime.now(timezone.utc),
        }

        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": ",".join(self.config.scopes),
            "response_type": "code",
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
        """Exchange code for user access token and then long-lived token."""
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": redirect_uri or self.config.redirect_uri,
            "code": code,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.TOKEN_URL, params=data)
            if resp.status_code != 200:
                raise AuthenticationError(f"Facebook token exchange failed: {resp.text}", platform="facebook")

            user_token_data = resp.json()
            short_token = user_token_data.get("access_token")

            # Exchange for long-lived user token (60 days)
            long_params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "fb_exchange_token": short_token,
            }
            long_resp = await client.get(self.TOKEN_URL, params=long_params)
            long_data = long_resp.json() if long_resp.status_code == 200 else user_token_data

            return {
                "access_token": long_data.get("access_token", short_token),
                "expires_in": long_data.get("expires_in", 5184000),
                "token_type": "Bearer",
            }

    async def get_available_pages(self, user_access_token: str) -> List[Dict[str, Any]]:
        """Fetch all Facebook Pages managed by the user."""
        headers = {"Authorization": f"Bearer {user_access_token}"}
        async with httpx.AsyncClient(base_url=self.GRAPH_BASE_URL) as client:
            resp = await client.get(
                "/me/accounts",
                headers=headers,
                params={"fields": "id,name,category,access_token,tasks,instagram_business_account{id,username,name,profile_picture_url}"},
            )
            if resp.status_code != 200:
                raise AuthenticationError(f"Failed to fetch Facebook pages: {resp.text}", platform="facebook")
            return resp.json().get("data", [])

    async def get_page_access_token(self, user_access_token: str, page_id: Optional[str] = None) -> Dict[str, Any]:
        """Get Facebook Page access token from user accounts with explicit Page selection support."""
        pages = await self.get_available_pages(user_access_token)
        if not pages:
            raise ValidationError("No Facebook Pages found. You must manage at least one Facebook Page to connect.", platform="facebook")

        target_page = None
        if page_id:
            for page in pages:
                if str(page.get("id")) == str(page_id):
                    target_page = page
                    break
            if not target_page:
                raise ValidationError(f"Facebook Page ID '{page_id}' not found among your managed Pages.", platform="facebook")
        else:
            # Auto-select the single page or first page
            target_page = pages[0]

        return {
            "page_id": target_page["id"],
            "page_name": target_page.get("name"),
            "page_access_token": target_page.get("access_token", user_access_token),
            "category": target_page.get("category"),
            "available_pages_count": len(pages),
        }

    async def get_user_profile(self, access_token: str, page_id: Optional[str] = None) -> Dict[str, Any]:
        """Get profile info for user/page."""
        target = page_id or "me"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(base_url=self.GRAPH_BASE_URL) as client:
            resp = await client.get(f"/{target}", headers=headers, params={"fields": "id,name,picture,fan_count,category,about"})
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "id": data.get("id"),
                    "username": data.get("name", "facebook_page"),
                    "name": data.get("name"),
                    "display_name": data.get("name"),
                    "profile_picture_url": data.get("picture", {}).get("data", {}).get("url"),
                    "account_type": "page",
                    "category": data.get("category"),
                    "followers_count": data.get("fan_count", 0),
                }
            return {"id": page_id or "fb_page", "username": "facebook_page", "name": "Facebook Page"}

    async def revoke_token(self, access_token: str) -> bool:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(base_url=self.GRAPH_BASE_URL) as client:
            resp = await client.delete("/me/permissions", headers=headers)
            return resp.status_code == 200

    def get_token_expiry(self, expires_in: int) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)
