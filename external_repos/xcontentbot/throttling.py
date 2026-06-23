#!/usr/bin/env python3
"""
Throttling and rate limiting system for xcontentbot.
Ensures compliance with platform limits and prevents abuse.

This module re-exports from the throttling package for backwards compatibility.
"""

# Re-export everything from the throttling package
from throttling import (
    # Types and configs
    ThrottleType,
    ThrottleConfig,
    # Rate limiters
    ThrottleBucket,
    SlidingWindowThrottle,
    # Manager
    ThrottleManager,
    throttle_manager,
    # Decorators
    ThrottleException,
    ThrottledFunction,
    throttle_posts_per_hour,
    throttle_posts_per_day,
    throttle_api_calls,
    throttle_login_attempts,
    throttle_search_requests,
    # Adaptive
    AdaptiveThrottle,
    # Convenience functions
    is_allowed,
    wait_if_throttled,
    get_throttle_status,
)

__all__ = [
    "ThrottleType",
    "ThrottleConfig",
    "ThrottleBucket",
    "SlidingWindowThrottle",
    "ThrottleManager",
    "throttle_manager",
    "ThrottleException",
    "ThrottledFunction",
    "throttle_posts_per_hour",
    "throttle_posts_per_day",
    "throttle_api_calls",
    "throttle_login_attempts",
    "throttle_search_requests",
    "AdaptiveThrottle",
    "is_allowed",
    "wait_if_throttled",
    "get_throttle_status",
]
