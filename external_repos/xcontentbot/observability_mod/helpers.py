"""Helper functions for observability."""
import time
import asyncio
import logging


def log_post_event(event: str, post_id: str, **kwargs):
    """Log a post-related event."""
    logger = logging.getLogger("xcontentbot.posts")
    logger.info(
        f"Post event: {event}",
        extra={"extra_fields": {"post_id": post_id, "event": event, **kwargs}}
    )


def log_selector_event(event: str, selector: str, **kwargs):
    """Log a selector-related event."""
    logger = logging.getLogger("xcontentbot.selectors")
    logger.info(
        f"Selector event: {event}",
        extra={"extra_fields": {"selector": selector, "event": event, **kwargs}}
    )


def log_api_event(event: str, endpoint: str, **kwargs):
    """Log an API-related event."""
    logger = logging.getLogger("xcontentbot.api")
    logger.info(
        f"API event: {event}",
        extra={"extra_fields": {"endpoint": endpoint, "event": event, **kwargs}}
    )


def measure_time(func_name: str):
    """Decorator to measure function execution time."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            from .manager import observability
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                observability.metrics_collector.record_timer(f"function.{func_name}", duration)
                return result
            except Exception:
                duration = time.time() - start_time
                observability.metrics_collector.record_timer(f"function.{func_name}.error", duration)
                raise

        def sync_wrapper(*args, **kwargs):
            from .manager import observability
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                observability.metrics_collector.record_timer(f"function.{func_name}", duration)
                return result
            except Exception:
                duration = time.time() - start_time
                observability.metrics_collector.record_timer(f"function.{func_name}.error", duration)
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
