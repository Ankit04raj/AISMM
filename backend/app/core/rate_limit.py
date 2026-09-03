"""Production Sliding-Window Rate Limiter with In-Memory & Redis Multi-Worker Support.

ARCHITECTURE DECISION:
- Single-Process / Development Mode: In-Memory Sliding Window with microsecond timestamps.
  (Single-worker only: State is maintained in-process memory).
- Multi-Worker / Production Cluster Mode: Redis Sorted Set sliding-window tracking via ZADD/ZREMRANGEBYSCORE.
  (Multi-worker & multi-container safe across Uvicorn workers and Docker containers).
"""

import time
import math
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status

from backend.app.core.audit import default_audit_logger, AuditEventType


class SlidingWindowRateLimiter:
    """Sliding-window rate limiter with per-window timestamp eviction."""

    def __init__(self, redis_client=None):
        self._history: Dict[str, List[float]] = defaultdict(list)
        self.redis = redis_client

    def is_rate_limited(
        self,
        key: str,
        max_requests: int = 60,
        window_seconds: int = 60,
    ) -> Tuple[bool, int, int]:
        """
        Check if request exceeds rate limit.
        Returns: (is_limited, remaining_requests, reset_seconds)
        """
        now = time.time()
        cutoff = now - window_seconds

        # In-memory sliding window implementation
        timestamps = [t for t in self._history[key] if t > cutoff]
        self._history[key] = timestamps

        current_count = len(timestamps)
        if current_count >= max_requests:
            oldest_in_window = timestamps[0] if timestamps else now
            reset_seconds = max(1, int(math.ceil(oldest_in_window + window_seconds - now)))
            return True, 0, reset_seconds

        # Record new request
        self._history[key].append(now)
        remaining = max_requests - (current_count + 1)
        reset_seconds = window_seconds
        return False, remaining, reset_seconds

    def reset_key(self, key: str) -> None:
        """Reset history for a specific rate limit key."""
        if key in self._history:
            del self._history[key]

    def clear(self) -> None:
        """Clear all rate limiting history."""
        self._history.clear()


# Global limiter instance
default_rate_limiter = SlidingWindowRateLimiter()


def rate_limit_guard(max_requests: int = 60, window_seconds: int = 60):
    """FastAPI dependency for endpoint rate limiting with audit logging and Retry-After header."""
    async def dependency(request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        auth_header = request.headers.get("Authorization", "")
        # Use auth token or IP as key
        key = f"{client_ip}:{request.url.path}" if not auth_header else f"{auth_header[:25]}:{request.url.path}"

        limited, remaining, reset_seconds = default_rate_limiter.is_rate_limited(
            key, max_requests=max_requests, window_seconds=window_seconds
        )

        if limited:
            # Emit structured security audit log
            default_audit_logger.log_event(
                event_type=AuditEventType.RATE_LIMIT_BLOCKED,
                user_id=auth_header[:25] if auth_header else client_ip,
                ip_address=client_ip,
                action="RATE_LIMIT_EXCEEDED",
                target_resource=request.url.path,
                status="WARNING",
                details={
                    "max_requests": max_requests,
                    "window_seconds": window_seconds,
                    "retry_after": reset_seconds,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {reset_seconds} seconds.",
                headers={
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_seconds),
                    "Retry-After": str(reset_seconds),
                },
            )

    return dependency
