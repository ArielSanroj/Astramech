#!/usr/bin/env python3
"""
Throttling and rate limiting system for xcontentbot.
Ensures compliance with platform limits and prevents abuse.
"""

from .rate_limiter import (
    ThrottleType,
    ThrottleConfig,
    ThrottleBucket,
    SlidingWindowThrottle,
)
from .manager import ThrottleManager
from .decorators import (
    ThrottleException,
    ThrottledFunction,
    throttle_posts_per_hour,
    throttle_posts_per_day,
    throttle_api_calls,
    throttle_login_attempts,
    throttle_search_requests,
)
from .adaptive import AdaptiveThrottle

from typing import Dict, Any

# Global throttle manager instance
throttle_manager = ThrottleManager()


# Convenience functions
def is_allowed(throttle_type: ThrottleType) -> bool:
    """Check if a request is allowed."""
    return throttle_manager.is_allowed(throttle_type)


def wait_if_throttled(throttle_type: ThrottleType) -> float:
    """Wait if throttled."""
    return throttle_manager.wait_if_throttled(throttle_type)


def get_throttle_status(throttle_type: ThrottleType = None) -> Dict[str, Any]:
    """Get throttle status."""
    if throttle_type:
        return throttle_manager.get_throttle_status(throttle_type)
    return throttle_manager.get_all_throttle_status()


__all__ = [
    # Types and configs
    "ThrottleType",
    "ThrottleConfig",
    # Rate limiters
    "ThrottleBucket",
    "SlidingWindowThrottle",
    # Manager
    "ThrottleManager",
    "throttle_manager",
    # Decorators
    "ThrottleException",
    "ThrottledFunction",
    "throttle_posts_per_hour",
    "throttle_posts_per_day",
    "throttle_api_calls",
    "throttle_login_attempts",
    "throttle_search_requests",
    # Adaptive
    "AdaptiveThrottle",
    # Convenience functions
    "is_allowed",
    "wait_if_throttled",
    "get_throttle_status",
]
