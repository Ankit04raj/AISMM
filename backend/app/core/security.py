"""Core security, JWT tokens, API keys, password hashing, and RFC 6238 TOTP 2FA utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union, Set
import secrets
import hashlib
import hmac
import struct
import time
import base64
import urllib.parse
import bcrypt

from jose import jwt, JWTError

from backend.app.config import get_settings
from backend.app.core.errors import AuthenticationError, TokenExpiredError

settings = get_settings()

# In-memory revoked tokens store (or synced with Redis in multi-worker)
_revoked_tokens: Set[str] = set()


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
        "jti": secrets.token_hex(16),
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
        "jti": secrets.token_hex(16),
        "type": "refresh",
    }

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def revoke_token(token: str) -> None:
    """Blacklist/revoke a JWT token server-side upon logout."""
    if token:
        _revoked_tokens.add(token)


def is_token_revoked(token: str) -> bool:
    """Check if token has been revoked on logout."""
    return token in _revoked_tokens


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    if is_token_revoked(token):
        raise AuthenticationError(message="Token has been revoked upon logout")

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


# =============================================================================
# RFC 6238 Standard TOTP 2FA Implementation (Pure Python Standard Library)
# =============================================================================

def generate_totp_secret() -> str:
    """Generate RFC 6238 base32 secret key for authenticator apps."""
    return base64.b32encode(secrets.token_bytes(20)).decode("utf-8")


def generate_totp_uri(secret: str, email: str, issuer: str = "AISMM") -> str:
    """Generate standard otpauth:// URI for QR code generation."""
    label = urllib.parse.quote(f"{issuer}:{email}")
    issuer_enc = urllib.parse.quote(issuer)
    return f"otpauth://totp/{label}?secret={secret}&issuer={issuer_enc}&algorithm=SHA1&digits=6&period=30"


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """Verify 6-digit TOTP code against base32 secret with ±1 time-step window tolerance."""
    if not secret or not code:
        return False
    try:
        clean_code = str(code).strip()
        key = base64.b32decode(secret, casefold=True)
        current_time_step = int(time.time() // 30)

        for step in range(current_time_step - window, current_time_step + window + 1):
            msg = struct.pack(">Q", step)
            h = hmac.new(key, msg, hashlib.sha1).digest()
            offset = h[-1] & 0x0F
            truncated_hash = struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF
            expected_code = str(truncated_hash % 1_000_000).zfill(6)
            if hmac.compare_digest(expected_code, clean_code):
                return True
        return False
    except Exception:
        return False
