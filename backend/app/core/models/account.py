"""Social Account model."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import Base


class AccountStatus(str, enum.Enum):
    """Social account connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    ERROR = "error"
    PENDING = "pending"


class SocialAccount(Base):
    """Social media account connected by a user."""

    __tablename__ = "social_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # instagram, facebook, x, linkedin, youtube
    platform_account_id: Mapped[str] = mapped_column(String(255), nullable=False)  # Platform's user ID
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Display name
    account_username: Mapped[str] = mapped_column(String(255), nullable=False)  # Handle/username
    access_token_ref: Mapped[str] = mapped_column(String(255), nullable=True)  # Reference to encrypted token in vault
    refresh_token_ref: Mapped[str] = mapped_column(String(255), nullable=True)  # Reference to encrypted refresh token
    token_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus), default=AccountStatus.PENDING, nullable=False, index=True
    )
    capabilities: Mapped[List[str]] = mapped_column(JSON, default=list)  # List of PlatformCapability values
    follower_count: Mapped[int] = mapped_column(default=0)
    following_count: Mapped[int] = mapped_column(default=0)
    posts_count: Mapped[int] = mapped_column(default=0)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="social_accounts")
    publications: Mapped[list["PostPublication"]] = relationship(
        "PostPublication", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SocialAccount(id={self.id}, platform={self.platform_id}, username={self.account_username})>"