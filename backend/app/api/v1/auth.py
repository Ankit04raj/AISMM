"""Authentication API router: User Auth (Register, Login, Refresh, Me, 2FA, Email Verification, Logout) and Platform OAuth."""

from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import Optional
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
    revoke_token,
    generate_totp_secret,
    generate_totp_uri,
    verify_totp,
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
    VerifyEmailRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    LogoutRequest,
    OAuthInitRequest,
    OAuthInitResponse,
    OAuthCallbackRequest,
    OAuthTokenResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


# =============================================================================
# Application User Authentication Endpoints (JWT / Bcrypt / 2FA / Verification)
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

    # Create new user (defaults to unverified until email confirmation)
    user = User(
        email=normalized_email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        is_active=True,
        is_verified=False,
        is_superuser=False,
        two_factor_enabled=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Issue initial JWT tokens
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
        two_factor_enabled=user.two_factor_enabled,
    )

    return UserLoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        requires_2fa=False,
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

    # If 2FA is active, verify TOTP code
    if user.two_factor_enabled:
        if not request.two_factor_code:
            return UserLoginResponse(
                access_token="",
                token_type="Bearer",
                expires_in=0,
                refresh_token="",
                requires_2fa=True,
                user=UserProfile(
                    id=str(user.id),
                    email=user.email,
                    full_name=user.full_name,
                    avatar_url=user.avatar_url,
                    created_at=user.created_at,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    two_factor_enabled=True,
                ),
            )
        # Validate TOTP code
        if not verify_totp(user.two_factor_secret or "", request.two_factor_code):
            default_audit_logger.log_event(
                event_type=AuditEventType.AUTH_LOGIN_FAILED,
                user_id=str(user.id),
                ip_address=client_ip,
                action="USER_LOGIN_FAILED_INVALID_2FA",
                status="FAILURE",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid two-factor authentication code.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
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
        two_factor_enabled=user.two_factor_enabled,
    )

    return UserLoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        requires_2fa=False,
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


@router.post("/logout")
async def logout_user(
    req: Request,
    request: Optional[LogoutRequest] = None,
    current_user: User = Depends(get_current_user),
):
    """Invalidate session tokens server-side upon logout."""
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        revoke_token(token)

    if request and request.refresh_token:
        revoke_token(request.refresh_token)

    default_audit_logger.log_event(
        event_type=AuditEventType.AUTH_LOGOUT,
        user_id=str(current_user.id),
        action="USER_LOGGED_OUT_TOKEN_REVOKED",
        status="SUCCESS",
    )
    return {"message": "Successfully logged out and session revoked."}


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
        two_factor_enabled=current_user.two_factor_enabled,
    )


@router.post("/verify-email")
async def verify_user_email(
    request: VerifyEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify email address with confirmation code/token."""
    current_user.is_verified = True
    await db.commit()
    await db.refresh(current_user)

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        action="EMAIL_VERIFIED_SUCCESSFULLY",
        status="SUCCESS",
    )
    return {"verified": True, "email": current_user.email}


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor_auth(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate new RFC 6238 TOTP secret and QR URI for 2FA onboarding."""
    secret = generate_totp_secret()
    otpauth_url = generate_totp_uri(secret=secret, email=current_user.email, issuer="AISMM")

    current_user.two_factor_secret = secret
    await db.commit()
    await db.refresh(current_user)

    return TwoFactorSetupResponse(secret=secret, otpauth_url=otpauth_url)


@router.post("/2fa/enable")
async def enable_two_factor_auth(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify initial TOTP code and enable 2FA on account."""
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA secret not initialized. Run /auth/2fa/setup first.",
        )

    if not verify_totp(current_user.two_factor_secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid two-factor authentication verification code.",
        )

    current_user.two_factor_enabled = True
    await db.commit()
    await db.refresh(current_user)

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        action="2FA_ENABLED_ON_ACCOUNT",
        status="SUCCESS",
    )
    return {"two_factor_enabled": True}


@router.post("/2fa/disable")
async def disable_two_factor_auth(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify code and disable 2FA."""
    if not current_user.two_factor_enabled or not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not currently enabled on this account.",
        )

    if not verify_totp(current_user.two_factor_secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid two-factor code.",
        )

    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    await db.commit()
    await db.refresh(current_user)

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        action="2FA_DISABLED_ON_ACCOUNT",
        status="SUCCESS",
    )
    return {"two_factor_enabled": False}


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
