#!/usr/bin/env python3
"""
LLM orchestrator for managing multiple providers with fallback.
"""

import time
import logging
from typing import Dict, Any, Optional, List

import httpx

from config_manager import (
    get_llm_provider,
    get_available_llm_providers,
    get_config
)
from .providers import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    MockProvider,
)

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """Orchestrates multiple LLM providers with fallback and load balancing."""

    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []
        self.provider_health: Dict[str, bool] = {}
        self.provider_metrics: Dict[str, Dict[str, Any]] = {}
        self._load_providers()

    def _load_providers(self):
        """Load all configured LLM providers."""
        available_providers = get_available_llm_providers()

        for provider_name in available_providers:
            self._load_single_provider(provider_name)

        self._set_primary_provider()
        self._set_fallback_providers()

    def _load_single_provider(self, provider_name: str):
        """Load a single provider by name."""
        try:
            config = get_llm_provider(provider_name)
            provider = self._create_provider(provider_name, config)
            if provider:
                self._register_provider(provider_name, provider)
        except Exception as e:
            logger.error(f"Failed to load provider {provider_name}: {e}")

    def _create_provider(self, name: str, config) -> Optional[LLMProvider]:
        """Create provider instance based on name."""
        provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "mock": MockProvider,
        }
        provider_class = provider_map.get(name)
        if provider_class:
            return provider_class(config)
        logger.warning(f"Unknown provider type: {name}")
        return None

    def _register_provider(self, name: str, provider: LLMProvider):
        """Register a provider and initialize its metrics."""
        self.providers[name] = provider
        self.provider_health[name] = True
        self.provider_metrics[name] = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "average_response_time": 0.0,
            "last_call_time": None
        }
        logger.info(f"Loaded LLM provider: {name}")

    def _set_primary_provider(self):
        """Set the primary provider from config or first available."""
        self.primary_provider = get_config("llm.default_provider")
        if self.primary_provider not in self.providers:
            if self.providers:
                self.primary_provider = list(self.providers.keys())[0]
                logger.warning(
                    f"Primary provider not available, using {self.primary_provider}"
                )
            else:
                logger.error("No LLM providers available!")

    def _set_fallback_providers(self):
        """Set fallback providers."""
        self.fallback_providers = [
            name for name in self.providers.keys()
            if name != self.primary_provider
        ]

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        provider: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> str:
        """Generate text using the specified or best available provider."""
        providers_to_try = self._get_providers_to_try(provider)
        last_error = None

        for provider_name in providers_to_try:
            result = await self._try_provider(
                provider_name, prompt, system_prompt,
                temperature, max_tokens, **kwargs
            )
            if result is not None:
                return result
            last_error = self._get_last_error(provider_name)

        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    def _get_providers_to_try(self, provider: str = None) -> List[str]:
        """Get list of providers to try in order."""
        if provider:
            return [provider]
        return [self.primary_provider] + self.fallback_providers

    async def _try_provider(
        self,
        provider_name: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> Optional[str]:
        """Try generating text with a specific provider."""
        if provider_name not in self.providers:
            return None
        if not self.provider_health.get(provider_name, True):
            logger.debug(f"Skipping unhealthy provider: {provider_name}")
            return None

        try:
            return await self._generate_with_provider(
                provider_name, prompt, system_prompt,
                temperature, max_tokens, **kwargs
            )
        except Exception as e:
            self._handle_provider_error(provider_name, e)
            return None

    async def _generate_with_provider(
        self,
        provider_name: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Execute text generation with a provider."""
        start_time = time.time()
        provider_instance = self.providers[provider_name]

        provider_kwargs = kwargs.copy()
        if temperature is not None:
            provider_kwargs['temperature'] = temperature
        if max_tokens is not None:
            provider_kwargs['max_tokens'] = max_tokens

        result = await provider_instance.generate_text(
            prompt, system_prompt, **provider_kwargs
        )

        duration = time.time() - start_time
        self._update_provider_metrics(provider_name, True, duration, len(result))
        logger.debug(f"Generated text using {provider_name}: {result[:100]}...")
        return result

    def _handle_provider_error(self, provider_name: str, error: Exception):
        """Handle provider error and update health status."""
        self._update_provider_metrics(provider_name, False, 0, 0)
        logger.warning(f"Provider {provider_name} failed: {error}")

        if isinstance(error, (httpx.HTTPStatusError, httpx.TimeoutException)):
            self.provider_health[provider_name] = False
            logger.warning(f"Marked provider {provider_name} as unhealthy")

    def _get_last_error(self, provider_name: str) -> str:
        """Get last error message for a provider."""
        return f"Provider {provider_name} failed"

    def _update_provider_metrics(
        self,
        provider_name: str,
        success: bool,
        duration: float,
        tokens: int
    ):
        """Update provider metrics."""
        metrics = self.provider_metrics[provider_name]
        metrics["total_calls"] += 1
        metrics["last_call_time"] = time.time()

        if success:
            metrics["successful_calls"] += 1
            metrics["total_tokens"] += tokens
            self._update_avg_response_time(metrics, duration)
        else:
            metrics["failed_calls"] += 1

    def _update_avg_response_time(self, metrics: Dict, duration: float):
        """Update average response time with exponential moving average."""
        if metrics["average_response_time"] == 0:
            metrics["average_response_time"] = duration
        else:
            metrics["average_response_time"] = (
                metrics["average_response_time"] * 0.9 + duration * 0.1
            )

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers."""
        health_results = {}
        for provider_name, provider in self.providers.items():
            health_results[provider_name] = await self._check_provider_health(
                provider_name, provider
            )
        return health_results

    async def _check_provider_health(
        self,
        provider_name: str,
        provider: LLMProvider
    ) -> bool:
        """Check health of a single provider."""
        try:
            is_healthy = await provider.health_check()
            self.provider_health[provider_name] = is_healthy
            if is_healthy:
                logger.debug(f"Provider {provider_name} is healthy")
            else:
                logger.warning(f"Provider {provider_name} is unhealthy")
            return is_healthy
        except Exception as e:
            logger.error(f"Health check failed for {provider_name}: {e}")
            self.provider_health[provider_name] = False
            return False

    def get_provider_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all providers."""
        return self.provider_metrics.copy()

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        healthy = sum(1 for h in self.provider_health.values() if h)
        total = len(self.providers)

        return {
            "total_providers": total,
            "healthy_providers": healthy,
            "unhealthy_providers": total - healthy,
            "primary_provider": self.primary_provider,
            "fallback_providers": self.fallback_providers,
            "provider_health": self.provider_health.copy(),
            "provider_metrics": self.get_provider_metrics()
        }

    def reset_provider_health(self, provider_name: str = None):
        """Reset provider health status."""
        if provider_name:
            self.provider_health[provider_name] = True
            logger.info(f"Reset health status for provider {provider_name}")
        else:
            for name in self.provider_health:
                self.provider_health[name] = True
            logger.info("Reset health status for all providers")
