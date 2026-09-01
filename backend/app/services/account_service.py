"""Social account service - Business logic for social account management."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.db.models import SocialAccount, User
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.schemas.account import (
    ConnectAccountRequest,
    SocialAccountResponse,
    UpdateAccountRequest,
    DisconnectAccountResponse,
    AccountInsights,
    FollowerDemographics,
    AccountProfile,
)
from backend.app.core.errors import NotFoundError, ValidationError, PlatformError


class AccountService:
    """Service for managing social accounts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def connect_account(
        self,
        user_id: UUID,
        request: ConnectAccountRequest,
    ) -> SocialAccountResponse:
        """Connect a social account via OAuth."""
        if not PlatformRegistry.is_registered(request.platform):
            raise ValidationError(f"Unsupported platform: {request.platform}")

        adapter = PlatformRegistry.get_adapter(request.platform)
        if not adapter:
            raise PlatformError(f"Adapter not available for {request.platform}")

        # Exchange code for tokens
        token_response = await adapter.auth.exchange_code(
            code=request.authorization_code,
            redirect_uri=request.redirect_uri,
        )

        # Get user profile from platform
        profile = await adapter.auth.get_user_profile(token_response["access_token"])

        # Check if account already connected
        existing = await self.db.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.user_id == user_id,
                    SocialAccount.platform == request.platform,
                    SocialAccount.platform_user_id == str(profile["id"]),
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValidationError("Account already connected")

        expires_in = token_response.get("expires_in")
        expiry_dt = None
        if expires_in:
            expiry_dt = datetime.fromtimestamp(expires_in + int(datetime.now(timezone.utc).timestamp()), tz=timezone.utc).replace(tzinfo=None)

        # Create social account
        account = SocialAccount(
            user_id=user_id,
            platform=request.platform,
            platform_user_id=str(profile["id"]),
            username=profile.get("username"),
            display_name=profile.get("name") or profile.get("display_name"),
            profile_image_url=profile.get("profile_picture_url"),
            account_type=profile.get("account_type"),
            access_token=token_response.get("access_token"),
            refresh_token=token_response.get("refresh_token"),
            token_expires_at=expiry_dt,
            permissions=token_response.get("scope", "").split(",") if isinstance(token_response.get("scope"), str) else [],
            account_metadata=profile,
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        return self._to_response(account)

    async def get_account(self, account_id: UUID, user_id: UUID) -> Optional[SocialAccount]:
        """Get a social account by ID."""
        result = await self.db.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.id == account_id,
                    SocialAccount.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_accounts(
        self,
        user_id: UUID,
        platform: Optional[str] = None,
    ) -> List[SocialAccount]:
        """Get all social accounts for a user."""
        query = select(SocialAccount).where(SocialAccount.user_id == user_id)

        if platform:
            query = query.where(SocialAccount.platform == platform)

        result = await self.db.execute(query.order_by(SocialAccount.connected_at.desc()))
        return result.scalars().all()

    async def get_account_responses(
        self,
        user_id: UUID,
        platform: Optional[str] = None,
    ) -> List[SocialAccountResponse]:
        """Get social account responses for a user."""
        accounts = await self.get_accounts(user_id, platform)
        return [self._to_response(acc) for acc in accounts]

    async def update_account(
        self,
        account_id: UUID,
        user_id: UUID,
        request: UpdateAccountRequest,
    ) -> Optional[SocialAccountResponse]:
        """Update a social account."""
        account = await self.get_account(account_id, user_id)
        if not account:
            return None

        if request.display_name is not None:
            account.display_name = request.display_name
        if request.is_active is not None:
            account.is_active = request.is_active
        if request.metadata is not None:
            account.account_metadata = {**(account.account_metadata or {}), **request.metadata}

        await self.db.commit()
        await self.db.refresh(account)
        return self._to_response(account)

    async def disconnect_account(self, account_id: UUID, user_id: UUID) -> DisconnectAccountResponse:
        """Disconnect a social account."""
        account = await self.get_account(account_id, user_id)
        if not account:
            raise NotFoundError("Account not found")

        adapter = PlatformRegistry.get_adapter(account.platform)
        if adapter and hasattr(adapter, "auth") and account.access_token:
            try:
                await adapter.auth.revoke_token(account.access_token)
            except Exception:
                pass

        platform = account.platform
        account_id_str = str(account.id)

        await self.db.delete(account)
        await self.db.commit()

        return DisconnectAccountResponse(
            id=account_id_str,
            platform=platform,
            disconnected=True,
        )

    async def refresh_token(self, account_id: UUID, user_id: UUID) -> bool:
        """Refresh access token for an account."""
        account = await self.get_account(account_id, user_id)
        if not account or not account.refresh_token:
            return False

        adapter = PlatformRegistry.get_adapter(account.platform)
        if not adapter or not hasattr(adapter, "auth"):
            return False

        try:
            new_tokens = await adapter.auth.refresh_access_token(account.refresh_token)
            account.access_token = new_tokens["access_token"]
            if "refresh_token" in new_tokens:
                account.refresh_token = new_tokens["refresh_token"]
            if new_tokens.get("expires_in"):
                account.token_expires_at = datetime.fromtimestamp(
                    new_tokens["expires_in"] + int(datetime.now(timezone.utc).timestamp()), tz=timezone.utc
                ).replace(tzinfo=None)
            await self.db.commit()
            return True
        except Exception:
            return False

    async def get_account_insights(
        self,
        account_id: UUID,
        user_id: UUID,
    ) -> Optional[AccountInsights]:
        """Get insights for a social account."""
        account = await self.get_account(account_id, user_id)
        if not account or not account.is_active:
            return None

        adapter = PlatformRegistry.get_adapter(account.platform)
        if not adapter:
            return None

        try:
            insights = await adapter.fetch_account_insights()
            norm = insights.get("normalized", {}) if isinstance(insights, dict) else {}
            return AccountInsights(
                platform=account.platform,
                account_id=account.platform_user_id,
                followers_count=norm.get("followers_count"),
                following_count=norm.get("following_count"),
                media_count=norm.get("media_count"),
                impressions=norm.get("impressions"),
                reach=norm.get("reach"),
                profile_views=norm.get("profile_views"),
                website_clicks=norm.get("clicks"),
                email_contacts=norm.get("email_contacts"),
                phone_call_clicks=norm.get("phone_call_clicks"),
                fetched_at=datetime.now(timezone.utc),
            )
        except Exception:
            return None

    async def get_account_profile(
        self,
        account_id: UUID,
        user_id: UUID,
    ) -> Optional[AccountProfile]:
        """Get profile details for an account."""
        account = await self.get_account(account_id, user_id)
        if not account:
            return None

        adapter = PlatformRegistry.get_adapter(account.platform)
        if not adapter:
            return self._to_profile(account)

        try:
            profile = await adapter.get_profile()
            return AccountProfile(
                id=str(account.id),
                platform=account.platform,
                username=profile.get("username", account.username or ""),
                display_name=profile.get("name") or profile.get("display_name", account.display_name),
                biography=profile.get("biography"),
                website=profile.get("website"),
                profile_image_url=profile.get("profile_picture_url", account.profile_image_url),
                account_type=profile.get("account_type", account.account_type),
                is_verified=profile.get("is_verified"),
                followers_count=profile.get("followers_count"),
                following_count=profile.get("follows_count"),
                media_count=profile.get("media_count"),
            )
        except Exception:
            return self._to_profile(account)

    def _to_response(self, account: SocialAccount) -> SocialAccountResponse:
        """Convert model to response schema."""
        return SocialAccountResponse(
            id=str(account.id),
            user_id=str(account.user_id),
            platform=account.platform,
            platform_user_id=account.platform_user_id,
            username=account.username or "",
            display_name=account.display_name,
            profile_image_url=account.profile_image_url,
            account_type=account.account_type,
            is_active=account.is_active if account.is_active is not None else True,
            connected_at=account.connected_at or datetime.now(timezone.utc),
            last_synced_at=account.last_synced_at,
            token_expires_at=account.token_expires_at,
            permissions=account.permissions or [],
            metadata=account.account_metadata or {},
        )

    def _to_profile(self, account: SocialAccount) -> AccountProfile:
        """Convert model to profile schema."""
        return AccountProfile(
            id=str(account.id),
            platform=account.platform,
            username=account.username or "",
            display_name=account.display_name,
            profile_image_url=account.profile_image_url,
            account_type=account.account_type,
        )
