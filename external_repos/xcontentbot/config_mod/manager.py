"""Configuration manager."""
import os
import yaml
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .dataclasses import (
    ConfigSource,
    LLMProviderConfig,
    RetryConfig,
    CircuitBreakerConfig,
    RateLimitConfig,
    PlaywrightConfig,
    LoggingConfig,
    ObservabilityConfig,
    AppConfig,
)

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages application configuration from multiple sources."""

    def __init__(self, config_file: str = "bot_config.yaml"):
        self.config_file = Path(config_file)
        self._config_lock = threading.RLock()
        self._config: Dict[str, Any] = {}
        self._config_sources: Dict[str, ConfigSource] = {}
        self._watchers: List[callable] = []

        self._load_defaults()

        if self.config_file.exists():
            self._load_from_file()

        self._load_from_env()
        self._validate_config()

    def _load_defaults(self):
        """Load default configuration."""
        with self._config_lock:
            self._config = {
                "app": AppConfig(),
                "llm": {
                    "providers": {
                        "openai": LLMProviderConfig(
                            name="openai",
                            model="gpt-4o-mini",
                            api_key_env="OPENAI_API_KEY"
                        ),
                        "anthropic": LLMProviderConfig(
                            name="anthropic",
                            model="claude-3-haiku-20240307",
                            api_key_env="ANTHROPIC_API_KEY"
                        )
                    },
                    "default_provider": "openai",
                    "refine_enabled": False,
                    "system_prompt": "Refine to warm, professional, under 280 chars. Avoid hard-sell."
                },
                "retry": RetryConfig(),
                "circuit_breaker": CircuitBreakerConfig(),
                "rate_limit": RateLimitConfig(),
                "playwright": PlaywrightConfig(),
                "logging": LoggingConfig(),
                "observability": ObservabilityConfig()
            }

            for key in self._config.keys():
                self._config_sources[key] = ConfigSource.DEFAULT

    def _load_from_file(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r') as f:
                file_config = yaml.safe_load(f) or {}

            with self._config_lock:
                self._deep_merge(self._config, file_config)

                for key in file_config.keys():
                    self._config_sources[key] = ConfigSource.FILE

            logger.info(f"Loaded configuration from {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to load configuration from {self.config_file}: {e}")

    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "QUERIES": ("app.queries", lambda x: [q.strip() for q in x.split(",") if q.strip()]),
            "LIMIT": ("app.limit", int),
            "MAX_POSTS_TO_PROCESS": ("app.max_posts_to_process", int),
            "AUTO_POST": ("app.auto_post", lambda x: x.lower() == "true"),
            "MCP_SERVER_URL": ("app.mcp_server_url", str),
            "MAX_CONCURRENT_POSTS": ("app.max_concurrent_posts", int),
            "LLM_PROVIDER": ("llm.default_provider", str),
            "LLM_MODEL": ("llm.providers.openai.model", str),
            "LLM_TEMPERATURE": ("llm.providers.openai.temperature", float),
            "LLM_MAX_TOKENS": ("llm.providers.openai.max_tokens", int),
            "LLM_REFINE": ("llm.refine_enabled", lambda x: x.lower() == "true"),
            "MAX_RETRIES": ("retry.max_retries", int),
            "BASE_DELAY": ("retry.base_delay", float),
            "MAX_DELAY": ("retry.max_delay", float),
            "EXPONENTIAL_BASE": ("retry.exponential_base", float),
            "RETRY_JITTER": ("retry.jitter", float),
            "RATE_LIMIT_PER_HOUR": ("rate_limit.posts_per_hour", int),
            "RATE_LIMIT_PER_DAY": ("rate_limit.posts_per_day", int),
            "HEADLESS": ("playwright.headless", lambda x: x.lower() == "true"),
            "PLAYWRIGHT_TIMEOUT": ("playwright.timeout", float),
            "PLAYWRIGHT_SLOW_MO": ("playwright.slow_mo", int),
            "LOG_LEVEL": ("logging.level", str),
            "LOG_FILE": ("logging.file_path", str),
            "ENABLE_METRICS": ("observability.enable_metrics", lambda x: x.lower() == "true"),
            "ENABLE_HEALTH_CHECKS": ("observability.enable_health_checks", lambda x: x.lower() == "true"),
        }

        with self._config_lock:
            for env_var, (config_path, converter) in env_mappings.items():
                value = os.getenv(env_var)
                if value is not None:
                    try:
                        converted_value = converter(value)
                        self._set_nested_config(config_path, converted_value)
                        self._config_sources[config_path.split('.')[0]] = ConfigSource.ENV
                    except Exception as e:
                        logger.warning(f"Failed to convert environment variable {env_var}={value}: {e}")

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _set_nested_config(self, path: str, value: Any):
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _get_nested_config(self, path: str, default: Any = None) -> Any:
        """Get a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def _validate_config(self):
        """Validate configuration values."""
        with self._config_lock:
            app_config = self._config.get("app", {})
            if not isinstance(app_config.get("queries"), list) or not app_config["queries"]:
                logger.warning("No queries configured, using defaults")
                self._config["app"]["queries"] = ["burnout", "employee well-being", "productivity"]

            llm_config = self._config.get("llm", {})
            default_provider = llm_config.get("default_provider", "openai")
            providers = llm_config.get("providers", {})

            if default_provider not in providers:
                logger.warning(f"Default LLM provider '{default_provider}' not found, using first available")
                if providers:
                    self._config["llm"]["default_provider"] = list(providers.keys())[0]
                else:
                    logger.error("No LLM providers configured!")

            numeric_validations = [
                ("app.limit", 1, 100),
                ("app.max_posts_to_process", 1, 50),
                ("retry.max_retries", 0, 10),
                ("rate_limit.posts_per_hour", 1, 1000),
            ]

            for path, min_val, max_val in numeric_validations:
                value = self._get_nested_config(path)
                if value is not None and not (min_val <= value <= max_val):
                    logger.warning(f"Configuration {path}={value} is outside valid range [{min_val}, {max_val}]")

    def get(self, path: str, default: Any = None) -> Any:
        """Get a configuration value by path."""
        with self._config_lock:
            return self._get_nested_config(path, default)

    def set(self, path: str, value: Any, source: ConfigSource = ConfigSource.RUNTIME):
        """Set a configuration value by path."""
        with self._config_lock:
            self._set_nested_config(path, value)
            self._config_sources[path.split('.')[0]] = source

            for watcher in self._watchers:
                try:
                    watcher(path, value, source)
                except Exception as e:
                    logger.error(f"Error in config watcher: {e}")

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        with self._config_lock:
            return self._config.get(section, {}).copy()

    def get_llm_provider(self, provider_name: str = None) -> LLMProviderConfig:
        """Get LLM provider configuration."""
        if provider_name is None:
            provider_name = self.get("llm.default_provider", "openai")

        providers = self.get("llm.providers", {})
        provider_config = providers.get(provider_name)

        if not provider_config:
            raise ValueError(f"LLM provider '{provider_name}' not found")

        if isinstance(provider_config, dict):
            return LLMProviderConfig(**provider_config)

        return provider_config

    def get_available_llm_providers(self) -> List[str]:
        """Get list of available LLM providers."""
        return list(self.get("llm.providers", {}).keys())

    def add_watcher(self, watcher: callable):
        """Add a configuration change watcher."""
        self._watchers.append(watcher)

    def remove_watcher(self, watcher: callable):
        """Remove a configuration change watcher."""
        if watcher in self._watchers:
            self._watchers.remove(watcher)

    def save_to_file(self, filepath: str = None):
        """Save current configuration to file."""
        if filepath is None:
            filepath = self.config_file

        with self._config_lock:
            clean_config = {}
            for section, config in self._config.items():
                if self._config_sources.get(section) != ConfigSource.RUNTIME:
                    clean_config[section] = config

            with open(filepath, 'w') as f:
                yaml.dump(clean_config, f, default_flow_style=False, indent=2)

            logger.info(f"Configuration saved to {filepath}")

    def reload(self):
        """Reload configuration from file and environment."""
        logger.info("Reloading configuration...")

        self._load_defaults()

        if self.config_file.exists():
            self._load_from_file()

        self._load_from_env()
        self._validate_config()

        logger.info("Configuration reloaded")

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        with self._config_lock:
            return {
                "sources": dict(self._config_sources),
                "config": self._config.copy(),
                "timestamp": datetime.utcnow().isoformat()
            }
