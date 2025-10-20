#!/usr/bin/env python3
"""
Test script for NVIDIA AI Endpoints integration

This script tests the NVIDIA AI Endpoints connection and functionality.
"""

import os
import sys
from dotenv import load_dotenv

def test_nvidia_imports():
    """Test NVIDIA AI Endpoints imports"""
    print("🧪 Testing NVIDIA AI Endpoints imports...")
    
    try:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
        print("✅ NVIDIA AI Endpoints imported successfully")
        return True
    except ImportError as e:
        print(f"❌ NVIDIA AI Endpoints import failed: {e}")
        return False

def test_nvidia_llm():
    """Test NVIDIA LLM connection"""
    print("\n🤖 Testing NVIDIA LLM...")
    
    try:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        
        llm = ChatNVIDIA(
            model="nvidia/nemotron-4-340b-instruct",
            nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
            temperature=0.7
        )
        
        response = llm.invoke("Hello! Can you tell me what model you are?")
        print(f"✅ NVIDIA LLM Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ NVIDIA LLM test failed: {e}")
        return False

def test_nvidia_embeddings():
    """Test NVIDIA embeddings"""
    print("\n🧠 Testing NVIDIA Embeddings...")
    
    try:
        from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
        
        embeddings = NVIDIAEmbeddings(
            model="NV-Embed-QA",
            nvidia_api_key=os.getenv("NVIDIA_API_KEY")
        )
        
        embedding = embeddings.embed_query("Test embedding for company efficiency")
        print(f"✅ NVIDIA Embeddings: Vector dimension {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"❌ NVIDIA Embeddings test failed: {e}")
        return False

def test_nvidia_crew():
    """Test NVIDIA crew initialization"""
    print("\n🚀 Testing NVIDIA Crew initialization...")
    
    try:
        from nvidia_crew import NVIDIADiagnosticCrew
        
        crew_instance = NVIDIADiagnosticCrew()
        print("✅ NVIDIA Crew initialized successfully")
        
        # Test connection
        if crew_instance.test_nvidia_connection():
            print("✅ NVIDIA connection test passed")
            return True
        else:
            print("❌ NVIDIA connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ NVIDIA Crew test failed: {e}")
        return False

def main():
    """Run all NVIDIA tests"""
    print("🚀 NVIDIA AI Endpoints Integration Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for NVIDIA API key
    if not os.getenv("NVIDIA_API_KEY"):
        print("❌ NVIDIA_API_KEY not found in environment")
        print("📝 Please add your NVIDIA API key to the .env file")
        return 1
    
    tests = [
        test_nvidia_imports,
        test_nvidia_llm,
        test_nvidia_embeddings,
        test_nvidia_crew
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
        print("🎉 All NVIDIA tests passed! The system is ready to use NVIDIA AI Endpoints.")
        print("\n📝 Next steps:")
        print("1. Run: python nvidia_main.py")
        print("2. Or run: python demo.py (still works without API keys)")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())