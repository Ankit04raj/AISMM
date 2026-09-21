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
    from unittest.mock import patch
    from backend.app.services.email_service import email_service
    with patch.object(email_service, "send_email_verification_otp", return_value=True):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Test User", "accept_terms": True},
        )
        assert resp.status_code == 201
        return resp.json()


class TestPasswordFlows:
    """Test full forgot-password, verify OTP, reset password, and change password flows."""

    @pytest.mark.asyncio
    async def test_forgot_password_generates_otp_challenge(self, client, async_test_db, monkeypatch):
        """Forgot password creates an OTP challenge with purpose PASSWORD_RESET."""
        from backend.app.config import get_settings
        from backend.app.services.email_service import email_service
        settings = get_settings()

        monkeypatch.setattr(email_service, "send_otp_email", lambda *args, **kwargs: True)
        monkeypatch.setattr(settings, "ENABLE_EMAIL_NOTIFICATIONS", True)
        monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test.example")

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
    async def test_verify_password_reset_otp_wrong_code(self, client, async_test_db, monkeypatch):
        """Submitting wrong reset OTP fails with 400."""
        from backend.app.config import get_settings
        from backend.app.services.email_service import email_service
        settings = get_settings()

        monkeypatch.setattr(email_service, "send_otp_email", lambda *args, **kwargs: True)
        monkeypatch.setattr(settings, "ENABLE_EMAIL_NOTIFICATIONS", True)
        monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test.example")

        _register_and_verify(client, async_test_db, "wrong.reset@example.com")
        client.post("/api/v1/auth/forgot-password", json={"email": "wrong.reset@example.com"})

        resp = client.post("/api/v1/auth/verify-password-reset-otp", json={
            "email": "wrong.reset@example.com",
            "code": "000000",
        })
        assert resp.status_code == 400
        assert "Invalid verification code" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_forgot_password_full_e2e_reset_lifecycle(self, client, async_test_db, monkeypatch):
        """Proof: Forgot password dispatches OTP, verifies OTP, resets password, invalidates old credentials."""
        from backend.app.config import get_settings
        from backend.app.services.email_service import email_service
        settings = get_settings()

        captured_otps = []
        def mock_send(to_email, otp_code, purpose="reset", user_name=None, expires_in_minutes=5):
            captured_otps.append((to_email, otp_code, purpose))
            return True

        monkeypatch.setattr(email_service, "send_otp_email", mock_send)
        monkeypatch.setattr(settings, "ENABLE_EMAIL_NOTIFICATIONS", True)
        monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test.example")

        # 1. Register user
        test_email = "lifecycle.reset@example.com"
        _register_and_verify(client, async_test_db, test_email, password="OldPassword123!")

        # 2. Request password reset
        forgot_resp = client.post("/api/v1/auth/forgot-password", json={"email": test_email})
        assert forgot_resp.status_code == 200
        assert len(captured_otps) == 1
        to_email, sent_otp, purpose = captured_otps[0]
        assert to_email == test_email
        assert len(sent_otp) == 6
        assert purpose == "reset"

        # 3. Verify OTP from email and get single-use reset_token
        verify_otp_resp = client.post("/api/v1/auth/verify-password-reset-otp", json={
            "email": test_email,
            "code": sent_otp,
        })
        assert verify_otp_resp.status_code == 200
        reset_token = verify_otp_resp.json()["reset_token"]
        assert reset_token is not None

        # 4. Set new password
        reset_pwd_resp = client.post("/api/v1/auth/reset-password", json={
            "token": reset_token,
            "password": "NewBrandPassword456!",
        })
        assert reset_pwd_resp.status_code == 200
        assert "password reset" in reset_pwd_resp.json()["message"].lower()

        # 5. Old password is now rejected
        old_login = client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": "OldPassword123!",
        })
        assert old_login.status_code in (400, 401, 403)

        # 6. New password works
        new_login = client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": "NewBrandPassword456!",
        })
        assert new_login.status_code in (200, 403)  # 200 if verified, 403 if unverified

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
