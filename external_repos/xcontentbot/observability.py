"""Structured logging and metrics collection - Main Entry Point."""
from observability_mod import (
    SensitiveDataFilter,
    StructuredFormatter,
    MetricsCollector,
    PostMetrics,
    SessionMetrics,
    SystemMetrics,
    ObservabilityManager,
    log_post_event,
    log_selector_event,
    log_api_event,
    measure_time,
)

# Global observability manager instance
observability = ObservabilityManager()

__all__ = [
    'SensitiveDataFilter',
    'StructuredFormatter',
    'MetricsCollector',
    'PostMetrics',
    'SessionMetrics',
    'SystemMetrics',
    'ObservabilityManager',
    'observability',
    'log_post_event',
    'log_selector_event',
    'log_api_event',
    'measure_time',
]
