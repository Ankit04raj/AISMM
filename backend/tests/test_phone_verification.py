"""Integration tests for phone number verification flow.

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
from backend.app.db.models import User


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


def _register(client, email, password="Password123!", full_name="Test User", phone_number=None, verification_method="email"):
    payload = {"email": email, "password": password, "full_name": full_name}
    if phone_number:
        payload["phone_number"] = phone_number
        payload["verification_method"] = verification_method
    return client.post(
        "/api/v1/auth/register",
        json=payload,
    )


def _auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


async def _get_user(async_test_db, email: str):
    stmt = select(User).where(User.email == email)
    result = await async_test_db.execute(stmt)
    return result.scalar_one_or_none()


class TestPhoneVerification:
    """Phone verification: OTP generated, verified with correct OTP, fails otherwise."""

    @pytest.mark.asyncio
    async def test_registration_with_phone_generates_otp_and_unverified_user(self, client, async_test_db):
        """Registering with phone method sets phone_verified=False and stores a non-empty OTP + expiry."""
        resp = _register(client, "phone.user@example.com", phone_number="+919876543210", verification_method="phone")
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["user"]["is_verified"] is False
        assert data["user"]["phone_verified"] is False
        assert data["user"]["phone_number"] == "+919876543210"

        # Dev mode: verification token should be in response
        assert "verification_token" in data
        assert data["verification_token"] is not None
        assert len(data["verification_token"]) == 6

        user = await _get_user(async_test_db, "phone.user@example.com")
        assert user is not None
        assert user.phone_verification_token is not None
        assert len(user.phone_verification_token) == 64  # SHA-256 hash
        assert user.phone_verification_expiry is not None
        assert user.phone_verification_expiry > datetime.now(timezone.utc).replace(tzinfo=None)

    @pytest.mark.asyncio
    async def test_verify_succeeds_with_correct_otp(self, client, async_test_db):
        """Verification succeeds only with the correct, unexpired OTP, then invalidates it."""
        resp = _register(client, "correct.phone@example.com", phone_number="+919876543211", verification_method="phone")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)
        otp = resp.json()["verification_token"]
        assert otp is not None

        verify_resp = client.post(
            "/api/v1/auth/verify-phone",
            headers=headers,
            json={"phone_number": "+919876543211", "code": otp},
        )
        assert verify_resp.status_code == 200, verify_resp.text
        assert verify_resp.json()["verified"] is True

        # OTP must be invalidated after use
        user = await _get_user(async_test_db, "correct.phone@example.com")
        assert user.phone_verified is True
        assert user.phone_verification_token is None
        assert user.phone_verification_expiry is None

    @pytest.mark.asyncio
    async def test_wrong_otp_fails(self, client, async_test_db):
        """A wrong verification OTP must be rejected (400)."""
        resp = _register(client, "wrong.phone@example.com", phone_number="+919876543212", verification_method="phone")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)

        verify_resp = client.post(
            "/api/v1/auth/verify-phone",
            headers=headers,
            json={"phone_number": "+919876543212", "code": "000000"},
        )
        assert verify_resp.status_code == 400
        assert "Invalid verification OTP" in verify_resp.json()["detail"]

        # User must remain unverified
        user = await _get_user(async_test_db, "wrong.phone@example.com")
        assert user.phone_verified is False

    @pytest.mark.asyncio
    async def test_expired_otp_fails(self, client, async_test_db):
        """An expired verification OTP must be rejected (400)."""
        resp = _register(client, "expired.phone@example.com", phone_number="+919876543213", verification_method="phone")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)

        # Simulate OTP expiry by backdating the stored expiry
        user = await _get_user(async_test_db, "expired.phone@example.com")
        user.phone_verification_expiry = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
        await async_test_db.commit()

        verify_resp = client.post(
            "/api/v1/auth/verify-phone",
            headers=headers,
            json={"phone_number": "+919876543213", "code": "123456"},
        )
        assert verify_resp.status_code == 400
        assert "expired" in verify_resp.json()["detail"].lower()

        user = await _get_user(async_test_db, "expired.phone@example.com")
        assert user.phone_verified is False

    @pytest.mark.asyncio
    async def test_resend_generates_new_otp(self, client, async_test_db):
        """Resend endpoint generates a fresh OTP and stores it."""
        resp = _register(client, "resend.phone@example.com", phone_number="+919876543214", verification_method="phone")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)

        user = await _get_user(async_test_db, "resend.phone@example.com")
        original_otp_hash = user.phone_verification_token

        resend_resp = client.post("/api/v1/auth/resend-phone-verification", headers=headers)
        assert resend_resp.status_code == 200, resend_resp.text

        user = await _get_user(async_test_db, "resend.phone@example.com")
        assert user.phone_verification_token is not None
        # OTP should be rotated (a new random OTP)
        assert user.phone_verification_token != original_otp_hash

    @pytest.mark.asyncio
    async def test_resend_rate_limit(self, client, async_test_db):
        """Resend endpoint is rate-limited to 3 requests per 5 minutes."""
        resp = _register(client, "ratelimit.phone@example.com", phone_number="+919876543215", verification_method="phone")
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]
        headers = _auth_headers(access_token)

        # First 3 should succeed
        for i in range(3):
            resend_resp = client.post("/api/v1/auth/resend-phone-verification", headers=headers)
            assert resend_resp.status_code == 200, f"Attempt {i+1}: {resend_resp.text}"

        # 4th should be rate-limited
        resend_resp = client.post("/api/v1/auth/resend-phone-verification", headers=headers)
        assert resend_resp.status_code == 429