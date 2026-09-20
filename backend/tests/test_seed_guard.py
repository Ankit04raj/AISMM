"""Unit tests for demo seed environment guards and cleanup utilities."""

import os
import sys
import subprocess
import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from backend.app.config.settings import get_settings
from backend.app.db.models import User, SocialAccount
from test_auth_and_scoping import async_test_db, app_with_db, client


def test_seed_script_refuses_production_environment():
    """seed_live_demo.py must exit with code 1 if ENVIRONMENT != development."""
    env = os.environ.copy()
    env["ENVIRONMENT"] = "production"
    env["AISMM_ALLOW_DEMO_SEED"] = "1"
    env["DEBUG"] = "false"

    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts/seed_live_demo.py"))

    proc = subprocess.run(
        [sys.executable, script_path],
        env=env,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert "FATAL ERROR" in proc.stderr
    assert "ENVIRONMENT=development" in proc.stderr


def test_seed_script_refuses_staging_environment():
    """seed_live_demo.py must exit with code 1 if ENVIRONMENT=staging."""
    env = os.environ.copy()
    env["ENVIRONMENT"] = "staging"
    env["AISMM_ALLOW_DEMO_SEED"] = "1"
    env["DEBUG"] = "false"

    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts/seed_live_demo.py"))

    proc = subprocess.run(
        [sys.executable, script_path],
        env=env,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert "FATAL ERROR" in proc.stderr
    assert "ENVIRONMENT=development" in proc.stderr


@pytest.mark.asyncio
async def test_cleanup_demo_data_script_execution(async_test_db):
    """Test that cleanup script correctly identifies and purges demo seed users."""
    from scripts.cleanup_demo_data import execute_cleanup
    from sqlalchemy import select

    # Insert a demo user and a genuine customer user
    demo_user = User(
        id=uuid4(),
        email="demo@aismm.ai",
        hashed_password="hashed_pw_123",
        full_name="Demo User",
        is_active=True,
        is_verified=True,
    )
    demo_account = SocialAccount(
        id=uuid4(),
        user_id=demo_user.id,
        platform="x",
        platform_user_id="tw_demo",
        username="demo_handle",
        access_token="dev_access_token_x_12345",
        account_metadata={"connected_via": "direct_url_or_handle"},
    )
    real_user = User(
        id=uuid4(),
        email="genuine.customer@company.com",
        hashed_password="hashed_pw_456",
        full_name="Real Customer",
        is_active=True,
        is_verified=True,
    )
    async_test_db.add(demo_user)
    async_test_db.add(demo_account)
    async_test_db.add(real_user)
    await async_test_db.commit()

    # Verify both exist
    users_before = (await async_test_db.execute(select(User))).scalars().all()
    assert len(users_before) >= 2

    # 1. Execute dry-run cleanup -> modifies nothing
    dry_res = await execute_cleanup(async_test_db, dry_run=True)
    assert dry_res["deleted_users_count"] >= 1
    assert dry_res["dry_run"] is True

    # 2. Execute real purge
    res = await execute_cleanup(async_test_db, dry_run=False)
    assert res["deleted_users_count"] >= 1
    assert res["dry_run"] is False

    # Demo user should be deleted, real user preserved
    remaining_demo = await async_test_db.scalar(select(User).where(User.email == "demo@aismm.ai"))
    assert remaining_demo is None

    remaining_real = await async_test_db.scalar(select(User).where(User.email == "genuine.customer@company.com"))
    assert remaining_real is not None


@pytest.mark.asyncio
async def test_cleanup_removes_mock_account_on_non_demo_user(async_test_db):
    from scripts.cleanup_demo_data import execute_cleanup
    from sqlalchemy import select

    real_user = User(
        id=uuid4(),
        email="real@company.com",
        hashed_password="pw",
        full_name="Real User",
        is_active=True,
        is_verified=True,
    )
    mock_acc = SocialAccount(
        id=uuid4(),
        user_id=real_user.id,
        platform="x",
        platform_user_id="tw_real",
        username="real_handle",
        access_token="dev_access_token_x_real",
        account_metadata={"connected_via": "direct_url_or_handle"},
    )
    async_test_db.add(real_user)
    async_test_db.add(mock_acc)
    await async_test_db.commit()

    res = await execute_cleanup(async_test_db, dry_run=False)
    assert res["deleted_mock_accounts_count"] >= 1

    acc_rem = await async_test_db.scalar(select(SocialAccount).where(SocialAccount.username == "real_handle"))
    assert acc_rem is None


SEED_ENV_BASE = {"ENVIRONMENT": "development", "DEBUG": "false"}


def _run_seed(env_overrides, extra_args=None):
    env = os.environ.copy()
    for key in ("AISMM_ALLOW_DEMO_SEED", "AISMM_REAL_OAUTH_TESTING", "AISMM_DEMO_DATABASE_URL",
                "X_CLIENT_ID", "FACEBOOK_CLIENT_ID", "INSTAGRAM_CLIENT_ID",
                "LINKEDIN_CLIENT_ID", "YOUTUBE_CLIENT_ID"):
        env.pop(key, None)
    env.update(env_overrides)
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts/seed_live_demo.py"))
    return subprocess.run(
        [sys.executable, script_path, *(extra_args or [])],
        env=env,
        capture_output=True,
        text=True,
    )


def test_seed_requires_explicit_demo_opt_in():
    """Without AISMM_ALLOW_DEMO_SEED the script must refuse even in development."""
    proc = _run_seed({"ENVIRONMENT": "development"})
    assert proc.returncode == 1
    assert "FATAL ERROR" in proc.stderr
    assert "AISMM_ALLOW_DEMO_SEED" in proc.stderr


def test_seed_refuses_when_real_oauth_testing_flag_set():
    proc = _run_seed({
        "ENVIRONMENT": "development",
        "AISMM_ALLOW_DEMO_SEED": "1",
        "AISMM_REAL_OAUTH_TESTING": "1",
        "AISMM_DEMO_DATABASE_URL": "sqlite+aiosqlite:///./demo_seed.db",
        "DATABASE_URL": "sqlite+aiosqlite:///./demo_seed.db",
    })
    assert proc.returncode == 1
    assert "real OAuth context detected" in proc.stderr


def test_seed_refuses_when_provider_credentials_configured():
    proc = _run_seed({
        "ENVIRONMENT": "development",
        "AISMM_ALLOW_DEMO_SEED": "1",
        "AISMM_DEMO_DATABASE_URL": "sqlite+aiosqlite:///./demo_seed.db",
        "DATABASE_URL": "sqlite+aiosqlite:///./demo_seed.db",
        "X_CLIENT_ID": "real-x-client-id",
    })
    assert proc.returncode == 1
    assert "real OAuth context detected" in proc.stderr
    assert "x" in proc.stderr


def test_seed_requires_dedicated_demo_database():
    proc = _run_seed({
        "ENVIRONMENT": "development",
        "AISMM_ALLOW_DEMO_SEED": "1",
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/aismm",
    })
    assert proc.returncode == 1
    assert "AISMM_DEMO_DATABASE_URL" in proc.stderr


def test_seed_refuses_production_even_with_demo_flags():
    proc = _run_seed({
        "ENVIRONMENT": "production",
        "AISMM_ALLOW_DEMO_SEED": "1",
        "AISMM_DEMO_DATABASE_URL": "sqlite+aiosqlite:///./demo_seed.db",
    })
    assert proc.returncode == 1
    assert "FATAL ERROR" in proc.stderr


def test_purge_path_is_blocked_without_opt_in():
    proc = _run_seed({"ENVIRONMENT": "development"}, extra_args=["--purge"])
    assert proc.returncode == 1
    assert "FATAL ERROR" in proc.stderr
    assert "AISMM_ALLOW_DEMO_SEED" in proc.stderr
