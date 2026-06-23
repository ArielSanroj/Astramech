"""Health check implementations."""
import logging
from typing import List

from .health_status import HealthStatus, HealthCheck

logger = logging.getLogger(__name__)


async def check_system_health(observability) -> HealthCheck:
    """Check system health (memory, CPU)."""
    try:
        system_metrics = observability.system_metrics.get_system_metrics()

        memory_percent = system_metrics.get("memory", {}).get("percent", 0)
        if memory_percent > 90:
            return HealthCheck(
                "system", HealthStatus.CRITICAL,
                f"High memory usage: {memory_percent:.1f}%",
                {"memory_percent": memory_percent}
            )
        elif memory_percent > 80:
            return HealthCheck(
                "system", HealthStatus.DEGRADED,
                f"Elevated memory usage: {memory_percent:.1f}%",
                {"memory_percent": memory_percent}
            )

        cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
        if cpu_percent > 95:
            return HealthCheck(
                "system", HealthStatus.CRITICAL,
                f"High CPU usage: {cpu_percent:.1f}%",
                {"cpu_percent": cpu_percent}
            )

        return HealthCheck(
            "system", HealthStatus.HEALTHY,
            "System resources normal",
            system_metrics
        )

    except Exception as e:
        return HealthCheck(
            "system", HealthStatus.UNHEALTHY,
            f"System health check failed: {e}",
            {"error": str(e)}
        )


async def check_application_health(observability) -> HealthCheck:
    """Check application health."""
    try:
        health_data = observability.get_health_status()
        status = health_data.get("status", "unknown")

        if status == "healthy":
            return HealthCheck(
                "application", HealthStatus.HEALTHY,
                "Application running normally",
                health_data
            )
        elif status == "degraded":
            return HealthCheck(
                "application", HealthStatus.DEGRADED,
                "Application performance degraded",
                health_data
            )
        else:
            return HealthCheck(
                "application", HealthStatus.UNHEALTHY,
                f"Application status: {status}",
                health_data
            )

    except Exception as e:
        return HealthCheck(
            "application", HealthStatus.UNHEALTHY,
            f"Application health check failed: {e}",
            {"error": str(e)}
        )


async def check_circuit_breaker_health(circuit_manager) -> HealthCheck:
    """Check circuit breaker health."""
    try:
        circuit_metrics = circuit_manager.get_all_metrics()

        open_circuits = 0
        total_circuits = len(circuit_metrics)

        for name, metrics in circuit_metrics.items():
            if metrics.get("state") == "open":
                open_circuits += 1

        if open_circuits == total_circuits and total_circuits > 0:
            return HealthCheck(
                "circuit_breakers", HealthStatus.CRITICAL,
                f"All {total_circuits} circuit breakers are open",
                {"open_circuits": open_circuits, "total_circuits": total_circuits}
            )
        elif open_circuits > 0:
            return HealthCheck(
                "circuit_breakers", HealthStatus.DEGRADED,
                f"{open_circuits}/{total_circuits} circuit breakers are open",
                {"open_circuits": open_circuits, "total_circuits": total_circuits}
            )
        else:
            return HealthCheck(
                "circuit_breakers", HealthStatus.HEALTHY,
                "All circuit breakers closed",
                {"open_circuits": open_circuits, "total_circuits": total_circuits}
            )

    except Exception as e:
        return HealthCheck(
            "circuit_breakers", HealthStatus.UNHEALTHY,
            f"Circuit breaker health check failed: {e}",
            {"error": str(e)}
        )


async def check_throttle_health(throttle_manager) -> HealthCheck:
    """Check throttle health."""
    try:
        throttle_status = throttle_manager.get_all_throttle_status()

        throttled_count = 0
        total_throttles = len(throttle_status)

        for throttle_name, status in throttle_status.items():
            if status.get("enabled", True):
                remaining = status.get("remaining_requests", 0)
                if remaining == 0:
                    throttled_count += 1

        if throttled_count == total_throttles and total_throttles > 0:
            return HealthCheck(
                "throttles", HealthStatus.DEGRADED,
                f"All {total_throttles} throttles are at limit",
                {"throttled_count": throttled_count, "total_throttles": total_throttles}
            )
        elif throttled_count > 0:
            return HealthCheck(
                "throttles", HealthStatus.HEALTHY,
                f"{throttled_count}/{total_throttles} throttles at limit",
                {"throttled_count": throttled_count, "total_throttles": total_throttles}
            )
        else:
            return HealthCheck(
                "throttles", HealthStatus.HEALTHY,
                "All throttles have capacity",
                {"throttled_count": throttled_count, "total_throttles": total_throttles}
            )

    except Exception as e:
        return HealthCheck(
            "throttles", HealthStatus.UNHEALTHY,
            f"Throttle health check failed: {e}",
            {"error": str(e)}
        )


async def check_llm_provider_health(llm_orchestrator) -> HealthCheck:
    """Check LLM provider health."""
    try:
        llm_status = llm_orchestrator.get_health_status()

        healthy_providers = llm_status.get("healthy_providers", 0)
        total_providers = llm_status.get("total_providers", 0)

        if healthy_providers == 0 and total_providers > 0:
            return HealthCheck(
                "llm_providers", HealthStatus.CRITICAL,
                "No LLM providers are healthy",
                llm_status
            )
        elif healthy_providers < total_providers:
            return HealthCheck(
                "llm_providers", HealthStatus.DEGRADED,
                f"{healthy_providers}/{total_providers} LLM providers healthy",
                llm_status
            )
        else:
            return HealthCheck(
                "llm_providers", HealthStatus.HEALTHY,
                f"All {total_providers} LLM providers healthy",
                llm_status
            )

    except Exception as e:
        return HealthCheck(
            "llm_providers", HealthStatus.UNHEALTHY,
            f"LLM provider health check failed: {e}",
            {"error": str(e)}
        )


async def check_configuration_health(config_manager) -> HealthCheck:
    """Check configuration health."""
    try:
        config_summary = config_manager.get_config_summary()

        required_configs = ["app.queries", "llm.default_provider"]
        missing_configs = []

        for config_path in required_configs:
            if not config_manager.get(config_path):
                missing_configs.append(config_path)

        if missing_configs:
            return HealthCheck(
                "configuration", HealthStatus.UNHEALTHY,
                f"Missing required configurations: {missing_configs}",
                {"missing_configs": missing_configs}
            )
        else:
            return HealthCheck(
                "configuration", HealthStatus.HEALTHY,
                "Configuration is valid",
                {"total_configs": len(config_summary.get("config", {}))}
            )

    except Exception as e:
        return HealthCheck(
            "configuration", HealthStatus.UNHEALTHY,
            f"Configuration health check failed: {e}",
            {"error": str(e)}
        )


def determine_overall_status(checks: List[HealthCheck]) -> HealthStatus:
    """Determine overall health status from individual checks."""
    if not checks:
        return HealthStatus.UNHEALTHY

    statuses = [check.status for check in checks]

    if HealthStatus.CRITICAL in statuses:
        return HealthStatus.CRITICAL
    elif HealthStatus.UNHEALTHY in statuses:
        return HealthStatus.UNHEALTHY
    elif HealthStatus.DEGRADED in statuses:
        return HealthStatus.DEGRADED
    else:
        return HealthStatus.HEALTHY
