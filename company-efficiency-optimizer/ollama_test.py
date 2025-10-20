#!/usr/bin/env python3
"""
Ollama Test Script for Company Efficiency Optimizer
Tests core functionality with Ollama without CrewAI dependencies
"""

import os
import sys
from dotenv import load_dotenv
from data_ingest import DataIngestion
from tools.kpi_calculator import KPICalculator

def test_ollama_connection():
    """Test Ollama connection and model availability"""
    print("🔗 Testing Ollama connection...")
    
    try:
        import ollama
        client = ollama.Client(host=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
        
        # Check if the model is available
        models = client.list()
        model_name = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        
        available_models = [model.model for model in models.models]
        if model_name not in available_models:
            print(f"⚠️ Model {model_name} not found. Available models: {available_models}")
            return False
        
        print(f"✅ Ollama connection successful. Model {model_name} is available.")
        
        # Test a simple query
        print("🧪 Testing model response...")
        response = client.chat(
            model=model_name,
            messages=[{
                'role': 'user',
                'content': 'Hello! Can you help me analyze company financial data?'
            }]
        )
        
        print(f"✅ Model response: {response['message']['content'][:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {str(e)}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def test_ollama_langchain():
    """Test Ollama with LangChain"""
    print("\n🔗 Testing Ollama with LangChain...")
    
    try:
        from langchain_ollama import ChatOllama
        
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.7
        )
        
        # Test a simple query
        response = llm.invoke("What are the key financial KPIs for a company?")
        print(f"✅ LangChain Ollama response: {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error with LangChain Ollama: {str(e)}")
        return False

def test_data_processing():
    """Test data processing functionality"""
    print("\n📊 Testing data processing...")
    
    try:
        # Test data ingestion
        data_ingestion = DataIngestion()
        hr_data = data_ingestion._create_sample_hr_data()
        financial_data = data_ingestion._create_sample_financial_data()
        
        print(f"✅ HR data created: {len(hr_data)} employees")
        print(f"✅ Financial data created: {len(financial_data)} periods")
        
        # Test KPI calculation
        calculator = KPICalculator()
        latest_period = financial_data.iloc[-1].to_dict()
        kpis = calculator.calculate_financial_kpis(latest_period)
        
        print(f"✅ KPIs calculated: {len(kpis)} metrics")
        for kpi in kpis:
            print(f"   • {kpi.name}: {kpi.value:.1f}% ({kpi.status})")
        
        # Test inefficiency detection
        inefficiencies = calculator.identify_inefficiencies(kpis)
        print(f"✅ Inefficiencies found: {len(inefficiencies)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in data processing: {str(e)}")
        return False

def test_ollama_analysis():
    """Test Ollama for business analysis"""
    print("\n🧠 Testing Ollama for business analysis...")
    
    try:
        from langchain_ollama import ChatOllama
        
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.7
        )
        
        # Sample financial data
        sample_data = {
            'revenue': 1000000,
            'cogs': 700000,
            'operating_income': 100000,
            'net_income': 80000,
            'employee_count': 50
        }
        
        # Create analysis prompt
        prompt = f"""
        Analyze this company's financial performance:
        - Revenue: ${sample_data['revenue']:,}
        - COGS: ${sample_data['cogs']:,}
        - Operating Income: ${sample_data['operating_income']:,}
        - Net Income: ${sample_data['net_income']:,}
        - Employees: {sample_data['employee_count']}
        
        Calculate key ratios and provide insights on:
        1. Gross margin
        2. Operating margin
        3. Net margin
        4. Revenue per employee
        5. Areas for improvement
        """
        
        response = llm.invoke(prompt)
        print("✅ Ollama analysis completed:")
        print(f"📊 Analysis: {response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Ollama analysis: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Company Efficiency Optimizer - Ollama Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        test_ollama_connection,
        test_ollama_langchain,
        test_data_processing,
        test_ollama_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ollama integration is working.")
        print("\n💡 Next steps:")
        print("   1. The core functionality works with Ollama")
        print("   2. CrewAI has version conflicts that need resolution")
        print("   3. Consider using the data processing + Ollama directly")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)