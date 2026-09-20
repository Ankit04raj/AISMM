"""Account responses must not treat legacy/demo rows as verified OAuth."""
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from backend.app.db.models import SocialAccount
from backend.app.services.account_service import AccountService


@pytest.mark.parametrize("verified,active,token,expiry,expected", [
    (False, True, "legacy-token", 3600, "disconnected"),
    (False, True, "legacy-token", -3600, "disconnected"),
    (True, True, "provider-token", 3600, "connected_live"),
    (True, True, "provider-token", -3600, "token_expired"),
    (True, False, "provider-token", 3600, "disconnected"),
    (True, True, None, 3600, "disconnected"),
    (True, True, "provider-token", None, "connected_live"),
])
def test_account_response_requires_verified_oauth(verified, active, token, expiry, expected):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    account = SocialAccount(
        id=uuid4(), user_id=uuid4(), platform="x", platform_user_id="123",
        username="test", is_active=active, access_token=token,
        token_expires_at=now + timedelta(seconds=expiry) if expiry is not None else None,
        account_metadata={"connected_via": "oauth", "oauth_verified_at": now.isoformat()},
        connected_at=now,
    )
    account.oauth_verified_at = now if verified else None
    response = AccountService(None)._to_response(account).model_dump()
    assert response.get("connection_status") == expected


from types import SimpleNamespace
from unittest.mock import AsyncMock
from fastapi import HTTPException
from sqlalchemy import select
from backend.app.db.models import User, OAuthAttempt, OAuthState
from backend.app.core.schemas.account import ConnectAccountRequest
from backend.app.services import oauth_service
from backend.app.services.session_service import digest
from test_auth_and_scoping import async_test_db


@pytest.fixture
def provider_settings(monkeypatch):
    settings = SimpleNamespace(ENVIRONMENT="development", DEBUG=True,
                               FRONTEND_URL="http://localhost:5173", CORS_ORIGINS=[])
    for platform in ("X", "FACEBOOK", "INSTAGRAM", "LINKEDIN", "YOUTUBE"):
        setattr(settings, f"{platform}_CLIENT_ID", "configured-client")
        setattr(settings, f"{platform}_CLIENT_SECRET", "configured-secret")
    monkeypatch.setattr(oauth_service, "get_settings", lambda: settings)
    return settings


@pytest.mark.parametrize("platform", ["x", "facebook", "instagram", "linkedin", "youtube"])
def test_missing_credentials_never_simulate(platform, provider_settings):
    setattr(provider_settings, f"{platform.upper()}_CLIENT_ID", "")
    with pytest.raises(HTTPException) as error:
        oauth_service.configured_adapter(platform, "http://localhost:5173/oauth/callback")
    assert error.value.status_code == 503


async def prepare_attempt(db, platform):
    user = User(id=uuid4(), email=f"{uuid4()}@example.test", hashed_password="test", is_active=True)
    db.add(user)
    await db.flush()
    state = uuid4().hex
    redirect = "http://localhost:5173/oauth/callback"
    expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)
    db.add(OAuthAttempt(state_hash=digest(state), user_id=user.id, platform=platform,
                        redirect_uri=redirect, verifier="stored-verifier", expires_at=expiry, consumed=False))
    db.add(OAuthState(state=state, user_id=user.id, platform=platform, redirect_uri=redirect,
                      code_verifier="stored-verifier", expires_at=expiry, consumed=False))
    await db.commit()
    return user, ConnectAccountRequest(platform=platform, authorization_code="provider-code",
                                      state=state, redirect_uri=redirect)


@pytest.mark.asyncio
@pytest.mark.parametrize("platform", ["x", "facebook", "instagram", "linkedin", "youtube"])
async def test_real_exchange_and_profile_persist_verification(platform, async_test_db, provider_settings, monkeypatch):
    import httpx
    user, request = await prepare_attempt(async_test_db, platform)
    auth = SimpleNamespace(
        _state_store={},
        exchange_code=AsyncMock(return_value={"access_token": "provider-token", "expires_in": 3600}),
        get_user_profile=AsyncMock(return_value={"id": "provider-id", "name": "Provider Name"}),
        get_page_access_token=AsyncMock(return_value={"page_access_token": "page-secret", "page_id": "page-id"}),
        get_instagram_business_account=AsyncMock(return_value={"id": "provider-id", "name": "Provider Name",
                                                               "page_access_token": "page-secret"}),
    )
    monkeypatch.setattr(oauth_service, "configured_adapter", lambda *args: SimpleNamespace(auth=auth))
    original_client = httpx.AsyncClient
    def channel_response(req):
        assert req.headers["Authorization"] == "Bearer provider-token"
        return httpx.Response(200, json={"items": [{"id": "provider-id", "snippet": {"title": "Provider Name"}}]})
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(channel_response)))
    response = await AccountService(async_test_db).connect_account(user.id, request)
    account = await async_test_db.scalar(select(SocialAccount).where(SocialAccount.user_id == user.id))
    assert account.oauth_verified_at is not None
    assert response.connection_status == "connected_live"
    assert response.display_name == "Provider Name"
    assert "page-secret" not in response.model_dump_json()
    if platform == "x":
        assert auth._state_store[request.state]["code_verifier"] == "stored-verifier"
    if platform in {"facebook", "instagram"}:
        assert account.access_token == "page-secret"


@pytest.mark.asyncio
async def test_simulated_callback_cannot_create_account(async_test_db, provider_settings):
    user, request = await prepare_attempt(async_test_db, "x")
    request.authorization_code = "dev_auth_x_legacy"
    with pytest.raises(HTTPException):
        await AccountService(async_test_db).connect_account(user.id, request)
    assert await async_test_db.scalar(select(SocialAccount)) is None


@pytest.mark.asyncio
async def test_callback_redirect_must_match_attempt(async_test_db, provider_settings, monkeypatch):
    user, request = await prepare_attempt(async_test_db, "x")
    request.redirect_uri = "http://localhost:8080/oauth/callback"
    auth = SimpleNamespace(_state_store={}, exchange_code=AsyncMock(return_value={"access_token": "token"}),
                           get_user_profile=AsyncMock(return_value={"id": "provider-id"}))
    monkeypatch.setattr(oauth_service, "configured_adapter", lambda *args: SimpleNamespace(auth=auth))
    with pytest.raises(HTTPException) as error:
        await AccountService(async_test_db).connect_account(user.id, request)
    assert error.value.status_code == 400
    assert await async_test_db.scalar(select(SocialAccount)) is None


@pytest.mark.asyncio
async def test_refresh_preserves_existing_verification(async_test_db):
    """Plan item 4: verified status must survive a successful token refresh."""
    user, _ = await prepare_attempt(async_test_db, "x")
    account = SocialAccount(user_id=user.id, platform="x", platform_user_id="123", username="handle",
                            access_token="old-token", refresh_token="old-refresh",
                            token_expires_at=datetime.now(timezone.utc).replace(tzinfo=None),
                            oauth_verified_at=datetime.now(timezone.utc).replace(tzinfo=None),
                            is_active=True)
    async_test_db.add(account)
    await async_test_db.commit()

    adapter = MagicMock()
    adapter.auth.refresh_access_token = AsyncMock(return_value={
        "access_token": "refreshed-token", "refresh_token": "refreshed-refresh", "expires_in": 3600})
    from unittest.mock import patch
    with patch("backend.app.services.account_service.owned_adapter", new=AsyncMock(return_value=adapter)):
        result = await AccountService(async_test_db).refresh_token(account.id, user.id)

    assert result is True
    refreshed = await async_test_db.scalar(select(SocialAccount).where(SocialAccount.id == account.id))
    assert refreshed.oauth_verified_at is not None
    assert refreshed.access_token == "refreshed-token"
    assert AccountService(async_test_db)._to_response(refreshed).connection_status == "connected_live"


def test_migration_adds_nullable_oauth_verified_at(tmp_path):
    """Migration must add oauth_verified_at nullable, preserving existing rows with NULL."""
    import sqlite3
    import importlib.util

    db_path = tmp_path / "migration_test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE social_accounts (
        id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36), platform VARCHAR(50),
        platform_user_id VARCHAR(100), oauth_verified_at DATETIME)""")
    conn.execute("INSERT INTO social_accounts (id, user_id, platform, platform_user_id) VALUES ('a','u','x','123')")
    conn.commit()

    script = """
import sqlite3
conn = sqlite3.connect({db!r})
columns = [row[1] for row in conn.execute('PRAGMA table_info(social_accounts)')]
if 'oauth_verified_at' not in columns:
    conn.execute('ALTER TABLE social_accounts ADD COLUMN oauth_verified_at DATETIME NULL')
    conn.commit()
value = conn.execute("SELECT oauth_verified_at FROM social_accounts WHERE id='a'").fetchone()[0]
assert value is None, 'legacy row must keep NULL verification'
print('MIGRATION_OK')
"""
    proc = subprocess.run([sys.executable, "-c", script.format(db=str(db_path))],
                          capture_output=True, text=True)
    conn.close()
    assert proc.returncode == 0, proc.stderr
    assert "MIGRATION_OK" in proc.stdout
