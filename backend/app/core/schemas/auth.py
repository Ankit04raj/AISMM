"""Authentication-related Pydantic schemas for API contracts."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OAuthInitRequest(BaseModel):
    """Request to initiate OAuth flow."""
    platform: str = Field(..., description="Platform to authenticate")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    state: Optional[str] = Field(None, description="Optional state parameter")
    scopes: Optional[List[str]] = Field(default=[], description="Requested scopes")


class OAuthInitResponse(BaseModel):
    """Response with authorization URL."""
    authorization_url: str = Field(..., description="URL to redirect user to")
    state: str = Field(..., description="OAuth state parameter")
    expires_at: datetime = Field(..., description="State expiry timestamp")


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request."""
    platform: str = Field(..., description="Platform")
    code: str = Field(..., description="Authorization code")
    state: Optional[str] = Field(None, description="State parameter")
    redirect_uri: str = Field(..., description="Redirect URI used")


class OAuthTokenResponse(BaseModel):
    """OAuth token response."""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token lifetime in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    scope: Optional[str] = Field(None, description="Granted scopes")


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    platform: str = Field(..., description="Platform")
    refresh_token: str = Field(..., description="Refresh token")


class TokenValidationResponse(BaseModel):
    """Token validation response."""
    valid: bool = Field(..., description="Whether token is valid")
    platform: str = Field(..., description="Platform")
    expires_at: Optional[datetime] = Field(None, description="Token expiry")
    scopes: Optional[List[str]] = Field(default=[], description="Token scopes")


class APIKeyRequest(BaseModel):
    """Request to create API key."""
    name: str = Field(..., max_length=100, description="API key name")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    expires_at: Optional[datetime] = Field(None, description="Expiry date")
    permissions: List[str] = Field(default=["read"], description="Permissions")


class APIKeyResponse(BaseModel):
    """API key response."""
    id: str
    name: str
    key_prefix: str = Field(..., description="Key prefix (last 4 chars visible)")
    created_at: datetime
    expires_at: Optional[datetime] = None
    permissions: List[str]


class UserLoginRequest(BaseModel):
    """User login request."""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Extended session")


class UserLoginResponse(BaseModel):
    """User login response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: str
    user: "UserProfile"


class UserProfile(BaseModel):
    """User profile response."""
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    is_active: bool = True
    is_verified: bool = False


class RegisterRequest(BaseModel):
    """User registration request."""
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: str = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str = Field(..., description="Reset token")
    password: str = Field(..., min_length=8, description="New password")


# Forward reference resolution
UserLoginResponse.update_forward_refs()