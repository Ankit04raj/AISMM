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
        raise HTTPException(400, f"OAuth redirect does not match configured frontend. Expected: {expected} (FRONTEND_URL={settings.FRONTEND_URL}). Set FRONTEND_URL to your real HTTPS domain.")

    return redirect_uri


def get_platform_oauth_status() -> dict:
    """Return dictionary of all supported platforms and their configuration status."""
    settings = get_settings()
    platforms = ["x", "linkedin", "youtube", "facebook", "instagram"]
    status_map = {}
    for p in platforms:
        client_id = getattr(settings, f"{p.upper()}_CLIENT_ID", None)
        client_secret = getattr(settings, f"{p.upper()}_CLIENT_SECRET", None)
        is_placeholder = bool(
            (client_id and client_id.startswith("your_")) or
            (client_secret and client_secret.startswith("your_"))
        )
        is_configured = bool(client_id and client_secret and not is_placeholder and client_id.strip() and client_secret.strip())
        status_map[p] = {
            "configured": is_configured,
            "has_client_id": bool(client_id and not client_id.startswith("your_") and client_id.strip()),
            "has_client_secret": bool(client_secret and not client_secret.startswith("your_") and client_secret.strip()),
            "client_id_preview": f"{client_id[:4]}...{client_id[-4:]}" if client_id and len(client_id) > 8 and not is_placeholder else ("placeholder" if is_placeholder else "missing"),
        }
    return status_map


def log_startup_oauth_status():
    """Log clear, high-visibility startup diagnostics showing platform OAuth readiness."""
    import logging
    logger = logging.getLogger("aismm.oauth")
    settings = get_settings()
    status_map = get_platform_oauth_status()

    logger.info("================================================================")
    logger.info("AISMM PLATFORM OAUTH CONFIGURATION STATUS (%s mode)", settings.ENVIRONMENT.upper())
    logger.info("================================================================")

    configured_count = 0
    for platform, info in status_map.items():
        name = {"x": "X (Twitter)", "linkedin": "LinkedIn", "youtube": "YouTube", "facebook": "Facebook Pages", "instagram": "Instagram Business"}.get(platform, platform.capitalize())
        if info["configured"]:
            configured_count += 1
            logger.info("  ✓ %-22s: CONFIGURED (Client ID: %s)", name, info["client_id_preview"])
        else:
            if settings.ENVIRONMENT == "development":
                logger.info("  ⚠ %-22s: NOT CONFIGURED (Dev fallback enabled)", name)
            else:
                logger.warning("  ✗ %-22s: NOT CONFIGURED (Missing credentials -> OAuth will return 503)", name)

    logger.info("----------------------------------------------------------------")
    logger.info("OAuth Readiness: %d/%d platforms configured", configured_count, len(status_map))
    logger.info("Redirect URI Base: %s/oauth/callback", settings.FRONTEND_URL.rstrip('/'))
    logger.info("================================================================")


def configured_adapter(platform: str, redirect_uri: str):
    """Retrieve platform adapter with configured or development fallback credentials."""
    settings = get_settings()
    platform_key = "x" if platform.lower() == "twitter" else platform.lower()

    if not PlatformRegistry.is_registered(platform_key):
        raise HTTPException(400, f'Unsupported platform: {platform}.')

    valid_redirect = validate_redirect_uri(redirect_uri)

    client_id = getattr(settings, f'{platform_key.upper()}_CLIENT_ID', None)
    client_secret = getattr(settings, f'{platform_key.upper()}_CLIENT_SECRET', None)

    is_unconfigured = (
        not client_id or
        not client_secret or
        not str(client_id).strip() or
        not str(client_secret).strip() or
        str(client_id).startswith("your_") or
        str(client_secret).startswith("your_")
    )

    # Fail closed in every environment: simulated OAuth must never be created.
    if is_unconfigured:
        raise HTTPException(
            503,
            f'{platform} OAuth credentials are not configured by the operator. '
            f'Set {platform_key.upper()}_CLIENT_ID and {platform_key.upper()}_CLIENT_SECRET '
            f'in .env to enable real OAuth 2.0.',
        )

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


async def exchange(db, user_id, platform, code, state, redirect_uri, page_id: str = None):
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

    # The callback must return to the exact redirect the flow started with.
    if (attempt.redirect_uri or '') != valid_redirect:
        raise HTTPException(400, 'OAuth redirect does not match the original authorization request.')

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

    # Synthetic development codes never reach a provider and must never mint an account.
    if not code or code.startswith("dev_auth_"):
        raise HTTPException(400, 'Synthetic authorization codes are not accepted. Complete a real OAuth authorization.')

    adapter = configured_adapter(platform_key, valid_redirect)

    try:
        if platform_key == 'x':
            adapter.auth._state_store[state] = {'code_verifier': attempt.verifier}
            tokens = await adapter.auth.exchange_code(code=code, state=state, redirect_uri=valid_redirect)
        else:
            tokens = await adapter.auth.exchange_code(code=code, redirect_uri=valid_redirect)

        if platform_key == 'facebook':
            page_info = await adapter.auth.get_page_access_token(tokens['access_token'], page_id=page_id)
            page_token = page_info.get('page_access_token', tokens['access_token'])
            profile = await adapter.auth.get_user_profile(page_token, page_id=page_info.get('page_id'))
            tokens['access_token'] = page_token
            tokens['page_id'] = page_info.get('page_id')
        elif platform_key == 'instagram':
            ig_info = await adapter.auth.get_instagram_business_account(tokens['access_token'], page_id=page_id)
            profile = ig_info
            if ig_info.get('page_access_token'):
                tokens['access_token'] = ig_info['page_access_token']
            tokens['ig_user_id'] = ig_info.get('id')
            tokens['linked_page_id'] = ig_info.get('linked_page_id')
        elif platform_key == 'youtube':
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
                    raise ValueError('No YouTube channel available for this account.')
                channel = items[0]
                profile = {
                    'id': channel['id'],
                    'username': channel['snippet']['title'],
                    'name': channel['snippet']['title'],
                    'display_name': channel['snippet']['title'],
                    'profile_picture_url': channel['snippet'].get('thumbnails', {}).get('default', {}).get('url'),
                    'account_type': 'creator',
                }
        else:
            profile = await adapter.auth.get_user_profile(tokens['access_token'])

        if not tokens.get('access_token'):
            raise ValueError('Provider did not return an access token')
        if not profile or not profile.get('id'):
            raise ValueError('Provider did not return an account identity')

        # Strip provider secrets before anything is persisted into account metadata.
        profile = {key: value for key, value in profile.items()
                   if key not in {"access_token", "refresh_token", "token", "client_secret", "page_access_token"}}

        return tokens, profile
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        from backend.app.core.errors import ValidationError as AISMMValidationError, AuthenticationError as AISMMAuthError
        if isinstance(e, (AISMMValidationError, AISMMAuthError)):
            raise HTTPException(400, error_msg)
        if "No Facebook Pages found" in error_msg or "No Instagram Business Account linked" in error_msg or "not found" in error_msg:
            raise HTTPException(400, error_msg)
        # Never surface raw provider bodies (they can include credentials).
        raise HTTPException(502, f'Platform authorization failed: {error_msg}')
