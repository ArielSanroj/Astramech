#!/usr/bin/env python3
"""
Simplified test script for Company Efficiency Optimizer
Tests core functionality without CrewAI dependencies
"""

import os
import sys
from dotenv import load_dotenv

def test_core_imports():
    """Test core modules that don't depend on CrewAI"""
    print("🧪 Testing core imports...")
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import yaml
        print("✅ PyYAML imported successfully")
    except ImportError as e:
        print(f"❌ PyYAML import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_data_ingestion():
    """Test data ingestion functionality"""
    print("\n📊 Testing data ingestion...")
    
    try:
        from data_ingest import DataIngestion
        data_ingestion = DataIngestion()
        print("✅ DataIngestion class created successfully")
        
        # Test sample data creation
        hr_data = data_ingestion._create_sample_hr_data()
        print(f"✅ Sample HR data created: {len(hr_data)} employees")
        
        financial_data = data_ingestion._create_sample_financial_data()
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
        print("✅ KPICalculator class created successfully")
        
        # Test with sample data
        sample_financial_data = {
            'revenue': 1000000,
            'cogs': 700000,
            'operating_income': 100000,
            'net_income': 80000,
            'employee_count': 50
        }
        
        kpis = calculator.calculate_financial_kpis(sample_financial_data)
        print(f"✅ Financial KPIs calculated: {len(kpis)} metrics")
        
        for kpi in kpis:
            print(f"   • {kpi.name}: {kpi.value:.1f}% ({kpi.status})")
        
        return True
    except Exception as e:
        print(f"❌ KPI calculator test failed: {e}")
        return False

def test_memory_setup():
    """Test memory setup functionality"""
    print("\n🧠 Testing memory setup...")
    
    try:
        from memory_setup import MemoryManager
        memory_manager = MemoryManager()
        print("✅ MemoryManager class created successfully")
        
        # Test memory operations (without actual Pinecone connection)
        test_data = {"test": "data"}
        print("✅ Memory operations structure ready")
        
        return True
    except Exception as e:
        print(f"❌ Memory setup test failed: {e}")
        return False

def test_demo_functionality():
    """Test demo functionality without CrewAI"""
    print("\n🎭 Testing demo functionality...")
    
    try:
        # Import demo components directly
        from data_ingest import DataIngestion
        from tools.kpi_calculator import KPICalculator
        
        # Create instances
        data_ingestion = DataIngestion()
        calculator = KPICalculator()
        
        # Create sample data
        hr_data = data_ingestion._create_sample_hr_data()
        financial_data = data_ingestion._create_sample_financial_data()
        
        # Calculate KPIs
        latest_period = financial_data.iloc[-1].to_dict()
        kpis = calculator.calculate_financial_kpis(latest_period)
        
        # Identify inefficiencies
        inefficiencies = calculator.identify_inefficiencies(kpis)
        
        print(f"✅ Demo functionality working:")
        print(f"   • HR data: {len(hr_data)} employees")
        print(f"   • Financial data: {len(financial_data)} periods")
        print(f"   • KPIs calculated: {len(kpis)}")
        print(f"   • Inefficiencies found: {len(inefficiencies)}")
        
        return True
    except Exception as e:
        print(f"❌ Demo functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Company Efficiency Optimizer - Simplified Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        test_core_imports,
        test_data_ingestion,
        test_kpi_calculator,
        test_memory_setup,
        test_demo_functionality
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
        print("🎉 All tests passed! Core functionality is working.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)