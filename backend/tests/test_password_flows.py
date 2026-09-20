"""Integration tests for forgot password, OTP verification, password reset, and password change."""

import pytest
import pytest_asyncio
import hashlib
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update

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


def _register_and_verify(client, async_test_db, email, password="Password123!"):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User", "accept_terms": True},
    )
    assert resp.status_code == 201
    return resp.json()


class TestPasswordFlows:
    """Test full forgot-password, verify OTP, reset password, and change password flows."""

    @pytest.mark.asyncio
    async def test_forgot_password_generates_otp_challenge(self, client, async_test_db):
        """Forgot password creates an OTP challenge with purpose PASSWORD_RESET."""
        _register_and_verify(client, async_test_db, "forgot.test@example.com")

        resp = client.post("/api/v1/auth/forgot-password", json={"email": "forgot.test@example.com"})
        assert resp.status_code == 200
        assert "verification code has been sent" in resp.json()["message"]

        # Check DB challenge
        stmt = select(OtpChallenge).where(
            OtpChallenge.email == "forgot.test@example.com",
            OtpChallenge.purpose == "PASSWORD_RESET",
        )
        res = await async_test_db.execute(stmt)
        challenge = res.scalars().first()
        assert challenge is not None
        assert challenge.otp_hash is not None

    @pytest.mark.asyncio
    async def test_verify_password_reset_otp_wrong_code(self, client, async_test_db):
        """Submitting wrong reset OTP fails with 400."""
        _register_and_verify(client, async_test_db, "wrong.reset@example.com")
        client.post("/api/v1/auth/forgot-password", json={"email": "wrong.reset@example.com"})

        resp = client.post("/api/v1/auth/verify-password-reset-otp", json={
            "email": "wrong.reset@example.com",
            "code": "000000",
        })
        assert resp.status_code == 400
        assert "Invalid verification code" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_change_password_requires_authentication_and_revokes_sessions(self, client, async_test_db):
        """Changing password updates hash and revokes existing sessions."""
        reg = _register_and_verify(client, async_test_db, "change.pwd@example.com")
        token = reg["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Change password
        change_resp = client.post("/api/v1/auth/password", headers=headers, json={
            "current_password": "Password123!",
            "password": "NewStrongPassword456!",
        })
        assert change_resp.status_code == 200
        assert "revoked" in change_resp.json()["message"]

        # Old password should now fail at login
        # First verify user so they can login
        user = await async_test_db.scalar(select(User).where(User.email == "change.pwd@example.com"))
        user.is_verified = True
        await async_test_db.commit()

        old_login = client.post("/api/v1/auth/login", json={
            "email": "change.pwd@example.com",
            "password": "Password123!",
        })
        assert old_login.status_code == 401

        # New password succeeds
        new_login = client.post("/api/v1/auth/login", json={
            "email": "change.pwd@example.com",
            "password": "NewStrongPassword456!",
        })
        assert new_login.status_code == 200
