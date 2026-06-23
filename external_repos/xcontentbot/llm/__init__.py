#!/usr/bin/env python3
"""
Decoupled LLM orchestration system for xcontentbot.
Supports multiple providers with configurable parameters and fallback strategies.
"""

from .providers import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    MockProvider,
)
from .orchestrator import LLMOrchestrator
from .helpers import (
    measure_llm_performance,
    generate_comment_prompt,
    get_system_prompt,
    get_refine_prompt,
)

# Global LLM orchestrator instance
llm_orchestrator = LLMOrchestrator()


# Convenience functions
async def generate_text(prompt: str, **kwargs) -> str:
    """Generate text using the LLM orchestrator."""
    return await llm_orchestrator.generate_text(prompt, **kwargs)


@measure_llm_performance("generate_comment")
async def generate_comment(post_text: str, author: str = None, **kwargs) -> str:
    """Generate a comment for a post."""
    system_prompt = await get_system_prompt()
    prompt = await generate_comment_prompt(post_text, author)
    return await generate_text(prompt, system_prompt=system_prompt, **kwargs)


@measure_llm_performance("refine_comment")
async def refine_comment(comment: str, **kwargs) -> str:
    """Refine an existing comment."""
    system_prompt, prompt = await get_refine_prompt(comment)
    return await generate_text(prompt, system_prompt=system_prompt, **kwargs)


# Apply performance measurement to generate_text
generate_text = measure_llm_performance("generate_text")(generate_text)


__all__ = [
    # Providers
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "MockProvider",
    # Orchestrator
    "LLMOrchestrator",
    "llm_orchestrator",
    # Convenience functions
    "generate_text",
    "generate_comment",
    "refine_comment",
    # Helpers
    "measure_llm_performance",
    "generate_comment_prompt",
    "get_system_prompt",
    "get_refine_prompt",
]
