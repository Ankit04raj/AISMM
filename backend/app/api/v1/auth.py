"""Authentication API router: User Auth (Register, Login, Refresh, Me, 2FA, Email Verification, Logout) and Platform OAuth."""

import secrets
import logging
import hashlib
import asyncio
from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.app.db.session import get_db
from backend.app.db.models import User, AuthSession
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
    generate_recovery_codes,
    hash_recovery_code,
    verify_recovery_code,
)
from backend.app.api.deps import get_current_user, get_current_verified_user
from backend.app.core.rate_limit import rate_limit_guard
from backend.app.core.audit import default_audit_logger, AuditEventType
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.services.session_service import issue_session, rotate_session, revoke_all
from backend.app.services.email_service import email_service
from backend.app.services.phone_service import phone_service
from backend.app.core.schemas.auth import (
    RegisterRequest,
    ProfileUpdate, PasswordChange, PasswordResetRequest, PasswordResetConfirm,
    UserLoginRequest,
    UserLoginResponse,
    UserProfile,
    AppRefreshTokenRequest,
    AppTokenRefreshResponse,
    VerifyEmailRequest,
    PhoneVerificationRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorEnableResponse,
    RegenerateRecoveryCodesRequest,
    RegenerateRecoveryCodesResponse,
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

    if not request.accept_terms and settings.ENVIRONMENT != "development":
        raise HTTPException(422, "You must accept the Terms and Privacy Policy.")
    if len(request.password.encode("utf-8")) > 72:
        raise HTTPException(422, "Password must be at most 72 UTF-8 bytes.")
    if request.verification_method not in {"email", "phone"}:
        raise HTTPException(422, "Unsupported verification method.")

    # Check if phone number is provided and already exists
    if request.phone_number:
        normalized_phone = request.phone_number.strip()
        phone_exists = await db.execute(select(User).where(User.phone_number == normalized_phone))
        if phone_exists.scalar_one_or_none():
            default_audit_logger.log_event(
                event_type=AuditEventType.AUTH_LOGIN_FAILED,
                user_id=normalized_email,
                ip_address=client_ip,
                action="USER_REGISTRATION_FAILED_DUPLICATE_PHONE",
                status="FAILURE",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this phone number already exists.",
            )

    # Determine verification method
    verification_method = request.verification_method if hasattr(request, 'verification_method') else "email"

    # Validate phone number is provided when verification method is phone
    if verification_method == "phone" and not request.phone_number:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Phone number is required when verification method is 'phone'.",
        )

    # Create new user (defaults to unverified until email/phone confirmation)
    # Generate verification token (use naive UTC for SQLite compatibility)
    verification_token = secrets.token_urlsafe(32)
    verification_token_hash = hashlib.sha256(verification_token.encode()).hexdigest()
    verification_expiry = (datetime.now(timezone.utc) + timedelta(minutes=30)).replace(tzinfo=None)

    # Generate phone OTP if phone verification method
    phone_otp = None
    phone_otp_hash = None
    phone_otp_expiry = None
    if verification_method == "phone" and request.phone_number:
        phone_otp = str(secrets.randbelow(900000) + 100000)  # 6-digit OTP
        phone_otp_hash = hashlib.sha256(phone_otp.encode()).hexdigest()
        phone_otp_expiry = (datetime.now(timezone.utc) + timedelta(minutes=10)).replace(tzinfo=None)

    user = User(
        terms_accepted_at=datetime.now(timezone.utc).replace(tzinfo=None) if request.accept_terms else None,
        email=normalized_email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        phone_number=request.phone_number.strip() if request.phone_number else None,
        is_active=True,
        is_verified=False,
        phone_verified=False,
        is_superuser=False,
        two_factor_enabled=False,
        email_verification_token=verification_token_hash,
        email_verification_expiry=verification_expiry,
        phone_verification_token=phone_otp_hash,
        phone_verification_expiry=phone_otp_expiry,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Send verification based on method
    email_sent = False
    phone_sent = False

    if verification_method == "email":
        # Send verification email (non-blocking, log failure but don't fail registration)
        try:
            if settings.ENABLE_EMAIL_NOTIFICATIONS and settings.SMTP_HOST:
                email_sent = await asyncio.to_thread(email_service.send_verification_email,
                    to_email=user.email,
                    verification_token=verification_token,
                    user_name=user.full_name,
                )
                if not email_sent:
                    logging.warning(f"Failed to send verification email to {user.email}")
        except Exception as e:
            # Log but don't fail registration if email fails
            logging.error(f"Error sending verification email to {user.email}: {e}")
    elif verification_method == "phone" and phone_otp:
        # Send verification SMS
        try:
            if settings.ENABLE_PHONE_VERIFICATION and settings.SMS_PROVIDER:
                phone_sent = phone_service.send_verification_sms(
                    to_number=user.phone_number,
                    otp=phone_otp,
                    user_name=user.full_name,
                )
                if not phone_sent:
                    logging.warning(f"Failed to send verification SMS to {user.phone_number}")
        except Exception as e:
            logging.error(f"Error sending verification SMS to {user.phone_number}: {e}")

    # Issue initial JWT tokens
    access_token, refresh_token = await issue_session(db, user.id)

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
        phone_number=user.phone_number,
        phone_verified=user.phone_verified,
        two_factor_enabled=user.two_factor_enabled,
    )

    response_data = UserLoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        requires_2fa=False,
        user=profile,
    )

    # Development mode ONLY: include verification token in response when email/SMS is disabled
    # In production or staging, this token is strictly NEVER returned in the API response under any circumstances.
    env_clean = str(settings.ENVIRONMENT or "").strip().lower()
    is_development_env = env_clean in {"development", "dev", "local", "test"} and settings.DEBUG is not False

    if is_development_env and not (settings.ENABLE_EMAIL_NOTIFICATIONS and settings.SMTP_HOST) and verification_method == "email":
        response_data.verification_token = verification_token
    elif is_development_env and not (settings.ENABLE_PHONE_VERIFICATION and settings.SMS_PROVIDER) and verification_method == "phone" and phone_otp:
        response_data.verification_token = phone_otp
    else:
        # Guaranteed None in all production and staging environments
        response_data.verification_token = None

    return response_data


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

    # If 2FA is active, verify TOTP code or backup recovery code
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
        code_input = request.two_factor_code.strip()
        is_totp = verify_totp(user.two_factor_secret or "", code_input)
        is_recovery = False
        matched_recovery_hash = None

        if not is_totp and user.two_factor_recovery_codes:
            is_recovery, matched_recovery_hash = verify_recovery_code(
                code_input, user.two_factor_recovery_codes
            )

        if not is_totp and not is_recovery:
            default_audit_logger.log_event(
                event_type=AuditEventType.AUTH_LOGIN_FAILED,
                user_id=str(user.id),
                ip_address=client_ip,
                action="USER_LOGIN_FAILED_INVALID_2FA",
                status="FAILURE",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid two-factor authentication code or recovery code.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if is_totp:
            import pyotp
            import time
            current_step = int(time.time() // 30)
            matched_step = next((step for step in range(current_step-1, current_step+2)
                if secrets.compare_digest(pyotp.TOTP(user.two_factor_secret).at(step*30), code_input)), None)
            if matched_step is None:
                raise HTTPException(401, "Authenticator code expired. Try the next code.")
            used = await db.execute(update(User).where(User.id==user.id,
                (User.two_factor_last_step.is_(None)) | (User.two_factor_last_step < matched_step)
            ).values(two_factor_last_step=matched_step))
            if used.rowcount != 1:
                await db.rollback()
                raise HTTPException(401, "Authenticator code already used. Wait for the next code.")
        elif is_recovery and matched_recovery_hash:
            # Single-use consumption of recovery code
            updated_codes = [h for h in (user.two_factor_recovery_codes or []) if h != matched_recovery_hash]
            user.two_factor_recovery_codes = updated_codes
            default_audit_logger.log_event(
                event_type=AuditEventType.SETTINGS_UPDATED,
                user_id=str(user.id),
                action="2FA_RECOVERY_CODE_CONSUMED",
                status="SUCCESS",
            )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)

    # Generate tokens with optional extended duration for remember_me
    refresh_delta = timedelta(days=30) if request.remember_me else None
    access_token, refresh_token = await issue_session(db, user.id, days=30 if request.remember_me else None)

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
        phone_number=user.phone_number,
        phone_verified=user.phone_verified,
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

    new_access_token, new_refresh_token = await rotate_session(db, request.refresh_token, user.id)

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
    db: AsyncSession = Depends(get_db),
):
    """Invalidate session tokens server-side upon logout."""
    from backend.app.core.security import decode_token
    payload = decode_token(req.headers["Authorization"].split(" ", 1)[1])
    await db.execute(update(AuthSession).where(
        AuthSession.id == payload["sid"], AuthSession.user_id == current_user.id
    ).values(revoked=True))
    await db.commit()

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
        phone_number=current_user.phone_number,
        phone_verified=current_user.phone_verified,
        two_factor_enabled=current_user.two_factor_enabled,
    )


@router.post(
    "/verify-email",
    dependencies=[Depends(rate_limit_guard(max_requests=10, window_seconds=60))],
)
async def verify_user_email(
    request: VerifyEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify email address with confirmation token.

    Token must match the stored token and not be expired.
    """
    # Check if already verified
    if current_user.is_verified:
        return {"verified": True, "email": current_user.email, "message": "Email already verified"}

    # Check if token exists
    if not current_user.email_verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification token found. Please request a new verification email.",
        )

    # Check if token has expired (use naive UTC for SQLite compatibility)
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if current_user.email_verification_expiry and current_user.email_verification_expiry < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new verification email.",
        )

    # Accept either token or code field (both should contain the same value)
    submitted_token = request.token or request.code
    if not submitted_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'token' or 'code' field is required.",
        )

    # Hash submitted token and compare using constant-time comparison
    submitted_token_hash = hashlib.sha256(submitted_token.encode()).hexdigest()
    if not secrets.compare_digest(current_user.email_verification_token, submitted_token_hash):
        default_audit_logger.log_event(
            event_type=AuditEventType.SETTINGS_UPDATED,
            user_id=str(current_user.id),
            action="EMAIL_VERIFICATION_FAILED_INVALID_TOKEN",
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token. Please check the token and try again.",
        )

    # Token is valid - verify the email
    current_user.is_verified = True
    current_user.email_verification_token = None  # Invalidate token after use
    current_user.email_verification_expiry = None
    await db.commit()
    await db.refresh(current_user)

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        action="EMAIL_VERIFIED_SUCCESSFULLY",
        status="SUCCESS",
    )
    return {"verified": True, "email": current_user.email}


@router.post(
    "/resend-verification",
    dependencies=[Depends(rate_limit_guard(max_requests=3, window_seconds=300))],
)
async def resend_verification_email(
    req: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resend email verification token. Rate-limited to 3 requests per 5 minutes."""
    client_ip = req.client.host if req.client else "127.0.0.1"

    # Already verified
    if current_user.is_verified:
        return {"message": "Email is already verified", "email": current_user.email}

    # Generate new verification token (use naive UTC for SQLite compatibility)
    verification_token = secrets.token_urlsafe(32)
    verification_token_hash = hashlib.sha256(verification_token.encode()).hexdigest()
    verification_expiry = (datetime.now(timezone.utc) + timedelta(minutes=30)).replace(tzinfo=None)

    current_user.email_verification_token = verification_token_hash
    current_user.email_verification_expiry = verification_expiry
    await db.commit()
    await db.refresh(current_user)

    # Send verification email
    email_sent = False
    try:
        if settings.ENABLE_EMAIL_NOTIFICATIONS and settings.SMTP_HOST:
            email_sent = await asyncio.to_thread(email_service.send_verification_email,
                to_email=current_user.email,
                verification_token=verification_token,
                user_name=current_user.full_name,
            )
    except Exception as e:
        logging.error(f"Error sending verification email to {current_user.email}: {e}")

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        ip_address=client_ip,
        action="VERIFICATION_EMAIL_RESENT",
        status="SUCCESS" if email_sent else "EMAIL_SEND_FAILED",
    )

    if not email_sent and settings.ENABLE_EMAIL_NOTIFICATIONS and settings.SMTP_HOST:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again later.",
        )

    response_data = {
        "message": "Verification email sent" if email_sent else "Verification token generated (email delivery disabled)",
        "email": current_user.email,
    }

    # Development mode: include verification token in response when email is disabled
    if settings.ENVIRONMENT == "development" and not (settings.ENABLE_EMAIL_NOTIFICATIONS and settings.SMTP_HOST):
        response_data["verification_token"] = verification_token

    return response_data


@router.post(
    "/verify-phone",
    dependencies=[Depends(rate_limit_guard(max_requests=10, window_seconds=60))],
)
async def verify_user_phone(
    request: PhoneVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify phone number with SMS OTP.

    Code must match the stored OTP and not be expired.
    """
    # Validate phone number matches user's stored phone
    if not current_user.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No phone number associated with this account.",
        )

    if request.phone_number != current_user.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number does not match the account's registered phone number.",
        )

    # Check if already verified
    if current_user.phone_verified:
        return {"verified": True, "phone": current_user.phone_number, "message": "Phone already verified"}

    # Check if OTP exists
    if not current_user.phone_verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification OTP found. Please request a new verification SMS.",
        )

    # Check if OTP has expired (use naive UTC for SQLite compatibility)
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if current_user.phone_verification_expiry and current_user.phone_verification_expiry < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification OTP has expired. Please request a new verification SMS.",
        )

    # Verify OTP using constant-time comparison
    submitted_otp_hash = hashlib.sha256(request.code.encode()).hexdigest()
    if not secrets.compare_digest(current_user.phone_verification_token, submitted_otp_hash):
        default_audit_logger.log_event(
            event_type=AuditEventType.SETTINGS_UPDATED,
            user_id=str(current_user.id),
            action="PHONE_VERIFICATION_FAILED_INVALID_OTP",
            status="FAILURE",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification OTP. Please check the code and try again.",
        )

    # OTP is valid - verify the phone
    current_user.phone_verified = True
    current_user.phone_verification_token = None  # Invalidate OTP after use
    current_user.phone_verification_expiry = None
    await db.commit()
    await db.refresh(current_user)

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        action="PHONE_VERIFIED_SUCCESSFULLY",
        status="SUCCESS",
    )
    return {"verified": True, "phone": current_user.phone_number}


@router.post(
    "/resend-phone-verification",
    dependencies=[Depends(rate_limit_guard(max_requests=3, window_seconds=300))],
)
async def resend_phone_verification(
    req: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resend phone verification SMS. Rate-limited to 3 requests per 5 minutes."""
    client_ip = req.client.host if req.client else "127.0.0.1"

    # Check if phone number exists
    if not current_user.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No phone number associated with this account.",
        )

    # Already verified
    if current_user.phone_verified:
        return {"message": "Phone is already verified", "phone": current_user.phone_number}

    # Generate new OTP
    phone_otp = str(secrets.randbelow(900000) + 100000)  # 6-digit OTP
    phone_otp_hash = hashlib.sha256(phone_otp.encode()).hexdigest()
    phone_otp_expiry = (datetime.now(timezone.utc) + timedelta(minutes=10)).replace(tzinfo=None)

    current_user.phone_verification_token = phone_otp_hash
    current_user.phone_verification_expiry = phone_otp_expiry
    await db.commit()
    await db.refresh(current_user)

    # Send verification SMS
    phone_sent = False
    try:
        if settings.ENABLE_PHONE_VERIFICATION and settings.SMS_PROVIDER:
            phone_sent = phone_service.send_verification_sms(
                to_number=current_user.phone_number,
                otp=phone_otp,
                user_name=current_user.full_name,
            )
    except Exception as e:
        logging.error(f"Error sending verification SMS to {current_user.phone_number}: {e}")

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        ip_address=client_ip,
        action="PHONE_VERIFICATION_SMS_RESENT",
        status="SUCCESS" if phone_sent else "SMS_SEND_FAILED",
    )

    if not phone_sent and settings.ENABLE_PHONE_VERIFICATION and settings.SMS_PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification SMS. Please try again later.",
        )

    response_data = {
        "message": "Verification SMS sent" if phone_sent else "Verification OTP generated (SMS delivery disabled)",
        "phone": current_user.phone_number,
    }

    # Development mode: include OTP in response when SMS is disabled
    if settings.ENVIRONMENT == "development" and not (settings.ENABLE_PHONE_VERIFICATION and settings.SMS_PROVIDER):
        response_data["verification_token"] = phone_otp

    return response_data


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor_auth(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate new RFC 6238 TOTP secret and QR URI for 2FA onboarding."""
    if current_user.two_factor_enabled:
        raise HTTPException(409, "Disable 2FA with your current authenticator before replacing its secret.")
    secret = generate_totp_secret()
    otpauth_url = generate_totp_uri(secret=secret, email=current_user.email, issuer="AISMM")

    current_user.two_factor_secret = secret
    await db.commit()
    await db.refresh(current_user)

    return TwoFactorSetupResponse(secret=secret, otpauth_url=otpauth_url)


@router.post("/2fa/enable", response_model=TwoFactorEnableResponse, dependencies=[Depends(rate_limit_guard(max_requests=5, window_seconds=60))])
async def enable_two_factor_auth(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify initial TOTP code and enable 2FA on account, generating backup recovery codes."""
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

    recovery_codes = generate_recovery_codes(count=8)
    hashed_codes = [hash_recovery_code(code) for code in recovery_codes]

    current_user.two_factor_enabled = True
    current_user.two_factor_recovery_codes = hashed_codes
    await db.commit()
    await db.refresh(current_user)

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        action="2FA_ENABLED_ON_ACCOUNT",
        status="SUCCESS",
    )
    return TwoFactorEnableResponse(two_factor_enabled=True, recovery_codes=recovery_codes)


@router.post("/2fa/recovery-codes", response_model=RegenerateRecoveryCodesResponse, dependencies=[Depends(rate_limit_guard(max_requests=5, window_seconds=60))])
async def regenerate_recovery_codes(
    request: RegenerateRecoveryCodesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate a fresh set of 2FA backup recovery codes using active TOTP code."""
    if not current_user.two_factor_enabled or not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not currently enabled on this account.",
        )

    if not verify_totp(current_user.two_factor_secret, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid two-factor authentication code.",
        )

    recovery_codes = generate_recovery_codes(count=8)
    hashed_codes = [hash_recovery_code(code) for code in recovery_codes]

    current_user.two_factor_recovery_codes = hashed_codes
    await db.commit()
    await db.refresh(current_user)

    default_audit_logger.log_event(
        event_type=AuditEventType.SETTINGS_UPDATED,
        user_id=str(current_user.id),
        action="2FA_RECOVERY_CODES_REGENERATED",
        status="SUCCESS",
    )
    return RegenerateRecoveryCodesResponse(recovery_codes=recovery_codes)


@router.post("/2fa/disable", dependencies=[Depends(rate_limit_guard(max_requests=5, window_seconds=60))])
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
    current_user.two_factor_last_step = None
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
async def oauth_init(request: OAuthInitRequest, current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    from backend.app.services.oauth_service import initiate
    return await initiate(db, current_user.id, request.platform, request.redirect_uri)


@router.post(
    "/oauth/callback",

    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def oauth_callback(request: OAuthCallbackRequest, current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    from backend.app.services.account_service import AccountService
    from backend.app.core.schemas.account import ConnectAccountRequest
    return await AccountService(db).connect_account(current_user.id, ConnectAccountRequest(
        platform=request.platform, authorization_code=request.code, state=request.state, redirect_uri=request.redirect_uri))


@router.post(
    "/oauth/refresh",
    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def oauth_refresh(request: RefreshTokenRequest, current_user: User = Depends(get_current_verified_user)):
    raise HTTPException(410, 'Use /accounts/{account_id}/refresh; platform credentials are never returned to the browser.')


@router.get(
    "/{provider}/connect",
    response_model=OAuthInitResponse,
    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def provider_connect(
    provider: str,
    redirect_uri: Optional[str] = None,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
):
    """Convenience endpoint to initiate OAuth connection for a specific provider."""
    from backend.app.services.oauth_service import initiate
    settings = get_settings()
    target_redirect = redirect_uri or (settings.FRONTEND_URL.rstrip('/') + '/oauth/callback')
    return await initiate(db, current_user.id, provider.lower(), target_redirect)


@router.get(
    "/{provider}/callback",
    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def provider_callback_get(
    provider: str,
    code: str,
    state: str,
    redirect_uri: Optional[str] = None,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
):
    """GET callback handler for OAuth providers redirecting directly to backend."""
    from backend.app.services.account_service import AccountService
    from backend.app.core.schemas.account import ConnectAccountRequest
    settings = get_settings()
    target_redirect = redirect_uri or (settings.FRONTEND_URL.rstrip('/') + '/oauth/callback')
    return await AccountService(db).connect_account(
        current_user.id,
        ConnectAccountRequest(
            platform=provider.lower(),
            authorization_code=code,
            state=state,
            redirect_uri=target_redirect,
        ),
    )


@router.post(
    "/{provider}/disconnect",
    dependencies=[Depends(rate_limit_guard(max_requests=20, window_seconds=60))],
)
async def provider_disconnect(
    provider: str,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect a social account by provider name."""
    from backend.app.services.account_service import AccountService
    service = AccountService(db)
    accounts = await service.get_accounts(current_user.id, platform=provider.lower())
    if not accounts:
        raise HTTPException(status_code=404, detail=f"No connected {provider} account found.")
    account = accounts[0]
    return await service.disconnect_account(account.id, current_user.id)


@router.patch('/me', response_model=UserProfile)
async def update_profile(request: ProfileUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.full_name = request.full_name.strip()
    await db.commit()
    return await get_current_user_profile(current_user)


@router.post('/password', dependencies=[Depends(rate_limit_guard(max_requests=5, window_seconds=300))])
async def change_password(request: PasswordChange, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(400, 'Current password is incorrect.')
    if current_user.two_factor_enabled and not verify_totp(current_user.two_factor_secret, request.two_factor_code):
        raise HTTPException(400, 'A valid authenticator code is required.')
    if len(request.password.encode()) > 72:
        raise HTTPException(422, 'Password exceeds 72 UTF-8 bytes.')
    current_user.hashed_password = get_password_hash(request.password)
    await revoke_all(db, current_user.id)
    await db.commit()
    return {'message': 'Password changed. All sessions revoked; sign in again.'}


@router.post('/forgot-password', dependencies=[Depends(rate_limit_guard(max_requests=3, window_seconds=300))])
async def forgot_password(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == request.email.strip().lower()))
    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        user.password_reset_hash = hashlib.sha256(token.encode()).hexdigest()
        user.password_reset_expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=30)
        await db.commit()
        if settings.ENABLE_EMAIL_NOTIFICATIONS:
            await asyncio.to_thread(email_service.send_password_reset_email, user.email, token, user.full_name)
    return {'message': 'If an account exists, a password reset link will be sent. Check your inbox.'}


@router.post('/reset-password', dependencies=[Depends(rate_limit_guard(max_requests=5, window_seconds=300))])
async def reset_password(request: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    if len(request.password.encode()) > 72:
        raise HTTPException(422, 'Password exceeds 72 UTF-8 bytes.')
    token_hash = hashlib.sha256(request.token.encode()).hexdigest()
    # Atomically consume the token to prevent reset replay across processes.
    result = await db.execute(update(User).where(
        User.password_reset_hash == token_hash,
        User.password_reset_expiry > datetime.now(timezone.utc).replace(tzinfo=None)
    ).values(hashed_password=get_password_hash(request.password), password_reset_hash=None,
             password_reset_expiry=None).returning(User.id))
    user_id = result.scalar_one_or_none()
    if user_id is None:
        raise HTTPException(400, 'Reset link is invalid or expired.')
    await revoke_all(db, user_id)
    await db.commit()
    return {'message': 'Password reset. Sign in with your new password.'}
