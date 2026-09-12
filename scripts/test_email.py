#!/usr/bin/env python3
"""Standalone CLI script to test SMTP connection and OTP email delivery.

Usage:
    python scripts/test_email.py --to user@example.com
    python scripts/test_email.py --verify-only
"""

import sys
import os
import argparse

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.email_service import email_service
from backend.app.config.settings import settings


def main():
    parser = argparse.ArgumentParser(description="Test AISMM SMTP connectivity and OTP email delivery.")
    parser.add_argument("--to", type=str, help="Recipient email address to send test OTP email")
    parser.add_argument("--purpose", type=str, default="signup", choices=["signup", "login", "reset"], help="OTP purpose template to test")
    parser.add_argument("--verify-only", action="store_true", help="Only verify SMTP credentials without sending an email")
    args = parser.parse_args()

    print("\n========================================================")
    print(" 📧 AISMM SMTP & Transactional Email Diagnostic Tool")
    print("========================================================")
    print(f"Host:       {settings.SMTP_HOST or '[NOT SET]'}")
    print(f"Port:       {settings.SMTP_PORT} ({'SSL' if settings.SMTP_PORT == 465 else 'STARTTLS'})")
    print(f"User:       {settings.SMTP_USER or '[NOT SET]'}")
    print(f"Sender:     {settings.FROM_NAME} <{settings.FROM_EMAIL}>")
    print(f"Enabled:    {settings.ENABLE_EMAIL_NOTIFICATIONS}")
    print("--------------------------------------------------------")

    print("\n🔍 Testing SMTP Transport Connection...")
    diag = email_service.verify_connection()

    if not diag.get("success"):
        print(f"\n❌ SMTP Connection Failed!")
        print(f"Error: {diag.get('error')}")
        print("\n🔧 Common Fixes:")
        print(" 1. Gmail SMTP: Ensure you use a 16-character 'App Password' (not normal account password).")
        print(" 2. Port: Use 465 for SSL or 587 for TLS/STARTTLS.")
        print(" 3. Transactional providers (Resend/SendGrid): Ensure FROM_EMAIL is verified on your domain.")
        sys.exit(1)

    print(f"✅ {diag.get('message')} [Mode: {diag.get('mode')}]")

    if args.verify_only:
        print("\nVerification complete. Exiting (--verify-only specified).")
        sys.exit(0)

    if not args.to:
        print("\n💡 To send a test OTP email, supply a recipient with --to your_email@example.com")
        sys.exit(0)

    test_otp = "849201"
    print(f"\n📨 Sending sample {args.purpose.upper()} OTP ({test_otp}) to {args.to}...")
    success = email_service.send_otp_email(
        to_email=args.to,
        otp_code=test_otp,
        purpose=args.purpose,
        user_name="AISMM Tester",
        expires_in_minutes=10,
    )

    if success:
        print(f"✅ OTP email successfully dispatched to {args.to}!")
        print("Check your Inbox / Spam folder.")
    else:
        print(f"❌ Failed to deliver OTP email to {args.to}. Check backend application logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
