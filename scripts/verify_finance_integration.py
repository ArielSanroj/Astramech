#!/usr/bin/env python3
"""
Script to verify the finance service integration.
Tests the API Gateway -> SuperVincent finance service connection.
"""
import asyncio
import httpx
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
FINANCE_SERVICE_URL = os.getenv("FINANCE_SERVICE_URL", "http://localhost:8001")


async def test_gateway_health():
    """Test API Gateway root endpoint."""
    print("🔍 Testing API Gateway health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_GATEWAY_URL}/")
            response.raise_for_status()
            print(f"✅ API Gateway is healthy: {response.json()}")
            return True
    except Exception as e:
        print(f"❌ API Gateway health check failed: {e}")
        return False


async def test_finance_service_health():
    """Test SuperVincent finance service health directly."""
    print("\n🔍 Testing Finance Service health (direct)...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FINANCE_SERVICE_URL}/health", timeout=5.0)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Finance Service is healthy:")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Services: {data.get('services', {})}")
            return True
    except Exception as e:
        print(f"❌ Finance Service health check failed: {e}")
        return False


async def test_gateway_finance_health():
    """Test finance health through API Gateway."""
    print("\n🔍 Testing Finance health through API Gateway...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_GATEWAY_URL}/api/v1/finance/health", timeout=10.0)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Finance health check via Gateway successful:")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            return True
    except Exception as e:
        print(f"❌ Finance health check via Gateway failed: {e}")
        return False


async def test_gateway_finance_process():
    """Test invoice processing through API Gateway (with mock file path)."""
    print("\n🔍 Testing invoice processing through API Gateway...")
    # Note: This will fail if the file doesn't exist, but tests the routing
    test_payload = {
        "file_path": "/app/uploads/test_invoice.pdf",
        "user_id": "test_user_123"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_GATEWAY_URL}/api/v1/finance/invoices/process",
                json=test_payload,
                timeout=30.0
            )
            # We expect either 200 (success) or 400/404 (file not found)
            if response.status_code == 200:
                print(f"✅ Invoice processing successful: {response.json()}")
                return True
            elif response.status_code in (400, 404):
                print(f"⚠️  Invoice processing endpoint works but file not found (expected):")
                print(f"   Response: {response.text[:200]}")
                return True  # Endpoint routing works
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except httpx.RequestError as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("Astramech Finance Service Integration Verification")
    print("=" * 60)
    
    results = []
    
    # Test 1: API Gateway health
    results.append(await test_gateway_health())
    
    # Test 2: Finance service health (direct)
    results.append(await test_finance_service_health())
    
    # Test 3: Finance health via Gateway
    results.append(await test_gateway_finance_health())
    
    # Test 4: Invoice processing via Gateway
    results.append(await test_gateway_finance_process())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Finance service integration is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

