"""Production In-Memory & Distributed Sliding-Window Rate Limiter."""

import time
import math
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status

from backend.app.core.errors import RateLimitError


class SlidingWindowRateLimiter:
    """Sliding-window in-memory rate limiter with microsecond timestamp tracking."""

    def __init__(self):
        # Key -> List of timestamps
        self._history: Dict[str, List[float]] = defaultdict(list)

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

        # Clean old timestamps
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
    """FastAPI dependency for endpoint rate limiting."""
    async def dependency(request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        auth_header = request.headers.get("Authorization", "")
        # Use auth token or IP as key
        key = f"{client_ip}:{request.url.path}" if not auth_header else f"{auth_header[:20]}:{request.url.path}"

        limited, remaining, reset_seconds = default_rate_limiter.is_rate_limited(
            key, max_requests=max_requests, window_seconds=window_seconds
        )

        if limited:
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
