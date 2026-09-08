"""Durable sessions with atomic, single-use refresh rotation across workers."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from fastapi import HTTPException
from backend.app.db.models import AuthSession
from backend.app.core.security import create_access_token, create_refresh_token, decode_token
from backend.app.config import get_settings


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


async def issue_session(db, user_id, days=None):
    days = days or get_settings().JWT_REFRESH_TOKEN_EXPIRE_DAYS
    sid = secrets.token_hex(32)
    access = create_access_token(user_id, extra_claims={"sid": sid})
    refresh = create_refresh_token(user_id, timedelta(days=days), {"sid": sid})
    db.add(AuthSession(id=sid, user_id=user_id, refresh_hash=digest(refresh),
                       expires_at=now()+timedelta(days=days), revoked=False))
    await db.commit()
    return access, refresh


async def validate_session(db, token, user_id):
    payload = decode_token(token)
    sid = payload.get("sid")
    session = await db.scalar(select(AuthSession).where(
        AuthSession.id == sid, AuthSession.user_id == user_id,
        AuthSession.revoked.is_(False), AuthSession.expires_at > now()))
    if not session:
        raise HTTPException(401, "Session expired or revoked. Please sign in again.")
    return session


async def rotate_session(db, token, user_id):
    session = await validate_session(db, token, user_id)
    remaining = session.expires_at - now()
    refresh = create_refresh_token(user_id, remaining, {"sid": session.id})
    result = await db.execute(update(AuthSession).where(
        AuthSession.id == session.id, AuthSession.revoked.is_(False),
        AuthSession.refresh_hash == digest(token)
    ).values(refresh_hash=digest(refresh)))
    if result.rowcount != 1:
        await db.rollback()
        raise HTTPException(401, "Refresh token already used or revoked.")
    await db.commit()
    return create_access_token(user_id, extra_claims={"sid": session.id}), refresh


async def revoke_all(db, user_id):
    await db.execute(update(AuthSession).where(AuthSession.user_id == user_id).values(revoked=True))
