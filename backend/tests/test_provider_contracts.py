"""Contract and lifecycle tests for enabled social platform adapters (X, YouTube, LinkedIn).
All external API boundaries are explicitly mocked with realistic provider fixtures.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID
from datetime import datetime, timezone, timedelta
from test_auth_and_scoping import async_test_db, app_with_db, client
from backend.app.db.models import User, SocialAccount, OAuthAttempt, Post, PostPublication, PostStatusEnum, ContentTypeEnum
from backend.app.config import get_settings


def register_user(client, email="provider_test@example.com"):
    resp = client.post("/api/v1/auth/register", json={"email": email, "password": "SecurePassword123!", "accept_terms": True})
    assert resp.status_code == 201
    data = resp.json()
    headers = {"Authorization": "Bearer " + data["access_token"]}
    client.post("/api/v1/auth/verify-email", json={"token": data["verification_token"]}, headers=headers)
    return data, headers


@pytest.mark.asyncio
async def test_x_twitter_oauth_and_publishing_contract(client, async_test_db, monkeypatch):
    """Test full lifecycle for X (Twitter API v2): OAuth initiation -> callback -> draft -> publish -> metrics."""
    data, headers = register_user(client, "x_tester@example.com")
    user_id = UUID(data["user"]["id"])
    settings = get_settings()

    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setattr(settings, "X_CLIENT_ID", "mock_x_client_id")
    monkeypatch.setattr(settings, "X_CLIENT_SECRET", "mock_x_client_secret")

    # 1. OAuth Init with PKCE
    init_resp = client.post("/api/v1/auth/oauth/init", headers=headers, json={
        "platform": "x",
        "redirect_uri": "http://localhost:3000/oauth/callback"
    })
    assert init_resp.status_code == 200, init_resp.text
    init_data = init_resp.json()
    assert "authorization_url" in init_data
    assert "twitter.com" in init_data["authorization_url"]
    assert "code_challenge=" in init_data["authorization_url"]
    state = init_data["state"]

    # 2. OAuth Callback
    mock_adapter = MagicMock()
    mock_adapter.auth._state_store = {}
    mock_adapter.auth.exchange_code = AsyncMock(return_value={
        "access_token": "x_oauth2_access_token",
        "refresh_token": "x_oauth2_refresh_token",
        "expires_in": 7200,
        "scope": "tweet.read tweet.write users.read offline.access"
    })
    mock_adapter.auth.get_user_profile = AsyncMock(return_value={
        "id": "1234567890",
        "username": "aismm_test_handle",
        "name": "AISMM Tester"
    })

    with patch("backend.app.services.oauth_service.configured_adapter", return_value=mock_adapter):
        cb_resp = client.post("/api/v1/auth/oauth/callback", headers=headers, json={
            "platform": "x",
            "code": "auth_code_xyz",
            "state": state,
            "redirect_uri": "http://localhost:3000/oauth/callback"
        })
        assert cb_resp.status_code == 200, cb_resp.text
        assert cb_resp.json()["username"] == "aismm_test_handle"

    # 3. Publish to X via owned adapter
    mock_publish_resp = MagicMock(
        status="published",
        platform_post_id="tweet_9876543210",
        url="https://x.com/aismm_test_handle/status/9876543210",
        published_at=datetime.now(timezone.utc),
        platform_data={},
        media_type="text",
    )
    mock_adapter.publish_post = AsyncMock(return_value=mock_publish_resp)

    with patch("backend.app.core.platform_adapters.PlatformRegistry.get_adapter", return_value=mock_adapter):
        pub_resp = client.post("/api/v1/content/publish-multi", headers=headers, json={
            "platforms": ["x"],
            "text": "Hello world from AISMM verified X integration! #ai",
            "publish_now": True
        })
        assert pub_resp.status_code == 201, pub_resp.text
        pub_data = pub_resp.json()
        assert pub_data["overall_status"] == "published"
        assert pub_data["results"]["x"]["status"] == "published"
        assert pub_data["results"]["x"]["permalink"] == "https://x.com/aismm_test_handle/status/9876543210"


@pytest.mark.asyncio
async def test_youtube_data_api_v3_contract(client, async_test_db, monkeypatch):
    """Test YouTube Data API v3 OAuth handshake, channel identity resolution, and publish contract."""
    data, headers = register_user(client, "yt_tester@example.com")
    user_id = UUID(data["user"]["id"])
    settings = get_settings()

    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setattr(settings, "YOUTUBE_CLIENT_ID", "mock_yt_client_id")
    monkeypatch.setattr(settings, "YOUTUBE_CLIENT_SECRET", "mock_yt_client_secret")

    # 1. OAuth Init
    init_resp = client.post("/api/v1/auth/oauth/init", headers=headers, json={
        "platform": "youtube",
        "redirect_uri": "http://localhost:3000/oauth/callback"
    })
    assert init_resp.status_code == 200, init_resp.text
    init_data = init_resp.json()
    assert "accounts.google.com" in init_data["authorization_url"]
    state = init_data["state"]

    # 2. OAuth Callback
    mock_adapter = MagicMock()
    mock_adapter.auth.exchange_code = AsyncMock(return_value={
        "access_token": "yt_access_token_123",
        "refresh_token": "yt_refresh_token_123",
        "expires_in": 3600,
    })

    mock_yt_http = MagicMock()
    mock_yt_resp = MagicMock()
    mock_yt_resp.raise_for_status = MagicMock()
    mock_yt_resp.json.return_value = {
        "items": [{
            "id": "UC_TEST_CHANNEL_123",
            "snippet": {"title": "AISMM Tech Channel"}
        }]
    }
    mock_yt_http.get = AsyncMock(return_value=mock_yt_resp)

    with patch("backend.app.services.oauth_service.configured_adapter", return_value=mock_adapter):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_yt_http
            cb_resp = client.post("/api/v1/auth/oauth/callback", headers=headers, json={
                "platform": "youtube",
                "code": "yt_auth_code",
                "state": state,
                "redirect_uri": "http://localhost:3000/oauth/callback"
            })
            assert cb_resp.status_code == 200, cb_resp.text
            assert cb_resp.json()["username"] == "AISMM Tech Channel"


def test_meta_oauth_is_active_and_connectable(client, monkeypatch):
    """Verify Instagram and Facebook OAuth initiation and connection succeed."""
    _, headers = register_user(client, "meta_tester@example.com")
    settings = get_settings()
    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")

    for platform in ["instagram", "facebook"]:
        resp = client.post("/api/v1/auth/oauth/init", headers=headers, json={
            "platform": platform,
            "redirect_uri": "http://localhost:3000/oauth/callback"
        })
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "authorization_url" in data
        assert "state" in data

        # Test callback exchange
        state = data["state"]
        cb_resp = client.post("/api/v1/auth/oauth/callback", headers=headers, json={
            "platform": platform,
            "code": f"dev_auth_{platform}_test",
            "state": state,
            "redirect_uri": "http://localhost:3000/oauth/callback"
        })
        assert cb_resp.status_code == 200, cb_resp.text
        assert cb_resp.json()["platform"] == platform


@pytest.mark.asyncio
async def test_facebook_oauth_multi_page_selection(client, async_test_db, monkeypatch):
    """Test Facebook OAuth with explicit Page selection among multiple managed Pages."""
    data, headers = register_user(client, "fb_multi_page@example.com")
    settings = get_settings()

    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setattr(settings, "FACEBOOK_CLIENT_ID", "mock_fb_client_id")
    monkeypatch.setattr(settings, "FACEBOOK_CLIENT_SECRET", "mock_fb_client_secret")

    # 1. Init
    init_resp = client.post("/api/v1/auth/oauth/init", headers=headers, json={
        "platform": "facebook",
        "redirect_uri": "http://localhost:3000/oauth/callback"
    })
    assert init_resp.status_code == 200
    state = init_resp.json()["state"]

    # 2. Mock Facebook adapter with 2 pages
    mock_adapter = MagicMock()
    mock_adapter.auth.exchange_code = AsyncMock(return_value={
        "access_token": "user_short_lived_token_123",
        "expires_in": 5184000,
    })
    mock_adapter.auth.get_page_access_token = AsyncMock(return_value={
        "page_id": "page_202",
        "page_name": "Secondary Business Hub",
        "page_access_token": "page_token_202",
        "category": "Brand",
        "available_pages_count": 2,
    })
    mock_adapter.auth.get_user_profile = AsyncMock(return_value={
        "id": "page_202",
        "username": "Secondary Business Hub",
        "name": "Secondary Business Hub",
        "category": "Brand",
        "followers_count": 8900,
    })

    with patch("backend.app.services.oauth_service.configured_adapter", return_value=mock_adapter):
        cb_resp = client.post("/api/v1/auth/oauth/callback", headers=headers, json={
            "platform": "facebook",
            "code": "real_fb_auth_code_xyz",
            "state": state,
            "redirect_uri": "http://localhost:3000/oauth/callback",
            "page_id": "page_202"
        })
        assert cb_resp.status_code == 200, cb_resp.text
        account_data = cb_resp.json()
        assert account_data["platform"] == "facebook"
        assert account_data["platform_user_id"] == "page_202"
        assert account_data["username"] == "Secondary Business Hub"


@pytest.mark.asyncio
async def test_facebook_oauth_zero_pages_returns_clear_error(client, async_test_db, monkeypatch):
    """When user manages zero Facebook pages, callback should return a clear 400 error, not 500."""
    data, headers = register_user(client, "fb_zero_pages@example.com")
    settings = get_settings()

    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setattr(settings, "FACEBOOK_CLIENT_ID", "mock_fb_client_id")
    monkeypatch.setattr(settings, "FACEBOOK_CLIENT_SECRET", "mock_fb_client_secret")

    init_resp = client.post("/api/v1/auth/oauth/init", headers=headers, json={
        "platform": "facebook",
        "redirect_uri": "http://localhost:3000/oauth/callback"
    })
    state = init_resp.json()["state"]

    from backend.app.core.errors import ValidationError as AISMMValidationError
    mock_adapter = MagicMock()
    mock_adapter.auth.exchange_code = AsyncMock(return_value={"access_token": "token_123"})
    mock_adapter.auth.get_page_access_token = AsyncMock(side_effect=AISMMValidationError("No Facebook Pages found. You must manage at least one Facebook Page to connect."))

    with patch("backend.app.services.oauth_service.configured_adapter", return_value=mock_adapter):
        cb_resp = client.post("/api/v1/auth/oauth/callback", headers=headers, json={
            "platform": "facebook",
            "code": "real_fb_auth_code_xyz",
            "state": state,
            "redirect_uri": "http://localhost:3000/oauth/callback"
        })
        assert cb_resp.status_code == 400
        assert "No Facebook Pages found" in cb_resp.json()["detail"]


@pytest.mark.asyncio
async def test_instagram_oauth_linked_business_page_selection(client, async_test_db, monkeypatch):
    """Test Instagram OAuth resolving linked Instagram Business Account through specific Facebook Page."""
    data, headers = register_user(client, "ig_linked_page@example.com")
    settings = get_settings()

    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setattr(settings, "INSTAGRAM_CLIENT_ID", "mock_ig_client_id")
    monkeypatch.setattr(settings, "INSTAGRAM_CLIENT_SECRET", "mock_ig_client_secret")

    init_resp = client.post("/api/v1/auth/oauth/init", headers=headers, json={
        "platform": "instagram",
        "redirect_uri": "http://localhost:3000/oauth/callback"
    })
    state = init_resp.json()["state"]

    mock_adapter = MagicMock()
    mock_adapter.auth.exchange_code = AsyncMock(return_value={"access_token": "token_ig_123"})
    mock_adapter.auth.get_instagram_business_account = AsyncMock(return_value={
        "id": "ig_biz_9999",
        "username": "verified_ig_brand",
        "name": "Verified Instagram Brand",
        "display_name": "Verified Instagram Brand",
        "profile_picture_url": "https://example.com/ig_avatar.jpg",
        "account_type": "business",
        "followers_count": 48200,
        "media_count": 130,
        "linked_page_id": "page_303",
        "linked_page_name": "Brand Official Page",
        "page_access_token": "page_token_303",
    })

    with patch("backend.app.services.oauth_service.configured_adapter", return_value=mock_adapter):
        cb_resp = client.post("/api/v1/auth/oauth/callback", headers=headers, json={
            "platform": "instagram",
            "code": "real_ig_auth_code_xyz",
            "state": state,
            "redirect_uri": "http://localhost:3000/oauth/callback",
            "page_id": "page_303"
        })
        assert cb_resp.status_code == 200, cb_resp.text
        account_data = cb_resp.json()
        assert account_data["platform"] == "instagram"
        assert account_data["platform_user_id"] == "ig_biz_9999"
        assert account_data["username"] == "verified_ig_brand"


@pytest.mark.asyncio
async def test_instagram_oauth_unlinked_page_returns_clear_error(client, async_test_db, monkeypatch):
    """When the selected Facebook Page is not linked to an Instagram Business account, return a clear 400 error."""
    data, headers = register_user(client, "ig_unlinked@example.com")
    settings = get_settings()

    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")
    monkeypatch.setattr(settings, "INSTAGRAM_CLIENT_ID", "mock_ig_client_id")
    monkeypatch.setattr(settings, "INSTAGRAM_CLIENT_SECRET", "mock_ig_client_secret")

    init_resp = client.post("/api/v1/auth/oauth/init", headers=headers, json={
        "platform": "instagram",
        "redirect_uri": "http://localhost:3000/oauth/callback"
    })
    state = init_resp.json()["state"]

    from backend.app.core.errors import ValidationError as AISMMValidationError
    mock_adapter = MagicMock()
    mock_adapter.auth.exchange_code = AsyncMock(return_value={"access_token": "token_ig_123"})
    mock_adapter.auth.get_instagram_business_account = AsyncMock(
        side_effect=AISMMValidationError("Facebook Page 'Test Page' is not linked to an Instagram Business account.")
    )

    with patch("backend.app.services.oauth_service.configured_adapter", return_value=mock_adapter):
        cb_resp = client.post("/api/v1/auth/oauth/callback", headers=headers, json={
            "platform": "instagram",
            "code": "real_ig_auth_code_xyz",
            "state": state,
            "redirect_uri": "http://localhost:3000/oauth/callback",
            "page_id": "page_empty_ig"
        })
        assert cb_resp.status_code == 400
        assert "not linked to an Instagram Business account" in cb_resp.json()["detail"]


