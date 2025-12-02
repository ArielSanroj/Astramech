"""
CRM router for API Gateway.
Delegates requests to CRM/Email service.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm", tags=["crm"])

CRM_SERVICE_URL = os.getenv("CRM_SERVICE_URL", "http://crm-email:5000")
client = httpx.AsyncClient(base_url=CRM_SERVICE_URL, timeout=60.0)


class LeadPayload(BaseModel):
    """Payload for creating a lead."""
    contact_name: str
    email: str
    company: str | None = None
    phone: str | None = None
    source: str | None = None


class BuyerSignalPayload(BaseModel):
    """Payload for detecting buyer signal."""
    lead_id: str
    signal_type: str
    strength: str
    metadata: dict | None = None


@router.post("/leads")
async def create_lead(payload: LeadPayload):
    """
    Create a new lead in CRM.
    Delegates to crm-email service.
    """
    try:
        response = await client.post("/api/v1/contacts", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"CRM service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"CRM service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to CRM service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CRM service unavailable"
        )


@router.post("/buyer-signal")
async def detect_buyer_signal(payload: BuyerSignalPayload):
    """
    Detect and process buyer signal.
    Publishes event to RabbitMQ.
    """
    try:
        response = await client.post("/api/v1/buyer-signal", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"CRM service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"CRM service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to CRM service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CRM service unavailable"
        )


@router.get("/leads/{lead_id}")
async def get_lead(lead_id: str):
    """
    Get lead information.
    """
    try:
        response = await client.get(f"/api/v1/contacts/{lead_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"CRM service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to CRM service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CRM service unavailable"
        )


@router.get("/health")
async def health():
    """
    Health check for CRM service.
    """
    try:
        response = await client.get("/health", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"CRM service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CRM service unavailable"
        )

