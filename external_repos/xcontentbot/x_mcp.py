"""
X (Twitter) MCP Server - Main Entry Point

Exposes MCP tools for X automation:
  - search_posts(query, limit, days)
  - get_post(id)
  - draft_comment(id)
  - submit_comment(id, text, auto)
  - clear_browser_state_tool()
"""
import logging
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from config import USE_MCP_MODE, LOG_LEVEL
from mcp_tools import mcp, search_posts, get_post, draft_comment, submit_comment, clear_browser_state_tool

# Logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("x-mcp")


class SubmitPayload(BaseModel):
    """Payload for submit_comment endpoint."""
    id: str
    text: Optional[str] = None
    auto: Optional[bool] = None


def create_rest_app() -> FastAPI:
    """Create FastAPI REST app."""
    app = FastAPI(title="X MCP Server", version="1.0.0")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "marketing-x"}

    @app.get("/mcp/search_posts")
    async def search_posts_endpoint(query: str = "burnout", limit: int = 10, days: int = 14):
        return await search_posts(query, limit, days)

    @app.get("/mcp/get_post")
    async def get_post_endpoint(id: str):
        return await get_post(id)

    @app.get("/mcp/draft_comment")
    async def draft_comment_endpoint(id: str):
        return await draft_comment(id)

    @app.post("/mcp/submit_comment")
    async def submit_comment_endpoint(payload: SubmitPayload):
        auto_value = payload.auto if payload.auto is not None else True
        return await submit_comment(payload.id, payload.text, auto_value)

    @app.post("/mcp/clear_browser_state")
    async def clear_browser_state_endpoint():
        return await clear_browser_state_tool()

    return app


if __name__ == "__main__":
    # To login first time, uncomment:
    # from browser_utils import x_login_once
    # import asyncio
    # asyncio.run(x_login_once())

    if USE_MCP_MODE:
        logger.info("Starting MCP server on http://0.0.0.0:8005/mcp")
        mcp.run_http(host="0.0.0.0", port=8005, path="/mcp")
    else:
        logger.info("Starting REST server on http://0.0.0.0:8005")
        app = create_rest_app()
        uvicorn.run(app, host="0.0.0.0", port=8005)
