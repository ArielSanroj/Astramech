#!/usr/bin/env python3
"""
Direct NVIDIA AI Endpoints test using requests

This bypasses the LangChain version conflicts and tests NVIDIA directly.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_nvidia_chat():
    """Test NVIDIA chat completion directly"""
    print("🤖 Testing NVIDIA Chat Completion...")
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ NVIDIA_API_KEY not found")
        return False
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "nvidia/nemotron-4-340b-instruct",
        "messages": [
            {"role": "user", "content": "Hello! Can you help me analyze a company's financial performance? Please respond briefly."}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ NVIDIA Response: {content}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_nvidia_embeddings():
    """Test NVIDIA embeddings directly"""
    print("\n🧠 Testing NVIDIA Embeddings...")
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ NVIDIA_API_KEY not found")
        return False
    
    url = "https://integrate.api.nvidia.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "nvidia/nv-embed-qa-e5-v5",
        "input": "Company efficiency optimization and KPI analysis"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            embedding = result['data'][0]['embedding']
            print(f"✅ Embedding dimension: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_company_analysis():
    """Test company analysis with NVIDIA"""
    print("\n📊 Testing Company Analysis with NVIDIA...")
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ NVIDIA_API_KEY not found")
        return False
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Sample P&L data
    sample_data = {
        "revenue": 1000000,
        "cogs": 700000,
        "operating_expenses": 200000,
        "net_income": 80000,
        "employee_count": 50
    }
    
    prompt = f"""
    Analyze this company's financial performance:
    
    Revenue: ${sample_data['revenue']:,}
    Cost of Goods Sold: ${sample_data['cogs']:,}
    Operating Expenses: ${sample_data['operating_expenses']:,}
    Net Income: ${sample_data['net_income']:,}
    Employee Count: {sample_data['employee_count']}
    
    Please calculate:
    1. Gross Margin percentage
    2. Operating Margin percentage
    3. Net Margin percentage
    4. Revenue per Employee
    
    Identify any inefficiencies and recommend optimization strategies.
    """
    
    payload = {
        "model": "nvidia/nemotron-4-340b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("✅ Company Analysis Results:")
            print(content)
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run all NVIDIA tests"""
    print("🚀 Direct NVIDIA AI Endpoints Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for NVIDIA API key
    if not os.getenv("NVIDIA_API_KEY"):
        print("❌ NVIDIA_API_KEY not found in environment")
        print("📝 Please add your NVIDIA API key to the .env file")
        return 1
    
    tests = [
        test_nvidia_chat,
        test_nvidia_embeddings,
        test_company_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All NVIDIA tests passed! The API is working correctly.")
        print("\n📝 Next steps:")
        print("1. The NVIDIA API is ready for integration")
        print("2. You can use the demo.py for full system capabilities")
        print("3. The system can be extended to use NVIDIA for LLM calls")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    main()