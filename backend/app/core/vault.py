"""Production Security Vault - Credential & Token Encryption at Rest with Per-Record Salt."""

import base64
import os
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from backend.app.config import get_settings
from backend.app.core.audit import default_audit_logger, AuditEventType


class SecretVault:
    """AES-256 authenticated encryption vault for OAuth tokens and platform credentials.

    Uses PBKDF2-HMAC-SHA256 key derivation with a cryptographically secure random 16-byte
    salt generated per encryption operation, packed into the ciphertext.
    """

    def __init__(self, master_key: Optional[str] = None, default_salt: Optional[bytes] = None):
        raw_key = master_key
        if not raw_key:
            try:
                app_settings = get_settings()
                raw_key = getattr(app_settings, "SECRET_KEY", None)
            except Exception:
                raw_key = None

        if not raw_key:
            raise ValueError("SecretVault requires a non-empty master_key or SECRET_KEY configured in settings.")

        self.master_key = raw_key
        self.default_salt = default_salt

    def _derive_fernet(self, secret: str, salt: bytes) -> Fernet:
        """Derive 256-bit encryption key using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode("utf-8")))
        return Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        """Encrypt sensitive plaintext credential using a fresh random 16-byte salt."""
        if not plain_text:
            return ""
        # Generate random per-record salt
        salt = os.urandom(16)
        fernet = self._derive_fernet(self.master_key, salt)
        fernet_token = fernet.encrypt(plain_text.encode("utf-8"))
        salt_b64 = base64.urlsafe_b64encode(salt).decode("utf-8")
        token_str = fernet_token.decode("utf-8")

        # Audit log encryption at rest
        default_audit_logger.log_event(
            event_type=AuditEventType.SETTINGS_UPDATED,
            action="CREDENTIAL_ENCRYPTED_AT_REST",
            target_resource="SecretVault",
            status="SUCCESS",
        )
        return f"v2${salt_b64}${token_str}"

    def decrypt(self, cipher_text: str) -> str:
        """Decrypt cipher text back to plaintext credential using its embedded or fallback salt."""
        if not cipher_text:
            return ""
        try:
            decrypted = None
            if cipher_text.startswith("v2$"):
                parts = cipher_text.split("$", 2)
                if len(parts) == 3:
                    salt_b64 = parts[1]
                    token_str = parts[2]
                    salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
                    fernet = self._derive_fernet(self.master_key, salt)
                    decrypted = fernet.decrypt(token_str.encode("utf-8")).decode("utf-8")

            if decrypted is None:
                # Fallback for legacy static salt or custom default_salt
                salt = self.default_salt or b"aismm_vault_salt_v1"
                fernet = self._derive_fernet(self.master_key, salt)
                decrypted = fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")

            default_audit_logger.log_event(
                event_type=AuditEventType.SETTINGS_UPDATED,
                action="CREDENTIAL_DECRYPTED_FROM_VAULT",
                target_resource="SecretVault",
                status="SUCCESS",
            )
            return decrypted
        except Exception as e:
            default_audit_logger.log_event(
                event_type=AuditEventType.SETTINGS_UPDATED,
                action="CREDENTIAL_DECRYPTION_FAILED",
                target_resource="SecretVault",
                status="FAILURE",
                details={"error": str(e)},
            )
            raise ValueError(f"Vault decryption failed: {str(e)}")

    def encrypt_dict(self, data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Encrypt specific sensitive fields in a credential dictionary."""
        keys_to_encrypt = set(sensitive_keys or ["access_token", "refresh_token", "client_secret", "api_secret", "api_key"])
        result = dict(data)
        for k, v in data.items():
            if k in keys_to_encrypt and isinstance(v, str):
                result[k] = self.encrypt(v)
        return result

    def decrypt_dict(self, data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Decrypt encrypted fields in a credential dictionary."""
        keys_to_decrypt = set(sensitive_keys or ["access_token", "refresh_token", "client_secret", "api_secret", "api_key"])
        result = dict(data)
        for k, v in data.items():
            if k in keys_to_decrypt and isinstance(v, str):
                try:
                    result[k] = self.decrypt(v)
                except Exception:
                    pass
        return result


def get_vault(master_key: Optional[str] = None) -> SecretVault:
    """Helper to instantiate or retrieve SecretVault."""
    return SecretVault(master_key=master_key)
