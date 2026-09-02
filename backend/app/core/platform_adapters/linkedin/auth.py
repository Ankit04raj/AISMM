"""LinkedIn 3-Legged OAuth 2.0 Flow and Organization Authorization."""

import secrets
from typing import Optional, Dict, Any, Tuple, List
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx

from .config import LinkedInAuthConfig
from ...errors import AuthenticationError, ValidationError


class LinkedInAuth:
    """Handles LinkedIn OAuth 2.0 authorization, token exchange, and Organization URN resolution."""

    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
    ORGANIZATIONS_URL = "https://api.linkedin.com/v2/organizationalEntityAcls"

    def __init__(self, config: LinkedInAuthConfig):
        self.config = config
        self._state_store: Dict[str, Dict[str, Any]] = {}

    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """Generate LinkedIn OAuth 2.0 authorization URL."""
        if state is None:
            state = secrets.token_urlsafe(32)

        self._state_store[state] = {
            "created_at": datetime.now(timezone.utc),
        }

        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "state": state,
            "scope": " ".join(self.config.scopes),
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
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": redirect_uri or self.config.redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, data=data, headers=headers)
            if resp.status_code != 200:
                raise AuthenticationError(f"LinkedIn token exchange failed: {resp.text}", platform="linkedin")

            token_data = resp.json()
            return {
                "access_token": token_data.get("access_token"),
                "expires_in": token_data.get("expires_in", 5184000),  # Typically 60 days
                "scope": token_data.get("scope"),
            }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch basic member profile details via OpenID UserInfo."""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.USERINFO_URL, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "id": data.get("sub"),
                    "name": data.get("name"),
                    "given_name": data.get("given_name"),
                    "family_name": data.get("family_name"),
                    "email": data.get("email"),
                    "profile_picture_url": data.get("picture"),
                }
            return {"id": "linkedin_user", "name": "LinkedIn Member"}

    async def get_administrated_organizations(self, access_token: str) -> List[Dict[str, Any]]:
        """Fetch organizations the authenticated member has admin/posting access to."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        params = {
            "q": "roleAssignee",
            "role": "ADMINISTRATOR",
            "state": "APPROVED",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.ORGANIZATIONS_URL, headers=headers, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            orgs = []
            for item in data.get("elements", []):
                org_urn = item.get("organizationalTarget")
                if org_urn:
                    org_id = org_urn.split(":")[-1]
                    orgs.append({
                        "organization_urn": org_urn,
                        "organization_id": org_id,
                        "role": item.get("role"),
                    })
            return orgs

    def get_token_expiry(self, expires_in: int) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)
