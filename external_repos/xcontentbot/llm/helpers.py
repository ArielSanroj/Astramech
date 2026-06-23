#!/usr/bin/env python3
"""
LLM helper functions and convenience utilities.
"""

import time
import logging
from typing import Callable

from config_manager import get_config

logger = logging.getLogger(__name__)


def measure_llm_performance(func_name: str):
    """Decorator to measure LLM function performance."""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"LLM {func_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"LLM {func_name} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator


async def generate_comment_prompt(post_text: str, author: str = None) -> str:
    """Build prompt for comment generation."""
    prompt = f"Post: {post_text}"
    if author:
        prompt += f"\nAuthor: {author}"
    prompt += "\nGenerate a relevant, engaging comment:"
    return prompt


async def get_system_prompt() -> str:
    """Get the system prompt from config."""
    default_prompt = (
        "Generate a warm, professional comment under 280 characters."
    )
    return get_config("llm.system_prompt", default_prompt)


async def get_refine_prompt(comment: str) -> tuple:
    """Get prompt for refining a comment."""
    system_prompt = (
        "Refine this comment to be warm, professional, "
        "and under 280 characters. Avoid hard-sell language."
    )
    prompt = f"Comment to refine: {comment}\nRefined version:"
    return system_prompt, prompt
