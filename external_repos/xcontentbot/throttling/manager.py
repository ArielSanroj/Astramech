#!/usr/bin/env python3
"""
Throttle manager for coordinating all throttling and rate limiting.
"""

import time
import logging
import threading
from typing import Dict, Any

from .rate_limiter import (
    ThrottleType,
    ThrottleConfig,
    ThrottleBucket,
    SlidingWindowThrottle,
)

logger = logging.getLogger(__name__)


class ThrottleManager:
    """Manages all throttling and rate limiting."""

    def __init__(self):
        self.throttles: Dict[ThrottleType, Any] = {}
        self.throttle_configs: Dict[ThrottleType, ThrottleConfig] = {}
        self.metrics: Dict[ThrottleType, Dict[str, int]] = {}
        self._lock = threading.Lock()
        self._setup_default_throttles()

    def _setup_default_throttles(self):
        """Setup default throttle configurations."""
        default_configs = [
            ThrottleConfig(ThrottleType.POSTS_PER_HOUR, 6, 3600, burst_limit=2),
            ThrottleConfig(ThrottleType.POSTS_PER_DAY, 50, 86400, burst_limit=10),
            ThrottleConfig(ThrottleType.API_CALLS_PER_MINUTE, 60, 60, burst_limit=10),
            ThrottleConfig(ThrottleType.LOGIN_ATTEMPTS_PER_HOUR, 5, 3600, burst_limit=1),
            ThrottleConfig(ThrottleType.SEARCH_REQUESTS_PER_MINUTE, 30, 60, burst_limit=5),
        ]
        for config in default_configs:
            self.add_throttle(config)

    def add_throttle(self, config: ThrottleConfig):
        """Add a new throttle configuration."""
        with self._lock:
            self.throttle_configs[config.throttle_type] = config
            self._create_throttle_instance(config)
            self._init_metrics(config.throttle_type)

    def _create_throttle_instance(self, config: ThrottleConfig):
        """Create appropriate throttle instance based on type."""
        post_types = [ThrottleType.POSTS_PER_HOUR, ThrottleType.POSTS_PER_DAY]
        if config.throttle_type in post_types:
            self.throttles[config.throttle_type] = SlidingWindowThrottle(
                config.limit, config.window_seconds
            )
        else:
            refill_rate = config.limit / config.window_seconds
            self.throttles[config.throttle_type] = ThrottleBucket(
                config.limit, refill_rate, config.burst_limit
            )

    def _init_metrics(self, throttle_type: ThrottleType):
        """Initialize metrics for a throttle type."""
        self.metrics[throttle_type] = {
            "total_requests": 0,
            "allowed_requests": 0,
            "throttled_requests": 0,
            "burst_requests": 0
        }

    def is_allowed(self, throttle_type: ThrottleType) -> bool:
        """Check if a request is allowed through the throttle."""
        if throttle_type not in self.throttles:
            logger.warning(f"Throttle {throttle_type} not configured")
            return True

        config = self.throttle_configs.get(throttle_type)
        if not config or not config.enabled:
            return True

        throttle = self.throttles[throttle_type]
        with self._lock:
            self.metrics[throttle_type]["total_requests"] += 1

        allowed = self._check_throttle(throttle)
        self._update_metrics(throttle_type, allowed)
        return allowed

    def _check_throttle(self, throttle) -> bool:
        """Check if request passes the throttle."""
        if isinstance(throttle, SlidingWindowThrottle):
            return throttle.try_allow()
        return throttle.try_consume()

    def _update_metrics(self, throttle_type: ThrottleType, allowed: bool):
        """Update metrics after throttle check."""
        with self._lock:
            if allowed:
                self.metrics[throttle_type]["allowed_requests"] += 1
            else:
                self.metrics[throttle_type]["throttled_requests"] += 1

    def wait_if_throttled(self, throttle_type: ThrottleType) -> float:
        """Wait if throttled and return wait time."""
        if throttle_type not in self.throttles:
            return 0.0

        throttle = self.throttles[throttle_type]
        wait_time = self._get_wait_time(throttle)

        if wait_time > 0:
            logger.info(f"Throttled on {throttle_type}, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        return wait_time

    def _get_wait_time(self, throttle) -> float:
        """Get wait time for a throttle."""
        if isinstance(throttle, SlidingWindowThrottle):
            return throttle.get_time_until_reset()
        return throttle.get_time_until_refill()

    def get_throttle_status(self, throttle_type: ThrottleType) -> Dict[str, Any]:
        """Get status of a specific throttle."""
        if throttle_type not in self.throttles:
            return {"error": "Throttle not configured"}

        throttle = self.throttles[throttle_type]
        config = self.throttle_configs[throttle_type]
        metrics = self.metrics[throttle_type]

        status = {
            "type": throttle_type.value,
            "limit": config.limit,
            "window_seconds": config.window_seconds,
            "enabled": config.enabled,
            "metrics": metrics.copy()
        }
        self._add_throttle_specific_status(status, throttle)
        return status

    def _add_throttle_specific_status(self, status: Dict, throttle):
        """Add throttle-specific status info."""
        if isinstance(throttle, SlidingWindowThrottle):
            status["remaining_requests"] = throttle.get_remaining_requests()
            status["time_until_reset"] = throttle.get_time_until_reset()
        else:
            status["available_tokens"] = throttle.get_available_tokens()
            status["time_until_refill"] = throttle.get_time_until_refill()

    def get_all_throttle_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all throttles."""
        return {
            throttle_type.value: self.get_throttle_status(throttle_type)
            for throttle_type in self.throttles.keys()
        }

    def reset_throttle(self, throttle_type: ThrottleType):
        """Reset a specific throttle."""
        if throttle_type not in self.throttles:
            return
        throttle = self.throttles[throttle_type]
        if isinstance(throttle, SlidingWindowThrottle):
            throttle.requests.clear()
        else:
            throttle.tokens = throttle.capacity
            throttle.last_refill = time.time()
        logger.info(f"Reset throttle {throttle_type}")

    def reset_all_throttles(self):
        """Reset all throttles."""
        for throttle_type in self.throttles.keys():
            self.reset_throttle(throttle_type)
