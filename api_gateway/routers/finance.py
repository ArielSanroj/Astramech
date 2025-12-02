"""
Finance router for API Gateway.
Delegates requests to the SuperVincent finance service.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finance", tags=["finance"])

FINANCE_SERVICE_URL = os.getenv("FINANCE_SERVICE_URL", "http://finance-supervincent:8000")
client = httpx.AsyncClient(base_url=FINANCE_SERVICE_URL, timeout=60.0)


class InvoiceProcessPayload(BaseModel):
    """Payload for processing a single invoice."""
    file_path: str
    user_id: str | None = None


class BatchInvoicePayload(BaseModel):
    """Payload for batch processing invoices."""
    file_paths: list[str]
    user_id: str | None = None


@router.post("/invoices/process")
async def process_invoice(payload: InvoiceProcessPayload):
    """
    Process a single invoice file.
    
    Delegates to SuperVincent service POST /process endpoint.
    """
    try:
        response = await client.post("/process", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Finance service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Finance service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to finance service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Finance service unavailable"
        )


@router.post("/invoices/batch")
async def batch_process(payload: BatchInvoicePayload):
    """
    Process multiple invoices in batch.
    
    Delegates to SuperVincent service POST /process/batch endpoint.
    """
    try:
        response = await client.post("/process/batch", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Finance service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Finance service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to finance service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Finance service unavailable"
        )


@router.get("/health")
async def health():
    """
    Health check endpoint for finance service.
    
    Delegates to SuperVincent service GET /health endpoint.
    """
    try:
        response = await client.get("/health", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Finance service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Finance service unavailable"
        )
