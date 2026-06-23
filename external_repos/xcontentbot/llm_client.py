"""LLM Client for text refinement with multiple provider support."""
import os
import importlib
import logging
from typing import Any, Dict, Optional

from openai import OpenAI

logger = logging.getLogger("x-mcp-client")


class LLMClient:
    """Client for LLM providers (OpenAI, Anthropic) with fallback support."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "openai")
        self.refine_enabled = config.get("refine", False)
        self.model = config.get("model", "gpt-4o-mini")
        self.system_prompt = config.get("system_prompt", "")
        self.max_tokens = int(config.get("max_tokens", 120))
        self.temperature = float(config.get("temperature", 0.4))
        self.clients: Dict[str, Any] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize LLM providers with fallback order."""
        if not self.refine_enabled:
            return

        ordered_providers = [self.provider]
        if self.provider == "openai":
            ordered_providers.append("anthropic")
        elif self.provider == "anthropic":
            ordered_providers.append("openai")

        for prov in ordered_providers:
            init_method = getattr(self, f"_init_{prov}", None)
            if init_method:
                try:
                    client = init_method()
                    if client:
                        self.clients[prov] = client
                except Exception as e:
                    logger.warning("Failed to initialize provider '%s': %s", prov, e)

    def _get_env_key(self, provider_name: str) -> Optional[str]:
        """Get API key from environment for a provider."""
        provider_cfg = self.config.get(provider_name, {})
        env_key = provider_cfg.get("api_key_env")
        if env_key:
            return os.getenv(env_key)
        return None

    def _init_openai(self) -> Optional[Any]:
        """Initialize OpenAI client."""
        api_key = self._get_env_key("openai")
        if not api_key:
            raise ValueError("OPENAI API key not configured")
        return OpenAI(api_key=api_key)

    def _init_anthropic(self) -> Optional[Any]:
        """Initialize Anthropic client."""
        api_key = self._get_env_key("anthropic")
        if not api_key:
            raise ValueError("ANTHROPIC API key not configured")
        try:
            anthropic_module = importlib.import_module("anthropic")
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError("anthropic package not installed") from e
        return anthropic_module.Anthropic(api_key=api_key)

    async def refine(self, text: str) -> str:
        """Refine text using available LLM providers with fallback."""
        if not self.refine_enabled:
            return text

        last_error: Optional[Exception] = None
        for prov, client in self.clients.items():
            try:
                if prov == "openai":
                    resp = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": f"Return only the refined reply:\n\n{text}"},
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                    )
                    return resp.choices[0].message.content.strip()
                if prov == "anthropic":
                    provider_model = self.config.get("anthropic", {}).get("model", "claude-3-haiku-20240307")
                    resp = client.messages.create(
                        model=provider_model,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        system=self.system_prompt,
                        messages=[{"role": "user", "content": text}],
                    )
                    if resp.content:
                        return resp.content[0].text.strip()
                    return text
            except Exception as e:
                last_error = e
                logger.warning("Provider '%s' failed to refine text: %s", prov, e)
        if last_error:
            logger.error("All providers failed to refine text: %s", last_error)
        return text
