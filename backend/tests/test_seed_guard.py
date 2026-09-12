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
    """seed_live_demo.py must exit with code 1 and print fatal error if ENVIRONMENT != development."""
    env = os.environ.copy()
    env["ENVIRONMENT"] = "production"
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
    assert "Refusing to execute demo seed script in 'production' environment" in proc.stderr


def test_seed_script_refuses_staging_environment():
    """seed_live_demo.py must exit with code 1 if ENVIRONMENT=staging."""
    env = os.environ.copy()
    env["ENVIRONMENT"] = "staging"
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
