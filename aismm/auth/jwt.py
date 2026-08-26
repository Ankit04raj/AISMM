"""
JWT Token Management

Access tokens (short-lived) and refresh tokens (longer-lived) with rotation.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from pydantic import BaseModel

from aismm.config import settings


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # User ID
    type: str  # "access" or "refresh"
    jti: str  # Token ID for revocation
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    scopes: list[str] = []


def create_access_token(
    user_id: str,
    scopes: Optional[list[str]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a short-lived access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    
    payload = TokenPayload(
        sub=user_id,
        type="access",
        jti=str(uuid.uuid4()),
        exp=int(expire.timestamp()),
        iat=int(now.timestamp()),
        scopes=scopes or []
    )
    
    return jwt.encode(
        payload.model_dump(),
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(user_id: str) -> str:
    """Create a longer-lived refresh token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = TokenPayload(
        sub=user_id,
        type="refresh",
        jti=str(uuid.uuid4()),
        exp=int(expire.timestamp()),
        iat=int(now.timestamp())
    )
    
    return jwt.encode(
        payload.model_dump(),
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


def verify_token(token: str, expected_type: str = "access") -> TokenPayload:
    """Verify token is valid and of expected type."""
    payload = decode_token(token)
    
    if payload.type != expected_type:
        raise ValueError(f"Expected {expected_type} token, got {payload.type}")
    
    # Check expiration
    if datetime.fromtimestamp(payload.exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Token expired")
    
    return payload


async def get_current_user(token: str) -> Dict[str, Any]:
    """Get current user from access token (for FastAPI dependency)."""
    payload = verify_token(token, "access")
    return {
        "user_id": payload.sub,
        "scopes": payload.scopes,
        "token_id": payload.jti
    }
