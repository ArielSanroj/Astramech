#!/usr/bin/env python3
"""
Test script for testastra.xlsx file parsing
"""

import os
import sys
import json
from data_ingest import EnhancedDataIngestion
from tools.kpi_calculator import KPICalculator

def test_testastra_parsing():
    """Test parsing of testastra.xlsx file"""
    
    file_path = '/Users/arielsanroj/Downloads/testastra2.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📊 Testing file: {file_path}")
    print(f"   File size: {os.path.getsize(file_path) / 1024:.1f} KB\n")
    
    # Initialize data ingestion
    data_ingestion = EnhancedDataIngestion()
    
    # Test Excel parsing
    print("=" * 60)
    print("STEP 1: Parsing Excel file with EnhancedDataIngestion")
    print("=" * 60)
    
    try:
        structured_data = data_ingestion.process_excel_file(
            file_path,
            company_name="TestAstra",
            department='Finance'
        )
        
        if not structured_data:
            print("❌ Parsing returned empty data")
            return False
        
        print("\n✅ Parsing successful!")
        print(f"\n📋 Extracted Data Summary:")
        print(f"   Company: {structured_data.get('company', 'N/A')}")
        print(f"   Industry: {structured_data.get('industry', 'N/A')}")
        print(f"   Currency: {structured_data.get('currency', 'N/A')}")
        print(f"   Period: {structured_data.get('period', 'N/A')}")
        print(f"   Employee Count: {structured_data.get('employee_count', 'N/A')}")
        
        # Financial metrics
        print(f"\n💰 Financial Metrics:")
        revenue = structured_data.get('revenue')
        cogs = structured_data.get('cogs')
        operating_expenses = structured_data.get('operating_expenses')
        operating_income = structured_data.get('operating_income')
        net_income = structured_data.get('net_income')
        
        if revenue:
            print(f"   Revenue: ${revenue:,.0f} {structured_data.get('currency', '')}")
        if cogs:
            print(f"   COGS: ${cogs:,.0f}")
        if operating_expenses:
            print(f"   Operating Expenses: ${operating_expenses:,.0f}")
        if operating_income:
            print(f"   Operating Income: ${operating_income:,.0f}")
        if net_income:
            print(f"   Net Income: ${net_income:,.0f}")
        
        # Balance sheet metrics
        print(f"\n📊 Balance Sheet Metrics:")
        total_assets = structured_data.get('total_assets')
        total_liabilities = structured_data.get('total_liabilities')
        total_equity = structured_data.get('total_equity')
        cash = structured_data.get('cash_and_equivalents')
        
        if total_assets:
            print(f"   Total Assets: ${total_assets:,.0f}")
        if total_liabilities:
            print(f"   Total Liabilities: ${total_liabilities:,.0f}")
        if total_equity:
            print(f"   Total Equity: ${total_equity:,.0f}")
        if cash:
            print(f"   Cash & Equivalents: ${cash:,.0f}")
        
        # Sheets processed
        sheets_processed = structured_data.get('sheets_processed', [])
        if sheets_processed:
            print(f"\n📑 Sheets Processed:")
            for sheet in sheets_processed:
                print(f"   - {sheet}")
        
        # Test KPI calculation
        print("\n" + "=" * 60)
        print("STEP 2: Testing KPI Calculation")
        print("=" * 60)
        
        # Create sample data structure
        sample_data = {
            'financial_data': {
                'revenue': revenue or 0,
                'cost_of_goods_sold': cogs or 0,
                'operating_expenses': operating_expenses or 0,
                'net_income': net_income or 0,
                'total_assets': total_assets or 0,
                'total_liabilities': total_liabilities or 0,
                'total_equity': total_equity or 0,
            },
            'hr_data': {
                'total_employees': structured_data.get('employee_count', 50),
            },
            'operational_data': {}
        }
        
        kpi_calculator = KPICalculator()
        kpi_results = kpi_calculator.calculate_all_kpis(sample_data)
        
        print(f"\n✅ KPI Calculation successful!")
        
        # Extract all KPIs from raw_kpis
        all_kpis = []
        raw_kpis = kpi_results.get('raw_kpis', {})
        for category in ['financial', 'hr', 'operational', 'department']:
            all_kpis.extend(raw_kpis.get(category, []))
        
        print(f"   Total KPIs calculated: {len(all_kpis)}")
        
        # Show efficiency score
        efficiency_score = kpi_results.get('efficiency_score')
        if efficiency_score is not None:
            print(f"   Overall Efficiency Score: {efficiency_score}%")
        
        # Show financial KPIs summary
        financial = kpi_results.get('financial', {})
        if financial:
            print(f"\n💰 Financial KPIs:")
            if financial.get('gross_margin') is not None:
                print(f"   Gross Margin: {financial['gross_margin']*100:.2f}%")
            if financial.get('operating_margin') is not None:
                print(f"   Operating Margin: {financial['operating_margin']*100:.2f}%")
            if financial.get('net_margin') is not None:
                print(f"   Net Margin: {financial['net_margin']*100:.2f}%")
            if financial.get('revenue_per_employee') is not None:
                print(f"   Revenue per Employee: ${financial['revenue_per_employee']:,.0f}")
        
        # Show HR KPIs
        hr = kpi_results.get('hr', {})
        if hr:
            print(f"\n👥 HR KPIs:")
            if hr.get('total_employees') is not None:
                print(f"   Total Employees: {hr['total_employees']}")
            if hr.get('turnover_rate') is not None:
                print(f"   Turnover Rate: {hr['turnover_rate']*100:.2f}%")
        
        # Show operational KPIs
        operational = kpi_results.get('operational', {})
        if operational:
            print(f"\n⚙️  Operational KPIs:")
            if operational.get('cost_efficiency_ratio') is not None:
                print(f"   Cost Efficiency Ratio: {operational['cost_efficiency_ratio']*100:.2f}%")
            if operational.get('productivity_index') is not None:
                print(f"   Productivity Index: {operational['productivity_index']:.2f}")
        
        # Show some key raw KPIs
        if all_kpis:
            print(f"\n📈 Sample Raw KPIs:")
            for kpi in all_kpis[:10]:  # Show first 10
                kpi_name = kpi.get('name', 'Unknown')
                kpi_value = kpi.get('value')
                kpi_benchmark = kpi.get('benchmark')
                kpi_status = kpi.get('status', 'unknown')
                
                status_icon = "✅" if kpi_status == 'good' else "⚠️" if kpi_status == 'warning' else "❌"
                
                if kpi_value is not None:
                    if kpi_benchmark is not None:
                        print(f"   {status_icon} {kpi_name}: {kpi_value:.2f}% (Benchmark: {kpi_benchmark:.2f}%)")
                    else:
                        print(f"   {status_icon} {kpi_name}: {kpi_value:.2f}%")
                else:
                    print(f"   ⚠️  {kpi_name}: N/A")
            
            if len(all_kpis) > 10:
                print(f"   ... and {len(all_kpis) - 10} more KPIs")
        
        # Check for N/A values
        na_count = sum(1 for kpi in all_kpis if kpi.get('value') is None or str(kpi.get('value')) == 'N/A')
        if na_count == 0:
            print(f"\n✅ All KPIs have valid values (no N/A)")
        else:
            print(f"\n⚠️  {na_count} KPIs have N/A values")
        
        # Show inefficiencies
        inefficiencies = kpi_results.get('inefficiencies', [])
        if inefficiencies:
            print(f"\n⚠️  Identified Inefficiencies: {len(inefficiencies)}")
            for ineff in inefficiencies[:5]:
                print(f"   - {ineff.get('issue_type', 'Unknown')}: {ineff.get('description', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during parsing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🧪 Testing testastra2.xlsx parsing\n")
    success = test_testastra_parsing()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ TEST PASSED - File parsing and KPI calculation successful!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED - Check errors above")
        print("=" * 60)
        sys.exit(1)

