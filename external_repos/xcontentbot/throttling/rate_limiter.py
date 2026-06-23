#!/usr/bin/env python3
"""
Rate limiting implementations: Token bucket and sliding window.
"""

import time
import threading
from collections import deque
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ThrottleType(Enum):
    """Types of throttling."""
    POSTS_PER_HOUR = "posts_per_hour"
    POSTS_PER_DAY = "posts_per_day"
    API_CALLS_PER_MINUTE = "api_calls_per_minute"
    LOGIN_ATTEMPTS_PER_HOUR = "login_attempts_per_hour"
    SEARCH_REQUESTS_PER_MINUTE = "search_requests_per_minute"


@dataclass
class ThrottleConfig:
    """Configuration for a throttle."""
    throttle_type: ThrottleType
    limit: int
    window_seconds: int
    burst_limit: Optional[int] = None
    enabled: bool = True


class ThrottleBucket:
    """Token bucket implementation for rate limiting."""

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        burst_limit: int = None
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.burst_limit = burst_limit or capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def try_consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        with self._lock:
            self._refill_tokens()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill_tokens(self):
        """Refill tokens based on time passed."""
        now = time.time()
        time_passed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + time_passed * self.refill_rate
        )
        self.last_refill = now

    def get_available_tokens(self) -> int:
        """Get currently available tokens."""
        with self._lock:
            self._refill_tokens()
            return int(self.tokens)

    def get_time_until_refill(self) -> float:
        """Get time until next token is available."""
        with self._lock:
            if self.tokens >= 1:
                return 0.0
            tokens_needed = 1 - self.tokens
            return tokens_needed / self.refill_rate


class SlidingWindowThrottle:
    """Sliding window implementation for rate limiting."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()
        self._lock = threading.Lock()

    def try_allow(self) -> bool:
        """Try to allow a request through the throttle."""
        with self._lock:
            self._cleanup_old_requests()
            if len(self.requests) < self.limit:
                self.requests.append(time.time())
                return True
            return False

    def _cleanup_old_requests(self):
        """Remove old requests outside the window."""
        now = time.time()
        window_start = now - self.window_seconds
        while self.requests and self.requests[0] < window_start:
            self.requests.popleft()

    def get_remaining_requests(self) -> int:
        """Get remaining requests in current window."""
        with self._lock:
            self._cleanup_old_requests()
            return max(0, self.limit - len(self.requests))

    def get_time_until_reset(self) -> float:
        """Get time until the window resets."""
        with self._lock:
            if not self.requests:
                return 0.0
            oldest_request = self.requests[0]
            return max(0.0, oldest_request + self.window_seconds - time.time())
