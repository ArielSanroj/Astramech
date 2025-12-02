"""
Cold Calling router for API Gateway.
Delegates requests to cold calling service.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calls", tags=["calls"])

CALLS_SERVICE_URL = os.getenv("CALLS_SERVICE_URL", "http://cold-calling:8000")
client = httpx.AsyncClient(base_url=CALLS_SERVICE_URL, timeout=60.0)


class OutboundCallPayload(BaseModel):
    """Payload for making an outbound call."""
    to_number: str
    campaign_id: str | None = None
    lead_id: str | None = None
    metadata: dict | None = None


class CallStatusPayload(BaseModel):
    """Payload for checking call status."""
    call_id: str


@router.post("/outbound")
async def make_outbound_call(payload: OutboundCallPayload):
    """
    Initiate an outbound call.
    Delegates to cold-calling service.
    """
    try:
        response = await client.post("/api/calls", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Cold calling service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Cold calling service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to cold calling service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cold calling service unavailable"
        )


@router.get("/status/{call_id}")
async def get_call_status(call_id: str):
    """
    Get status of a call.
    """
    try:
        response = await client.get(f"/api/calls/{call_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Cold calling service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to cold calling service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cold calling service unavailable"
        )


@router.get("/health")
async def health():
    """
    Health check for cold calling service.
    """
    try:
        response = await client.get("/health", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Cold calling service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cold calling service unavailable"
        )

