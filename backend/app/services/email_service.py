"""Email service for sending verification emails and notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from backend.app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        """Initialize email service with SMTP configuration from settings."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    def _get_smtp_connection(self):
        """Create and return authenticated SMTP connection."""
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
            raise ValueError(
                "SMTP configuration incomplete. Check SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in .env"
            )

        try:
            # Use SMTP_SSL if port is 465, otherwise use STARTTLS
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()

            server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise

    def send_verification_email(
        self, to_email: str, verification_token: str, user_name: Optional[str] = None
    ) -> bool:
        """
        Send email verification link to user.

        Args:
            to_email: Recipient email address
            verification_token: Unique verification token
            user_name: Optional user's name for personalization

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create verification link
            verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

            # Compose email
            subject = "Verify your AISMM account"
            greeting = f"Hi {user_name}," if user_name else "Hi,"

            html_body = f"""
            <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">AISMM</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">AI-Powered Social Media Management</p>
                </div>
                <div style="background: #ffffff; padding: 40px 30px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #1e293b; margin-top: 0;">Verify Your Email Address</h2>
                    <p style="color: #64748b; font-size: 16px;">{greeting}</p>
                    <p style="color: #64748b; font-size: 16px; margin: 20px 0;">
                        Thank you for creating an AISMM account! To get started with managing your social media presence,
                        please verify your email address by clicking the button below:
                    </p>
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{verification_link}"
                           style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
                                  color: white;
                                  padding: 14px 40px;
                                  text-decoration: none;
                                  border-radius: 8px;
                                  font-weight: 600;
                                  font-size: 16px;
                                  display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    <p style="color: #64748b; font-size: 14px; margin-top: 30px;">
                        Or copy and paste this link into your browser:
                    </p>
                    <p style="color: #7c3aed; font-size: 13px; word-break: break-all; background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        {verification_link}
                    </p>
                    <p style="color: #94a3b8; font-size: 13px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                        This verification link will expire in 30 minutes. If you didn't create an AISMM account, you can safely ignore this email.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 20px; padding: 20px; color: #94a3b8; font-size: 12px;">
                    <p style="margin: 5px 0;">© 2026 AISMM. All rights reserved.</p>
                    <p style="margin: 5px 0;">AI-Powered Social Media Management Platform</p>
                </div>
            </body>
            </html>
            """

            text_body = f"""
{greeting}

Thank you for creating an AISMM account!

To get started with managing your social media presence, please verify your email address by clicking the link below:

{verification_link}

This verification link will expire in 30 minutes.

If you didn't create an AISMM account, you can safely ignore this email.

---
AISMM - AI-Powered Social Media Management
© 2026 AISMM. All rights reserved.
            """

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with self._get_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"Verification email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {to_email}: {e}")
            return False

    def send_password_reset_email(
        self, to_email: str, reset_token: str, user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset link to user.

        Args:
            to_email: Recipient email address
            reset_token: Unique reset token
            user_name: Optional user's name for personalization

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create reset link
            reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

            # Compose email
            subject = "Reset your AISMM password"
            greeting = f"Hi {user_name}," if user_name else "Hi,"

            html_body = f"""
            <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">AISMM</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">AI-Powered Social Media Management</p>
                </div>
                <div style="background: #ffffff; padding: 40px 30px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #1e293b; margin-top: 0;">Password Reset Request</h2>
                    <p style="color: #64748b; font-size: 16px;">{greeting}</p>
                    <p style="color: #64748b; font-size: 16px; margin: 20px 0;">
                        We received a request to reset your AISMM account password. Click the button below to create a new password:
                    </p>
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{reset_link}"
                           style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
                                  color: white;
                                  padding: 14px 40px;
                                  text-decoration: none;
                                  border-radius: 8px;
                                  font-weight: 600;
                                  font-size: 16px;
                                  display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p style="color: #64748b; font-size: 14px; margin-top: 30px;">
                        Or copy and paste this link into your browser:
                    </p>
                    <p style="color: #7c3aed; font-size: 13px; word-break: break-all; background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0;">
                        {reset_link}
                    </p>
                    <p style="color: #94a3b8; font-size: 13px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                        This password reset link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 20px; padding: 20px; color: #94a3b8; font-size: 12px;">
                    <p style="margin: 5px 0;">© 2026 AISMM. All rights reserved.</p>
                    <p style="margin: 5px 0;">AI-Powered Social Media Management Platform</p>
                </div>
            </body>
            </html>
            """

            text_body = f"""
{greeting}

We received a request to reset your AISMM account password.

To create a new password, click the link below:

{reset_link}

This password reset link will expire in 1 hour.

If you didn't request a password reset, you can safely ignore this email.

---
AISMM - AI-Powered Social Media Management
© 2026 AISMM. All rights reserved.
            """

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with self._get_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"Password reset email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {e}")
            return False


# Singleton instance
email_service = EmailService()
