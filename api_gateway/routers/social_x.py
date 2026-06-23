"""
X (Twitter) router for API Gateway.
Delegates requests to the xcontentbot marketing-x service.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social/x", tags=["social-x"])

X_SERVICE_URL = os.getenv("X_SERVICE_URL", "http://marketing-x:8005")

x_client = httpx.AsyncClient(base_url=X_SERVICE_URL, timeout=60.0)


class SearchPayload(BaseModel):
    """Payload for searching X posts."""
    query: str = "burnout"
    limit: int = 10
    days: int = 14


class CommentPayload(BaseModel):
    """Payload for submitting a comment on an X post."""
    id: str
    text: str | None = None
    auto: bool | None = True


@router.post("/search")
async def search_posts(payload: SearchPayload):
    """Search X posts by topic."""
    try:
        response = await x_client.get(
            "/mcp/search_posts",
            params={"query": payload.query, "limit": payload.limit, "days": payload.days},
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"X service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"X service error: {e.response.text}",
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to X service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="X service unavailable",
        )


@router.get("/post/{post_id}")
async def get_post(post_id: str):
    """Get details of a specific X post."""
    try:
        response = await x_client.get("/mcp/get_post", params={"id": post_id})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"X service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to X service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="X service unavailable",
        )


@router.post("/draft/{post_id}")
async def draft_comment(post_id: str):
    """Generate an AI draft comment for an X post."""
    try:
        response = await x_client.get("/mcp/draft_comment", params={"id": post_id})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"X service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to X service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="X service unavailable",
        )


@router.post("/comment")
async def submit_comment(payload: CommentPayload):
    """Submit a comment on an X post."""
    try:
        response = await x_client.post(
            "/mcp/submit_comment",
            json={"id": payload.id, "text": payload.text, "auto": payload.auto},
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"X service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"X service error: {e.response.text}",
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to X service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="X service unavailable",
        )


@router.get("/health")
async def x_health():
    """Health check for X service."""
    try:
        response = await x_client.get("/health", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"X service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="X service unavailable",
        )
