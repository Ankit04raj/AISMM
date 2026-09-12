"""Centralized token retrieval service with automatic refresh logic.

Provides `get_valid_access_token(account_id, user_id)` which:
1. Loads the SocialAccount from the database.
2. Checks `token_expires_at`. If expired (or within 5 minutes), triggers refresh.
3. Updates the database with new tokens and expiry.
4. Returns the active token string.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import SocialAccount
from backend.app.db.session import get_db_context


class TokenServiceError(Exception):
    pass


class TokenNotFoundError(TokenServiceError):
    pass


class TokenRefreshFailedError(TokenServiceError):
    pass


class TokenService:
    """Centralized access-token retrieval with automatic refresh."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def get_valid_access_token(
        self,
        account_id: UUID,
        user_id: UUID,
    ) -> str:
        """Retrieve a valid access token for the account, refreshing if needed."""
        db = self.db
        # Load account
        query = select(SocialAccount).where(
            SocialAccount.id == (str(account_id) if not isinstance(account_id, UUID) else account_id),
            SocialAccount.user_id == (str(user_id) if not isinstance(user_id, UUID) else user_id),
        )
        session = db
        if session is None:
            async with get_db_context() as session:
                result = await session.execute(query)
                account = result.scalar_one_or_none()
                if account is None:
                    raise TokenNotFoundError(f"SocialAccount {account_id} not found for user {user_id}")
                token = await self._process_account(session, account)
                return token
        else:
            result = await session.execute(query)
            account = result.scalar_one_or_none()
            if account is None:
                raise TokenNotFoundError(f"SocialAccount {account_id} not found for user {user_id}")
            return await self._process_account(session, account)

    async def _process_account(self, session: AsyncSession, account: SocialAccount) -> str:
        """Check expiry and refresh if needed, then return the token."""
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        needs_refresh = True
        if account.token_expires_at is not None:
            expires_naive = account.token_expires_at.replace(tzinfo=None) if hasattr(account.token_expires_at, "replace") else account.token_expires_at
            needs_refresh = (expires_naive - timedelta(minutes=5)) < now_utc

        if needs_refresh and account.refresh_token:
            # Import service-level refresh
            from backend.app.services.account_service import AccountService
            service = AccountService(session)
            refreshed = await service.refresh_token(account.id, account.user_id)
            if refreshed:
                # Refresh the model instance
                await session.refresh(account)
            else:
                # If refresh fails, try to use existing token as best-effort
                # (provider may still accept it)
                pass
        else:
            # Token is still valid; refresh model from DB to get latest values
            await session.refresh(account)

        # Decrypt access token through the vault mechanism (EncryptedText decorator handles this)
        # The access_token property is already decrypted when read from DB
        if not account.access_token:
            raise TokenNotFoundError(f"Access token is empty for account {account.id}")
        return account.access_token

    async def get_account_by_id(self, account_id: UUID, user_id: UUID) -> Optional[SocialAccount]:
        query = select(SocialAccount).where(
            SocialAccount.id == (str(account_id) if not isinstance(account_id, UUID) else account_id),
            SocialAccount.user_id == (str(user_id) if not isinstance(user_id, UUID) else user_id),
        )
        session = self.db
        if session is None:
            async with get_db_context() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
        result = await session.execute(query)
        return result.scalar_one_or_none()
