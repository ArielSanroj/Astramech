"""Monitoring and health check system for xcontentbot - Main Entry Point."""
from monitoring import (
    HealthStatus,
    HealthCheck,
    MonitoringService,
    start_monitoring,
)
from monitoring.service import monitoring_service

__all__ = [
    'HealthStatus',
    'HealthCheck',
    'MonitoringService',
    'monitoring_service',
    'start_monitoring',
]

if __name__ == "__main__":
    start_monitoring()
