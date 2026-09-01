"""Core security and authentication utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import secrets
import hashlib
import hmac
import bcrypt

from jose import jwt, JWTError

from backend.app.config import get_settings
from backend.app.core.errors import AuthenticationError, TokenExpiredError

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for a password."""
    salt = bcrypt.gensalt(rounds=getattr(settings, "BCRYPT_ROUNDS", 12))
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError(message="Token has expired")
    except JWTError as e:
        raise AuthenticationError(message=f"Invalid token: {str(e)}")


def verify_token(token: str, expected_type: str = "access") -> str:
    """Verify a token and return the subject (user_id)."""
    payload = decode_token(token)
    token_type = payload.get("type")
    if token_type != expected_type:
        raise AuthenticationError(message=f"Expected {expected_type} token, got {token_type}")
    sub = payload.get("sub")
    if not sub:
        raise AuthenticationError(message="Token missing subject claim")
    return sub


def generate_api_key() -> tuple[str, str, str]:
    """Generate an API key: returns (full_key, key_prefix, key_hash)."""
    raw_key = secrets.token_urlsafe(32)
    prefix = raw_key[:8]
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return raw_key, prefix, key_hash


def verify_api_key(raw_key: str, key_hash: str) -> bool:
    """Verify an API key against its stored SHA-256 hash."""
    computed_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return hmac.compare_digest(computed_hash, key_hash)
