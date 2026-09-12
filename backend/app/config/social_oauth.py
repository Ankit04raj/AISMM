"""Backend Social OAuth Configuration & Domain Matrix.

Provides centralized provider metadata, default scopes, developer portal URLs,
and authorized redirect URI resolvers matching production and development domains.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
from backend.app.config import get_settings


class PlatformOAuthConfig(BaseModel):
    name: str
    provider: str
    display_name: str
    authorization_url: str
    token_url: str
    default_scopes: List[str]
    callback_path: str
    developer_portal_url: str
    documentation_url: str
    pkce_required: bool = False
    response_type: str = "code"


SOCIAL_OAUTH_REGISTRY: Dict[str, PlatformOAuthConfig] = {
    "meta": PlatformOAuthConfig(
        name="Meta",
        provider="meta",
        display_name="Meta (Facebook & Instagram)",
        authorization_url="https://www.facebook.com/v20.0/dialog/oauth",
        token_url="https://graph.facebook.com/v20.0/oauth/access_token",
        default_scopes=[
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_posts",
            "instagram_basic",
            "instagram_content_publish",
            "instagram_manage_insights",
        ],
        callback_path="/api/auth/meta/callback",
        developer_portal_url="https://developers.facebook.com/apps",
        documentation_url="https://developers.facebook.com/docs/facebook-login",
        pkce_required=False,
    ),
    "facebook": PlatformOAuthConfig(
        name="Facebook",
        provider="facebook",
        display_name="Facebook Pages",
        authorization_url="https://www.facebook.com/v20.0/dialog/oauth",
        token_url="https://graph.facebook.com/v20.0/oauth/access_token",
        default_scopes=[
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_posts",
            "read_insights",
        ],
        callback_path="/api/auth/meta/callback",
        developer_portal_url="https://developers.facebook.com/apps",
        documentation_url="https://developers.facebook.com/docs/pages",
        pkce_required=False,
    ),
    "instagram": PlatformOAuthConfig(
        name="Instagram",
        provider="instagram",
        display_name="Instagram Business",
        authorization_url="https://www.facebook.com/v20.0/dialog/oauth",
        token_url="https://graph.facebook.com/v20.0/oauth/access_token",
        default_scopes=[
            "instagram_basic",
            "instagram_content_publish",
            "instagram_manage_insights",
            "pages_show_list",
            "pages_read_engagement",
        ],
        callback_path="/api/auth/meta/callback",
        developer_portal_url="https://developers.facebook.com/apps",
        documentation_url="https://developers.facebook.com/docs/instagram-api",
        pkce_required=False,
    ),
    "x": PlatformOAuthConfig(
        name="X",
        provider="x",
        display_name="X (Twitter v2)",
        authorization_url="https://twitter.com/i/oauth2/authorize",
        token_url="https://api.twitter.com/2/oauth2/token",
        default_scopes=[
            "tweet.read",
            "tweet.write",
            "users.read",
            "offline.access",
        ],
        callback_path="/api/auth/twitter/callback",
        developer_portal_url="https://developer.twitter.com/en/portal/dashboard",
        documentation_url="https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code",
        pkce_required=True,
    ),
    "twitter": PlatformOAuthConfig(
        name="Twitter",
        provider="twitter",
        display_name="X (Twitter v2)",
        authorization_url="https://twitter.com/i/oauth2/authorize",
        token_url="https://api.twitter.com/2/oauth2/token",
        default_scopes=[
            "tweet.read",
            "tweet.write",
            "users.read",
            "offline.access",
        ],
        callback_path="/api/auth/twitter/callback",
        developer_portal_url="https://developer.twitter.com/en/portal/dashboard",
        documentation_url="https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code",
        pkce_required=True,
    ),
    "linkedin": PlatformOAuthConfig(
        name="LinkedIn",
        provider="linkedin",
        display_name="LinkedIn",
        authorization_url="https://www.linkedin.com/oauth/v2/authorization",
        token_url="https://www.linkedin.com/oauth/v2/accessToken",
        default_scopes=[
            "openid",
            "profile",
            "email",
            "w_member_social",
            "r_organization_social",
            "w_organization_social",
        ],
        callback_path="/api/auth/linkedin/callback",
        developer_portal_url="https://www.linkedin.com/developers/apps",
        documentation_url="https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow",
        pkce_required=False,
    ),
    "google": PlatformOAuthConfig(
        name="Google",
        provider="google",
        display_name="Google / YouTube",
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        default_scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.upload",
        ],
        callback_path="/api/auth/google/callback",
        developer_portal_url="https://console.cloud.google.com/apis/credentials",
        documentation_url="https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps",
        pkce_required=False,
    ),
    "youtube": PlatformOAuthConfig(
        name="YouTube",
        provider="youtube",
        display_name="YouTube",
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        default_scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.upload",
        ],
        callback_path="/api/auth/google/callback",
        developer_portal_url="https://console.cloud.google.com/apis/credentials",
        documentation_url="https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps",
        pkce_required=False,
    ),
}


def get_redirect_uri(provider: str, custom_base_url: Optional[str] = None) -> str:
    """Resolve exact callback URI for a given provider based on backend/frontend settings."""
    settings = get_settings()
    base = (custom_base_url or settings.FRONTEND_URL or "http://localhost:3000").rstrip("/")
    platform_key = provider.lower()
    config = SOCIAL_OAUTH_REGISTRY.get(platform_key)
    if not config:
        raise ValueError(f"Unknown social platform provider: {provider}")
    return f"{base}{config.callback_path}"
