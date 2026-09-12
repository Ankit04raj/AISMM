"""Persistent OAuth state service — replaces in-memory adapter stores.

Provides database-backed storage and retrieval for OAuth 2.0 / PKCE state tokens,
code verifiers, and nonces, enabling reliable multi-worker/cross-process callbacks.
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import OAuthState
from backend.app.db.session import get_db_context
from backend.app.core.audit import default_audit_logger, AuditEventType


class OAuthStateService:
    """Persistent OAuth state — multi-worker safe, single-use, time-bound."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_nonce() -> str:
        return secrets.token_urlsafe(32)

    async def create_state(
        self,
        user_id: str,
        platform: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
        nonce: Optional[str] = None,
        state: Optional[str] = None,
        expires_in_minutes: int = 15,
    ) -> OAuthState:
        """Create and persist a new OAuth state record."""
        db = self.db
        if db is None:
            async with get_db_context() as session:
                return await self._create(session, user_id, platform, redirect_uri,
                                          code_verifier, nonce, state, expires_in_minutes)
        return await self._create(db, user_id, platform, redirect_uri,
                                  code_verifier, nonce, state, expires_in_minutes)

    async def _create(
        self,
        session: AsyncSession,
        user_id: str,
        platform: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
        nonce: Optional[str] = None,
        state: Optional[str] = None,
        expires_in_minutes: int = 15,
    ) -> OAuthState:
        from uuid import UUID
        state_value = state or self.generate_state()
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=expires_in_minutes)
        record = OAuthState(
            user_id=UUID(str(user_id)) if isinstance(user_id, str) else user_id,
            platform=platform,
            state=state_value,
            code_verifier=code_verifier,
            nonce=nonce,
            redirect_uri=redirect_uri,
            expires_at=expires_at,
            consumed=False,
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    async def get_state(
        self,
        state: str,
        user_id: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> Optional[OAuthState]:
        db = self.db
        query = select(OAuthState).where(
            OAuthState.state == state,
            OAuthState.consumed.is_(False),
            OAuthState.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
        )
        if user_id is not None:
            from uuid import UUID
            query = query.where(OAuthState.user_id == (UUID(str(user_id)) if isinstance(user_id, str) else user_id))
        if platform is not None:
            query = query.where(OAuthState.platform == platform)
        if db is None:
            async with get_db_context() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def consume_state(self, state: str, user_id: Optional[str] = None) -> bool:
        """Consume (mark used) a state record. Returns True if exactly one row consumed."""
        from uuid import UUID
        conditions = [
            OAuthState.state == state,
            OAuthState.consumed.is_(False),
            OAuthState.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
        ]
        if user_id is not None:
            conditions.append(OAuthState.user_id == (UUID(str(user_id)) if isinstance(user_id, str) else user_id))
        query = (
            update(OAuthState)
            .where(*conditions)
            .values(consumed=True)
        )
        db = self.db
        if db is None:
            async with get_db_context() as session:
                result = await session.execute(query)
                await session.commit()
                return result.rowcount == 1
        result = await db.execute(query)
        await db.commit()
        return result.rowcount == 1

    async def get_code_verifier(self, state: str, user_id: Optional[str] = None) -> Optional[str]:
        state_record = await self.get_state(state, user_id=user_id)
        if state_record:
            return state_record.code_verifier
        return None

    async def cleanup_expired_states(self) -> int:
        """Delete expired OAuth state records."""
        query = delete(OAuthState).where(
            OAuthState.expires_at < datetime.now(timezone.utc).replace(tzinfo=None),
        )
        db = self.db
        if db is None:
            async with get_db_context() as session:
                result = await session.execute(query)
                await session.commit()
                return result.rowcount
        result = await db.execute(query)
        await db.commit()
        return result.rowcount

    async def delete_state_by_state(self, state: str) -> bool:
        query = delete(OAuthState).where(OAuthState.state == state)
        db = self.db
        if db is None:
            async with get_db_context() as session:
                result = await session.execute(query)
                await session.commit()
                return result.rowcount > 0
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
