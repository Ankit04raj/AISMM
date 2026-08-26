"""
Secure Credential Store

Encrypts and stores OAuth tokens and API keys.
Uses Fernet symmetric encryption for token storage.
"""

import os
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from aismm.config import settings
from aismm.db.session import get_db_session
from aismm.db.models import SocialAccount


@dataclass
class TokenData:
    """Stored token data."""
    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[datetime]
    scope: Optional[str]


class CredentialStore:
    """
    Secure credential storage using Fernet encryption.
    Master key derived from SECRET_KEY.
    """
    
    def __init__(self):
        self._fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet cipher from SECRET_KEY."""
        # Derive a 32-byte key from SECRET_KEY
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'aismm-credential-salt',  # Fixed salt for deterministic key
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string."""
        return self._fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypt a string."""
        return self._fernet.decrypt(encrypted.encode()).decode()
    
    async def store_tokens(
        self,
        user_id: str,
        platform_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        scope: Optional[str] = None,
        platform_account_id: Optional[str] = None,
        account_username: Optional[str] = None,
        account_name: Optional[str] = None,
    ) -> SocialAccount:
        """Store encrypted tokens in database."""
        async with get_db_session() as session:
            # Find or create social account
            from sqlalchemy import select
            result = await session.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user_id,
                    SocialAccount.platform_id == platform_id,
                    SocialAccount.platform_account_id == platform_account_id
                )
            )
            account = result.scalar_one_or_none()
            
            if not account:
                account = SocialAccount(
                    user_id=user_id,
                    platform_id=platform_id,
                    platform_account_id=platform_account_id or "unknown",
                    account_username=account_username,
                    account_name=account_name,
                    status=SocialAccount.Status.CONNECTED,
                )
                session.add(account)
            
            # Encrypt and store tokens
            account.access_token_ref = self.encrypt(access_token)
            if refresh_token:
                account.refresh_token_ref = self.encrypt(refresh_token)
            
            if expires_in:
                account.capabilities = account.capabilities or {}
                account.capabilities["token_expires_at"] = (
                    datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                ).isoformat()
            
            if scope:
                account.capabilities = account.capabilities or {}
                account.capabilities["scope"] = scope
            
            account.status = SocialAccount.Status.CONNECTED
            account.last_error = None
            account.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(account)
            return account
    
    async def get_access_token(self, user_id: str, platform_id: str, 
                               platform_account_id: Optional[str] = None) -> Optional[str]:
        """Get decrypted access token."""
        async with get_db_session() as session:
            from sqlalchemy import select
            query = select(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform_id == platform_id,
                SocialAccount.status == SocialAccount.Status.CONNECTED
            )
            if platform_account_id:
                query = query.where(SocialAccount.platform_account_id == platform_account_id)
            
            result = await session.execute(query)
            account = result.scalar_one_or_none()
            
            if not account or not account.access_token_ref:
                return None
            
            try:
                return self.decrypt(account.access_token_ref)
            except Exception:
                return None
    
    async def get_refresh_token(self, user_id: str, platform_id: str,
                                platform_account_id: Optional[str] = None) -> Optional[str]:
        """Get decrypted refresh token."""
        async with get_db_session() as session:
            from sqlalchemy import select
            query = select(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform_id == platform_id,
                SocialAccount.status == SocialAccount.Status.CONNECTED
            )
            if platform_account_id:
                query = query.where(SocialAccount.platform_account_id == platform_account_id)
            
            result = await session.execute(query)
            account = result.scalar_one_or_none()
            
            if not account or not account.refresh_token_ref:
                return None
            
            try:
                return self.decrypt(account.refresh_token_ref)
            except Exception:
                return None
    
    async def get_token_data(self, user_id: str, platform_id: str,
                             platform_account_id: Optional[str] = None) -> Optional[TokenData]:
        """Get full token data."""
        access = await self.get_access_token(user_id, platform_id, platform_account_id)
        if not access:
            return None
        
        refresh = await self.get_refresh_token(user_id, platform_id, platform_account_id)
        
        async with get_db_session() as session:
            from sqlalchemy import select
            query = select(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform_id == platform_id
            )
            if platform_account_id:
                query = query.where(SocialAccount.platform_account_id == platform_account_id)
            
            result = await session.execute(query)
            account = result.scalar_one_or_none()
            
            expires_at = None
            scope = None
            if account and account.capabilities:
                expires_str = account.capabilities.get("token_expires_at")
                if expires_str:
                    try:
                        expires_at = datetime.fromisoformat(expires_str)
                    except Exception:
                        pass
                scope = account.capabilities.get("scope")
            
            return TokenData(
                access_token=access,
                refresh_token=refresh,
                expires_at=expires_at,
                scope=scope
            )
    
    async def delete_tokens(self, user_id: str, platform_id: str,
                            platform_account_id: Optional[str] = None) -> bool:
        """Delete stored tokens (disconnect account)."""
        async with get_db_session() as session:
            from sqlalchemy import select, delete
            query = delete(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform_id == platform_id
            )
            if platform_account_id:
                query = query.where(SocialAccount.platform_account_id == platform_account_id)
            
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0
    
    async def update_account_status(self, user_id: str, platform_id: str,
                                    status: SocialAccount.Status,
                                    error: Optional[str] = None) -> bool:
        """Update account connection status."""
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user_id,
                    SocialAccount.platform_id == platform_id
                )
            )
            account = result.scalar_one_or_none()
            
            if not account:
                return False
            
            account.status = status
            account.last_error = error
            account.updated_at = datetime.utcnow()
            
            await session.commit()
            return True
    
    async def list_user_accounts(self, user_id: str) -> list[SocialAccount]:
        """List all connected accounts for a user."""
        async with get_db_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user_id
                )
            )
            return list(result.scalars().all())


# Global instance
_credential_store: Optional[CredentialStore] = None


def get_credential_store() -> CredentialStore:
    global _credential_store
    if _credential_store is None:
        _credential_store = CredentialStore()
    return _credential_store
