"""Metrics collection classes."""
import time
import threading
import psutil
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict, deque


class MetricsCollector:
    """Collects and stores application metrics."""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        with self._lock:
            key = self._make_key(name, tags)
            self.counters[key] += value
            self.metrics[f"counter.{name}"].append({
                "timestamp": time.time(),
                "value": value,
                "tags": tags or {}
            })

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        with self._lock:
            key = self._make_key(name, tags)
            self.gauges[key] = value
            self.metrics[f"gauge.{name}"].append({
                "timestamp": time.time(),
                "value": value,
                "tags": tags or {}
            })

    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record a timing metric."""
        with self._lock:
            key = self._make_key(name, tags)
            self.timers[key].append(duration)
            if len(self.timers[key]) > self.max_history:
                self.timers[key] = self.timers[key][-self.max_history:]

            self.metrics[f"timer.{name}"].append({
                "timestamp": time.time(),
                "duration": duration,
                "tags": tags or {}
            })

    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Create a unique key for a metric with tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        with self._lock:
            summary = {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "timers": {}
            }

            for name, durations in self.timers.items():
                if durations:
                    summary["timers"][name] = {
                        "count": len(durations),
                        "min": min(durations),
                        "max": max(durations),
                        "avg": sum(durations) / len(durations),
                        "p95": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                        "p99": sorted(durations)[int(len(durations) * 0.99)] if durations else 0
                    }

            return summary


@dataclass
class PostMetrics:
    """Metrics for a single post processing."""
    post_id: str
    query: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "pending"
    error_message: Optional[str] = None
    retry_count: int = 0
    selector_failures: int = 0
    api_calls: int = 0
    api_failures: int = 0

    @property
    def duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return asdict(self)


class SessionMetrics:
    """Tracks session and login metrics."""

    def __init__(self):
        self.login_attempts = 0
        self.login_successes = 0
        self.login_failures = 0
        self.last_login_time = None
        self.session_duration = 0
        self.selector_validation_failures = 0
        self.redirect_count = 0
        self.captcha_encounters = 0

    def record_login_attempt(self, success: bool):
        """Record a login attempt."""
        self.login_attempts += 1
        if success:
            self.login_successes += 1
            self.last_login_time = time.time()
        else:
            self.login_failures += 1

    def get_success_rate(self) -> float:
        """Get login success rate."""
        if self.login_attempts == 0:
            return 0.0
        return self.login_successes / self.login_attempts


class SystemMetrics:
    """Collects system-level metrics."""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()

            return {
                "memory": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": self.process.memory_percent()
                },
                "cpu": {
                    "percent": cpu_percent,
                    "num_threads": self.process.num_threads()
                },
                "uptime": time.time() - self.start_time,
                "open_files": len(self.process.open_files()) if hasattr(self.process, 'open_files') else 0
            }
        except Exception as e:
            return {"error": str(e)}
