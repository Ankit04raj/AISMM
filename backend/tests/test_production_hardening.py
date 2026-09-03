"""Comprehensive test suite for Production Hardening, Rate Limiting, Circuit Breaking, and Security."""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app, create_app
from backend.app.db.session import get_db, Base
from backend.app.core.vault import SecretVault
from backend.app.core.rate_limit import SlidingWindowRateLimiter, default_rate_limiter
from backend.app.core.resilience import CircuitBreaker, CircuitState, async_retry_with_backoff
from backend.app.core.audit import AuditLogger, AuditEventType, default_audit_logger
from backend.app.core.errors import PlatformError, PlatformUnavailableError
from backend.app.core.platform_adapters import PlatformRegistry

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


class TestRateLimiterWiringAndProof:
    """Test sliding window rate limiting and live HTTP 429 response enforcement."""

    @pytest.fixture(autouse=True)
    def clean_rate_limiter(self):
        default_rate_limiter.clear()
        yield
        default_rate_limiter.clear()

    def test_live_login_rate_limit_exceeded_returns_429_with_retry_after(self):
        """Proof 1: Exceeding the login rate limit (10 reqs/min) returns a real HTTP 429 with Retry-After header."""
        mock_session = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_res
        app.dependency_overrides[get_db] = lambda: mock_session

        try:
            test_client = TestClient(app)
            login_body = {"email": "ratelimit_user@aismm.io", "password": "WrongPassword123!"}

            # Make 10 login requests (allowed up to limit)
            for i in range(10):
                resp = test_client.post("/api/v1/auth/login", json=login_body)
                assert resp.status_code in (401, 200), f"Request {i+1} failed unexpectedly: {resp.status_code}"

            # 11th request must exceed limit and return 429
            resp_429 = test_client.post("/api/v1/auth/login", json=login_body)
            assert resp_429.status_code == 429, f"Expected 429, got {resp_429.status_code}: {resp_429.text}"

            # Check headers
            headers = resp_429.headers
            assert "Retry-After" in headers
            retry_after = int(headers["Retry-After"])
            assert retry_after > 0
            assert headers.get("X-RateLimit-Limit") == "10"
            assert headers.get("X-RateLimit-Remaining") == "0"
            assert "Rate limit exceeded" in resp_429.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_db, None)


class TestCircuitBreakerWiringAndProof:
    """Test circuit breaker state transitions, repeated failures, and short-circuiting."""

    @pytest.mark.asyncio
    async def test_repeated_adapter_failures_trip_circuit_and_short_circuit(self):
        """Proof 2: Repeated adapter failures trip the circuit breaker OPEN, causing subsequent calls to fast-fail."""
        cb = CircuitBreaker("instagram_live", failure_threshold=3, recovery_timeout_seconds=60.0)
        assert cb.state == CircuitState.CLOSED

        call_count = 0

        async def failing_platform_network_call():
            nonlocal call_count
            call_count += 1
            raise PlatformError("Simulated remote 500 API Gateway Timeout from Platform", platform="instagram")

        # 1. First 3 attempts fail and trip the circuit
        for attempt in range(3):
            with pytest.raises(PlatformError):
                await async_retry_with_backoff(
                    failing_platform_network_call,
                    max_retries=0,
                    circuit_breaker=cb,
                )

        assert cb.state == CircuitState.OPEN
        assert call_count == 3

        # 2. Subsequent outbound calls are immediately short-circuited by the circuit breaker (never calling the outbound network)
        with pytest.raises(PlatformUnavailableError) as exc_info:
            await async_retry_with_backoff(
                failing_platform_network_call,
                max_retries=0,
                circuit_breaker=cb,
            )

        assert "is OPEN. Fast failing to prevent cascade" in str(exc_info.value)
        # Call count remains 3 (the outbound call was never reached!)
        assert call_count == 3


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
