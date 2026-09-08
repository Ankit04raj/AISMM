"""Never reuse mutable, credential-bearing adapter instances between users."""
from sqlalchemy import select
from fastapi import HTTPException
from backend.app.db.models import SocialAccount
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.config import get_settings


async def owned_adapter(db, user_id, platform):
    result = await db.execute(select(SocialAccount).where(
        SocialAccount.user_id == user_id, SocialAccount.platform == platform, SocialAccount.is_active.is_(True)))
    accounts = result.scalars().all()
    if not accounts:
        raise HTTPException(409, f'Connect your {platform} account before publishing or managing engagement.')
    if len(accounts) > 1:
        raise HTTPException(409, 'Multiple accounts on this platform require explicit account selection; disconnect extras before publishing.')
    account = accounts[0]
    if not account.access_token:
        raise HTTPException(409, 'Reconnect this account; its credentials are missing.')
    settings = get_settings()
    adapter = PlatformRegistry.get_adapter(platform, config={
        'client_id': getattr(settings, f'{platform.upper()}_CLIENT_ID', None),
        'client_secret': getattr(settings, f'{platform.upper()}_CLIENT_SECRET', None),
        'redirect_uri': settings.FRONTEND_URL.rstrip('/')+'/oauth/callback',
        'access_token': account.access_token, 'refresh_token': account.refresh_token,
        'ig_user_id': account.platform_user_id, 'page_id': account.platform_user_id,
        'account_user_id': account.platform_user_id, 'channel_id': account.platform_user_id,
        'author_id': account.platform_user_id, 'author_urn': f'urn:li:person:{account.platform_user_id}'})
    if not adapter:
        raise HTTPException(409, 'Platform adapter is unavailable.')
    return adapter
