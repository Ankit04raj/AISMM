"""Email service for sending verification emails, OTP codes, and security notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import logging

try:
    from backend.app.config.settings import settings, get_settings
except Exception:
    settings = None
    get_settings = None

logger = logging.getLogger(__name__)


_UNSET = object()


class EmailService:
    """Service for sending transactional emails and OTP codes via SMTP."""

    def __init__(
        self,
        smtp_host: Any = _UNSET,
        smtp_port: Any = _UNSET,
        smtp_user: Any = _UNSET,
        smtp_password: Any = _UNSET,
        from_email: Any = _UNSET,
        from_name: Any = _UNSET,
    ):
        """Initialize email service with SMTP configuration from settings or explicit parameters."""
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._from_email = from_email
        self._from_name = from_name

    @property
    def _settings(self):
        """Fetch current settings dynamically."""
        if get_settings:
            try:
                return get_settings()
            except Exception:
                pass
        return settings

    @property
    def smtp_host(self) -> Optional[str]:
        if self._smtp_host is not _UNSET:
            return self._smtp_host
        s = self._settings
        return getattr(s, "SMTP_HOST", None) if s else None

    @smtp_host.setter
    def smtp_host(self, value: Optional[str]):
        self._smtp_host = value

    @property
    def smtp_port(self) -> int:
        if self._smtp_port is not _UNSET:
            try:
                return int(self._smtp_port)
            except (ValueError, TypeError):
                return 587
        s = self._settings
        port = getattr(s, "SMTP_PORT", 587) if s else 587
        try:
            return int(port) if port is not None else 587
        except (ValueError, TypeError):
            return 587

    @smtp_port.setter
    def smtp_port(self, value: Optional[int]):
        self._smtp_port = value

    @property
    def smtp_user(self) -> Optional[str]:
        if self._smtp_user is not _UNSET:
            return self._smtp_user
        s = self._settings
        if not s:
            return None
        return getattr(s, "SMTP_USER", None) or getattr(s, "SMTP_USERNAME", None)

    @smtp_user.setter
    def smtp_user(self, value: Optional[str]):
        self._smtp_user = value

    @property
    def smtp_password(self) -> Optional[str]:
        if self._smtp_password is not _UNSET:
            return self._smtp_password
        s = self._settings
        return getattr(s, "SMTP_PASSWORD", None) if s else None

    @smtp_password.setter
    def smtp_password(self, value: Optional[str]):
        self._smtp_password = value

    @property
    def from_email(self) -> str:
        if self._from_email is not _UNSET and self._from_email is not None:
            return self._from_email
        s = self._settings
        if not s:
            return "noreply@aismm.app"
        return getattr(s, "FROM_EMAIL", None) or getattr(s, "SMTP_FROM_EMAIL", None) or "noreply@aismm.app"

    @from_email.setter
    def from_email(self, value: Optional[str]):
        self._from_email = value

    @property
    def from_name(self) -> str:
        if self._from_name is not _UNSET and self._from_name is not None:
            return self._from_name
        s = self._settings
        if not s:
            return "AISMM"
        return getattr(s, "FROM_NAME", None) or getattr(s, "SMTP_FROM_NAME", None) or "AISMM"

    @from_name.setter
    def from_name(self, value: Optional[str]):
        self._from_name = value

    @property
    def frontend_url(self) -> str:
        s = self._settings
        return getattr(s, "FRONTEND_URL", "http://localhost:3000") if s else "http://localhost:3000"

    def verify_connection(self) -> Dict[str, Any]:
        """Verify SMTP connectivity and credentials. Returns diagnostic dict without leaking secrets."""
        host = self.smtp_host
        port = self.smtp_port
        user = self.smtp_user
        password = self.smtp_password

        if not all([host, port, user, password]):
            missing = []
            if not host:
                missing.append("SMTP_HOST")
            if not port:
                missing.append("SMTP_PORT")
            if not user:
                missing.append("SMTP_USER / SMTP_USERNAME")
            if not password:
                missing.append("SMTP_PASSWORD")
            return {
                "success": False,
                "error": f"Incomplete SMTP configuration. Missing: {', '.join(missing)} in .env",
                "host": host,
                "port": port,
            }

        try:
            with self._get_smtp_connection() as server:
                server.noop()
            return {
                "success": True,
                "message": "SMTP Connection Successful! Ready to send emails.",
                "host": host,
                "port": port,
                "mode": "SSL (Port 465)" if port == 465 else "STARTTLS (Port 587/25)",
            }
        except Exception as e:
            logger.error(f"SMTP verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "host": host,
                "port": port,
            }

    def _get_smtp_connection(self):
        """Create and return authenticated SMTP connection."""
        host = self.smtp_host
        port = self.smtp_port
        user = self.smtp_user
        password = self.smtp_password

        if not all([host, port, user, password]):
            raise ValueError(
                "SMTP configuration incomplete. Check SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in .env"
            )

        try:
            # Use SMTP_SSL if port is 465, otherwise use STARTTLS
            if port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            else:
                server = smtplib.SMTP(host, port, timeout=10)
                server.ehlo()
                if server.has_extn("STARTTLS"):
                    server.starttls()
                    server.ehlo()

            server.login(user, password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server ({host}:{port}): {e}")
            raise

    def send_otp_email(
        self,
        to_email: str,
        otp_code: str,
        purpose: str = "signup",
        user_name: Optional[str] = None,
        expires_in_minutes: int = 10,
    ) -> bool:
        """
        Send a high-visibility 6-digit numeric OTP email for signup, login 2FA, or password reset.

        Args:
            to_email: Recipient email address
            otp_code: 6-digit verification code
            purpose: One of 'signup', 'login', 'reset'
            user_name: Optional user's name
            expires_in_minutes: TTL in minutes (default 10)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            greeting = f"Hi {user_name}," if user_name else "Hi,"

            if purpose == "signup":
                subject = f"Your AISMM Verification Code: {otp_code} (Expires in {expires_in_minutes} minutes)"
                title = "Verify Your Account"
                intro = "Thank you for signing up for AISMM. Please use the 6-digit verification code below to confirm your account:"
            elif purpose == "login":
                subject = f"Your AISMM Login Code: {otp_code}"
                title = "Sign-In Verification"
                intro = "A sign-in attempt requires two-factor verification. Enter the code below to complete your login:"
            elif purpose == "reset":
                subject = f"Your Password Reset OTP: {otp_code}"
                title = "Reset Your Password"
                intro = "We received a request to reset your AISMM account password. Use the verification code below to proceed:"
            else:
                subject = f"Your AISMM Security Code: {otp_code}"
                title = "Security Verification"
                intro = "Please use the verification code below to authorize this action:"

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #07090e; margin: 0; padding: 24px;">
                <div style="max-width: 540px; margin: 0 auto; background: #0d121f; border: 1px solid #1e293b; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
                    <div style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%); padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;">AISMM</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 6px 0 0 0; font-size: 13px; font-weight: 500;">AI-Powered Social Media Management</p>
                    </div>
                    <div style="padding: 36px 30px; background: #0d121f; color: #cbd5e1;">
                        <h2 style="color: #ffffff; margin-top: 0; font-size: 20px; font-weight: 700;">{title}</h2>
                        <p style="color: #94a3b8; font-size: 15px; margin-bottom: 20px;">{greeting}</p>
                        <p style="color: #94a3b8; font-size: 15px; margin-bottom: 28px;">{intro}</p>

                        <div style="background: #07090e; border: 1px solid #334155; border-radius: 14px; padding: 22px; text-align: center; margin: 28px 0;">
                            <span style="font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #38bdf8; text-shadow: 0 0 12px rgba(56,189,248,0.4);">{otp_code}</span>
                            <p style="color: #64748b; font-size: 12px; margin: 8px 0 0 0; text-transform: uppercase; letter-spacing: 1px;">Single-Use Security Code</p>
                        </div>

                        <p style="color: #64748b; font-size: 13px; margin-top: 24px; padding-top: 20px; border-top: 1px solid #1e293b;">
                            This code will expire in <strong>{expires_in_minutes} minutes</strong>. If you did not request this code, please ignore this email or update your password.
                        </p>
                    </div>
                    <div style="background: #07090e; padding: 18px; text-align: center; border-top: 1px solid #1e293b; color: #64748b; font-size: 11px;">
                        <p style="margin: 0;">© 2026 AISMM. Protected by AISMM Security Engine.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_body = f"""
{greeting}

{intro}

----------------------------------------
YOUR VERIFICATION CODE: {otp_code}
----------------------------------------

This code will expire in {expires_in_minutes} minutes.

If you did not request this code, please safely ignore this email.

---
AISMM - AI-Powered Social Media Management
© 2026 AISMM. All rights reserved.
            """

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)

            with self._get_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"OTP ({purpose}) email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send OTP email to {to_email}: {e}")
            return False

    def send_email_verification_otp(
        self, to_email: str, otp_code: str, user_name: Optional[str] = None
    ) -> bool:
        """Send a 6-digit OTP for email verification."""
        try:
            greeting = f"Hi {user_name}," if user_name else "Hi,"
            subject = "Verify your AISMM account"
            intro = "Thank you for creating an AISMM account. Use the 6-digit verification code below to confirm your email address:"

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #07090e; margin: 0; padding: 24px;">
                <div style="max-width: 540px; margin: 0 auto; background: #0d121f; border: 1px solid #1e293b; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
                    <div style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%); padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;">AISMM</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 6px 0 0 0; font-size: 13px; font-weight: 500;">AI-Powered Social Media Management</p>
                    </div>
                    <div style="padding: 36px 30px; background: #0d121f; color: #cbd5e1;">
                        <h2 style="color: #ffffff; margin-top: 0; font-size: 20px; font-weight: 700;">Verify Your Email Address</h2>
                        <p style="color: #94a3b8; font-size: 15px; margin-bottom: 20px;">{greeting}</p>
                        <p style="color: #94a3b8; font-size: 15px; margin-bottom: 28px;">{intro}</p>
                        <div style="background: #07090e; border: 1px solid #334155; border-radius: 14px; padding: 22px; text-align: center; margin: 28px 0;">
                            <span style="font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #38bdf8; text-shadow: 0 0 12px rgba(56,189,248,0.4);">{otp_code}</span>
                            <p style="color: #64748b; font-size: 12px; margin: 8px 0 0 0; text-transform: uppercase; letter-spacing: 1px;">Verification Code</p>
                        </div>
                        <p style="color: #64748b; font-size: 13px; margin-top: 24px; padding-top: 20px; border-top: 1px solid #1e293b;">
                            This code expires in 5 minutes. If you did not create an AISMM account, ignore this email.
                        </p>
                    </div>
                    <div style="background: #07090e; padding: 18px; text-align: center; border-top: 1px solid #1e293b; color: #64748b; font-size: 11px;">
                        <p style="margin: 0;">© 2026 AISMM. Protected by AISMM Security Engine.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_body = f"""
{greeting}

{intro}

----------------------------------------
YOUR VERIFICATION CODE: {otp_code}
----------------------------------------

This code expires in 5 minutes.

If you did not create an AISMM account, ignore this email.

---
AISMM - AI-Powered Social Media Management
© 2026 AISMM. All rights reserved.
            """

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)

            with self._get_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"Email verification OTP sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email verification OTP to {to_email}: {e}")
            return False

    def send_verification_email(
        self, to_email: str, verification_token: str, user_name: Optional[str] = None
    ) -> bool:
        """Send email verification link and OTP token to user."""
        try:
            # Create verification link
            verification_link = f"{self.frontend_url}/verify-email?token={verification_token}"
            greeting = f"Hi {user_name}," if user_name else "Hi,"
            subject = "Verify your AISMM account"

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #cbd5e1; background-color: #07090e; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #0d121f; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden;">
                    <div style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 800;">AISMM</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 6px 0 0 0; font-size: 14px;">AI-Powered Social Media Management</p>
                    </div>
                    <div style="padding: 36px 30px; background: #0d121f;">
                        <h2 style="color: #ffffff; margin-top: 0; font-size: 20px;">Verify Your Email Address</h2>
                        <p style="color: #94a3b8; font-size: 15px;">{greeting}</p>
                        <p style="color: #94a3b8; font-size: 15px; margin: 20px 0;">
                            Thank you for creating an AISMM account! Click the button below to verify your email address and activate your workspace:
                        </p>
                        <div style="text-align: center; margin: 32px 0;">
                            <a href="{verification_link}"
                               style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
                                      color: white;
                                      padding: 14px 36px;
                                      text-decoration: none;
                                      border-radius: 10px;
                                      font-weight: 700;
                                      font-size: 15px;
                                      display: inline-block;">
                                Verify Email Address
                            </a>
                        </div>
                        <p style="color: #64748b; font-size: 13px; margin-top: 24px;">
                            Or copy and paste this link into your browser:
                        </p>
                        <p style="color: #38bdf8; font-size: 12px; word-break: break-all; background: #07090e; padding: 12px; border-radius: 8px; border: 1px solid #1e293b; font-family: monospace;">
                            {verification_link}
                        </p>
                        <p style="color: #64748b; font-size: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid #1e293b;">
                            This verification link will expire in 30 minutes. If you didn't create an AISMM account, you can safely ignore this email.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_body = f"""
{greeting}

Thank you for creating an AISMM account!

To get started, please verify your email address by visiting the link below:

{verification_link}

This verification link will expire in 30 minutes.

If you didn't create an AISMM account, you can safely ignore this email.

---
AISMM - AI-Powered Social Media Management
© 2026 AISMM. All rights reserved.
            """

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)

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
        """Send password reset link and token to user."""
        try:
            reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
            greeting = f"Hi {user_name}," if user_name else "Hi,"
            subject = "Reset your AISMM password"

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #cbd5e1; background-color: #07090e; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #0d121f; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden;">
                    <div style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 800;">AISMM</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 6px 0 0 0; font-size: 14px;">AI-Powered Social Media Management</p>
                    </div>
                    <div style="padding: 36px 30px; background: #0d121f;">
                        <h2 style="color: #ffffff; margin-top: 0; font-size: 20px;">Password Reset Request</h2>
                        <p style="color: #94a3b8; font-size: 15px;">{greeting}</p>
                        <p style="color: #94a3b8; font-size: 15px; margin: 20px 0;">
                            We received a request to reset your AISMM account password. Click the button below to create a new password:
                        </p>
                        <div style="text-align: center; margin: 32px 0;">
                            <a href="{reset_link}"
                               style="background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
                                      color: white;
                                      padding: 14px 36px;
                                      text-decoration: none;
                                      border-radius: 10px;
                                      font-weight: 700;
                                      font-size: 15px;
                                      display: inline-block;">
                                Reset Password
                            </a>
                        </div>
                        <p style="color: #64748b; font-size: 13px; margin-top: 24px;">
                            Or copy and paste this link into your browser:
                        </p>
                        <p style="color: #38bdf8; font-size: 12px; word-break: break-all; background: #07090e; padding: 12px; border-radius: 8px; border: 1px solid #1e293b; font-family: monospace;">
                            {reset_link}
                        </p>
                        <p style="color: #64748b; font-size: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid #1e293b;">
                            This password reset link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
                        </p>
                    </div>
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

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)

            with self._get_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"Password reset email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {e}")
            return False


# Singleton instance
email_service = EmailService()



# Singleton instance
email_service = EmailService()
