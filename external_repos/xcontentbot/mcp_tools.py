"""MCP tools for X automation."""
import asyncio
import random
import html
import logging
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from playwright.async_api import Page

from config import SELECTORS
from browser_utils import with_browser, dismiss_overlays, clear_browser_state
from scraper import search_x_internal, validate_x_results, POSTS
from outreach import generate_outreach

logger = logging.getLogger("x-mcp")
mcp = FastMCP("XBurnout")


async def post_reply(page: Page, pid: str, text: str) -> Dict:
    """Post a reply to a specific post."""
    post = POSTS.get(pid)
    if not post:
        return {"status": "error", "reason": "unknown-id"}
    url = post.get("url")
    if not url or not url.startswith("https://"):
        return {"status": "error", "reason": "invalid-url"}

    await page.goto(url)
    await page.wait_for_load_state("load", timeout=60000)
    await dismiss_overlays(page)

    try:
        await page.locator(SELECTORS["comment_button"]).first.click(timeout=6000)
        await asyncio.sleep(random.uniform(0.5, 1.2))
    except Exception:
        pass

    editor = page.locator(SELECTORS["comment_editor"]).first
    try:
        await editor.fill(text)
    except:
        await editor.type(text, delay=10)
    await asyncio.sleep(random.uniform(0.5, 1.2))

    try:
        post_button = page.locator(SELECTORS["post_comment_button"]).first
        if await post_button.is_visible():
            await post_button.click(timeout=4000)
            await asyncio.sleep(0.5)
    except Exception:
        pass

    return {"status": "posted", "url": url}


@mcp.tool()
async def search_posts(query: str = "burnout", limit: int = 10, days: int = 14) -> List[Dict]:
    """Find recent posts. Returns list of {id, url, author, text_preview}."""
    logger.info("MCP: search_posts query=%s limit=%d", query, limit)
    results = await with_browser(lambda page: search_x_internal(page, query, limit))
    return validate_x_results(results)


@mcp.tool()
async def get_post(id: str) -> Dict:
    """Return full post text & meta by id."""
    logger.info("MCP: get_post id=%s", id)
    post = POSTS.get(id, {})
    if post and not post["url"].startswith("https://"):
        post["url"] = "https://x.com" + post["url"]
    return post


@mcp.tool()
async def draft_comment(id: str) -> Dict:
    """Return a <280-char empathetic outreach reply for the post id."""
    logger.info("MCP: draft_comment id=%s", id)
    post = POSTS.get(id, {})
    text = post.get("text", "")[:4000]
    comment = generate_outreach(text, post.get("author"))
    return {"id": id, "comment": comment[:280]}


@mcp.tool()
async def submit_comment(id: str, text: Optional[str] = None, auto: Optional[bool] = None) -> Dict:
    """Post reply. Set auto=False to preview only."""
    logger.info("MCP: submit_comment id=%s auto=%s", id, auto)

    if not id or not isinstance(id, str):
        return {"status": "error", "reason": "invalid-id"}

    if text:
        text = text.strip()
        if len(text) > 280:
            return {"status": "error", "reason": "text-too-long", "max": 280}
        if len(text) < 1:
            return {"status": "error", "reason": "text-empty"}
        text = html.escape(text)

    use_auto = True if auto is None else bool(auto)
    post = POSTS.get(id)
    if not post:
        return {"status": "error", "reason": "unknown-id"}
    if not text:
        text = generate_outreach(post.get("text", ""), post.get("author"))[:280]

    if not use_auto:
        return {"status": "preview", "id": id, "comment": text}

    logger.info("AUTO-POSTING reply to %s", id)
    return await with_browser(lambda page: post_reply(page, id, text))


@mcp.tool()
async def clear_browser_state_tool() -> Dict:
    """Clear browser state to fix redirect issues."""
    logger.info("MCP: clear_browser_state_tool")
    await clear_browser_state()
    return {"status": "success", "message": "Browser state cleared."}
