"""Configuration management - Main Entry Point."""
from config_mod import (
    ConfigSource,
    LLMProviderConfig,
    RetryConfig,
    CircuitBreakerConfig,
    RateLimitConfig,
    PlaywrightConfig,
    LoggingConfig,
    ObservabilityConfig,
    AppConfig,
    ConfigurationManager,
)
from typing import Any, List

# Global configuration manager instance
config_manager = ConfigurationManager()


# Convenience functions
def get_config(path: str, default: Any = None) -> Any:
    """Get a configuration value."""
    return config_manager.get(path, default)


def set_config(path: str, value: Any):
    """Set a configuration value."""
    config_manager.set(path, value)


def get_llm_provider(provider_name: str = None) -> LLMProviderConfig:
    """Get LLM provider configuration."""
    return config_manager.get_llm_provider(provider_name)


def get_available_llm_providers() -> List[str]:
    """Get available LLM providers."""
    return config_manager.get_available_llm_providers()


__all__ = [
    'ConfigSource',
    'LLMProviderConfig',
    'RetryConfig',
    'CircuitBreakerConfig',
    'RateLimitConfig',
    'PlaywrightConfig',
    'LoggingConfig',
    'ObservabilityConfig',
    'AppConfig',
    'ConfigurationManager',
    'config_manager',
    'get_config',
    'set_config',
    'get_llm_provider',
    'get_available_llm_providers',
]
