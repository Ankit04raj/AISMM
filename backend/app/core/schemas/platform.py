"""Models/Schemas for platform connectivity."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PlatformAccount(BaseModel):
    """Schema for a connected platform account."""
    id: str
    platform: str
    account_name: str
    account_username: str
    status: str  # connected, disconnected, error
    capabilities: List[str]
    last_sync_at: Optional[datetime] = None

class PlatformConfig(BaseModel):
    """Schema for platform capability config."""
    name: str
    display_name: str
    capabilities: List[str]
    limits: Dict[str, Any]
    supported_media: List[str]
    api_version: str
    auth_type: str
