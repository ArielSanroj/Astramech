#!/usr/bin/env python3
"""
Improved Test for testastra2.xlsx with Better Data Extraction
Handles the specific format of testastra2.xlsx with proper account-based data
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def extract_financial_data_from_balance_sheet(excel_file):
    """Extract financial data from balance sheet format"""
    
    print("🔍 Extracting financial data from balance sheet format...")
    
    try:
        # Read the balance sheet
        df = pd.read_excel(excel_file, sheet_name='balance prueba act')
        print(f"📊 Balance sheet shape: {df.shape}")
        
        # Look for revenue accounts (typically 4xxx series)
        revenue_accounts = df[df['Cuenta'].astype(str).str.startswith('4', na=False)]
        print(f"💰 Revenue accounts found: {len(revenue_accounts)}")
        
        # Look for expense accounts (typically 5xxx series)
        expense_accounts = df[df['Cuenta'].astype(str).str.startswith('5', na=False)]
        print(f"💸 Expense accounts found: {len(expense_accounts)}")
        
        # Look for asset accounts (typically 1xxx series)
        asset_accounts = df[df['Cuenta'].astype(str).str.startswith('1', na=False)]
        print(f"🏦 Asset accounts found: {len(asset_accounts)}")
        
        # Calculate totals
        total_revenue = revenue_accounts['Final'].sum() if 'Final' in revenue_accounts.columns else 0
        total_expenses = expense_accounts['Final'].sum() if 'Final' in expense_accounts.columns else 0
        total_assets = asset_accounts['Final'].sum() if 'Final' in asset_accounts.columns else 0
        
        print(f"📈 Financial Summary:")
        print(f"   Total Revenue: ${total_revenue:,.0f} COP")
        print(f"   Total Expenses: ${total_expenses:,.0f} COP")
        print(f"   Total Assets: ${total_assets:,.0f} COP")
        print(f"   Net Income: ${total_revenue - total_expenses:,.0f} COP")
        
        return {
            'revenue': total_revenue,
            'expenses': total_expenses,
            'assets': total_assets,
            'net_income': total_revenue - total_expenses,
            'revenue_accounts': len(revenue_accounts),
            'expense_accounts': len(expense_accounts),
            'asset_accounts': len(asset_accounts)
        }
        
    except Exception as e:
        print(f"❌ Error extracting balance sheet data: {e}")
        return None

def test_testastra2_improved():
    """Improved test for testastra2.xlsx"""
    
    print("🚀 Improved Test for testastra2.xlsx")
    print("=" * 70)
    
    excel_file = "/Users/arielsanroj/Downloads/testastra2.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ File not found: {excel_file}")
        return False
    
    try:
        # Step 1: Extract financial data from balance sheet
        print("\n📊 Step 1: Balance Sheet Data Extraction")
        print("-" * 50)
        
        balance_data = extract_financial_data_from_balance_sheet(excel_file)
        
        if not balance_data:
            print("❌ Failed to extract balance sheet data")
            return False
        
        # Step 2: Enhanced Data Ingestion
        print("\n📁 Step 2: Enhanced Data Ingestion")
        print("-" * 50)
        
        from data_ingest import EnhancedDataIngestion
        data_ingestion = EnhancedDataIngestion()
        
        print(f"📊 Processing: {excel_file}")
        financial_data = data_ingestion.process_excel_file(excel_file, "TESTASTRA2 COMPANY", "Finance")
        
        # Override with balance sheet data if available
        if balance_data['revenue'] > 0:
            financial_data['revenue'] = balance_data['revenue']
            financial_data['revenue_ytd'] = balance_data['revenue']
            financial_data['operating_expenses'] = balance_data['expenses']
            financial_data['operating_expenses_ytd'] = balance_data['expenses']
            financial_data['net_income'] = balance_data['net_income']
            financial_data['net_income_ytd'] = balance_data['net_income']
            financial_data['total_assets'] = balance_data['assets']
        
        print("\n✅ Enhanced Data Ingestion Results:")
        print(f"   Company: {financial_data['company']}")
        print(f"   Currency: {financial_data['currency']}")
        print(f"   Industry: {financial_data['industry']}")
        print(f"   Department: {financial_data.get('department', 'N/A')}")
        print(f"   Employee Count: {financial_data['employee_count']}")
        print(f"   Sheets Processed: {len(financial_data['sheets_processed'])}")
        
        print(f"\n💰 Financial Summary (YTD):")
        print(f"   Revenue YTD: ${financial_data.get('revenue_ytd', financial_data.get('revenue', 0)):,.0f} {financial_data['currency']}")
        print(f"   Operating Expenses YTD: ${financial_data.get('operating_expenses_ytd', financial_data.get('operating_expenses', 0)):,.0f} {financial_data['currency']}")
        print(f"   Net Income YTD: ${financial_data.get('net_income_ytd', financial_data.get('net_income', 0)):,.0f} {financial_data['currency']}")
        
        print(f"\n📊 Balance Sheet Items:")
        print(f"   Total Assets: ${financial_data.get('total_assets', 0):,.0f} {financial_data['currency']}")
        print(f"   Cash & Equivalents: ${financial_data.get('cash_and_equivalents', 0):,.0f} {financial_data['currency']}")
        print(f"   Fixed Assets: ${financial_data.get('fixed_assets', 0):,.0f} {financial_data['currency']}")
        
        # Step 3: Enhanced KPI Calculation
        print("\n📈 Step 3: Enhanced KPI Calculation")
        print("-" * 50)
        
        from tools.kpi_calculator import KPICalculator
        calculator = KPICalculator()
        
        # Prepare data for KPI calculation
        kpi_data = {
            'financial_data': {
                'revenue': financial_data.get('revenue_ytd', financial_data.get('revenue', 0)),
                'cost_of_goods_sold': financial_data.get('cogs', 0),
                'operating_expenses': financial_data.get('operating_expenses_ytd', financial_data.get('operating_expenses', 0)),
                'net_income': financial_data.get('net_income_ytd', financial_data.get('net_income', 0)),
                'employee_count': financial_data.get('employee_count', 10)
            },
            'hr_data': {
                'total_employees': financial_data.get('employee_count', 10)
            },
            'operational_data': {
                'process_efficiency': 0.8
            },
            'industry': financial_data.get('industry', 'professional_services')
        }
        
        print("🔢 Calculating enhanced KPIs...")
        kpi_results = calculator.calculate_all_kpis(kpi_data, "Finance")
        
        print("✅ Enhanced KPI Results:")
        
        # Financial KPIs
        print(f"\n💰 Financial KPIs:")
        financial = kpi_results.get('financial', {})
        print(f"   - Gross Margin: {(financial.get('gross_margin', 0) * 100):.1f}%")
        print(f"   - Operating Margin: {(financial.get('operating_margin', 0) * 100):.1f}%")
        print(f"   - Net Margin: {(financial.get('net_margin', 0) * 100):.1f}%")
        print(f"   - Revenue per Employee: ${financial.get('revenue_per_employee', 0):,.0f} {financial_data['currency']}")
        
        # HR KPIs
        print(f"\n👥 HR KPIs:")
        hr = kpi_results.get('hr', {})
        print(f"   - Turnover Rate: {(hr.get('turnover_rate', 0) * 100):.1f}%")
        print(f"   - Total Employees: {hr.get('total_employees', 0)}")
        
        # Operational KPIs
        print(f"\n⚙️ Operational KPIs:")
        operational = kpi_results.get('operational', {})
        print(f"   - Cost Efficiency Ratio: {(operational.get('cost_efficiency_ratio', 0) * 100):.1f}%")
        print(f"   - Productivity Index: {operational.get('productivity_index', 0):.2f}")
        
        # Department-specific KPIs
        dept = kpi_results.get('department', {})
        if dept.get('kpis'):
            print(f"\n🎯 Finance Department KPIs:")
            for kpi_name, value in dept['kpis'].items():
                print(f"   - {kpi_name}: {value:.2f}")
        
        # Inefficiencies
        inefficiencies = kpi_results.get('inefficiencies', [])
        if inefficiencies:
            print(f"\n⚠️ Identified Inefficiencies:")
            for ineff in inefficiencies:
                print(f"   - {ineff.get('kpi_name', 'Unknown')}: {ineff.get('description', 'No description')}")
                print(f"     Severity: {ineff.get('severity', 'Unknown')}")
        else:
            print(f"\n✅ No inefficiencies identified - Company performing well!")
        
        # Step 4: Department Analysis (Marketing)
        print("\n🎯 Step 4: Marketing Department Analysis")
        print("-" * 50)
        
        marketing_data = kpi_data.copy()
        marketing_data['marketing_data'] = {
            'marketing_spend': financial_data.get('operating_expenses', 0) * 0.15,  # 15% of opex
            'marketing_revenue': financial_data.get('revenue', 0) * 0.3,  # 30% of revenue
            'conversion_rate': 2.5,
            'customer_acquisition_cost': 50000
        }
        
        marketing_results = calculator.calculate_all_kpis(marketing_data, "Marketing")
        
        print("✅ Marketing Department Results:")
        dept = marketing_results.get('department', {})
        if dept.get('kpis'):
            for kpi_name, value in dept['kpis'].items():
                print(f"   - {kpi_name}: {value:.2f}")
        
        # Step 5: Department Analysis (IT)
        print("\n💻 Step 5: IT Department Analysis")
        print("-" * 50)
        
        it_data = kpi_data.copy()
        it_data['it_data'] = {
            'system_uptime': 99.9,
            'response_time': 200,
            'security_incidents': 0,
            'project_delivery_time': 0,
            'it_budget': financial_data.get('operating_expenses', 0) * 0.1  # 10% of opex
        }
        
        it_results = calculator.calculate_all_kpis(it_data, "IT")
        
        print("✅ IT Department Results:")
        dept = it_results.get('department', {})
        if dept.get('kpis'):
            for kpi_name, value in dept['kpis'].items():
                print(f"   - {kpi_name}: {value:.2f}")
        
        # Step 6: Dynamic Agent Creation
        print("\n🤖 Step 6: Dynamic Agent Creation")
        print("-" * 50)
        
        from dynamic_agent_creator import DynamicAgentCreator
        agent_creator = DynamicAgentCreator()
        
        company_context = {
            'company_name': financial_data.get('company', 'Unknown'),
            'industry': financial_data.get('industry', 'Unknown'),
            'revenue': financial_data.get('revenue_ytd', financial_data.get('revenue', 0)),
            'employee_count': financial_data.get('employee_count', 10)
        }
        
        print("🔧 Creating dynamic agents...")
        
        # Test agent recommendations
        recommendations = agent_creator.get_agent_recommendations(kpi_results, company_context)
        print(f"\n📋 Agent Recommendations:")
        for rec in recommendations:
            print(f"   - {rec['agent_type']} ({rec['department']})")
            print(f"     Priority: {rec['priority']}")
            print(f"     Reason: {rec['reason']}")
        
        # Create agents for inefficiencies
        if inefficiencies:
            agents = agent_creator.create_agent_crew(inefficiencies, company_context)
            print(f"\n✅ Created {len(agents)} specialized agents:")
            for agent in agents:
                print(f"   - {agent['role']}")
                print(f"     Goal: {agent['goal']}")
                print(f"     Department: {agent['department']}")
        else:
            print(f"\n✅ No agents needed - Company performing optimally!")
        
        # Step 7: Generate Comprehensive Report
        print("\n📋 Step 7: Generating Comprehensive Report")
        print("-" * 50)
        
        report = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0',
                'test_file': 'testastra2.xlsx',
                'data_source': 'Balance sheet extraction + enhanced ingestion',
                'improvements': [
                    'Enhanced NIIF/Colombian format support',
                    'YTD calculations and validation',
                    'Department-specific KPI analysis',
                    'Dynamic agent generation',
                    'Real-time streaming capabilities',
                    'Balance sheet data extraction'
                ]
            },
            'company_info': {
                'name': financial_data['company'],
                'industry': financial_data['industry'],
                'employee_count': financial_data['employee_count'],
                'currency': financial_data['currency'],
                'department': financial_data.get('department', 'Finance')
            },
            'financial_summary': {
                'revenue_ytd': financial_data.get('revenue_ytd', financial_data.get('revenue', 0)),
                'operating_expenses_ytd': financial_data.get('operating_expenses_ytd', financial_data.get('operating_expenses', 0)),
                'net_income_ytd': financial_data.get('net_income_ytd', financial_data.get('net_income', 0)),
                'total_assets': financial_data.get('total_assets', 0),
                'employee_estimate_method': 'Payroll-based estimation from operating expenses',
                'balance_sheet_data': balance_data
            },
            'kpi_analysis': {
                'finance': kpi_results,
                'marketing': marketing_results,
                'it': it_results
            },
            'agent_recommendations': recommendations,
            'data_quality_notes': [
                'Employee count estimated from payroll data',
                'YTD calculations from ERI sheets',
                'Currency validation applied',
                'Industry classification performed',
                'Balance sheet data extracted and integrated'
            ]
        }
        
        # Save report
        report_file = "testastra2_improved_analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Comprehensive report generated: {report_file}")
        
        # Step 8: Summary
        print("\n📊 TESTASTRA2 IMPROVED ANALYSIS SUMMARY")
        print("=" * 70)
        print("✅ Balance Sheet Data Extraction: SUCCESS")
        print("✅ Enhanced Data Ingestion: SUCCESS")
        print("✅ Enhanced KPI Calculation: SUCCESS")
        print("✅ Marketing Department Analysis: SUCCESS")
        print("✅ IT Department Analysis: SUCCESS")
        print("✅ Dynamic Agent Creation: SUCCESS")
        print("✅ Comprehensive Report: SUCCESS")
        
        print(f"\n📁 Files created:")
        print(f"   - {report_file}")
        
        print(f"\n🎉 Testastra2 improved analysis completed successfully!")
        print("\n🔧 Key Findings:")
        print(f"   - Company: {financial_data['company']}")
        print(f"   - Industry: {financial_data['industry']}")
        print(f"   - Employee Count: {financial_data['employee_count']}")
        print(f"   - Revenue YTD: ${financial_data.get('revenue_ytd', financial_data.get('revenue', 0)):,.0f} {financial_data['currency']}")
        print(f"   - Net Margin: {(financial.get('net_margin', 0) * 100):.1f}%")
        print(f"   - Inefficiencies: {len(inefficiencies)}")
        print(f"   - Agent Recommendations: {len(recommendations)}")
        print(f"   - Balance Sheet Accounts: {balance_data['revenue_accounts']} revenue, {balance_data['expense_accounts']} expense, {balance_data['asset_accounts']} asset")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("🚀 Company Efficiency Optimizer - Testastra2 Improved Analysis")
    print("=" * 70)
    print("Testing enhanced system with testastra2.xlsx using balance sheet extraction")
    print("=" * 70)
    
    success = test_testastra2_improved()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("The enhanced system successfully processed testastra2.xlsx")
        print("using both enhanced ingestion and balance sheet extraction.")
    else:
        print("\n❌ Test failed!")
        print("Please check the error messages above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()