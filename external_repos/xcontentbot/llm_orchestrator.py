#!/usr/bin/env python3
"""
Decoupled LLM orchestration system for xcontentbot.
Supports multiple providers with configurable parameters and fallback strategies.

This module re-exports from the llm package for backwards compatibility.
"""

# Re-export everything from the llm package
from llm import (
    # Providers
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    MockProvider,
    # Orchestrator
    LLMOrchestrator,
    llm_orchestrator,
    # Convenience functions
    generate_text,
    generate_comment,
    refine_comment,
    # Helpers
    measure_llm_performance,
    generate_comment_prompt,
    get_system_prompt,
    get_refine_prompt,
)

__all__ = [
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "MockProvider",
    "LLMOrchestrator",
    "llm_orchestrator",
    "generate_text",
    "generate_comment",
    "refine_comment",
    "measure_llm_performance",
    "generate_comment_prompt",
    "get_system_prompt",
    "get_refine_prompt",
]
