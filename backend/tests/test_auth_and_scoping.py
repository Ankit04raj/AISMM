"""Integration tests for User Authentication, Token Authorization, 2FA, Email Verification, and User Scoping."""

import pytest
import pytest_asyncio
import struct
import time
import base64
import hmac
import hashlib
from uuid import uuid4, UUID
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from backend.app.main import create_app
from backend.app.db.session import Base, get_db
from backend.app.db.models import (
    User,
    SocialAccount,
    Post,
    PostPublication,
    ContentTypeEnum,
    PostStatusEnum,
)
from backend.app.core.security import verify_totp


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_test_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def app_with_db(async_test_db):
    app = create_app()

    async def override_get_db():
        yield async_test_db

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def client(app_with_db):
    return TestClient(app_with_db)


def compute_current_totp_code(secret_b32: str) -> str:
    """Helper computing expected 6-digit TOTP code for test verification."""
    key = base64.b32decode(secret_b32, casefold=True)
    step = int(time.time() // 30)
    msg = struct.pack(">Q", step)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    truncated_hash = struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(truncated_hash % 1_000_000).zfill(6)


class TestAuthAndUserScoping:
    """Test (a) 401 on missing token, (b) register/login/access flow, (c) user data isolation, (d) 2FA TOTP, (e) email verification, (f) logout token revocation."""

    def test_unauthenticated_protected_routes_return_401(self, client):
        """Proof: Accessing protected routes without a token must return 401 Unauthorized."""
        protected_routes = [
            ("GET", "/api/v1/auth/me"),
            ("GET", "/api/v1/accounts"),
            ("GET", "/api/v1/posts"),
            ("POST", "/api/v1/posts", {"platform": "instagram", "caption": "test"}),
            ("GET", "/api/v1/analytics/dashboard"),
            ("GET", "/api/v1/growth/accounts/00000000-0000-0000-0000-000000000001/projections"),
            ("POST", "/api/v1/scheduling/recommend-times", {"platform": "instagram", "target_date": "2026-09-05"}),
            ("GET", "/api/v1/strategy/dashboard"),
            ("GET", "/api/v1/metrics/overview"),
            ("GET", "/api/v1/models/registry"),
            ("POST", "/api/v1/reply/classify", {"text": "hello"}),
        ]

        for method, route, *body in protected_routes:
            if method == "GET":
                resp = client.get(route)
            else:
                resp = client.post(route, json=body[0] if body else {})
            assert resp.status_code == 401, f"Expected 401 for {method} {route}, got {resp.status_code}: {resp.text}"
            assert "detail" in resp.json() or "error" in resp.json()

    def test_public_routes_remain_accessible_without_token(self, client):
        """Public routes (health, root, platform oauth init, webhooks) must remain accessible."""
        resp_root = client.get("/")
        assert resp_root.status_code == 200

        resp_health = client.get("/health")
        assert resp_health.status_code == 200

        resp_oauth = client.post("/api/v1/auth/oauth/init", json={
            "platform": "instagram",
            "redirect_uri": "http://localhost:8000/cb",
        })
        assert resp_oauth.status_code == 200

    def test_register_login_and_authenticated_access(self, client):
        """Proof: Register -> Login -> Access with Bearer token -> 200 and scoped profile."""
        # 1. Register User 1
        reg_payload = {
            "email": "user1@aismm.io",
            "password": "SecurePassword123!",
            "full_name": "Test User One",
        }
        reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 201
        reg_data = reg_resp.json()
        assert "access_token" in reg_data
        assert "refresh_token" in reg_data
        assert reg_data["user"]["email"] == "user1@aismm.io"
        assert reg_data["user"]["full_name"] == "Test User One"
        user1_id = reg_data["user"]["id"]

        # Duplicate registration fails
        dup_resp = client.post("/api/v1/auth/register", json=reg_payload)
        assert dup_resp.status_code == 400

        # 2. Login User 1
        login_payload = {
            "email": "user1@aismm.io",
            "password": "SecurePassword123!",
        }
        login_resp = client.post("/api/v1/auth/login", json=login_payload)
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # Invalid password returns 401
        bad_login = client.post("/api/v1/auth/login", json={"email": "user1@aismm.io", "password": "wrong"})
        assert bad_login.status_code == 401

        # 3. Access /auth/me with Bearer token
        headers = {"Authorization": f"Bearer {access_token}"}
        me_resp = client.get("/api/v1/auth/me", headers=headers)
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["id"] == user1_id
        assert me_data["email"] == "user1@aismm.io"

        # 4. Refresh token flow
        refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 200
        new_access_token = refresh_resp.json()["access_token"]
        assert new_access_token != ""

    @pytest.mark.asyncio
    async def test_multi_user_data_isolation(self, client, async_test_db):
        """Proof: User 2 cannot see or access User 1's accounts, posts, or scoped metrics."""
        # 1. Register User 1
        u1_resp = client.post("/api/v1/auth/register", json={
            "email": "alice@aismm.io",
            "password": "PasswordAlice123!",
            "full_name": "Alice Developer",
        })
        assert u1_resp.status_code == 201
        u1_token = u1_resp.json()["access_token"]
        u1_id = UUID(u1_resp.json()["user"]["id"])
        u1_headers = {"Authorization": f"Bearer {u1_token}"}

        # 2. Register User 2
        u2_resp = client.post("/api/v1/auth/register", json={
            "email": "bob@aismm.io",
            "password": "PasswordBob123!",
            "full_name": "Bob Analyst",
        })
        assert u2_resp.status_code == 201
        u2_token = u2_resp.json()["access_token"]
        u2_headers = {"Authorization": f"Bearer {u2_token}"}

        # 3. Create a SocialAccount and Post in DB owned by User 1
        u1_account = SocialAccount(
            user_id=u1_id,
            platform="instagram",
            platform_user_id="alice_ig_999",
            username="alice_official",
            display_name="Alice Studio",
            is_active=True,
        )
        async_test_db.add(u1_account)

        u1_post = Post(
            user_id=u1_id,
            caption="Alice exclusive launch post #ai #social",
            content_type=ContentTypeEnum.POST,
            status=PostStatusEnum.PUBLISHED,
        )
        async_test_db.add(u1_post)
        await async_test_db.commit()
        await async_test_db.refresh(u1_account)
        await async_test_db.refresh(u1_post)

        u1_account_id = str(u1_account.id)
        u1_post_id = str(u1_post.id)

        # 4. Verify User 1 sees their account and post
        u1_accounts = client.get("/api/v1/accounts", headers=u1_headers).json()
        assert u1_accounts["total"] == 1
        assert u1_accounts["accounts"][0]["id"] == u1_account_id

        u1_posts = client.get("/api/v1/posts", headers=u1_headers).json()
        assert u1_posts["total"] == 1
        assert u1_posts["posts"][0]["id"] == u1_post_id

        # 5. Verify User 2 sees ZERO accounts and ZERO posts
        u2_accounts = client.get("/api/v1/accounts", headers=u2_headers).json()
        assert u2_accounts["total"] == 0
        assert u2_accounts["accounts"] == []

        u2_posts = client.get("/api/v1/posts", headers=u2_headers).json()
        assert u2_posts["total"] == 0
        assert u2_posts["posts"] == []

        # 6. User 2 directly requesting User 1's post or account by ID must return 404
        u2_get_post = client.get(f"/api/v1/posts/{u1_post_id}", headers=u2_headers)
        assert u2_get_post.status_code == 404

        u2_get_account = client.get(f"/api/v1/accounts/{u1_account_id}", headers=u2_headers)
        assert u2_get_account.status_code == 404

        u2_del_post = client.delete(f"/api/v1/posts/{u1_post_id}", headers=u2_headers)
        assert u2_del_post.status_code == 404

    def test_email_verification_flow(self, client):
        """Proof 2.1: Email verification flow updates account is_verified state."""
        reg_resp = client.post("/api/v1/auth/register", json={
            "email": "unverified_user@aismm.io",
            "password": "Password123!",
            "full_name": "Unverified User",
        })
        assert reg_resp.status_code == 201
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Profile starts with is_verified = False
        me_resp = client.get("/api/v1/auth/me", headers=headers)
        assert me_resp.json()["is_verified"] is False

        # Verify email with code
        verify_resp = client.post("/api/v1/auth/verify-email", headers=headers, json={"code": "274819"})
        assert verify_resp.status_code == 200
        assert verify_resp.json()["verified"] is True

        # Profile is now verified
        me_after = client.get("/api/v1/auth/me", headers=headers)
        assert me_after.json()["is_verified"] is True

    def test_two_factor_authentication_totp_flow(self, client):
        """Proof 2.1: TOTP 2FA setup, activation, and login challenge enforcement."""
        reg_resp = client.post("/api/v1/auth/register", json={
            "email": "totp_user@aismm.io",
            "password": "SecurePassword123!",
            "full_name": "TOTP User",
        })
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 2FA Setup -> returns base32 secret and otpauth URI
        setup_resp = client.post("/api/v1/auth/2fa/setup", headers=headers)
        assert setup_resp.status_code == 200
        secret = setup_resp.json()["secret"]
        assert "otpauth://" in setup_resp.json()["otpauth_url"]
        assert len(secret) >= 16

        # 2. Enable 2FA with computed TOTP code
        totp_code = compute_current_totp_code(secret)
        enable_resp = client.post("/api/v1/auth/2fa/enable", headers=headers, json={"code": totp_code})
        assert enable_resp.status_code == 200
        assert enable_resp.json()["two_factor_enabled"] is True

        # Invalid code rejected
        bad_enable = client.post("/api/v1/auth/2fa/enable", headers=headers, json={"code": "000000"})
        assert bad_enable.status_code == 400

        # 3. Login with 2FA enabled:
        # 3a. Initial login without 2FA code returns requires_2fa: True
        login_resp = client.post("/api/v1/auth/login", json={"email": "totp_user@aismm.io", "password": "SecurePassword123!"})
        assert login_resp.status_code == 200
        assert login_resp.json()["requires_2fa"] is True
        assert login_resp.json()["access_token"] == ""

        # 3b. Login with valid 2FA code returns full JWT access token
        valid_totp_code = compute_current_totp_code(secret)
        login_with_2fa = client.post("/api/v1/auth/login", json={
            "email": "totp_user@aismm.io",
            "password": "SecurePassword123!",
            "two_factor_code": valid_totp_code,
        })
        assert login_with_2fa.status_code == 200
        assert login_with_2fa.json()["requires_2fa"] is False
        assert login_with_2fa.json()["access_token"] != ""

    def test_server_side_logout_token_revocation(self, client):
        """Proof 2.2: Logout blacklists/revokes JWT tokens server-side."""
        reg_resp = client.post("/api/v1/auth/register", json={
            "email": "logout_user@aismm.io",
            "password": "Password123!",
            "full_name": "Logout User",
        })
        token = reg_resp.json()["access_token"]
        refresh_token = reg_resp.json()["refresh_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Token works before logout
        assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

        # Logout user
        logout_resp = client.post("/api/v1/auth/logout", headers=headers, json={"refresh_token": refresh_token})
        assert logout_resp.status_code == 200

        # Accessing protected route with revoked token must now return 401 Unauthorized
        revoked_access = client.get("/api/v1/auth/me", headers=headers)
        assert revoked_access.status_code == 401
        assert "revoked" in revoked_access.json()["detail"].lower()
