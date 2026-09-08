"""Shared API dependencies: database sessions and authenticated user context."""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.core.security import verify_token
from backend.app.core.errors import AuthenticationError, TokenExpiredError

# Security scheme extracting Bearer tokens
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate Bearer JWT access token and return current authenticated User model."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        user_id_str = verify_token(token, expected_type="access")
        user_uuid = UUID(user_id_str)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please refresh your session.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (AuthenticationError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from backend.app.services.session_service import validate_session
    await validate_session(db, token, user_uuid)

    # Query user from DB
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Validate that the current user has completed email verification.
    For phone-verified users (where phone_number exists and phone_verified is True),
    email verification is considered satisfied.
    """
    # Check if user has phone number and phone is verified
    has_phone_verified = current_user.phone_number and current_user.phone_verified
    # Check if user has email verified
    has_email_verified = current_user.is_verified

    if not (has_email_verified or has_phone_verified):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account verification required. Please verify your email or phone number.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def get_current_email_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Validate that the current user has completed email verification specifically.
    Use this for endpoints that strictly require email verification.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please verify your email address.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_phone_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Validate that the current user has completed phone verification specifically.
    Use this for endpoints that strictly require phone verification.
    """
    if not current_user.phone_number or not current_user.phone_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Phone verification required. Please verify your phone number.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure current user has administrative/superuser privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )
    return current_user
