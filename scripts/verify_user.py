#!/usr/bin/env python3
"""Secure User Activation & Verification CLI Utility for AISMM.

Allows workspace administrators and local developers to securely activate
and verify user accounts directly in the database without requiring SMTP.

Usage:
    python scripts/verify_user.py ankit.freelance04@gmail.com
    python scripts/verify_user.py --all
"""

import sys
import os
import argparse
from datetime import datetime, timezone
import asyncio

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, update
from backend.app.db.session import get_db_context, init_db
from backend.app.db.models import User, OtpChallenge


async def verify_user(email: str) -> bool:
    """Activate and verify a user by email."""
    init_db()
    async with get_db_context() as db:
        normalized_email = email.strip().lower()
        stmt = select(User).where(User.email == normalized_email)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user:
            print(f"❌ User not found with email: {normalized_email}")
            return False

        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

        # Update User verification fields
        user.is_verified = True
        user.is_active = True
        user.email_verified_at = now_utc
        user.email_verification_token = None
        user.email_verification_expiry = None

        # Mark all pending OtpChallenges for this email as used
        await db.execute(
            update(OtpChallenge)
            .where(
                OtpChallenge.email == normalized_email,
                OtpChallenge.used_at.is_(None),
            )
            .values(used_at=now_utc)
        )

        await db.commit()
        await db.refresh(user)

        print(f"\n========================================================")
        print(f" ✅ AISMM Account Activated & Verified Successfully!")
        print(f"========================================================")
        print(f" • User ID:       {user.id}")
        print(f" • Email:         {user.email}")
        print(f" • Full Name:     {user.full_name or '[Not set]'}")
        print(f" • Is Active:     {user.is_active}")
        print(f" • Is Verified:   {user.is_verified}")
        print(f" • Verified At:   {user.email_verified_at} UTC")
        print(f"--------------------------------------------------------")
        print(f" 🚀 You can now refresh/sign in to AISMM Studio directly!")
        print(f"========================================================\n")
        return True


async def verify_all_users() -> int:
    """Verify all unverified users in the database."""
    init_db()
    async with get_db_context() as db:
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = select(User).where(User.is_verified.is_(False))
        res = await db.execute(stmt)
        unverified_users = res.scalars().all()

        if not unverified_users:
            print("ℹ️ All users in the database are already verified.")
            return 0

        count = 0
        for user in unverified_users:
            user.is_verified = True
            user.is_active = True
            user.email_verified_at = now_utc
            user.email_verification_token = None
            user.email_verification_expiry = None
            count += 1
            print(f"✅ Verified: {user.email} (ID: {user.id})")

        # Mark all pending OtpChallenges as used
        await db.execute(
            update(OtpChallenge)
            .where(OtpChallenge.used_at.is_(None))
            .values(used_at=now_utc)
        )

        await db.commit()
        print(f"\n🎉 Total verified accounts: {count}")
        return count


def main():
    parser = argparse.ArgumentParser(description="AISMM User Verification Utility")
    parser.add_argument("email", nargs="?", help="Email address of the user to verify")
    parser.add_argument("--all", action="store_true", help="Verify all unverified users")
    args = parser.parse_args()

    if args.all:
        asyncio.run(verify_all_users())
    elif args.email:
        asyncio.run(verify_user(args.email))
    else:
        # Default to ankit.freelance04@gmail.com if no arg provided
        asyncio.run(verify_user("ankit.freelance04@gmail.com"))


if __name__ == "__main__":
    main()
