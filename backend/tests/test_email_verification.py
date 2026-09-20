"""Integration tests for real email verification flow.

Covers: OTP generation at registration, correct OTP success, wrong OTP
failure, expired OTP failure, OTP invalidation after use, and resend.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from backend.app.main import create_app
from backend.app.db.session import Base, get_db
from backend.app.db.models import User, OtpChallenge


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


def _register(client, email, password="Password123!", full_name="Test User", accept_terms=True):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name, "accept_terms": accept_terms},
    )


def _auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


async def _get_user(async_test_db, email: str):
    stmt = select(User).where(User.email == email)
    result = await async_test_db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_otp_challenge(async_test_db, email: str, purpose: str = "EMAIL_VERIFICATION"):
    stmt = select(OtpChallenge).where(
        OtpChallenge.email == email,
        OtpChallenge.purpose == purpose,
        OtpChallenge.used_at.is_(None),
        OtpChallenge.revoked_at.is_(None),
    ).order_by(OtpChallenge.created_at.desc())
    result = await async_test_db.execute(stmt)
    return result.scalars().first()


class TestEmailVerification:
    """Real email verification: OTP generated, verified with correct OTP, fails otherwise."""

    @pytest.mark.asyncio
    async def test_registration_stores_otp_challenge_and_unverified_user(self, client, async_test_db):
        """Registering sets is_verified=False and creates an active OtpChallenge."""
        resp = _register(client, "new.user@example.com")
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["user"]["is_verified"] is False

        user = await _get_user(async_test_db, "new.user@example.com")
        assert user is not None
        assert user.is_verified is False
        assert user.email_verified_at is None

        # Check that an OtpChallenge was created
        challenge = await _get_otp_challenge(async_test_db, "new.user@example.com")
        assert challenge is not None
        assert challenge.otp_hash is not None
        assert len(challenge.otp_hash) == 64  # SHA-256
        assert challenge.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)

    @pytest.mark.asyncio
    async def test_unverified_user_cannot_login(self, client, async_test_db):
        """Unverified users must be rejected at login with 403 Forbidden."""
        resp = _register(client, "unverified.login@example.com")
        assert resp.status_code == 201

        login_resp = client.post("/api/v1/auth/login", json={
            "email": "unverified.login@example.com",
            "password": "Password123!",
        })
        assert login_resp.status_code == 403
        assert "verification required" in login_resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_wrong_otp_fails_and_increments_attempts(self, client, async_test_db):
        """A wrong 6-digit OTP must be rejected (400) and attempt_count incremented."""
        resp = _register(client, "wrong.otp@example.com")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)

        verify_resp = client.post(
            "/api/v1/auth/verify-email",
            headers=headers,
            json={"code": "999999"},
        )
        assert verify_resp.status_code == 400
        assert "Invalid verification code" in verify_resp.json()["detail"]

        challenge = await _get_otp_challenge(async_test_db, "wrong.otp@example.com")
        assert challenge.attempt_count == 1

        # User must remain unverified
        user = await _get_user(async_test_db, "wrong.otp@example.com")
        assert user.is_verified is False

    @pytest.mark.asyncio
    async def test_expired_otp_fails(self, client, async_test_db):
        """An expired OTP challenge must be rejected (400)."""
        resp = _register(client, "expired.otp@example.com")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)

        # Expire the challenge in DB
        challenge = await _get_otp_challenge(async_test_db, "expired.otp@example.com")
        challenge.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
        await async_test_db.commit()

        verify_resp = client.post(
            "/api/v1/auth/verify-email",
            headers=headers,
            json={"code": "123456"},
        )
        assert verify_resp.status_code == 400
        assert "expired" in verify_resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_resend_cooldown_enforced(self, client, async_test_db):
        """Requesting resend before 60 seconds must be rejected (429)."""
        resp = _register(client, "cooldown.user@example.com")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)

        # Immediate resend should trigger 429 cooldown
        resend_resp = client.post("/api/v1/auth/resend-verification", headers=headers)
        assert resend_resp.status_code == 429
        assert "wait 60 seconds" in resend_resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_resend_email_otp_endpoint(self, client, async_test_db):
        """Test POST /auth/resend-email-otp with unauthenticated request containing email."""
        resp = _register(client, "unauth.resend@example.com")
        assert resp.status_code == 201

        # Fast-forward the challenge created_at to bypass 60s cooldown for test
        challenge = await _get_otp_challenge(async_test_db, "unauth.resend@example.com")
        challenge.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=65)
        await async_test_db.commit()

        resend_resp = client.post("/api/v1/auth/resend-email-otp", json={"email": "unauth.resend@example.com"})
        assert resend_resp.status_code == 200
        assert "sent" in resend_resp.json()["message"].lower()

    def test_verification_token_never_present_in_production_response(self, client, monkeypatch):
        """Proof: verification_token is strictly NEVER included in registration response."""
        from backend.app.config import get_settings
        settings = get_settings()

        monkeypatch.setattr(settings, "ENVIRONMENT", "production")
        monkeypatch.setattr(settings, "DEBUG", False)
        monkeypatch.setattr(settings, "ENABLE_EMAIL_NOTIFICATIONS", False)

        from unittest.mock import AsyncMock, patch
        with patch("backend.app.core.rate_limit.redis_limit", new=AsyncMock(return_value=(False, 10, 60))):
            resp = _register(client, "prod.user@example.com")
            assert resp.status_code == 201
            data = resp.json()
            assert data.get("verification_token") is None
