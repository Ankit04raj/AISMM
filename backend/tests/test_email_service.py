"""Unit and integration tests for EmailService subsystem."""

import unittest
from unittest.mock import MagicMock, patch
import pytest

from backend.app.services.email_service import EmailService


class TestEmailService(unittest.TestCase):
    """Test suite for EmailService verifying delivery, formatting, TLS/SSL, and security."""

    def setUp(self):
        """Set up test instances with known configurations."""
        self.service = EmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="test_user@example.com",
            smtp_password="super_secret_password_123",
            from_email="noreply@aismm.app",
            from_name="AISMM",
        )

    def test_verify_connection_missing_credentials(self):
        """verify_connection must report failure and missing keys when config is incomplete."""
        incomplete_service = EmailService(
            smtp_host=None,
            smtp_port=587,
            smtp_user=None,
            smtp_password=None,
        )
        diag = incomplete_service.verify_connection()
        self.assertFalse(diag["success"])
        self.assertIn("Incomplete SMTP configuration", diag["error"])
        self.assertIn("SMTP_HOST", diag["error"])
        self.assertIn("SMTP_USER", diag["error"])
        self.assertIn("SMTP_PASSWORD", diag["error"])
        self.assertIsNone(diag["host"])
        self.assertEqual(diag["port"], 587)

    @patch("smtplib.SMTP")
    def test_verify_connection_starttls_port_587(self, mock_smtp_cls):
        """verify_connection must use STARTTLS for port 587 and report correct diagnostic mode."""
        mock_server = MagicMock()
        mock_server.has_extn.return_value = True
        mock_smtp_cls.return_value = mock_server
        mock_server.__enter__.return_value = mock_server

        diag = self.service.verify_connection()
        self.assertTrue(diag["success"])
        self.assertEqual(diag["host"], "smtp.example.com")
        self.assertEqual(diag["port"], 587)
        self.assertEqual(diag["mode"], "STARTTLS (Port 587/25)")

        mock_smtp_cls.assert_called_with("smtp.example.com", 587, timeout=10)
        mock_server.ehlo.assert_called()
        mock_server.starttls.assert_called()
        mock_server.login.assert_called_with("test_user@example.com", "super_secret_password_123")
        mock_server.noop.assert_called()

    @patch("smtplib.SMTP_SSL")
    def test_verify_connection_ssl_port_465(self, mock_ssl_cls):
        """verify_connection must use SMTP_SSL for port 465 and report SSL mode."""
        ssl_service = EmailService(
            smtp_host="smtp.gmail.com",
            smtp_port=465,
            smtp_user="gmail_user@gmail.com",
            smtp_password="app_password_123",
        )
        mock_server = MagicMock()
        mock_ssl_cls.return_value = mock_server
        mock_server.__enter__.return_value = mock_server

        diag = ssl_service.verify_connection()
        self.assertTrue(diag["success"])
        self.assertEqual(diag["host"], "smtp.gmail.com")
        self.assertEqual(diag["port"], 465)
        self.assertEqual(diag["mode"], "SSL (Port 465)")

        mock_ssl_cls.assert_called_with("smtp.gmail.com", 465, timeout=10)
        mock_server.login.assert_called_with("gmail_user@gmail.com", "app_password_123")
        mock_server.noop.assert_called()

    @patch("smtplib.SMTP")
    def test_verify_connection_error_and_no_credential_leak(self, mock_smtp_cls):
        """verify_connection must catch connection exceptions and never leak password in output."""
        mock_smtp_cls.side_effect = Exception("SMTPAuthenticationError: (535, b'Authentication failed')")

        diag = self.service.verify_connection()
        self.assertFalse(diag["success"])
        self.assertIn("Authentication failed", diag["error"])
        self.assertNotIn("super_secret_password_123", str(diag))

    @patch("smtplib.SMTP")
    def test_send_email_verification_otp(self, mock_smtp_cls):
        """send_email_verification_otp must generate multipart email with branding, 6-digit code, 5m TTL, and disclaimer."""
        mock_server = MagicMock()
        mock_smtp_cls.return_value = mock_server
        mock_server.__enter__.return_value = mock_server

        sent = self.service.send_email_verification_otp(
            to_email="test.recipient@example.com",
            otp_code="582910",
            user_name="Alex Mercer",
        )
        self.assertTrue(sent)
        self.assertTrue(mock_server.send_message.called)

        # Inspect generated message
        msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg["To"], "test.recipient@example.com")
        self.assertEqual(msg["From"], "AISMM <noreply@aismm.app>")
        self.assertEqual(msg["Subject"], "Verify your AISMM account")
        self.assertTrue(msg.is_multipart())

        parts = msg.get_payload()
        self.assertEqual(len(parts), 2)
        text_content = parts[0].get_payload(decode=True).decode("utf-8")
        html_content = parts[1].get_payload(decode=True).decode("utf-8")

        # Check plain text content
        self.assertIn("Hi Alex Mercer,", text_content)
        self.assertIn("YOUR VERIFICATION CODE: 582910", text_content)
        self.assertIn("This code expires in 5 minutes.", text_content)
        self.assertIn("If you did not create an AISMM account, ignore this email.", text_content)
        self.assertIn("AISMM - AI-Powered Social Media Management", text_content)

        # Check HTML content
        self.assertIn("AISMM", html_content)
        self.assertIn("582910", html_content)
        self.assertIn("Verify Your Email Address", html_content)
        self.assertIn("This code expires in 5 minutes.", html_content)
        self.assertIn("If you did not create an AISMM account, ignore this email.", html_content)

    @patch("smtplib.SMTP")
    def test_send_otp_email_purposes(self, mock_smtp_cls):
        """send_otp_email must properly customize subject, title, and body for signup, login, and reset."""
        mock_server = MagicMock()
        mock_smtp_cls.return_value = mock_server
        mock_server.__enter__.return_value = mock_server

        # 1. Signup purpose
        self.service.send_otp_email("user@example.com", "111222", purpose="signup", expires_in_minutes=10)
        msg_signup = mock_server.send_message.call_args[0][0]
        self.assertIn("Your AISMM Verification Code: 111222 (Expires in 10 minutes)", msg_signup["Subject"])
        html_signup = msg_signup.get_payload()[1].get_payload(decode=True).decode("utf-8")
        self.assertIn("Verify Your Account", html_signup)
        self.assertIn("111222", html_signup)

        # 2. Login purpose (2FA)
        self.service.send_otp_email("user@example.com", "333444", purpose="login")
        msg_login = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg_login["Subject"], "Your AISMM Login Code: 333444")
        html_login = msg_login.get_payload()[1].get_payload(decode=True).decode("utf-8")
        self.assertIn("Sign-In Verification", html_login)
        self.assertIn("333444", html_login)

        # 3. Reset purpose
        self.service.send_otp_email("user@example.com", "555666", purpose="reset")
        msg_reset = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg_reset["Subject"], "Your Password Reset OTP: 555666")
        html_reset = msg_reset.get_payload()[1].get_payload(decode=True).decode("utf-8")
        self.assertIn("Reset Your Password", html_reset)
        self.assertIn("555666", html_reset)

    @patch("smtplib.SMTP")
    def test_send_password_reset_email(self, mock_smtp_cls):
        """send_password_reset_email must produce clean reset link, 1-hour expiry, and disclaimer."""
        mock_server = MagicMock()
        mock_smtp_cls.return_value = mock_server
        mock_server.__enter__.return_value = mock_server

        sent = self.service.send_password_reset_email(
            to_email="reset.user@example.com",
            reset_token="sample_reset_token_xyz987",
            user_name="Jordan",
        )
        self.assertTrue(sent)
        msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg["Subject"], "Reset your AISMM password")
        self.assertEqual(msg["To"], "reset.user@example.com")

        text_content = msg.get_payload()[0].get_payload(decode=True).decode("utf-8")
        html_content = msg.get_payload()[1].get_payload(decode=True).decode("utf-8")

        self.assertIn("reset-password?token=sample_reset_token_xyz987", text_content)
        self.assertIn("reset-password?token=sample_reset_token_xyz987", html_content)
        self.assertIn("1 hour", text_content)
        self.assertIn("1 hour", html_content)
        self.assertIn("safely ignore this email", text_content)
        self.assertIn("safely ignore this email", html_content)

    @patch("smtplib.SMTP")
    def test_send_verification_email(self, mock_smtp_cls):
        """send_verification_email must produce clean verification link, 30-minute expiry, and disclaimer."""
        mock_server = MagicMock()
        mock_smtp_cls.return_value = mock_server
        mock_server.__enter__.return_value = mock_server

        sent = self.service.send_verification_email(
            to_email="verify.user@example.com",
            verification_token="token_abc_123",
            user_name="Sam",
        )
        self.assertTrue(sent)
        msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(msg["Subject"], "Verify your AISMM account")

        text_content = msg.get_payload()[0].get_payload(decode=True).decode("utf-8")
        html_content = msg.get_payload()[1].get_payload(decode=True).decode("utf-8")

        self.assertIn("verify-email?token=token_abc_123", text_content)
        self.assertIn("verify-email?token=token_abc_123", html_content)
        self.assertIn("30 minutes", text_content)
        self.assertIn("30 minutes", html_content)
