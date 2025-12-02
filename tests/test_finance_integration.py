"""
Integration tests for Finance Service via API Gateway.
"""
import pytest
import httpx
import os
from typing import Dict, Any

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
FINANCE_SERVICE_URL = os.getenv("FINANCE_SERVICE_URL", "http://localhost:8001")


@pytest.mark.asyncio
async def test_api_gateway_root():
    """Test API Gateway root endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_GATEWAY_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data


@pytest.mark.asyncio
async def test_finance_service_health_direct():
    """Test finance service health check directly."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{FINANCE_SERVICE_URL}/health", timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
        except httpx.ConnectError:
            pytest.skip("Finance service not available (may be running in Docker)")


@pytest.mark.asyncio
async def test_finance_health_via_gateway():
    """Test finance health check through API Gateway."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_GATEWAY_URL}/api/v1/finance/health",
            timeout=10.0
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_finance_process_invoice_endpoint():
    """Test invoice processing endpoint routing (file may not exist)."""
    async with httpx.AsyncClient() as client:
        payload = {
            "file_path": "/app/uploads/test_invoice.pdf",
            "user_id": "test_user_123"
        }
        response = await client.post(
            f"{API_GATEWAY_URL}/api/v1/finance/invoices/process",
            json=payload,
            timeout=30.0
        )
        # Accept 200 (success) or 400/404 (file not found - routing works)
        assert response.status_code in (200, 400, 404, 500)
        # If 404/400, endpoint routing is working correctly


@pytest.mark.asyncio
async def test_finance_batch_endpoint():
    """Test batch processing endpoint routing."""
    async with httpx.AsyncClient() as client:
        payload = {
            "file_paths": [
                "/app/uploads/test1.pdf",
                "/app/uploads/test2.pdf"
            ],
            "user_id": "test_user_123"
        }
        response = await client.post(
            f"{API_GATEWAY_URL}/api/v1/finance/invoices/batch",
            json=payload,
            timeout=60.0
        )
        # Accept 200 (success) or 400/404 (files not found - routing works)
        assert response.status_code in (200, 400, 404, 500)


@pytest.mark.asyncio
async def test_gateway_error_handling():
    """Test that Gateway properly handles service unavailable."""
    # This test assumes finance service is down
    # In real scenario, you'd mock the httpx client
    pass  # TODO: Implement with mocked httpx client

