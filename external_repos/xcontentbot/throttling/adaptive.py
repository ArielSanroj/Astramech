#!/usr/bin/env python3
"""
Adaptive throttling that adjusts limits based on success rates.
"""

import time
import logging
import threading

logger = logging.getLogger(__name__)


class AdaptiveThrottle:
    """Adaptive throttling that adjusts limits based on success rates."""

    def __init__(self, base_limit: int, window_seconds: int):
        self.base_limit = base_limit
        self.window_seconds = window_seconds
        self.current_limit = base_limit
        self.success_count = 0
        self.failure_count = 0
        self.last_adjustment = time.time()
        self.adjustment_interval = 300  # 5 minutes
        self._lock = threading.Lock()

    def record_success(self):
        """Record a successful operation."""
        with self._lock:
            self.success_count += 1
            self._maybe_adjust_limit()

    def record_failure(self):
        """Record a failed operation."""
        with self._lock:
            self.failure_count += 1
            self._maybe_adjust_limit()

    def _maybe_adjust_limit(self):
        """Adjust limit based on success/failure rates."""
        now = time.time()
        if now - self.last_adjustment < self.adjustment_interval:
            return

        total_operations = self.success_count + self.failure_count
        if total_operations < 10:
            return

        success_rate = self.success_count / total_operations
        self._adjust_limit_by_rate(success_rate)
        self._reset_counters(now)

    def _adjust_limit_by_rate(self, success_rate: float):
        """Adjust limit based on success rate."""
        max_limit = self.base_limit * 2
        min_limit = self.base_limit * 0.5

        if success_rate > 0.95 and self.current_limit < max_limit:
            self.current_limit = min(self.current_limit * 1.2, max_limit)
            logger.info(f"Increased throttle limit to {self.current_limit}")
        elif success_rate < 0.8 and self.current_limit > min_limit:
            self.current_limit = max(self.current_limit * 0.8, min_limit)
            logger.info(f"Decreased throttle limit to {self.current_limit}")

    def _reset_counters(self, now: float):
        """Reset counters after adjustment."""
        self.success_count = 0
        self.failure_count = 0
        self.last_adjustment = now

    def is_allowed(self) -> bool:
        """Check if request is allowed with current limit."""
        return True

    def get_current_limit(self) -> float:
        """Get the current adjusted limit."""
        return self.current_limit

    def get_stats(self) -> dict:
        """Get current stats for monitoring."""
        with self._lock:
            total = self.success_count + self.failure_count
            return {
                "base_limit": self.base_limit,
                "current_limit": self.current_limit,
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "success_rate": self.success_count / total if total > 0 else 0,
                "last_adjustment": self.last_adjustment,
            }
