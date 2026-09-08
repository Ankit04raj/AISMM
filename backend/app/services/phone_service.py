"""Phone/SMS service for sending verification OTPs via SMS providers."""

import logging
from typing import Optional
import requests

from backend.app.config.settings import settings

logger = logging.getLogger(__name__)


class PhoneService:
    """Service for sending SMS verification codes via configured provider."""

    def __init__(self):
        """Initialize phone service with SMS provider configuration from settings."""
        self.provider = settings.SMS_PROVIDER
        self.api_key = settings.SMS_API_KEY
        self.api_secret = settings.SMS_API_SECRET
        self.sender_id = settings.SMS_SENDER_ID
        self.from_number = settings.SMS_FROM_NUMBER

    def send_verification_sms(
        self, to_number: str, otp: str, user_name: Optional[str] = None
    ) -> bool:
        """
        Send verification SMS to user.

        Args:
            to_number: Recipient phone number in E.164 format (e.g., +919876543210)
            otp: 6-digit verification code
            user_name: Optional user's name for personalization

        Returns:
            True if SMS sent successfully, False otherwise
        """
        try:
            if self.provider == "msg91":
                return self._send_via_msg91(to_number, otp)
            elif self.provider == "fast2sms":
                return self._send_via_fast2sms(to_number, otp)
            elif self.provider == "twilio":
                return self._send_via_twilio(to_number, otp)
            else:
                logger.warning(f"Unknown SMS provider: {self.provider}")
                return False
        except Exception as e:
            logger.error(f"Failed to send verification SMS to {to_number}: {e}")
            return False

    def _send_via_msg91(self, to_number: str, otp: str) -> bool:
        """Send SMS via MSG91 API (India-focused provider)."""
        if not all([self.api_key, self.sender_id]):
            logger.error("MSG91 configuration incomplete (SMS_API_KEY, SMS_SENDER_ID required)")
            return False

        url = "https://api.msg91.com/api/v5/flow/"
        headers = {
            "authkey": self.api_key,
            "content-type": "application/json",
        }
        payload = {
            "flow_id": "verification_flow",  # Pre-configured template in MSG91
            "sender": self.sender_id,
            "mobiles": to_number.replace("+", ""),
            "var1": otp,  # {{var1}} in template
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"MSG91 verification SMS sent to {to_number}")
        return True

    def _send_via_fast2sms(self, to_number: str, otp: str) -> bool:
        """Send SMS via Fast2SMS API (India-focused provider)."""
        if not self.api_key:
            logger.error("Fast2SMS configuration incomplete (SMS_API_KEY required)")
            return False

        url = "https://www.fast2sms.com/dev/bulkV2"
        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "route": "otp",
            "numbers": to_number.replace("+", ""),
            "message": f"Your AISMM verification code is {otp}. Valid for 10 minutes.",
            "sender_id": self.sender_id or "AISMM",
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Fast2SMS verification SMS sent to {to_number}")
        return True

    def _send_via_twilio(self, to_number: str, otp: str) -> bool:
        """Send SMS via Twilio API (Global provider)."""
        if not all([self.api_key, self.api_secret, self.from_number]):
            logger.error("Twilio configuration incomplete (SMS_API_KEY=SID, SMS_API_SECRET=AuthToken, SMS_FROM_NUMBER required)")
            return False

        from twilio.rest import Client
        client = Client(self.api_key, self.api_secret)

        message = client.messages.create(
            body=f"Your AISMM verification code is {otp}. Valid for 10 minutes.",
            from_=self.from_number,
            to=to_number,
        )
        logger.info(f"Twilio verification SMS sent to {to_number} (SID: {message.sid})")
        return True


# Singleton instance
phone_service = PhoneService()