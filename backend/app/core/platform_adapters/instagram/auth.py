"""Instagram OAuth2.0 Authentication Flow & Meta Graph API Integration."""

import secrets
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx
from ...errors import AuthenticationError, ValidationError


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
                "instagram_basic",
                "instagram_content_publish",
                "instagram_manage_comments",
                "instagram_manage_insights",
                "pages_show_list",
                "pages_read_engagement",
                "pages_manage_posts",
                "business_management",
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
    """Handles Instagram OAuth2.0 flows, long-lived token exchanges, and Page-linked Instagram Business account resolution."""

    API_VERSION = "v20.0"
    AUTH_BASE_URL = f"https://www.facebook.com/{API_VERSION}/dialog/oauth"
    TOKEN_URL = f"https://graph.facebook.com/{API_VERSION}/oauth/access_token"
    REFRESH_URL = f"https://graph.facebook.com/{API_VERSION}/oauth/access_token"
    GRAPH_BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

    def __init__(self, config: InstagramAuthConfig):
        self.config = config
        self._state_store: Dict[str, Dict] = {}

    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """Generate authorization URL with PKCE and Facebook login dialog."""
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

        if datetime.now(timezone.utc) - created > timedelta(minutes=15):
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

    async def exchange_code(self, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """Exchange authorization code for access token and upgrade to long-lived token."""
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri or self.config.redirect_uri,
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.TOKEN_URL, params=data)
            if response.status_code != 200:
                raise AuthenticationError(f"Instagram token exchange failed: {response.text}", platform="instagram")
            res_data = response.json()
            short_token = res_data.get("access_token", "")

            # Upgrade to long-lived (60 days) user access token
            long_params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "fb_exchange_token": short_token,
            }
            long_resp = await client.get(self.REFRESH_URL, params=long_params)
            long_data = long_resp.json() if long_resp.status_code == 200 else res_data

            return {
                "access_token": long_data.get("access_token", short_token),
                "token_type": "Bearer",
                "expires_in": long_data.get("expires_in", 5184000),
                "scope": res_data.get("scope"),
            }

    async def get_available_accounts(self, user_access_token: str) -> List[Dict[str, Any]]:
        """Fetch all Facebook Pages and linked Instagram Business accounts."""
        headers = {"Authorization": f"Bearer {user_access_token}"}
        async with httpx.AsyncClient(base_url=self.GRAPH_BASE_URL) as client:
            resp = await client.get(
                "/me/accounts",
                headers=headers,
                params={"fields": "id,name,category,access_token,instagram_business_account{id,username,name,profile_picture_url,followers_count,media_count,account_type}"},
            )
            if resp.status_code != 200:
                raise AuthenticationError(f"Failed to fetch Facebook Pages: {resp.text}", platform="instagram")
            return resp.json().get("data", [])

    async def get_instagram_business_account(self, user_access_token: str, page_id: Optional[str] = None) -> Dict[str, Any]:
        """Resolve linked Instagram Business Account with explicit Page selection support."""
        pages = await self.get_available_accounts(user_access_token)
        if not pages:
            raise ValidationError(
                "No Facebook Pages found for this account. Instagram Business accounts must be linked to a Facebook Page.",
                platform="instagram",
            )

        target_page = None
        ig_account = None

        if page_id:
            for page in pages:
                if str(page.get("id")) == str(page_id):
                    target_page = page
                    ig_account = page.get("instagram_business_account")
                    break
            if not target_page:
                raise ValidationError(f"Facebook Page ID '{page_id}' not found among your managed Pages.", platform="instagram")
            if not ig_account:
                raise ValidationError(
                    f"Facebook Page '{target_page.get('name')}' is not linked to an Instagram Business account. "
                    "Link your Instagram Professional account to this Page in Meta Business Suite.",
                    platform="instagram",
                )
        else:
            # Search for the first page that has an Instagram Business account
            for page in pages:
                if page.get("instagram_business_account"):
                    target_page = page
                    ig_account = page.get("instagram_business_account")
                    break

            if not ig_account:
                raise ValidationError(
                    "No Instagram Business Account linked to your Facebook Pages. "
                    "Convert your Instagram account to a Professional/Business account and link it to a Facebook Page in Meta Business Suite.",
                    platform="instagram",
                )

        return {
            "id": ig_account.get("id"),
            "username": ig_account.get("username", "instagram_user"),
            "name": ig_account.get("name") or ig_account.get("username", "Instagram Business"),
            "display_name": ig_account.get("name") or ig_account.get("username", "Instagram Business"),
            "profile_picture_url": ig_account.get("profile_picture_url"),
            "account_type": ig_account.get("account_type", "business"),
            "followers_count": ig_account.get("followers_count", 0),
            "media_count": ig_account.get("media_count", 0),
            "linked_page_id": target_page.get("id"),
            "linked_page_name": target_page.get("name"),
            "page_access_token": target_page.get("access_token"),
            "available_pages_count": len(pages),
        }

    async def get_user_profile(self, access_token: str, page_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetch profile for the connected account."""
        return await self.get_instagram_business_account(access_token, page_id=page_id)

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh long-lived access token."""
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "fb_exchange_token": refresh_token,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.REFRESH_URL, params=params)
            if response.status_code != 200:
                raise AuthenticationError(f"Instagram token refresh failed: {response.text}", platform="instagram")
            res_data = response.json()
            return {
                "access_token": res_data.get("access_token", refresh_token),
                "expires_in": res_data.get("expires_in", 5184000),
                "token_type": "Bearer",
            }

    async def revoke_token(self, access_token: str) -> bool:
        """Revoke application permissions."""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(base_url=self.GRAPH_BASE_URL) as client:
            resp = await client.delete("/me/permissions", headers=headers)
            return resp.status_code == 200

    def get_token_expiry(self, expires_in: int) -> datetime:
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
            new_token = await self.auth.refresh_access_token(self._current_token.access_token)
            self._current_token = TokenResponse(
                access_token=new_token["access_token"],
                expires_in=new_token.get("expires_in", 5184000),
            )
            self._token_expiry = self.auth.get_token_expiry(new_token.get("expires_in", 5184000))
        return self._current_token.access_token
