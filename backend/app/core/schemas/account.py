"""Account-related Pydantic schemas for API contracts."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr


class SocialAccountBase(BaseModel):
    """Base social account schema."""
    platform: str = Field(..., description="Platform name")
    platform_user_id: str = Field(..., description="Platform-specific user ID")
    username: str = Field(..., description="Platform username")
    display_name: Optional[str] = Field(None, description="Display name")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    account_type: Optional[str] = Field(None, description="Account type (personal, business, creator)")
    is_active: bool = Field(default=True, description="Account connection status")


class ConnectAccountRequest(BaseModel):
    """Request to connect a social account."""
    platform: str = Field(..., description="Platform to connect")
    authorization_code: str = Field(..., description="OAuth authorization code")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    state: Optional[str] = Field(None, description="OAuth state parameter")
    permissions: Optional[List[str]] = Field(default=[], description="Requested permissions")


class SocialAccountResponse(SocialAccountBase):
    """Response schema for social account."""
    id: str = Field(..., description="Internal account ID")
    user_id: str = Field(..., description="Owner user ID")
    connected_at: datetime = Field(..., description="Connection timestamp")
    last_synced_at: Optional[datetime] = Field(None, description="Last sync timestamp")
    token_expires_at: Optional[datetime] = Field(None, description="Access token expiry")
    permissions: List[str] = Field(default=[], description="Granted permissions")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Platform-specific metadata")


class SocialAccountListResponse(BaseModel):
    """Response for listing social accounts."""
    accounts: List[SocialAccountResponse]
    total: int = Field(..., ge=0)


class UpdateAccountRequest(BaseModel):
    """Request to update account settings."""
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class DisconnectAccountResponse(BaseModel):
    """Response for account disconnection."""
    id: str
    platform: str
    disconnected: bool = True


class AccountInsights(BaseModel):
    """Account-level insights."""
    platform: str
    account_id: str
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None
    impressions: Optional[int] = None
    reach: Optional[int] = None
    profile_views: Optional[int] = None
    website_clicks: Optional[int] = None
    email_contacts: Optional[int] = None
    phone_call_clicks: Optional[int] = None
    fetched_at: Optional[datetime] = None


class FollowerDemographics(BaseModel):
    """Follower demographics breakdown."""
    age_gender: Optional[Dict[str, Dict[str, int]]] = Field(None, description="Age/gender distribution")
    top_countries: Optional[Dict[str, int]] = Field(None, description="Top countries")
    top_cities: Optional[Dict[str, int]] = Field(None, description="Top cities")
    locales: Optional[Dict[str, int]] = Field(None, description="Language locales")


class AccountProfile(BaseModel):
    """Account profile details."""
    id: str
    platform: str
    username: str
    display_name: Optional[str] = None
    biography: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None
    account_type: Optional[str] = None
    is_verified: Optional[bool] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None