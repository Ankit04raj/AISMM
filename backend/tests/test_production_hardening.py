"""Comprehensive test suite for Phase 16 Production Hardening & Security."""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.core.vault import SecretVault
from backend.app.core.rate_limit import SlidingWindowRateLimiter
from backend.app.core.resilience import CircuitBreaker, CircuitState, async_retry_with_backoff
from backend.app.core.audit import AuditLogger, AuditEventType
from backend.app.core.errors import PlatformError, PlatformUnavailableError

client = TestClient(app)


class TestSecretVault:
    """Test AES-256 SecretVault encryption at rest and key derivation."""

    @pytest.fixture
    def vault(self):
        return SecretVault(master_key="test_production_master_secret_key_2026")

    def test_encrypt_and_decrypt_plaintext(self, vault):
        secret_token = "EAABwzLixnjYBAOd8gH7K4J9L3N"
        cipher = vault.encrypt(secret_token)
        assert cipher != secret_token
        decrypted = vault.decrypt(cipher)
        assert decrypted == secret_token

    def test_encrypt_dict_sensitive_keys(self, vault):
        credentials = {
            "client_id": "public_app_123",
            "client_secret": "super_secret_app_key",
            "access_token": "oauth2_token_xyz",
            "page_id": "987654321",
        }
        encrypted = vault.encrypt_dict(credentials)
        assert encrypted["client_id"] == "public_app_123"
        assert encrypted["page_id"] == "987654321"
        assert encrypted["client_secret"] != "super_secret_app_key"
        assert encrypted["access_token"] != "oauth2_token_xyz"

        decrypted = vault.decrypt_dict(encrypted)
        assert decrypted["client_secret"] == "super_secret_app_key"
        assert decrypted["access_token"] == "oauth2_token_xyz"

    def test_empty_string_handling(self, vault):
        assert vault.encrypt("") == ""
        assert vault.decrypt("") == ""


class TestRateLimiter:
    """Test sliding window rate limiting."""

    @pytest.fixture
    def limiter(self):
        return SlidingWindowRateLimiter()

    def test_rate_limiter_allows_under_limit(self, limiter):
        key = "user_123:/posts"
        for i in range(5):
            limited, remaining, reset = limiter.is_rate_limited(key, max_requests=5, window_seconds=10)
            assert limited is False
            assert remaining == 5 - (i + 1)
            assert reset == 10

    def test_rate_limiter_blocks_over_limit(self, limiter):
        key = "user_456:/publish"
        for _ in range(3):
            limiter.is_rate_limited(key, max_requests=3, window_seconds=5)

        # 4th request exceeds limit
        limited, remaining, reset = limiter.is_rate_limited(key, max_requests=3, window_seconds=5)
        assert limited is True
        assert remaining == 0
        assert reset > 0

    def test_rate_limiter_reset_key(self, limiter):
        key = "user_789:/search"
        limiter.is_rate_limited(key, max_requests=1, window_seconds=10)
        limiter.reset_key(key)

        limited, remaining, _ = limiter.is_rate_limited(key, max_requests=1, window_seconds=10)
        assert limited is False
        assert remaining == 0


class TestResilienceAndCircuitBreaker:
    """Test circuit breaker state machine and exponential backoff."""

    def test_circuit_breaker_transitions(self):
        cb = CircuitBreaker("facebook_api", failure_threshold=3, recovery_timeout_seconds=0.1)
        assert cb.state == CircuitState.CLOSED
        assert cb.allow_request() is True

        # Record 3 failures -> Trips OPEN
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.allow_request() is False

        # Wait recovery timeout -> HALF_OPEN
        time.sleep(0.15)
        assert cb.allow_request() is True
        assert cb.state == CircuitState.HALF_OPEN

        # 2 successes in HALF_OPEN -> Closes back to CLOSED
        cb.record_success()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_async_retry_with_backoff_success_after_retries(self):
        attempts = 0

        async def flaky_api_call():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise PlatformError("Transient network glitch", platform="x")
            return "api_response_success"

        res = await async_retry_with_backoff(
            flaky_api_call,
            max_retries=3,
            base_delay_seconds=0.01,
            retry_exceptions=(PlatformError,),
        )
        assert res == "api_response_success"
        assert attempts == 2

    @pytest.mark.asyncio
    async def test_async_retry_fast_fails_on_open_circuit(self):
        cb = CircuitBreaker("x_api", failure_threshold=1, recovery_timeout_seconds=60.0)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        async def dummy_call():
            return "ok"

        with pytest.raises(PlatformUnavailableError) as exc_info:
            await async_retry_with_backoff(dummy_call, circuit_breaker=cb)

        assert "OPEN" in str(exc_info.value)


class TestAuditLogger:
    """Test structured compliance audit logging."""

    def test_audit_event_creation(self):
        logger = AuditLogger()
        event = logger.log_event(
            event_type=AuditEventType.POST_PUBLISHED,
            user_id="usr_123",
            ip_address="192.168.1.10",
            action="Publish multi-platform post",
            target_resource="post_888",
            status="SUCCESS",
            details={"platforms": ["instagram", "facebook"], "scheduled": False},
        )
        assert event.event_type == AuditEventType.POST_PUBLISHED
        assert event.user_id == "usr_123"
        assert event.target_resource == "post_888"
        assert event.status == "SUCCESS"


class TestHealthAndObservabilityEndpoints:
    """Test production health probes and middleware telemetry."""

    def test_liveness_probe_endpoint(self):
        response = client.get("/api/v1/health/liveness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "uptime_seconds" in data

    def test_readiness_probe_endpoint(self):
        with patch("backend.app.api.v1.health.get_db") as mock_get_db:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock()
            app.dependency_overrides[get_db] = lambda: mock_session

            response = client.get("/api/v1/health/readiness")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["registered_platforms_count"] >= 5
            assert data["registered_models_count"] >= 6

            app.dependency_overrides.clear()

    def test_telemetry_endpoint(self):
        response = client.get("/api/v1/health/telemetry")
        assert response.status_code == 200
        data = response.json()
        assert "process" in data
        assert "platforms" in data
        assert "models" in data
        assert data["platforms"]["count"] >= 5

    def test_correlation_id_and_process_time_headers(self):
        response = client.get("/api/v1/health/liveness", headers={"X-Correlation-ID": "test-req-123"})
        assert response.status_code == 200
        assert response.headers.get("X-Correlation-ID") == "test-req-123"
        assert "X-Process-Time-Ms" in response.headers
