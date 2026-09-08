"""Authenticated OAuth handshake; single-use state persisted across workers."""
import secrets
from datetime import timedelta
from sqlalchemy import select, update
from fastapi import HTTPException
from backend.app.config import get_settings
from backend.app.db.models import OAuthAttempt
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.services.session_service import now, digest


def configured_adapter(platform, redirect_uri):
    settings = get_settings()
    if not PlatformRegistry.is_registered(platform):
        raise HTTPException(400, 'Unsupported platform.')
    expected = settings.FRONTEND_URL.rstrip('/') + '/oauth/callback'
    if redirect_uri != expected:
        raise HTTPException(400, 'OAuth redirect does not match the configured frontend.')
    if platform in {'instagram', 'facebook'}:
        # Existing Meta adapters target an obsolete API and omit Page selection.
        # Do not send credentials through an unvalidated identity flow.
        raise HTTPException(503, 'Meta account connection is not available yet. The adapter requires an updated API and Page/business-account selection before live use.')
    client_id = getattr(settings, f'{platform.upper()}_CLIENT_ID', None)
    client_secret = getattr(settings, f'{platform.upper()}_CLIENT_SECRET', None)
    if not client_id or not client_secret:
        raise HTTPException(503, f'{platform} OAuth credentials are not configured by the operator.')
    return PlatformRegistry.get_adapter(platform, config={
        'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': expected})


async def initiate(db, user_id, platform, redirect_uri):
    adapter = configured_adapter(platform, redirect_uri)
    state = secrets.token_urlsafe(32)
    url, _ = adapter.auth.get_authorization_url(state=state)
    entry = adapter.auth._state_store.get(state, {})
    expiry = now() + timedelta(minutes=10)
    db.add(OAuthAttempt(state_hash=digest(state), user_id=user_id, platform=platform,
                       redirect_uri=redirect_uri, verifier=entry.get('code_verifier'),
                       expires_at=expiry, consumed=False))
    await db.commit()
    return {'authorization_url': url, 'state': state, 'expires_at': expiry}


async def exchange(db, user_id, platform, code, state, redirect_uri):
    if not state:
        raise HTTPException(400, 'OAuth state is required. Start a new connection.')
    attempt = await db.scalar(select(OAuthAttempt).where(
        OAuthAttempt.state_hash == digest(state), OAuthAttempt.user_id == user_id,
        OAuthAttempt.platform == platform, OAuthAttempt.redirect_uri == redirect_uri,
        OAuthAttempt.consumed.is_(False), OAuthAttempt.expires_at > now()))
    if not attempt:
        raise HTTPException(400, 'OAuth state is invalid, expired, or already used.')
    adapter = configured_adapter(platform, redirect_uri)
    consumed = await db.execute(update(OAuthAttempt).where(
        OAuthAttempt.state_hash == digest(state), OAuthAttempt.consumed.is_(False)
    ).values(consumed=True))
    if consumed.rowcount != 1:
        raise HTTPException(400, 'OAuth state already used.')
    await db.commit()
    try:
        if platform == 'x':
            adapter.auth._state_store[state] = {'code_verifier': attempt.verifier}
            tokens = await adapter.auth.exchange_code(code=code, state=state, redirect_uri=redirect_uri)
        else:
            tokens = await adapter.auth.exchange_code(code=code, redirect_uri=redirect_uri)
        if platform == 'youtube':
            import httpx
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get('https://www.googleapis.com/youtube/v3/channels',
                    params={'part':'snippet', 'mine':'true'}, headers={'Authorization':f"Bearer {tokens['access_token']}"})
                response.raise_for_status()
                items = response.json().get('items', [])
                if not items:
                    raise ValueError('No YouTube channel available')
                channel = items[0]
                profile = {'id':channel['id'], 'username':channel['snippet']['title'], 'name':channel['snippet']['title']}
        else:
            profile = await adapter.auth.get_user_profile(tokens['access_token'])
        if not profile or not profile.get('id'):
            raise ValueError('Provider did not return an account identity')
        return tokens, profile
    except HTTPException:
        raise
    except Exception:
        # Never surface raw provider bodies (they can include credentials).
        raise HTTPException(502, 'Platform authorization failed. Check app permissions and start a new connection.')
