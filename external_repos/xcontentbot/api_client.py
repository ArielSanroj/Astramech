"""API client functions for MCP server communication."""
import asyncio
import random
import logging
from typing import Dict, List

import httpx

from client_config import MCP_SERVER_URL, RETRY_CONFIG, CONFIG
from llm_client import LLMClient

logger = logging.getLogger("x-mcp-client")

# Initialize LLM client
llm_client = LLMClient(CONFIG.get("llm", {}))


def _first_n_chars(s: str, n: int = 280) -> str:
    """Truncate string to first n characters."""
    return (s or "")[:n]


async def _safe_json(resp: httpx.Response):
    """Safely parse JSON response."""
    try:
        return resp.json()
    except Exception as e:
        logger.error("Non-JSON response for %s: %s (text: %s)", resp.url, e, resp.text[:500])
        return None


def _calculate_backoff_delay(attempt: int) -> float:
    """Calculate exponential backoff delay with jitter."""
    delay = min(
        RETRY_CONFIG["base_delay"] * (RETRY_CONFIG["exponential_base"] ** attempt),
        RETRY_CONFIG["max_delay"]
    )
    jitter = random.uniform(0, RETRY_CONFIG["jitter"] * delay)
    return delay + jitter


async def _retry_request(func, log_name: str, *args, **kwargs):
    """Retry request with exponential backoff and centralized configuration."""
    max_retries = RETRY_CONFIG["max_retries"]

    for attempt in range(max_retries):
        try:
            response = await func(*args, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [500, 502, 503, 504] and attempt < max_retries - 1:
                delay = _calculate_backoff_delay(attempt)
                logger.warning("Retrying %s after %d error (attempt %d/%d, delay: %.2fs)",
                               log_name, e.response.status_code, attempt + 1, max_retries, delay)
                await asyncio.sleep(delay)
            else:
                logger.error("Failed %s after %d attempts: %s", log_name, attempt + 1, e)
                raise
        except httpx.HTTPError as e:
            if attempt < max_retries - 1:
                delay = _calculate_backoff_delay(attempt)
                logger.warning("Retrying %s after HTTP error (attempt %d/%d, delay: %.2fs): %s",
                               log_name, attempt + 1, max_retries, delay, e)
                await asyncio.sleep(delay)
            else:
                logger.error("HTTP error for %s after %d attempts: %s", log_name, attempt + 1, e)
                raise
        except Exception as e:
            logger.error("Unexpected error for %s: %s", log_name, e)
            raise


async def fetch_posts(client: httpx.AsyncClient, query: str, limit: int) -> List[Dict]:
    """Fetch posts from MCP server for a query."""
    async def _fetch():
        return await client.get(f"{MCP_SERVER_URL}/search_posts", params={"query": query, "limit": limit}, timeout=90.0)
    r = await _retry_request(_fetch, "fetch_posts")
    data = await _safe_json(r)
    return data if isinstance(data, list) else []


async def get_post(client: httpx.AsyncClient, post_id: str) -> Dict:
    """Get a single post by ID."""
    async def _get():
        return await client.get(f"{MCP_SERVER_URL}/get_post", params={"id": post_id}, timeout=90.0)
    r = await _retry_request(_get, "get_post")
    return await _safe_json(r) or {}


async def draft_comment(client: httpx.AsyncClient, post_id: str) -> Dict:
    """Draft a comment for a post."""
    async def _draft():
        return await client.get(f"{MCP_SERVER_URL}/draft_comment", params={"id": post_id}, timeout=120.0)
    r = await _retry_request(_draft, "draft_comment")
    return await _safe_json(r) or {}


async def submit_comment(client: httpx.AsyncClient, post_id: str, text: str, auto: bool = True) -> Dict:
    """Submit a comment to a post."""
    if not post_id or not text:
        return {"status": "error", "reason": "invalid-input"}
    payload = {"id": post_id, "text": text, "auto": auto}
    async def _submit():
        return await client.post(f"{MCP_SERVER_URL}/submit_comment", json=payload, timeout=120.0)
    r = await _retry_request(_submit, "submit_comment")
    res = await _safe_json(r) or {}
    logger.info(f"Submit result for {post_id}: {res}")
    return res


async def refine_with_ai(draft_text: str) -> str:
    """Refine draft text with AI."""
    refined = await llm_client.refine(draft_text)
    if refined.strip() == draft_text.strip():
        return _first_n_chars(draft_text, 280)
    return _first_n_chars(refined, 280)
