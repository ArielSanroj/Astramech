#!/usr/bin/env python3
"""
Throttling decorators and convenience functions.
"""

import asyncio
import logging
from typing import Callable, Dict, Any

from .rate_limiter import ThrottleType

logger = logging.getLogger(__name__)


class ThrottleException(Exception):
    """Exception raised when a request is throttled."""
    pass


class ThrottledFunction:
    """Decorator for throttling function calls."""

    def __init__(
        self,
        throttle_type: ThrottleType,
        wait_on_throttle: bool = True,
        throttle_manager=None
    ):
        self.throttle_type = throttle_type
        self.wait_on_throttle = wait_on_throttle
        self._throttle_manager = throttle_manager

    @property
    def throttle_manager(self):
        """Get throttle manager lazily to avoid circular imports."""
        if self._throttle_manager is None:
            from . import throttle_manager
            self._throttle_manager = throttle_manager
        return self._throttle_manager

    def __call__(self, func: Callable):
        if asyncio.iscoroutinefunction(func):
            return self._wrap_async(func)
        return self._wrap_sync(func)

    def _wrap_async(self, func: Callable):
        """Wrap async function with throttling."""
        async def wrapper(*args, **kwargs):
            self._check_and_wait()
            return await func(*args, **kwargs)
        return wrapper

    def _wrap_sync(self, func: Callable):
        """Wrap sync function with throttling."""
        def wrapper(*args, **kwargs):
            self._check_and_wait()
            return func(*args, **kwargs)
        return wrapper

    def _check_and_wait(self):
        """Check throttle and wait if needed."""
        if not self.throttle_manager.is_allowed(self.throttle_type):
            if self.wait_on_throttle:
                wait_time = self.throttle_manager.wait_if_throttled(
                    self.throttle_type
                )
                logger.info(
                    f"Waited {wait_time:.2f}s for throttle {self.throttle_type}"
                )
            else:
                raise ThrottleException(
                    f"Request throttled by {self.throttle_type}"
                )


def throttle_posts_per_hour(wait_on_throttle: bool = True):
    """Throttle posts to 6 per hour."""
    return ThrottledFunction(ThrottleType.POSTS_PER_HOUR, wait_on_throttle)


def throttle_posts_per_day(wait_on_throttle: bool = True):
    """Throttle posts to 50 per day."""
    return ThrottledFunction(ThrottleType.POSTS_PER_DAY, wait_on_throttle)


def throttle_api_calls(wait_on_throttle: bool = True):
    """Throttle API calls to 60 per minute."""
    return ThrottledFunction(ThrottleType.API_CALLS_PER_MINUTE, wait_on_throttle)


def throttle_login_attempts(wait_on_throttle: bool = False):
    """Throttle login attempts to 5 per hour."""
    return ThrottledFunction(ThrottleType.LOGIN_ATTEMPTS_PER_HOUR, wait_on_throttle)


def throttle_search_requests(wait_on_throttle: bool = True):
    """Throttle search requests to 30 per minute."""
    return ThrottledFunction(
        ThrottleType.SEARCH_REQUESTS_PER_MINUTE,
        wait_on_throttle
    )
