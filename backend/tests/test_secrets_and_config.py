"""Tests for Section 1: Secrets, Configuration, and Security Vault."""

import os
import subprocess
import sys
import pytest
from pydantic import ValidationError

from backend.app.config.settings import Settings, DENYLISTED_SECRETS
from backend.app.core.vault import SecretVault


class TestSecretConfiguration:
    """Test secret configuration validation and production denylist checks."""

    def test_missing_secret_key_fails_validation(self, monkeypatch):
        """Settings instantiation must fail when SECRET_KEY or JWT_SECRET_KEY is missing."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)
        errors = str(exc_info.value)
        assert "secret_key" in errors.lower() or "jwt_secret_key" in errors.lower()

    @pytest.mark.parametrize("denylisted", list(DENYLISTED_SECRETS)[:6])
    def test_production_refuses_denylisted_secret_key(self, monkeypatch, denylisted):
        """Production environment must refuse to boot with known placeholder secrets."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", denylisted)
        monkeypatch.setenv("JWT_SECRET_KEY", "valid_super_secure_jwt_secret_key_32_chars_long")
        with pytest.raises(ValueError) as exc_info:
            Settings(_env_file=None)
        assert "FATAL SECURITY ERROR" in str(exc_info.value)
        assert "SECRET_KEY cannot be a known placeholder value" in str(exc_info.value)

    @pytest.mark.parametrize("denylisted", list(DENYLISTED_SECRETS)[:6])
    def test_production_refuses_denylisted_jwt_secret_key(self, monkeypatch, denylisted):
        """Production environment must refuse to boot with known placeholder JWT secrets."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "valid_super_secure_master_secret_key_32_chars_long")
        monkeypatch.setenv("JWT_SECRET_KEY", denylisted)
        with pytest.raises(ValueError) as exc_info:
            Settings(_env_file=None)
        assert "FATAL SECURITY ERROR" in str(exc_info.value)
        assert "JWT_SECRET_KEY cannot be a known placeholder value" in str(exc_info.value)

    def test_production_refuses_short_secret_keys(self, monkeypatch):
        """Production environment must refuse keys shorter than 16 chars."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "short_key")
        monkeypatch.setenv("JWT_SECRET_KEY", "valid_super_secure_jwt_secret_key_32_chars_long")
        with pytest.raises(ValueError) as exc_info:
            Settings(_env_file=None)
        assert "must be at least 16 characters long" in str(exc_info.value)

    def test_production_boots_cleanly_with_generated_secure_secrets(self, monkeypatch):
        """Production environment boots cleanly when provided with valid secure secrets."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "prod_master_sec_key_98374829374892374892374892374892")
        monkeypatch.setenv("JWT_SECRET_KEY", "prod_jwt_signing_key_10293847561029384756102938475610")
        monkeypatch.setenv("WEBHOOK_SECRET", "prod_webhook_sec_key_10293847561029384756102938475610")
        s = Settings(_env_file=None)
        assert s.ENVIRONMENT == "production"
        assert s.SECRET_KEY.startswith("prod_master_sec_key")


class TestSecretVaultPerRecordSalt:
    """Test SecretVault random per-record salt and security guarantees."""

    def test_vault_requires_master_key(self, monkeypatch):
        """Vault must raise ValueError when master key is absent."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        from backend.app.config.settings import get_settings
        get_settings.cache_clear()
        with pytest.raises(ValueError) as exc_info:
            SecretVault(master_key=None)
        assert "SecretVault requires a non-empty master_key" in str(exc_info.value)

    def test_random_per_record_salt_generates_unique_ciphertexts(self):
        """Encrypting the exact same plaintext multiple times must yield distinct ciphertexts with different salts."""
        master_key = "a_very_secure_master_vault_key_for_testing_purposes_only"
        vault = SecretVault(master_key=master_key)
        plaintext = "sensitive_oauth_access_token_xyz_12345"

        cipher1 = vault.encrypt(plaintext)
        cipher2 = vault.encrypt(plaintext)
        cipher3 = vault.encrypt(plaintext)

        # Ciphertexts must be unique due to random per-record salt
        assert cipher1 != cipher2
        assert cipher2 != cipher3
        assert cipher1 != cipher3

        # Must use v2 prefix with packed salt
        assert cipher1.startswith("v2$")
        assert cipher2.startswith("v2$")
        assert cipher3.startswith("v2$")

        # All must decrypt back to original plaintext
        assert vault.decrypt(cipher1) == plaintext
        assert vault.decrypt(cipher2) == plaintext
        assert vault.decrypt(cipher3) == plaintext

    def test_vault_encrypt_decrypt_dict(self):
        """Vault encrypt_dict and decrypt_dict must encrypt sensitive fields with unique salts and decrypt cleanly."""
        master_key = "a_very_secure_master_vault_key_for_testing_purposes_only"
        vault = SecretVault(master_key=master_key)
        data = {
            "account_id": "act_999",
            "access_token": "EAABwz12345_token",
            "refresh_token": "rfr_98765_token",
            "public_name": "My Business Page",
        }
        encrypted = vault.encrypt_dict(data)
        assert encrypted["account_id"] == "act_999"
        assert encrypted["public_name"] == "My Business Page"
        assert encrypted["access_token"].startswith("v2$")
        assert encrypted["refresh_token"].startswith("v2$")
        assert encrypted["access_token"] != data["access_token"]

        decrypted = vault.decrypt_dict(encrypted)
        assert decrypted == data
