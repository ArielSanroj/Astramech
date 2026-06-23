"""Configuration dataclasses."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List


class ConfigSource(Enum):
    """Configuration source types."""
    ENV = "environment"
    FILE = "file"
    RUNTIME = "runtime"
    DEFAULT = "default"


@dataclass
class LLMProviderConfig:
    """Configuration for LLM providers."""
    name: str
    model: str
    api_key_env: str
    temperature: float = 0.4
    max_tokens: int = 120
    timeout: float = 30.0
    max_retries: int = 3
    base_url: Optional[str] = None
    extra_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: float = 0.1


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3
    timeout: float = 30.0


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    posts_per_hour: int = 6
    posts_per_day: int = 50
    api_calls_per_minute: int = 60
    burst_limit: int = 10


@dataclass
class PlaywrightConfig:
    """Playwright configuration."""
    headless: bool = True
    timeout: float = 30.0
    slow_mo: int = 0
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    block_resources: List[str] = None

    def __post_init__(self):
        if self.block_resources is None:
            self.block_resources = ["image", "stylesheet", "font", "media"]


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "structured"
    file_path: str = "logs/xcontentbot.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class ObservabilityConfig:
    """Observability configuration."""
    enable_metrics: bool = True
    enable_health_checks: bool = True
    metrics_export_interval: int = 300
    health_check_interval: int = 60
    export_path: str = "metrics"


@dataclass
class AppConfig:
    """Main application configuration."""
    queries: List[str] = None
    limit: int = 10
    max_posts_to_process: int = 3
    auto_post: bool = False
    mcp_server_url: str = "http://127.0.0.1:8000/mcp"
    mcp_timeout: float = 60.0
    max_concurrent_posts: int = 2
    enable_scheduler: bool = False
    run_on_startup: bool = False
    schedule_timezone: str = "Europe/Madrid"
    schedule_cron: str = "0 8 * * *"
    state_file: str = "bot_state.json"

    def __post_init__(self):
        if self.queries is None:
            self.queries = ["burnout", "employee well-being", "productivity"]
