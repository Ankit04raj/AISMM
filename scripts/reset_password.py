#!/usr/bin/env python3
"""Secure Password Reset CLI Utility for AISMM.

Allows workspace administrators and developers to securely reset any user's
password directly in the database and revoke all active sessions.

Usage:
    python scripts/reset_password.py ankit.freelance04@gmail.com
    python scripts/reset_password.py ankit.freelance04@gmail.com "NewSecurePassword123!"
"""

import sys
import os
import argparse
import getpass
from datetime import datetime, timezone
import asyncio

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, update
from backend.app.db.session import get_db_context, init_db
from backend.app.db.models import User, AuthSession, OtpChallenge
from backend.app.core.security import get_password_hash


async def reset_user_password(email: str, new_password: str) -> bool:
    """Reset a user's password directly in the database."""
    if not new_password or len(new_password) < 8:
        print("❌ Error: Password must be at least 8 characters long.")
        return False

    if len(new_password.encode("utf-8")) > 72:
        print("❌ Error: Password must be at most 72 UTF-8 bytes (bcrypt limit).")
        return False

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

        # Update password hash
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_hash = None
        user.password_reset_expiry = None
        user.updated_at = now_utc

        # Invalidate all active password reset challenges
        await db.execute(
            update(OtpChallenge)
            .where(
                OtpChallenge.email == normalized_email,
                OtpChallenge.purpose == "PASSWORD_RESET",
                OtpChallenge.used_at.is_(None),
            )
            .values(used_at=now_utc)
        )

        # Revoke all active login sessions to force re-authentication
        await db.execute(
            update(AuthSession)
            .where(
                AuthSession.user_id == user.id,
                AuthSession.revoked.is_(False),
            )
            .values(revoked=True)
        )

        await db.commit()
        await db.refresh(user)

        print(f"\n========================================================")
        print(f" 🔐 Password Reset Successfully!")
        print(f"========================================================")
        print(f" • User ID:       {user.id}")
        print(f" • Email:         {user.email}")
        print(f" • Full Name:     {user.full_name or '[Not set]'}")
        print(f" • Sessions:      All active sessions revoked")
        print(f" • Updated At:    {user.updated_at} UTC")
        print(f"--------------------------------------------------------")
        print(f" 🚀 You can now log in immediately with your new password!")
        print(f"========================================================\n")
        return True


def main():
    parser = argparse.ArgumentParser(description="AISMM Password Reset CLI Utility")
    parser.add_argument("email", nargs="?", help="Email address of the user to reset")
    parser.add_argument("password", nargs="?", help="Optional new password (prompted securely if omitted)")
    args = parser.parse_args()

    email = args.email
    if not email:
        email = input("Enter user email: ").strip()

    if not email:
        print("❌ Email is required.")
        sys.exit(1)

    password = args.password
    if not password:
        password = getpass.getpass("Enter new password (min 8 chars): ")
        confirm = getpass.getpass("Confirm new password: ")
        if password != confirm:
            print("❌ Passwords do not match.")
            sys.exit(1)

    success = asyncio.run(reset_user_password(email, password))
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
