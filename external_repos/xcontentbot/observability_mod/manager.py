"""Observability manager."""
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dataclasses import asdict
import json

from .logging import SensitiveDataFilter, StructuredFormatter
from .metrics import MetricsCollector, PostMetrics, SessionMetrics, SystemMetrics


class ObservabilityManager:
    """Main observability manager."""

    def __init__(self, log_file: str = "logs/xcontentbot.log"):
        self.metrics_collector = MetricsCollector()
        self.session_metrics = SessionMetrics()
        self.system_metrics = SystemMetrics()
        self.post_metrics: Dict[str, PostMetrics] = {}
        self.logging = type('obj', (object,), {'file_path': log_file})()

        self._setup_logging(log_file)
        self._start_background_tasks()

    def _setup_logging(self, log_file: str):
        """Setup structured logging."""
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter())
        file_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        console_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(console_handler)

        logging.getLogger("xcontentbot").setLevel(logging.DEBUG)
        logging.getLogger("playwright").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        def metrics_collector():
            while True:
                try:
                    system_metrics = self.system_metrics.get_system_metrics()
                    for key, value in system_metrics.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                self.metrics_collector.set_gauge(
                                    f"system.{key}.{sub_key}",
                                    sub_value
                                )
                        else:
                            self.metrics_collector.set_gauge(f"system.{key}", value)

                    time.sleep(30)
                except Exception as e:
                    logging.error(f"Error in metrics collection: {e}")
                    time.sleep(30)

        thread = threading.Thread(target=metrics_collector, daemon=True)
        thread.start()

    def start_post_processing(self, post_id: str, query: str) -> PostMetrics:
        """Start tracking a post processing."""
        metrics = PostMetrics(
            post_id=post_id,
            query=query,
            start_time=time.time()
        )
        self.post_metrics[post_id] = metrics
        self.metrics_collector.increment_counter("posts.started", tags={"query": query})
        return metrics

    def end_post_processing(self, post_id: str, status: str, error_message: str = None):
        """End tracking a post processing."""
        if post_id in self.post_metrics:
            metrics = self.post_metrics[post_id]
            metrics.end_time = time.time()
            metrics.status = status
            metrics.error_message = error_message

            self.metrics_collector.record_timer(
                "post.processing_duration",
                metrics.duration or 0,
                tags={"query": metrics.query, "status": status}
            )

            self.metrics_collector.increment_counter(
                f"posts.{status}",
                tags={"query": metrics.query}
            )

            logger = logging.getLogger("xcontentbot.posts")
            logger.info(
                f"Post processing completed",
                extra={
                    "extra_fields": {
                        "post_id": post_id,
                        "query": metrics.query,
                        "status": status,
                        "duration": metrics.duration,
                        "retry_count": metrics.retry_count,
                        "selector_failures": metrics.selector_failures,
                        "api_calls": metrics.api_calls,
                        "api_failures": metrics.api_failures
                    }
                }
            )

    def record_selector_failure(self, post_id: str, selector: str, error: str):
        """Record a selector failure."""
        if post_id in self.post_metrics:
            self.post_metrics[post_id].selector_failures += 1

        self.metrics_collector.increment_counter("selectors.failures", tags={"selector": selector})

        logger = logging.getLogger("xcontentbot.selectors")
        logger.warning(
            f"Selector failure: {selector}",
            extra={
                "extra_fields": {
                    "post_id": post_id,
                    "selector": selector,
                    "error": error
                }
            }
        )

    def record_api_call(self, post_id: str, endpoint: str, success: bool, duration: float = None):
        """Record an API call."""
        if post_id in self.post_metrics:
            self.post_metrics[post_id].api_calls += 1
            if not success:
                self.post_metrics[post_id].api_failures += 1

        status = "success" if success else "failure"
        self.metrics_collector.increment_counter(
            f"api.calls.{status}",
            tags={"endpoint": endpoint}
        )

        if duration:
            self.metrics_collector.record_timer(
                "api.call_duration",
                duration,
                tags={"endpoint": endpoint, "status": status}
            )

    def record_login_attempt(self, success: bool, duration: float = None):
        """Record a login attempt."""
        self.session_metrics.record_login_attempt(success)

        status = "success" if success else "failure"
        self.metrics_collector.increment_counter(f"login.{status}")

        if duration:
            self.metrics_collector.record_timer("login.duration", duration)

        logger = logging.getLogger("xcontentbot.auth")
        logger.info(
            f"Login attempt: {status}",
            extra={
                "extra_fields": {
                    "success": success,
                    "duration": duration,
                    "success_rate": self.session_metrics.get_success_rate()
                }
            }
        )

    def record_redirect(self, from_url: str, to_url: str):
        """Record a redirect."""
        self.session_metrics.redirect_count += 1
        self.metrics_collector.increment_counter("redirects.total")

        logger = logging.getLogger("xcontentbot.navigation")
        logger.info(
            f"Redirect detected",
            extra={
                "extra_fields": {
                    "from_url": from_url,
                    "to_url": to_url,
                    "redirect_count": self.session_metrics.redirect_count
                }
            }
        )

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        metrics_summary = self.metrics_collector.get_metrics_summary()

        total_posts = metrics_summary["counters"].get("posts.started", 0)
        successful_posts = metrics_summary["counters"].get("posts.success", 0)
        failed_posts = metrics_summary["counters"].get("posts.error", 0)

        success_rate = successful_posts / max(total_posts, 1)
        failure_rate = failed_posts / max(total_posts, 1)

        login_success_rate = self.session_metrics.get_success_rate()

        if success_rate >= 0.8 and login_success_rate >= 0.9:
            health_status = "healthy"
        elif success_rate >= 0.6 and login_success_rate >= 0.7:
            health_status = "degraded"
        else:
            health_status = "unhealthy"

        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "posts": {
                    "total": total_posts,
                    "successful": successful_posts,
                    "failed": failed_posts,
                    "success_rate": success_rate,
                    "failure_rate": failure_rate
                },
                "login": {
                    "attempts": self.session_metrics.login_attempts,
                    "successes": self.session_metrics.login_successes,
                    "failures": self.session_metrics.login_failures,
                    "success_rate": login_success_rate
                },
                "system": self.system_metrics.get_system_metrics()
            },
            "circuit_breakers": self.get_circuit_breaker_status()
        }

    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status (if available)."""
        try:
            from circuit_breaker import circuit_manager
            return circuit_manager.get_all_metrics()
        except ImportError:
            return {}

    def export_metrics(self, filepath: str = None) -> str:
        """Export metrics to JSON file."""
        if not filepath:
            filepath = f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": self.metrics_collector.get_metrics_summary(),
            "session": asdict(self.session_metrics),
            "system": self.system_metrics.get_system_metrics(),
            "health": self.get_health_status()
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        return filepath
