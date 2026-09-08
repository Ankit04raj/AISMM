"""Production Resilience - Circuit Breaker & Exponential Backoff Retries."""

import asyncio
import random
import time
from typing import Callable, Any, Optional, Type, Tuple
from enum import Enum

from backend.app.core.errors import PlatformError, RateLimitError, PlatformUnavailableError


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Tripped, rejecting fast
    HALF_OPEN = "HALF_OPEN"# Testing recovery


class CircuitBreaker:
    """Circuit Breaker preventing cascade failures on dead platform APIs."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
        expected_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_seconds
        self.expected_exceptions = expected_exceptions

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.success_count_half_open = 0

    def record_success(self) -> None:
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count_half_open += 1
            if self.success_count_half_open >= 2:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count_half_open = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def allow_request(self) -> bool:
        """Check if request is allowed through."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count_half_open = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False


async def async_retry_with_backoff(
    coro_func: Callable[..., Any],
    *args,
    max_retries: int = 3,
    base_delay_seconds: float = 0.5,
    max_delay_seconds: float = 8.0,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    circuit_breaker: Optional[CircuitBreaker] = None,
    **kwargs,
) -> Any:
    """
    Execute async function with exponential backoff and randomized full jitter.
    Integrates with optional CircuitBreaker.
    """
    if circuit_breaker and not circuit_breaker.allow_request():
        raise PlatformUnavailableError(
            platform=circuit_breaker.name,
            message=f"Circuit breaker for {circuit_breaker.name} is OPEN. Fast failing to prevent cascade.",
        )

    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            result = await coro_func(*args, **kwargs)
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
        except retry_exceptions as exc:
            last_exc = exc
            if circuit_breaker:
                circuit_breaker.record_failure()

            if attempt == max_retries:
                break

            # Calculate exponential backoff with full jitter: delay = uniform(0, min(max_delay, base * 2^attempt))
            calculated_delay = min(max_delay_seconds, base_delay_seconds * (2 ** attempt))
            jittered_delay = random.uniform(0.1, calculated_delay)
            await asyncio.sleep(jittered_delay)

    if last_exc:
        raise last_exc
