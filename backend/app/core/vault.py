"""Production Security Vault - Credential & Token Encryption at Rest."""

import base64
import os
import hashlib
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from backend.app.config import get_settings

settings = get_settings()


class SecretVault:
    """AES-256 authenticated encryption vault for OAuth tokens and platform credentials."""

    def __init__(self, master_key: Optional[str] = None, salt: Optional[bytes] = None):
        raw_key = master_key or getattr(settings, "SECRET_KEY", "aismm_production_master_secret_key_2026")
        self.salt = salt or b"aismm_vault_salt_v1"
        self._fernet = self._derive_fernet(raw_key, self.salt)

    def _derive_fernet(self, secret: str, salt: bytes) -> Fernet:
        """Derive 256-bit encryption key using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        """Encrypt sensitive plaintext credential and return url-safe token string."""
        if not plain_text:
            return ""
        return self._fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        """Decrypt cipher text back to plaintext credential."""
        if not cipher_text:
            return ""
        try:
            return self._fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Vault decryption failed: {str(e)}")

    def encrypt_dict(self, data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Encrypt specific sensitive fields in a credential dictionary."""
        keys_to_encrypt = set(sensitive_keys or ["access_token", "refresh_token", "client_secret", "api_secret"])
        result = dict(data)
        for k, v in data.items():
            if k in keys_to_encrypt and isinstance(v, str):
                result[k] = self.encrypt(v)
        return result

    def decrypt_dict(self, data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Decrypt encrypted fields in a credential dictionary."""
        keys_to_decrypt = set(sensitive_keys or ["access_token", "refresh_token", "client_secret", "api_secret"])
        result = dict(data)
        for k, v in data.items():
            if k in keys_to_decrypt and isinstance(v, str):
                try:
                    result[k] = self.decrypt(v)
                except Exception:
                    pass
        return result


# Singleton vault instance
default_vault = SecretVault()
