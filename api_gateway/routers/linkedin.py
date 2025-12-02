"""
LinkedIn router for API Gateway.
Delegates requests to LinkedIn posting service.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/linkedin", tags=["linkedin"])

LINKEDIN_SERVICE_URL = os.getenv("LINKEDIN_SERVICE_URL", "http://linkedin-posting:8001")
client = httpx.AsyncClient(base_url=LINKEDIN_SERVICE_URL, timeout=60.0)


class LinkedInPostPayload(BaseModel):
    """Payload for posting a LinkedIn comment."""
    post_id: str
    brand_voice: str | None = None
    comment_text: str | None = None


class SearchPayload(BaseModel):
    """Payload for searching LinkedIn posts."""
    query: str
    limit: int = 10


@router.post("/posts/comment")
async def post_comment(payload: LinkedInPostPayload):
    """
    Post a comment on a LinkedIn post.
    Delegates to linkedin-posting service.
    """
    try:
        response = await client.post("/api/v1/comment", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"LinkedIn service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"LinkedIn service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to LinkedIn service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn service unavailable"
        )


@router.post("/posts/search")
async def search_posts(payload: SearchPayload):
    """
    Search for LinkedIn posts.
    """
    try:
        response = await client.post("/api/v1/search", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"LinkedIn service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to LinkedIn service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn service unavailable"
        )


@router.get("/health")
async def health():
    """
    Health check for LinkedIn service.
    """
    try:
        response = await client.get("/status", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"LinkedIn service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn service unavailable"
        )

