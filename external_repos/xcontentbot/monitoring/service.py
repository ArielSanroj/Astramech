"""Monitoring service implementation."""
import os
import time
import asyncio
import logging
import threading
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
from typing import Dict, Any, List

from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .health_status import HealthStatus, HealthCheck
from .health_checks import (
    check_system_health, check_application_health, check_circuit_breaker_health,
    check_throttle_health, check_llm_provider_health, check_configuration_health,
    determine_overall_status
)
from .diagnostics import (
    get_system_diagnostics, get_application_diagnostics,
    get_network_diagnostics, get_dependency_diagnostics
)
from .dashboard import generate_dashboard_html

logger = logging.getLogger(__name__)


class MonitoringService:
    """Main monitoring service."""

    def __init__(self, port: int = 8080):
        self.port = port
        self.app = FastAPI(title="xcontentbot Monitoring", version="1.0.0")
        self.health_checks: List[HealthCheck] = []
        self.start_time = time.time()

        # Import dependencies lazily
        self._observability = None
        self._circuit_manager = None
        self._throttle_manager = None
        self._llm_orchestrator = None
        self._config_manager = None

        self._setup_routes()
        self._setup_middleware()
        self._start_background_tasks()

    def _load_dependencies(self):
        """Load dependencies lazily."""
        if self._observability is None:
            from observability import observability
            from circuit_breaker import circuit_manager
            from throttling import throttle_manager
            from llm_orchestrator import llm_orchestrator
            from config_manager import config_manager

            self._observability = observability
            self._circuit_manager = circuit_manager
            self._throttle_manager = throttle_manager
            self._llm_orchestrator = llm_orchestrator
            self._config_manager = config_manager

    def _setup_middleware(self):
        """Setup CORS and other middleware."""
        allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup monitoring endpoints."""

        @self.app.get("/")
        async def root():
            return {
                "service": "xcontentbot",
                "version": "1.0.0",
                "status": "running",
                "uptime": time.time() - self.start_time,
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics",
                    "status": "/status",
                    "config": "/config",
                    "logs": "/logs",
                    "diagnostics": "/diagnostics"
                }
            }

        @self.app.get("/health")
        async def health():
            health_data = await self._run_health_checks()
            overall_status = determine_overall_status(health_data)

            status_code = 200
            if overall_status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                status_code = 503

            return JSONResponse(
                content={
                    "status": overall_status.value,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "checks": [asdict(check) for check in health_data],
                    "summary": self._get_health_summary(health_data)
                },
                status_code=status_code
            )

        @self.app.get("/metrics")
        async def metrics():
            self._load_dependencies()
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "system": self._observability.system_metrics.get_system_metrics(),
                "application": self._observability.metrics_collector.get_metrics_summary(),
                "circuit_breakers": self._circuit_manager.get_all_metrics(),
                "throttles": self._throttle_manager.get_all_throttle_status(),
                "llm_providers": self._llm_orchestrator.get_health_status()
            }

        @self.app.get("/status")
        async def status():
            self._load_dependencies()
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "uptime": time.time() - self.start_time,
                "health": await self._run_health_checks(),
                "metrics": self._observability.metrics_collector.get_metrics_summary(),
                "configuration": self._config_manager.get_config_summary()
            }

        @self.app.get("/config")
        async def config():
            self._load_dependencies()
            return self._config_manager.get_config_summary()

        @self.app.get("/logs")
        async def logs(limit: int = 100, level: str = None):
            self._load_dependencies()
            log_file = self._observability.logging.file_path
            if not Path(log_file).exists():
                return {"error": "Log file not found"}

            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()

                if level:
                    lines = [line for line in lines if f'"level":"{level.upper()}"' in line]

                recent_lines = lines[-limit:] if limit > 0 else lines

                return {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "log_file": log_file,
                    "lines": len(recent_lines),
                    "logs": recent_lines
                }
            except Exception as e:
                return {"error": f"Failed to read logs: {e}"}

        @self.app.get("/diagnostics")
        async def diagnostics():
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "system": get_system_diagnostics(),
                "application": get_application_diagnostics(self.start_time),
                "network": await get_network_diagnostics(self.port),
                "dependencies": get_dependency_diagnostics()
            }

        @self.app.post("/health/reset")
        async def reset_health():
            self._load_dependencies()
            self._circuit_manager.reset_all()
            self._throttle_manager.reset_all_throttles()
            self._llm_orchestrator.reset_provider_health()

            return {"message": "Health status reset", "timestamp": datetime.utcnow().isoformat() + "Z"}

        @self.app.get("/dashboard")
        async def dashboard():
            return HTMLResponse(content=generate_dashboard_html())

    async def _run_health_checks(self) -> List[HealthCheck]:
        """Run all health checks."""
        self._load_dependencies()
        checks = []

        checks.append(await check_system_health(self._observability))
        checks.append(await check_application_health(self._observability))
        checks.append(await check_circuit_breaker_health(self._circuit_manager))
        checks.append(await check_throttle_health(self._throttle_manager))
        checks.append(await check_llm_provider_health(self._llm_orchestrator))
        checks.append(await check_configuration_health(self._config_manager))

        return checks

    def _get_health_summary(self, checks: List[HealthCheck]) -> Dict[str, Any]:
        """Get health summary statistics."""
        status_counts = {}
        for check in checks:
            status = check.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_checks": len(checks),
            "status_counts": status_counts,
            "overall_status": determine_overall_status(checks).value
        }

    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        def health_monitor():
            while True:
                try:
                    asyncio.run(self._run_health_checks())
                    time.sleep(60)
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=health_monitor, daemon=True)
        thread.start()

    def start(self):
        """Start the monitoring service."""
        logger.info(f"Starting monitoring service on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")


# Global monitoring service instance
monitoring_service = MonitoringService()


def start_monitoring(port: int = 8080):
    """Start the monitoring service."""
    global monitoring_service
    monitoring_service = MonitoringService(port)
    monitoring_service.start()
