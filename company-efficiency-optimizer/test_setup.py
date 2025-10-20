#!/usr/bin/env python3
"""
Test script for Company Efficiency Optimizer setup

This script tests the basic functionality of the system without requiring API keys.
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import crewai
        print("✅ CrewAI imported successfully")
    except ImportError as e:
        print(f"❌ CrewAI import failed: {e}")
        return False
    
    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import pinecone
        print("✅ Pinecone imported successfully")
    except ImportError as e:
        print(f"❌ Pinecone import failed: {e}")
        return False
    
    return True

def test_config_files():
    """Test that configuration files exist and are valid"""
    print("\n📋 Testing configuration files...")
    
    config_files = [
        'config/agents.yaml',
        'config/tasks.yaml',
        '.env'
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def test_data_ingestion():
    """Test data ingestion functionality"""
    print("\n📊 Testing data ingestion...")
    
    try:
        from data_ingest import DataIngestion
        data_ingestion = DataIngestion()
        
        # Test sample data creation
        hr_data = data_ingestion._create_sample_hr_data()
        financial_data = data_ingestion._create_sample_financial_data()
        
        print(f"✅ Sample HR data created: {len(hr_data)} employees")
        print(f"✅ Sample financial data created: {len(financial_data)} periods")
        
        return True
    except Exception as e:
        print(f"❌ Data ingestion test failed: {e}")
        return False

def test_kpi_calculator():
    """Test KPI calculator functionality"""
    print("\n📈 Testing KPI calculator...")
    
    try:
        from tools.kpi_calculator import KPICalculator
        calculator = KPICalculator()
        
        # Test sample financial data
        sample_data = {
            'revenue': 1000000,
            'cogs': 700000,
            'operating_income': 100000,
            'net_income': 80000,
            'employee_count': 50
        }
        
        kpis = calculator.calculate_financial_kpis(sample_data)
        print(f"✅ Calculated {len(kpis)} financial KPIs")
        
        # Test inefficiency identification
        inefficiencies = calculator.identify_inefficiencies(kpis)
        print(f"✅ Identified {len(inefficiencies)} inefficiencies")
        
        return True
    except Exception as e:
        print(f"❌ KPI calculator test failed: {e}")
        return False

def test_crew_initialization():
    """Test crew initialization (without API keys)"""
    print("\n🤖 Testing crew initialization...")
    
    try:
        # Set placeholder API keys for testing
        os.environ['OPENAI_API_KEY'] = 'test-key'
        os.environ['PINECONE_API_KEY'] = 'test-key'
        
        from simple_crew import DiagnosticCrew
        
        # Test crew creation
        crew_instance = DiagnosticCrew()
        print("✅ Crew class imported and initialized successfully")
        print("✅ Agents and tasks created successfully")
        print("⚠️  Full execution requires valid API keys")
        
        return True
    except Exception as e:
        print(f"❌ Crew initialization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Company Efficiency Optimizer - Setup Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        test_imports,
        test_config_files,
        test_data_ingestion,
        test_kpi_calculator,
        test_crew_initialization
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
        print("🎉 All tests passed! The system is ready for configuration.")
        print("\n📝 Next steps:")
        print("1. Update .env file with your API keys")
        print("2. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())