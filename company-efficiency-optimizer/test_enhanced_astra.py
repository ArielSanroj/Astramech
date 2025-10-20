#!/usr/bin/env python3
"""
Enhanced test script for CARMANFE SAS using the new data ingestion module

This script demonstrates the enhanced capabilities including:
- Multi-sheet processing
- Colombian accounting format support
- Dynamic industry classification
- Department-specific data extraction
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from enhanced_data_ingest import EnhancedDataIngestion
from tools.kpi_calculator import KPICalculator

def test_enhanced_data_ingestion():
    """Test the enhanced data ingestion with CARMANFE SAS data"""
    print("🚀 Enhanced Data Ingestion Test - CARMANFE SAS")
    print("=" * 60)
    
    try:
        # Initialize enhanced data ingestion
        ingestion = EnhancedDataIngestion()
        
        # Process the Excel file
        print("📊 Processing Excel file with enhanced ingestion...")
        financial_data = ingestion.process_excel_file(
            '/Users/arielsanroj/Downloads/testastra.xlsx',
            company_name='CARMANFE SAS'
        )
        
        if not financial_data:
            print("❌ Failed to process financial data")
            return None
        
        print(f"\n✅ Successfully processed {len(financial_data['sheets_processed'])} sheets:")
        for sheet in financial_data['sheets_processed']:
            print(f"   • {sheet}")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Error in enhanced data ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def run_enhanced_kpi_analysis(financial_data):
    """Run KPI analysis with industry-specific benchmarks"""
    print(f"\n📈 Enhanced KPI Analysis for {financial_data.get('company', 'Company')}")
    print("-" * 60)
    
    try:
        # Initialize KPI calculator
        calculator = KPICalculator()
        
        # Get industry for appropriate benchmarks
        industry = financial_data.get('industry', 'services')
        print(f"🏭 Using {industry} industry benchmarks")
        
        # Calculate financial KPIs
        kpis = calculator.calculate_financial_kpis(financial_data, industry=industry)
        
        # Display results
        print(f"\n📊 Financial KPIs ({industry.title()} Industry):")
        for kpi in kpis:
            status_emoji = {
                'excellent': '🟢',
                'good': '🟡', 
                'warning': '🟠',
                'critical': '🔴'
            }
            emoji = status_emoji.get(kpi.status, '⚪')
            print(f"  {emoji} {kpi.name}: {kpi.value:.1f}% (Benchmark: {kpi.benchmark:.1f}%)")
            print(f"      Status: {kpi.status.upper()}")
            print(f"      Description: {kpi.description}")
            print()
        
        # Identify inefficiencies
        print("🔍 Inefficiency Analysis:")
        inefficiencies = calculator.identify_inefficiencies(kpis)
        
        if inefficiencies:
            print(f"\n⚠️  Found {len(inefficiencies)} inefficiencies:")
            for i, inefficiency in enumerate(inefficiencies, 1):
                print(f"  {i}. {inefficiency['kpi_name']}: {inefficiency['severity']} severity")
                print(f"     Current: {inefficiency['current_value']:.1f}% vs Benchmark: {inefficiency['benchmark']:.1f}%")
                print(f"     Recommended agent: {inefficiency['recommended_agent']}")
                print(f"     Issue type: {inefficiency['issue_type']}")
                print()
        else:
            print("✅ No critical inefficiencies found!")
        
        return kpis, inefficiencies
        
    except Exception as e:
        print(f"❌ Error in enhanced KPI analysis: {str(e)}")
        return [], []

def generate_enhanced_summary(financial_data, kpis, inefficiencies):
    """Generate enhanced executive summary"""
    print(f"\n📋 Enhanced Executive Summary for {financial_data.get('company', 'Company')}")
    print("=" * 70)
    
    print(f"Company: {financial_data.get('company', 'Unknown')}")
    print(f"Industry: {financial_data.get('industry', 'Unknown').title()}")
    print(f"Period: {financial_data.get('period', 'Unknown')}")
    print(f"Currency: {financial_data.get('currency', 'Unknown')}")
    print(f"Sheets Processed: {len(financial_data.get('sheets_processed', []))}")
    
    print(f"\n💰 Financial Overview:")
    print(f"   • Revenue: ${financial_data.get('revenue', 0):,.0f} {financial_data.get('currency', '')}")
    print(f"   • Net Income: ${financial_data.get('net_income', 0):,.0f} {financial_data.get('currency', '')}")
    print(f"   • Total Assets: ${financial_data.get('total_assets', 0):,.0f} {financial_data.get('currency', '')}")
    print(f"   • Employee Count: {financial_data.get('employee_count', 0)}")
    
    print(f"\n📊 Key Performance Indicators:")
    for kpi in kpis:
        status_emoji = {'excellent': '🟢', 'good': '🟡', 'warning': '🟠', 'critical': '🔴'}
        emoji = status_emoji.get(kpi.status, '⚪')
        print(f"  {emoji} {kpi.name}: {kpi.value:.1f}%")
    
    if inefficiencies:
        print(f"\n⚠️  Critical Issues Identified:")
        for inefficiency in inefficiencies:
            print(f"  • {inefficiency['kpi_name']}: {inefficiency['severity']} severity")
            print(f"    Recommended action: Deploy {inefficiency['recommended_agent']}")
    
    # Show processed sheets
    if financial_data.get('sheets_processed'):
        print(f"\n📋 Processed Financial Statements:")
        for sheet in financial_data['sheets_processed']:
            print(f"   • {sheet}")
    
    # Show HR data if available
    if 'hr_data' in financial_data and financial_data['hr_data']:
        hr_data = financial_data['hr_data']
        print(f"\n👥 HR Information:")
        print(f"   • Employee Count: {hr_data.get('employee_count', 'Not available')}")
        if hr_data.get('departments'):
            print(f"   • Departments: {', '.join(hr_data['departments'][:3])}...")
    
    print(f"\n🎯 Recommended Next Steps:")
    print("  1. Review financial performance against industry benchmarks")
    print("  2. Implement targeted optimization strategies")
    print("  3. Monitor KPIs on a regular basis")
    print("  4. Consider specialized agent recommendations for critical issues")
    print("  5. Leverage multi-sheet analysis for comprehensive insights")

def main():
    """Run the enhanced test with CARMANFE SAS data"""
    print("🚀 Company Efficiency Optimizer - Enhanced Test")
    print("=" * 70)
    print("Testing enhanced data ingestion capabilities")
    print("Company: CARMANFE SAS")
    print("Features: Multi-sheet processing, Colombian accounting, Industry classification")
    print()
    
    try:
        # Step 1: Test enhanced data ingestion
        financial_data = test_enhanced_data_ingestion()
        if not financial_data:
            print("❌ Failed to process financial data")
            return 1
        
        # Step 2: Run enhanced KPI analysis
        kpis, inefficiencies = run_enhanced_kpi_analysis(financial_data)
        
        # Step 3: Generate enhanced summary
        generate_enhanced_summary(financial_data, kpis, inefficiencies)
        
        print("\n" + "=" * 70)
        print("🎉 Enhanced test completed successfully!")
        print("\n📝 Key Achievements:")
        print(f"   • Processed {len(financial_data.get('sheets_processed', []))} financial sheets")
        print(f"   • Classified industry as: {financial_data.get('industry', 'Unknown')}")
        print(f"   • Analyzed {len(kpis)} key performance indicators")
        print(f"   • Identified {len(inefficiencies)} areas for improvement")
        print(f"   • Used appropriate industry benchmarks")
        print(f"   • Demonstrated multi-format data processing")
        
        return 0
        
    except Exception as e:
        print(f"❌ Enhanced test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())