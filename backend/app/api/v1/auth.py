"""Authentication API router: User Auth (Register, Login, Refresh, Me) and Platform OAuth."""

from datetime import datetime, timezone, timedelta
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.config import get_settings
from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from backend.app.api.deps import get_current_user
from backend.app.core.rate_limit import rate_limit_guard
from backend.app.core.audit import default_audit_logger, AuditEventType
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.schemas.auth import (
    RegisterRequest,
    UserLoginRequest,
    UserLoginResponse,
    UserProfile,
    AppRefreshTokenRequest,
    AppTokenRefreshResponse,
    OAuthInitRequest,
    OAuthInitResponse,
    OAuthCallbackRequest,
    OAuthTokenResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


# =============================================================================
# Application User Authentication Endpoints (JWT / Bcrypt)
# =============================================================================

@router.post(
    "/register",
    response_model=UserLoginResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_guard(max_requests=10, window_seconds=60))],
)
async def register_user(
    request: RegisterRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new application user and issue initial access & refresh JWT tokens."""
    client_ip = req.client.host if req.client else "127.0.0.1"
    normalized_email = request.email.strip().lower()

    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == normalized_email))
    if existing.scalar_one_or_none():
        default_audit_logger.log_event(
            event_type=AuditEventType.AUTH_LOGIN_FAILED,
            user_id=normalized_email,
            ip_address=client_ip,
            action="USER_REGISTRATION_FAILED_DUPLICATE_EMAIL",
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Create new user
    user = User(
        email=normalized_email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        is_active=True,
        is_verified=False,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Issue JWT tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Audit log successful registration
    default_audit_logger.log_event(
        event_type=AuditEventType.AUTH_LOGIN_SUCCESS,
        user_id=str(user.id),
        ip_address=client_ip,
        action="USER_REGISTERED_AND_LOGGED_IN",
        status="SUCCESS",
    )

    profile = UserProfile(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )

    return UserLoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user=profile,
    )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    dependencies=[Depends(rate_limit_guard(max_requests=10, window_seconds=60))],
)
async def login_user(
    request: UserLoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate an application user via email & password and return signed JWT tokens."""
    client_ip = req.client.host if req.client else "127.0.0.1"
    normalized_email = request.email.strip().lower()
    result = await db.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        default_audit_logger.log_event(
            event_type=AuditEventType.AUTH_LOGIN_FAILED,
            user_id=normalized_email,
            ip_address=client_ip,
            action="USER_LOGIN_FAILED_INVALID_CREDENTIALS",
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        default_audit_logger.log_event(
            event_type=AuditEventType.AUTH_LOGIN_FAILED,
            user_id=str(user.id),
            ip_address=client_ip,
            action="USER_LOGIN_FAILED_ACCOUNT_DEACTIVATED",
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    # Generate tokens with optional extended duration for remember_me
    refresh_delta = timedelta(days=30) if request.remember_me else None
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id, expires_delta=refresh_delta)

    # Audit log login success
    default_audit_logger.log_event(
        event_type=AuditEventType.AUTH_LOGIN_SUCCESS,
        user_id=str(user.id),
        ip_address=client_ip,
        action="USER_LOGIN_SUCCESS",
        status="SUCCESS",
    )

    profile = UserProfile(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )

    return UserLoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        user=profile,
    )


@router.post(
    "/refresh",
    response_model=AppTokenRefreshResponse,
    dependencies=[Depends(rate_limit_guard(max_requests=30, window_seconds=60))],
)
async def refresh_app_token(
    request: AppRefreshTokenRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a valid JWT refresh token for a newly signed access token."""
    client_ip = req.client.host if req.client else "127.0.0.1"
    try:
        user_id_str = verify_token(request.refresh_token, expected_type="refresh")
        user_uuid = UUID(user_id_str)
    except Exception as e:
        default_audit_logger.log_event(
            event_type=AuditEventType.AUTH_LOGIN_FAILED,
            user_id="unknown",
            ip_address=client_ip,
            action="TOKEN_REFRESH_FAILED_INVALID_TOKEN",
            status="FAILURE",
            details={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account invalid or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    default_audit_logger.log_event(
        event_type=AuditEventType.AUTH_TOKEN_REFRESH,
        user_id=str(user.id),
        ip_address=client_ip,
        action="TOKEN_REFRESH_SUCCESS",
        status="SUCCESS",
    )

    return AppTokenRefreshResponse(
        access_token=new_access_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Retrieve the currently authenticated user's profile."""
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )


# =============================================================================
# Social Platform OAuth Flows (Instagram, Facebook, X, LinkedIn, YouTube)
# =============================================================================

@router.post(
    "/oauth/init",
    response_model=OAuthInitResponse,
    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def oauth_init(request: OAuthInitRequest):
    """Initiate OAuth flow for a social media platform."""
    if not PlatformRegistry.is_registered(request.platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

    adapter = PlatformRegistry.get_adapter(request.platform)
    if not adapter or not hasattr(adapter, "auth"):
        raise HTTPException(status_code=400, detail=f"OAuth not supported for: {request.platform}")

    auth_url, state = adapter.auth.get_authorization_url(state=request.state)
    return OAuthInitResponse(
        authorization_url=auth_url,
        state=state,
        expires_at=adapter.auth.get_token_expiry(600),
    )


@router.post(
    "/oauth/callback",
    response_model=OAuthTokenResponse,
    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def oauth_callback(request: OAuthCallbackRequest):
    """Handle OAuth callback and code exchange."""
    if not PlatformRegistry.is_registered(request.platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

    adapter = PlatformRegistry.get_adapter(request.platform)
    if not adapter or not hasattr(adapter, "auth"):
        raise HTTPException(status_code=400, detail=f"OAuth not supported for: {request.platform}")

    token_response = await adapter.auth.exchange_code(
        code=request.code,
        redirect_uri=request.redirect_uri,
    )
    return OAuthTokenResponse(
        access_token=token_response["access_token"],
        token_type=token_response.get("token_type", "Bearer"),
        expires_in=token_response.get("expires_in", 3600),
        refresh_token=token_response.get("refresh_token"),
        scope=token_response.get("scope"),
    )


@router.post(
    "/oauth/refresh",
    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def oauth_refresh(request: RefreshTokenRequest):
    """Refresh platform access token."""
    if not PlatformRegistry.is_registered(request.platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

    adapter = PlatformRegistry.get_adapter(request.platform)
    if not adapter or not hasattr(adapter, "auth"):
        raise HTTPException(status_code=400, detail=f"OAuth refresh not supported for: {request.platform}")

    refreshed = await adapter.auth.refresh_access_token(request.refresh_token)
    return refreshed
