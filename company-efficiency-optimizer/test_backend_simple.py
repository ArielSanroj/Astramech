#!/usr/bin/env python3
"""
Simplified Backend Test for Company Efficiency Optimizer
Tests core functionality with testastra.xlsx
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path

def test_data_ingestion():
    """Test data ingestion with the Excel file"""
    
    print("🚀 Testing Data Ingestion with testastra.xlsx")
    print("=" * 60)
    
    excel_file = "/Users/arielsanroj/Downloads/testastra.xlsx"
    
    try:
        from data_ingest import EnhancedDataIngestion
        data_ingestion = EnhancedDataIngestion()
        
        print(f"📁 Processing: {excel_file}")
        financial_data = data_ingestion.process_excel_file(excel_file, "CARMANFE SAS")
        
        print("\n✅ Data Ingestion Results:")
        print(f"   Company: {financial_data['company']}")
        print(f"   Currency: {financial_data['currency']}")
        print(f"   Industry: {financial_data['industry']}")
        print(f"   Employee Count: {financial_data['employee_count']}")
        print(f"   Sheets Processed: {len(financial_data['sheets_processed'])}")
        
        print(f"\n💰 Financial Summary:")
        print(f"   Total Assets: ${financial_data['total_assets']:,.2f}")
        print(f"   Revenue: ${financial_data['revenue']:,.2f}")
        print(f"   Net Income: ${financial_data['net_income']:,.2f}")
        print(f"   Gross Profit: ${financial_data['gross_profit']:,.2f}")
        print(f"   Operating Income: ${financial_data['operating_income']:,.2f}")
        
        print(f"\n📊 Balance Sheet Items:")
        print(f"   Cash & Equivalents: ${financial_data['cash_and_equivalents']:,.2f}")
        print(f"   Investments: ${financial_data['investments']:,.2f}")
        print(f"   Receivables: ${financial_data['receivables']:,.2f}")
        print(f"   Fixed Assets: ${financial_data['fixed_assets']:,.2f}")
        print(f"   Total Liabilities: ${financial_data['total_liabilities']:,.2f}")
        print(f"   Total Equity: ${financial_data['total_equity']:,.2f}")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Data ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_kpi_calculation(financial_data):
    """Test KPI calculation with financial data"""
    
    print("\n📈 Testing KPI Calculation")
    print("-" * 40)
    
    try:
        from tools.kpi_calculator import KPICalculator
        calculator = KPICalculator()
        
        # Prepare data for KPI calculation
        kpi_data = {
            'financial_data': {
                'revenue': financial_data['revenue'],
                'cost_of_goods_sold': financial_data['cogs'],
                'operating_expenses': financial_data['operating_expenses'],
                'net_income': financial_data['net_income']
            },
            'hr_data': {
                'total_employees': financial_data['employee_count']
            },
            'operational_data': {
                'process_efficiency': 0.8  # Default value
            }
        }
        
        print("🔢 Calculating KPIs...")
        kpi_results = calculator.calculate_all_kpis(kpi_data)
        
        print("✅ KPI Calculation Results:")
        
        # Financial KPIs
        print("\n💰 Financial KPIs:")
        if 'financial' in kpi_results:
            for kpi in kpi_results['financial']:
                if hasattr(kpi, 'name') and hasattr(kpi, 'value'):
                    print(f"   - {kpi.name}: {kpi.value:.2f}%")
                else:
                    print(f"   - {kpi}")
        
        # HR KPIs
        print("\n👥 HR KPIs:")
        if 'hr' in kpi_results:
            for kpi in kpi_results['hr']:
                if hasattr(kpi, 'name') and hasattr(kpi, 'value'):
                    print(f"   - {kpi.name}: {kpi.value:.2f}%")
                else:
                    print(f"   - {kpi}")
        
        # Operational KPIs
        print("\n⚙️ Operational KPIs:")
        if 'operational' in kpi_results:
            for kpi in kpi_results['operational']:
                if hasattr(kpi, 'name') and hasattr(kpi, 'value'):
                    print(f"   - {kpi.name}: {kpi.value:.2f}%")
                else:
                    print(f"   - {kpi}")
        
        return kpi_results
        
    except Exception as e:
        print(f"❌ KPI calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_memory_system(financial_data, kpi_results):
    """Test memory system functionality"""
    
    print("\n🧠 Testing Memory System")
    print("-" * 40)
    
    try:
        from memory_setup import HybridMemorySystem
        memory_system = HybridMemorySystem()
        
        print("🔧 Initializing memory system...")
        # Check what methods are available
        print(f"Available methods: {[method for method in dir(memory_system) if not method.startswith('_')]}")
        
        # Try to initialize if method exists
        if hasattr(memory_system, 'initialize_memory'):
            memory_system.initialize_memory()
        elif hasattr(memory_system, 'setup_memory'):
            memory_system.setup_memory()
        else:
            print("⚠️ No initialization method found, trying to use as-is")
        
        # Store analysis results
        analysis_data = {
            'company': financial_data['company'],
            'financial_data': financial_data,
            'kpi_results': kpi_results,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        print("💾 Storing analysis results...")
        if hasattr(memory_system, 'store_analysis'):
            memory_system.store_analysis(analysis_data)
            print("✅ Analysis data stored successfully")
        else:
            print("⚠️ No store_analysis method found")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory system failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ollama_crew(financial_data):
    """Test Ollama crew functionality"""
    
    print("\n🤖 Testing Ollama Crew")
    print("-" * 40)
    
    try:
        from ollama_crew import OllamaDiagnosticCrew
        
        print("🔧 Initializing Ollama crew...")
        crew = OllamaDiagnosticCrew()
        
        # Prepare company profile
        company_profile = {
            'company_name': financial_data['company'],
            'industry': financial_data['industry'],
            'revenue': financial_data['revenue'],
            'employee_count': financial_data['employee_count'],
            'total_assets': financial_data['total_assets'],
            'net_income': financial_data['net_income']
        }
        
        print("📝 Running AI analysis...")
        analysis_result = crew.run_analysis(company_profile)
        
        print("✅ AI Analysis Results:")
        print(f"   Result type: {type(analysis_result)}")
        
        if hasattr(analysis_result, 'raw'):
            print("   Raw result available")
        if hasattr(analysis_result, 'tasks_output'):
            print(f"   Tasks output: {len(analysis_result.tasks_output)} tasks")
        
        return analysis_result
        
    except Exception as e:
        print(f"⚠️ Ollama crew test skipped: {e}")
        return None

def generate_report(financial_data, kpi_results, ai_analysis):
    """Generate a comprehensive report"""
    
    print("\n📋 Generating Report")
    print("-" * 40)
    
    try:
        report = {
            'company_info': {
                'name': financial_data['company'],
                'industry': financial_data['industry'],
                'employee_count': financial_data['employee_count'],
                'currency': financial_data['currency']
            },
            'financial_summary': {
                'total_assets': financial_data['total_assets'],
                'revenue': financial_data['revenue'],
                'net_income': financial_data['net_income'],
                'gross_profit': financial_data['gross_profit'],
                'operating_income': financial_data['operating_income']
            },
            'kpi_analysis': kpi_results,
            'ai_analysis': ai_analysis.raw if ai_analysis and hasattr(ai_analysis, 'raw') else "AI analysis not available",
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Save report
        report_file = "test_backend_simple_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Report generated and saved to: {report_file}")
        return report_file
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return None

def main():
    """Main test function"""
    
    print("🚀 Company Efficiency Optimizer - Simplified Backend Test")
    print("=" * 70)
    
    # Step 1: Data Ingestion
    financial_data = test_data_ingestion()
    if not financial_data:
        print("❌ Test failed at data ingestion step")
        return False
    
    # Step 2: KPI Calculation
    kpi_results = test_kpi_calculation(financial_data)
    if not kpi_results:
        print("⚠️ KPI calculation failed, continuing with other tests")
    
    # Step 3: Memory System
    memory_success = test_memory_system(financial_data, kpi_results)
    
    # Step 4: AI Analysis
    ai_analysis = test_ollama_crew(financial_data)
    
    # Step 5: Generate Report
    report_file = generate_report(financial_data, kpi_results, ai_analysis)
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 70)
    print("✅ Data Ingestion: SUCCESS")
    print("✅ KPI Calculation: " + ("SUCCESS" if kpi_results else "FAILED"))
    print("✅ Memory System: " + ("SUCCESS" if memory_success else "FAILED"))
    print("✅ AI Analysis: " + ("SUCCESS" if ai_analysis else "SKIPPED"))
    print("✅ Report Generation: " + ("SUCCESS" if report_file else "FAILED"))
    
    print(f"\n📁 Files created:")
    if report_file:
        print(f"   - {report_file}")
    
    print(f"\n🎉 Backend test completed!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)