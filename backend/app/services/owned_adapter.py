"""Never reuse mutable, credential-bearing adapter instances between users."""
from uuid import UUID
from sqlalchemy import select, and_
from fastapi import HTTPException
from backend.app.db.models import SocialAccount
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.config import get_settings


async def owned_adapter(db, user_id, platform, account_id=None, **kwargs):
    """Retrieve an authenticated, tenant-isolated platform adapter for the user."""
    platform_key = "x" if platform.lower() in {"x", "twitter"} else platform.lower()

    query = select(SocialAccount).where(
        SocialAccount.user_id == user_id,
        SocialAccount.platform == platform_key,
        SocialAccount.is_active.is_(True)
    )
    if account_id:
        acc_uuid = UUID(str(account_id)) if isinstance(account_id, str) else account_id
        query = query.where(SocialAccount.id == acc_uuid)

    result = await db.execute(query)
    accounts = result.scalars().all()

    if not accounts:
        if account_id:
            raise HTTPException(404, f'Connected {platform} account {account_id} not found or inactive.')
        raise HTTPException(409, f'Connect your {platform} account before publishing or managing engagement.')

    if len(accounts) > 1 and not account_id:
        raise HTTPException(
            409,
            f'Multiple active accounts connected for {platform}. Specify the target account_id for publishing.'
        )

    account = accounts[0]
    access_token = kwargs.get('access_token') or account.access_token
    refresh_token = kwargs.get('refresh_token') or account.refresh_token

    if not access_token:
        # In direct/handle-only connection without token, allow adapter creation with basic config
        access_token = f"direct_{account.platform}_{account.username or account.platform_user_id}"

    settings = get_settings()
    adapter = PlatformRegistry.get_adapter(platform_key, config={
        'client_id': getattr(settings, f'{platform_key.upper()}_CLIENT_ID', None),
        'client_secret': getattr(settings, f'{platform_key.upper()}_CLIENT_SECRET', None),
        'redirect_uri': settings.FRONTEND_URL.rstrip('/') + '/oauth/callback',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'ig_user_id': account.platform_user_id,
        'page_id': account.platform_user_id,
        'account_user_id': account.platform_user_id,
        'account_username': account.username,
        'channel_id': account.platform_user_id,
        'author_id': account.platform_user_id,
        'author_urn': f'urn:li:person:{account.platform_user_id}',
    })
    if not adapter:
        raise HTTPException(409, f'Platform adapter for {platform} is unavailable.')
    return adapter

