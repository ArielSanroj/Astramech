#!/usr/bin/env python3
"""
LLM provider implementations for different AI services.
"""

import os
import asyncio
import logging
from abc import ABC, abstractmethod

from openai import AsyncOpenAI
import anthropic

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config):
        self.config = config
        self.name = config.name
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.timeout = config.timeout
        self.max_retries = config.max_retries

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        """Generate text using the LLM provider."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""

    def __init__(self, config):
        super().__init__(config)
        api_key = config.api_key_env and os.getenv(config.api_key_env)
        self.client = AsyncOpenAI(api_key=api_key, base_url=config.base_url)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API."""
        try:
            messages = self._build_messages(prompt, system_prompt)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _build_messages(self, prompt: str, system_prompt: str = None) -> list:
        """Build messages list for OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def health_check(self) -> bool:
        """Check OpenAI API health."""
        try:
            await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
                timeout=5.0
            )
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    def __init__(self, config):
        super().__init__(config)
        api_key = config.api_key_env and os.getenv(config.api_key_env)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        """Generate text using Anthropic API."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                timeout=self.timeout,
                **kwargs
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check Anthropic API health."""
        try:
            await self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}],
                timeout=5.0
            )
            return True
        except Exception as e:
            logger.warning(f"Anthropic health check failed: {e}")
            return False


class MockProvider(LLMProvider):
    """Mock provider for testing and development."""

    def __init__(self, config):
        super().__init__(config)
        self.responses = [
            "This is a mock response about burnout and productivity.",
            "Mock comment: Great insights on employee well-being!",
            "Mock response: I appreciate your perspective on this topic."
        ]
        self.response_index = 0

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        """Generate mock text."""
        await asyncio.sleep(0.1)
        response = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1
        logger.debug(f"Mock provider generated: {response}")
        return response

    async def health_check(self) -> bool:
        """Mock health check always returns True."""
        return True
