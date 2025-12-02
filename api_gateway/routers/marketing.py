"""
Marketing router for API Gateway.
Delegates requests to marketing services (Google Ads and TikTok).
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketing", tags=["marketing"])

GOOGLE_ADS_SERVICE_URL = os.getenv("GOOGLE_ADS_SERVICE_URL", "http://marketing-googleads:8080")
TIKTOK_SERVICE_URL = os.getenv("TIKTOK_SERVICE_URL", "http://marketing-tiktok:8002")

google_ads_client = httpx.AsyncClient(base_url=GOOGLE_ADS_SERVICE_URL, timeout=60.0)
tiktok_client = httpx.AsyncClient(base_url=TIKTOK_SERVICE_URL, timeout=60.0)


# Google Ads Models
class CampaignPayload(BaseModel):
    """Payload for creating a Google Ads campaign."""
    email: str
    hotel_url: str
    instagram_url: str | None = None


class CampaignStatusPayload(BaseModel):
    """Payload for checking campaign status."""
    request_id: str


# TikTok Models
class TikTokRunPayload(BaseModel):
    """Payload for running TikTok marketing analysis."""
    brands: list[str] | None = None


@router.post("/google-ads/analyze")
async def analyze_hotel(payload: CampaignPayload):
    """
    Analyze a hotel and create Google Ads campaign.
    Delegates to marketing-googleads service.
    """
    try:
        response = await google_ads_client.post("/analyze", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Ads service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Google Ads service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Google Ads service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Ads service unavailable"
        )


@router.get("/google-ads/status/{request_id}")
async def get_campaign_status(request_id: str):
    """
    Get status of a Google Ads campaign analysis.
    """
    try:
        response = await google_ads_client.get(f"/status/{request_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Ads service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Google Ads service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Ads service unavailable"
        )


@router.get("/google-ads/performance")
async def get_performance():
    """
    Get Google Ads performance statistics.
    """
    try:
        response = await google_ads_client.get("/performance")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Google Ads service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Ads service unavailable"
        )


@router.post("/tiktok/run")
async def run_tiktok_analysis(payload: TikTokRunPayload):
    """
    Run TikTok marketing analysis for brands.
    Delegates to marketing-tiktok service.
    """
    try:
        response = await tiktok_client.post("/run", json=payload.dict())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"TikTok service error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"TikTok service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to TikTok service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TikTok service unavailable"
        )


@router.get("/tiktok/health")
async def tiktok_health():
    """
    Health check for TikTok service.
    """
    try:
        response = await tiktok_client.get("/health", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"TikTok service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TikTok service unavailable"
        )


@router.get("/google-ads/health")
async def google_ads_health():
    """
    Health check for Google Ads service.
    """
    try:
        response = await google_ads_client.get("/performance", timeout=5.0)
        response.raise_for_status()
        return {"status": "healthy", "service": "google-ads"}
    except httpx.RequestError as e:
        logger.error(f"Google Ads service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Ads service unavailable"
        )

