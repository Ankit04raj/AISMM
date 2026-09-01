"""Tests for core security, error hierarchy, and logging foundation."""

import pytest
from datetime import timedelta
from uuid import uuid4

from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    generate_api_key,
    verify_api_key,
)
from backend.app.core.errors import (
    AISMMError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    PlatformError,
    RateLimitError,
    TokenExpiredError,
    UnsupportedCapabilityError,
)
from backend.app.logging import setup_logging, get_logger, JSONFormatter


class TestSecurityFoundation:
    """Test security utilities."""

    def test_password_hashing_and_verification(self):
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_access_token_creation_and_verification(self):
        user_id = str(uuid4())
        token = create_access_token(subject=user_id, extra_claims={"role": "admin"})
        assert isinstance(token, str)

        verified_sub = verify_token(token, expected_type="access")
        assert verified_sub == user_id

        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_refresh_token_creation_and_type_check(self):
        user_id = str(uuid4())
        refresh_token = create_refresh_token(subject=user_id)
        verified_sub = verify_token(refresh_token, expected_type="refresh")
        assert verified_sub == user_id

        # Access token verification should reject a refresh token
        with pytest.raises(AuthenticationError, match="Expected access token, got refresh"):
            verify_token(refresh_token, expected_type="access")

    def test_expired_token_handling(self):
        user_id = str(uuid4())
        expired_token = create_access_token(
            subject=user_id, expires_delta=timedelta(seconds=-10)
        )
        with pytest.raises(TokenExpiredError):
            decode_token(expired_token)

    def test_api_key_generation_and_verification(self):
        raw_key, prefix, key_hash = generate_api_key()
        assert len(prefix) == 8
        assert raw_key.startswith(prefix)
        assert verify_api_key(raw_key, key_hash) is True
        assert verify_api_key("wrong-key", key_hash) is False


class TestErrorHierarchy:
    """Test AISMM error classes."""

    def test_aismm_base_error(self):
        err = AISMMError(message="Something failed", error_code="CUSTOM_ERR", status_code=500)
        assert str(err) == "Something failed"
        assert err.status_code == 500

    def test_not_found_error(self):
        err = NotFoundError(resource="Post 123", platform="instagram")
        assert err.status_code == 404
        assert err.error_code == "NOT_FOUND"
        assert err.platform == "instagram"

    def test_platform_error_str(self):
        err = PlatformError(message="Rate limit reached", platform="instagram", status_code=429)
        assert "[instagram] Rate limit reached" in str(err)
        assert err.status_code == 429

    def test_unsupported_capability_error(self):
        err = UnsupportedCapabilityError(capability="post_story", platform="twitter")
        assert err.status_code == 400
        assert err.capability == "post_story"


class TestLoggingFoundation:
    """Test structured logging."""

    def test_get_logger_and_setup(self):
        setup_logging()
        logger = get_logger("aismm.test")
        assert logger.name == "aismm.test"

    def test_json_formatter_structure(self):
        import logging

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Hello %s",
            args=("world",),
            exc_info=None,
        )
        output = formatter.format(record)
        assert '"message": "Hello world"' in output
        assert '"level": "INFO"' in output
