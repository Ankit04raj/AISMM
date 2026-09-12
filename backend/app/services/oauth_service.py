"""Authenticated OAuth handshake; single-use state persisted across workers."""
import secrets
from datetime import timedelta, datetime, timezone
from urllib.parse import urlparse
from sqlalchemy import select, update
from fastapi import HTTPException
from backend.app.config import get_settings
from backend.app.db.models import OAuthAttempt, OAuthState
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.services.session_service import now, digest
from backend.app.core.oauth_state_service import OAuthStateService


def validate_redirect_uri(redirect_uri: str) -> str:
    """Validate that redirect_uri belongs to an authorized frontend origin and callback path."""
    settings = get_settings()
    expected = settings.FRONTEND_URL.rstrip('/') + '/oauth/callback'
    if not redirect_uri or redirect_uri == expected:
        return expected

    parsed = urlparse(redirect_uri)
    allowed_hosts = {"localhost", "127.0.0.1", "app.yourdomain.com", "yourdomain.com"}

    # Also add hosts from settings
    if settings.FRONTEND_URL:
        frontend_host = urlparse(settings.FRONTEND_URL).hostname
        if frontend_host:
            allowed_hosts.add(frontend_host)

    if settings.CORS_ORIGINS:
        for origin in settings.CORS_ORIGINS:
            host = urlparse(origin).hostname
            if host:
                allowed_hosts.add(host)

    if parsed.hostname not in allowed_hosts or parsed.path != "/oauth/callback":
        raise HTTPException(400, "OAuth redirect does not match the configured frontend.")

    return redirect_uri


def configured_adapter(platform: str, redirect_uri: str):
    """Retrieve platform adapter with configured or development fallback credentials."""
    settings = get_settings()
    platform_key = "x" if platform.lower() == "twitter" else platform.lower()

    if not PlatformRegistry.is_registered(platform_key):
        raise HTTPException(400, f'Unsupported platform: {platform}.')

    valid_redirect = validate_redirect_uri(redirect_uri)

    client_id = getattr(settings, f'{platform_key.upper()}_CLIENT_ID', None)
    client_secret = getattr(settings, f'{platform_key.upper()}_CLIENT_SECRET', None)

    # In development mode, provide fallback mock credentials if real OAuth app is not configured
    if not client_id or not client_secret:
        if settings.ENVIRONMENT == "development" or settings.DEBUG:
            client_id = f"dev_{platform_key}_client_id"
            client_secret = f"dev_{platform_key}_secret"
        else:
            raise HTTPException(503, f'{platform} OAuth credentials are not configured by the operator.')

    return PlatformRegistry.get_adapter(
        platform_key,
        config={'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': valid_redirect}
    )


async def initiate(db, user_id, platform, redirect_uri):
    """Initiate an OAuth flow and persist single-use state."""
    platform_key = "x" if platform.lower() == "twitter" else platform.lower()
    valid_redirect = validate_redirect_uri(redirect_uri)
    adapter = configured_adapter(platform_key, valid_redirect)

    state = secrets.token_urlsafe(32)
    settings = get_settings()

    # Check if we are in dev simulation mode (no real credentials set in .env)
    real_client_id = getattr(settings, f'{platform_key.upper()}_CLIENT_ID', None)
    real_client_secret = getattr(settings, f'{platform_key.upper()}_CLIENT_SECRET', None)

    if settings.ENVIRONMENT == "development" and (not real_client_id or not real_client_secret or real_client_id.startswith("your_")):
        # Generate seamless local dev authorization redirect directly to callback
        dev_code = f"dev_auth_{platform_key}_{secrets.token_hex(12)}"
        url = f"{valid_redirect}?code={dev_code}&state={state}"
        code_verifier = secrets.token_urlsafe(64)
    else:
        url, _ = adapter.auth.get_authorization_url(state=state)
        entry = adapter.auth._state_store.get(state, {})
        code_verifier = entry.get('code_verifier')

    expiry = now() + timedelta(minutes=15)

    # Store in legacy OAuthAttempt table for compatibility
    db.add(OAuthAttempt(
        state_hash=digest(state),
        user_id=user_id,
        platform=platform_key,
        redirect_uri=valid_redirect,
        verifier=code_verifier,
        expires_at=expiry,
        consumed=False
    ))

    # Also store in persistent OAuthState model
    state_svc = OAuthStateService(db)
    await state_svc.create_state(
        user_id=user_id,
        platform=platform_key,
        redirect_uri=valid_redirect,
        code_verifier=code_verifier,
        state=state,
        expires_in_minutes=15
    )

    await db.commit()
    return {'authorization_url': url, 'state': state, 'expires_at': expiry}


async def exchange(db, user_id, platform, code, state, redirect_uri):
    """Verify state and exchange authorization code for platform credentials and profile."""
    if not state:
        raise HTTPException(400, 'OAuth state is required. Start a new connection.')

    platform_key = "x" if platform.lower() == "twitter" else platform.lower()
    valid_redirect = validate_redirect_uri(redirect_uri)

    attempt = await db.scalar(select(OAuthAttempt).where(
        OAuthAttempt.state_hash == digest(state),
        OAuthAttempt.user_id == user_id,
        OAuthAttempt.platform == platform_key,
        OAuthAttempt.consumed.is_(False),
        OAuthAttempt.expires_at > now()
    ))

    if not attempt:
        raise HTTPException(400, 'OAuth state is invalid, expired, or already used.')

    consumed = await db.execute(update(OAuthAttempt).where(
        OAuthAttempt.state_hash == digest(state),
        OAuthAttempt.consumed.is_(False)
    ).values(consumed=True))

    if consumed.rowcount != 1:
        raise HTTPException(400, 'OAuth state already used.')

    # Consume from OAuthState
    state_svc = OAuthStateService(db)
    await state_svc.consume_state(state, user_id=user_id)
    await db.commit()

    # Handle development code exchange
    if code and code.startswith("dev_auth_"):
        from backend.app.db.models import User
        user_record = await db.scalar(select(User).where(User.id == user_id))
        user_handle = (user_record.email.split("@")[0].lower() if user_record and user_record.email else "ankit_raj")
        user_display = (user_record.full_name if user_record and user_record.full_name else "Ankit Raj")
        user_avatar = user_record.avatar_url if user_record and user_record.avatar_url else f"https://api.dicebear.com/7.x/identicon/svg?seed={user_handle}"

        tokens = {
            "access_token": f"dev_access_token_{platform_key}_{secrets.token_hex(16)}",
            "refresh_token": f"dev_refresh_token_{platform_key}_{secrets.token_hex(16)}",
            "expires_in": 5184000,  # 60 days
            "token_type": "Bearer",
            "scope": "read,write,insights,publish"
        }

        profile = {
            "id": f"{platform_key}_{user_handle}",
            "username": f"{user_handle}",
            "name": f"{user_display}",
            "display_name": f"{user_display}",
            "profile_picture_url": user_avatar,
            "account_type": "creator",
            "followers_count": 28450,
            "media_count": 42,
            "is_verified": True
        }
        return tokens, profile

    adapter = configured_adapter(platform_key, valid_redirect)

    try:
        if platform_key == 'x':
            adapter.auth._state_store[state] = {'code_verifier': attempt.verifier}
            tokens = await adapter.auth.exchange_code(code=code, state=state, redirect_uri=valid_redirect)
        else:
            tokens = await adapter.auth.exchange_code(code=code, redirect_uri=valid_redirect)

        if platform_key == 'youtube':
            import httpx
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(
                    'https://www.googleapis.com/youtube/v3/channels',
                    params={'part': 'snippet', 'mine': 'true'},
                    headers={'Authorization': f"Bearer {tokens['access_token']}"}
                )
                response.raise_for_status()
                items = response.json().get('items', [])
                if not items:
                    raise ValueError('No YouTube channel available')
                channel = items[0]
                profile = {
                    'id': channel['id'],
                    'username': channel['snippet']['title'],
                    'name': channel['snippet']['title'],
                    'profile_picture_url': channel['snippet'].get('thumbnails', {}).get('default', {}).get('url')
                }
        else:
            profile = await adapter.auth.get_user_profile(tokens['access_token'])

        if not profile or not profile.get('id'):
            raise ValueError('Provider did not return an account identity')

        return tokens, profile
    except HTTPException:
        raise
    except Exception as e:
        # Never surface raw provider bodies (they can include credentials).
        raise HTTPException(502, f'Platform authorization failed. Check app permissions and start a new connection.')
