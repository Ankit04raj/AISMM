"""Pytest fixtures and environment initialization for AISMM test suite."""

import os
from uuid import UUID
from datetime import datetime, timezone
import pytest

# Ensure standard test secrets exist in environment for unit tests
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-development-and-unit-tests-32char")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-development-and-unit-tests")
os.environ.setdefault("WEBHOOK_SECRET", "webhook-secret-change-in-production")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/aismm_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")

from backend.app.main import app
from backend.app.api.deps import get_current_user
from backend.app.db.models import User

# Default test user for unit test suites
_test_user = User(
    id=UUID("00000000-0000-0000-0000-000000000001"),
    email="testuser@aismm.io",
    full_name="Default Test User",
    is_active=True,
    is_verified=True,
    is_superuser=False,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)


async def _mock_get_current_user():
    return _test_user


@pytest.fixture(autouse=True)
def setup_default_auth_override():
    """By default, override get_current_user on the shared app for unit test suites."""
    app.dependency_overrides[get_current_user] = _mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)
