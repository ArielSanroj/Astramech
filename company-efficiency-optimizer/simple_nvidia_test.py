#!/usr/bin/env python3
"""
Simple NVIDIA AI Endpoints test

This script tests basic NVIDIA AI Endpoints functionality with different model configurations.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_nvidia_api_direct():
    """Test NVIDIA API directly"""
    print("🧪 Testing NVIDIA API directly...")
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ NVIDIA_API_KEY not found")
        return False
    
    # Try different NVIDIA endpoints
    endpoints = [
        "https://integrate.api.nvidia.com/v1/chat/completions",
        "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions",
        "https://api.nvcf.nvidia.com/v2/nvcf/pexec/status"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple request
    payload = {
        "model": "nvidia/nemotron-4-340b-instruct",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    
    for endpoint in endpoints:
        try:
            print(f"   Testing endpoint: {endpoint}")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Success with endpoint: {endpoint}")
                return True
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {str(e)[:100]}")
    
    return False

def test_available_models():
    """Test what models are available"""
    print("\n🔍 Checking available models...")
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ NVIDIA_API_KEY not found")
        return False
    
    # Try to get available models
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://integrate.api.nvidia.com/v1/models",
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print("✅ Available models:")
            for model in models.get('data', []):
                print(f"   - {model.get('id', 'Unknown')}")
            return True
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def main():
    """Run NVIDIA tests"""
    print("🚀 Simple NVIDIA AI Endpoints Test")
    print("=" * 40)
    
    # Test 1: Direct API call
    if test_nvidia_api_direct():
        print("\n✅ NVIDIA API is working!")
    else:
        print("\n❌ NVIDIA API test failed")
    
    # Test 2: Available models
    test_available_models()
    
    print("\n" + "=" * 40)
    print("📝 If tests fail, check:")
    print("1. NVIDIA API key is correct")
    print("2. Account has access to the models")
    print("3. Model names are correct")
    print("4. API endpoint URLs are correct")

if __name__ == "__main__":
    main()