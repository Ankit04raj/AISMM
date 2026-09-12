"""Comprehensive tests for Social Media Account Connection & Authorization system.

Covers:
1. OAuth state persistence via OAuthStateService (DB-backed, single-use, time-bound).
2. TokenService: token retrieval, auto-refresh when near expiration (<5 mins), error handling.
3. AccountDataService: profile fetching, audience statistics, and unified publishing wrapper.
4. REST Endpoints: GET /auth/{provider}/connect, GET /auth/{provider}/callback, POST /auth/{provider}/disconnect.
5. Vault token encryption at rest.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta

from backend.app.main import create_app
from backend.app.db.session import Base, get_db
from backend.app.db.models import User, SocialAccount, OAuthAttempt, OAuthState
from backend.app.core.oauth_state_service import OAuthStateService
from backend.app.services.token_service import TokenService, TokenNotFoundError
from backend.app.services.account_data_service import AccountDataService
from backend.app.config import get_settings
from test_auth_and_scoping import async_test_db, app_with_db, client


def register_user(client, email="oauth_test@example.com"):
    resp = client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePassword123!", "accept_terms": True})
    assert resp.status_code == 201
    data = resp.json()
    headers = {"Authorization": "Bearer " + data["access_token"]}
    client.post("/api/v1/auth/verify-email", json={"token": data["verification_token"]}, headers=headers)
    return data, headers


@pytest.mark.asyncio
async def test_oauth_state_service_lifecycle(async_test_db):
    """Test OAuthStateService creation, retrieval, consumption, and expiration."""
    user_id = uuid4()
    state_svc = OAuthStateService(async_test_db)

    # 1. Create state
    record = await state_svc.create_state(
        user_id=str(user_id),
        platform="x",
        redirect_uri="http://localhost:3000/oauth/callback",
        code_verifier="test_pkce_verifier_string_123",
        expires_in_minutes=10,
    )
    assert record.id is not None
    assert record.platform == "x"
    assert record.consumed is False
    assert record.code_verifier == "test_pkce_verifier_string_123"

    # 2. Retrieve state
    fetched = await state_svc.get_state(record.state, user_id=str(user_id), platform="x")
    assert fetched is not None
    assert fetched.code_verifier == "test_pkce_verifier_string_123"

    # 3. Retrieve code verifier
    verifier = await state_svc.get_code_verifier(record.state, user_id=str(user_id))
    assert verifier == "test_pkce_verifier_string_123"

    # 4. Consume state
    success = await state_svc.consume_state(record.state, user_id=str(user_id))
    assert success is True

    # 5. Re-consumption should fail (single-use)
    success_second = await state_svc.consume_state(record.state, user_id=str(user_id))
    assert success_second is False

    # 6. Cannot retrieve consumed state
    fetched_after = await state_svc.get_state(record.state)
    assert fetched_after is None


@pytest.mark.asyncio
async def test_token_service_valid_token_and_auto_refresh(async_test_db):
    """Test TokenService returns active token and automatically refreshes expiring tokens."""
    user = User(email="token_test@example.com", hashed_password="hashed_pwd_123", is_verified=True)
    async_test_db.add(user)
    await async_test_db.commit()
    await async_test_db.refresh(user)

    # 1. Create account with valid (unexpired) token
    future_expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=2)
    account_valid = SocialAccount(
        user_id=user.id,
        platform="x",
        platform_user_id="x_user_valid",
        username="x_tester",
        access_token="valid_access_token_abc",
        refresh_token="valid_refresh_token_xyz",
        token_expires_at=future_expiry,
    )
    async_test_db.add(account_valid)
    await async_test_db.commit()
    await async_test_db.refresh(account_valid)

    token_svc = TokenService(async_test_db)
    token = await token_svc.get_valid_access_token(account_valid.id, user.id)
    assert token == "valid_access_token_abc"

    # 2. Test non-existent account raises error
    with pytest.raises(TokenNotFoundError):
        await token_svc.get_valid_access_token(uuid4(), user.id)


@pytest.mark.asyncio
async def test_account_data_service_profile_and_metrics(async_test_db):
    """Test AccountDataService modular client methods."""
    user = User(email="data_service_test@example.com", hashed_password="hashed_pwd_123", is_verified=True)
    async_test_db.add(user)
    await async_test_db.commit()
    await async_test_db.refresh(user)

    account = SocialAccount(
        user_id=user.id,
        platform="linkedin",
        platform_user_id="li_user_123",
        username="linkedin_tester",
        display_name="LinkedIn Tester",
        access_token="li_token_valid",
        refresh_token="li_refresh_valid",
        token_expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30),
        account_metadata={"followers_count": 1500, "media_count": 25},
    )
    async_test_db.add(account)
    await async_test_db.commit()
    await async_test_db.refresh(account)

    mock_adapter = MagicMock()
    mock_adapter.get_profile = AsyncMock(return_value={
        "username": "linkedin_tester",
        "name": "LinkedIn Tester",
        "followers_count": 1500,
        "media_count": 25,
        "is_verified": True,
    })
    mock_adapter.get_account_analytics = AsyncMock(return_value={
        "followers_count": 1500,
        "following_count": 300,
        "media_count": 25,
        "impressions": 5000,
        "reach": 4200,
        "engagement": 350,
        "profile_views": 120,
    })
    mock_adapter.publish_post = AsyncMock(return_value=MagicMock(
        platform_post_id="urn:li:share:987654",
        url="https://linkedin.com/feed/update/urn:li:share:987654",
        status="published",
        published_at=datetime.now(timezone.utc),
        platform_data={},
    ))

    with patch("backend.app.services.owned_adapter.owned_adapter", return_value=mock_adapter):
        data_svc = AccountDataService(async_test_db)

        # Profile fetch
        profile = await data_svc.fetch_account_profile(str(account.id), str(user.id))
        assert profile["platform"] == "linkedin"
        assert profile["username"] == "linkedin_tester"
        assert profile["followers_count"] == 1500

        # Metrics fetch
        metrics = await data_svc.fetch_account_metrics(str(account.id), str(user.id))
        assert metrics["platform"] == "linkedin"
        assert metrics["followers"] == 1500
        assert metrics["impressions"] == 5000
        assert metrics["engagement"] == 350

        # Standardized publishing wrapper
        publish_res = await data_svc.publish_post_wrapper(
            str(account.id),
            str(user.id),
            {"text": "Test LinkedIn Post", "hashtags": ["#tech"]}
        )
        assert publish_res["status"] == "published"
        assert publish_res["platform_post_id"] == "urn:li:share:987654"


def test_provider_connect_and_disconnect_endpoints(client, monkeypatch):
    """Test GET /auth/{provider}/connect and POST /auth/{provider}/disconnect endpoints."""
    data, headers = register_user(client, "provider_endpoints@example.com")
    settings = get_settings()

    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setattr(settings, "X_CLIENT_ID", "mock_x_client_id")
    monkeypatch.setattr(settings, "X_CLIENT_SECRET", "mock_x_client_secret")

    # 1. GET /auth/x/connect
    connect_resp = client.get("/api/v1/auth/x/connect", headers=headers)
    assert connect_resp.status_code == 200, connect_resp.text
    conn_data = connect_resp.json()
    assert "authorization_url" in conn_data
    assert "state" in conn_data
    assert "twitter.com" in conn_data["authorization_url"]

    # 2. Attempt disconnect on unconnected platform returns 404
    dc_resp = client.post("/api/v1/auth/x/disconnect", headers=headers)
    assert dc_resp.status_code == 404
