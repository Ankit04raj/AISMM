#!/usr/bin/env python3
"""Standalone Pre-Go-Live Database Cleanup & Demo Account Purge Script.

Usage:
    python scripts/cleanup_demo_data.py [--dry-run]

Safely scans and removes placeholder demo accounts, mock social accounts,
and test publications created during local development, ensuring production
databases contain exclusively genuine, verified, user-owned records.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, or_

from backend.app.config.settings import get_settings
from backend.app.db.models import User, SocialAccount, Post, Comment


async def execute_cleanup(db: AsyncSession, dry_run: bool = False) -> dict:
    """Core purge routine to delete demo accounts and mock social profiles."""
    demo_identifiers = [
        "rishideoraj4@gmail.com",
        "demo@aismm.ai",
        "ankit.freelance04@gmail.com",
    ]

    # 1. Audit Demo Users
    res_users = await db.execute(select(User).where(User.email.in_(demo_identifiers)))
    demo_users = res_users.scalars().all()
    deleted_users_count = len(demo_users)
    for u in demo_users:
        if not dry_run:
            await db.delete(u)

    # 2. Audit Mock / Direct Social Accounts
    res_accs = await db.execute(select(SocialAccount))
    all_accs = res_accs.scalars().all()
    mock_accs = [
        acc for acc in all_accs
        if (acc.account_metadata or {}).get("connected_via") == "direct_url_or_handle"
        or (acc.access_token and "dev_access_token" in acc.access_token)
    ]
    deleted_accs_count = len(mock_accs)
    for a in mock_accs:
        if not dry_run and a not in [u.social_accounts for u in demo_users if u.social_accounts]:
            await db.delete(a)

    if not dry_run:
        await db.commit()

    return {
        "deleted_users_count": deleted_users_count,
        "deleted_mock_accounts_count": deleted_accs_count,
        "dry_run": dry_run,
    }


async def cleanup():
    settings = get_settings()
    dry_run = "--dry-run" in sys.argv

    print("================================================================")
    print(f"AISMM PRE-GO-LIVE DATABASE AUDIT & PURGE ({settings.ENVIRONMENT.upper()} mode)")
    print(f"Dry Run: {dry_run}")
    print("================================================================")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        res = await execute_cleanup(db, dry_run=dry_run)
        print(f"Deleted demo users: {res['deleted_users_count']}")
        print(f"Deleted mock social accounts: {res['deleted_mock_accounts_count']}")
        if not dry_run:
            print("\n✅ Pre-go-live database purge successfully committed.")
        else:
            print("\n[DRY RUN COMPLETE] No records were modified.")
        print("================================================================")


if __name__ == "__main__":
    asyncio.run(cleanup())
