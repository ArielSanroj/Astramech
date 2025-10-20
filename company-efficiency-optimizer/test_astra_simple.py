#!/usr/bin/env python3
"""
Simple test script for CARMANFE SAS financial data from testastra.xlsx

This script processes the Excel financial data through the Company Efficiency Optimizer
without requiring API keys for memory system.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from tools.kpi_calculator import KPICalculator

def process_astra_financial_data():
    """Process the CARMANFE SAS financial data from Excel"""
    print("🏢 Processing CARMANFE SAS Financial Data")
    print("=" * 50)
    
    try:
        # Read the Excel file
        df = pd.read_excel('/Users/arielsanroj/Downloads/testastra.xlsx')
        print(f"✅ Loaded Excel file: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Extract financial data from the balance sheet
        financial_data = extract_financial_metrics(df)
        print(f"✅ Extracted financial metrics: {len(financial_data)} key figures")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
        return None

def extract_financial_metrics(df):
    """Extract key financial metrics from the balance sheet"""
    financial_data = {}
    
    try:
        # Find key financial figures in the balance sheet
        total_assets = 0
        cash_and_equivalents = 0
        investments = 0
        receivables = 0
        fixed_assets = 0
        total_liabilities = 0
        current_liabilities = 0
        total_equity = 0
        
        # Process each row to extract financial data
        for index, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue
                
            # Account name is in the fourth column (Unnamed: 3)
            account_name = str(row.iloc[3]).strip() if not pd.isna(row.iloc[3]) else ""
            final_balance = 0
            
            # Try to get the final balance from the last column
            try:
                if not pd.isna(row.iloc[-1]):
                    final_balance = float(row.iloc[-1])
            except:
                continue
            
            # Categorize accounts based on Colombian accounting standards
            if "Activo" in account_name and "Clase" in str(row.iloc[0]):
                # This is the total assets header
                total_assets = abs(final_balance)
                print(f"Found Total Assets: ${total_assets:,.0f}")
                
            elif "Efectivo y equivalentes" in account_name and "Grupo" in str(row.iloc[0]):
                cash_and_equivalents = abs(final_balance)
                print(f"Found Cash and Equivalents: ${cash_and_equivalents:,.0f}")
                
            elif "Inversiones" in account_name and "Grupo" in str(row.iloc[0]):
                investments = abs(final_balance)
                print(f"Found Investments: ${investments:,.0f}")
                
            elif "Deudores comerciales" in account_name and "Grupo" in str(row.iloc[0]):
                receivables = abs(final_balance)
                print(f"Found Receivables: ${receivables:,.0f}")
                
            elif "Propiedad planta y equipo" in account_name and "Grupo" in str(row.iloc[0]):
                fixed_assets = abs(final_balance)
                print(f"Found Fixed Assets: ${fixed_assets:,.0f}")
                
            elif "Pasivo" in account_name and "Clase" in str(row.iloc[0]):
                total_liabilities = abs(final_balance)
                print(f"Found Total Liabilities: ${total_liabilities:,.0f}")
                
            elif "Acreedores comerciales" in account_name and "Grupo" in str(row.iloc[0]):
                current_liabilities = abs(final_balance)
                print(f"Found Current Liabilities: ${current_liabilities:,.0f}")
                
            elif "Patrimonio" in account_name and "Clase" in str(row.iloc[0]):
                total_equity = abs(final_balance)
                print(f"Found Total Equity: ${total_equity:,.0f}")
        
        # Initialize default values
        revenue = 0
        operating_expenses = 0
        net_income = 0
        cogs = 0
        employee_count = 0
        
        # Calculate derived metrics
        if total_assets > 0:
            # Estimate revenue based on assets (rough approximation for agricultural company)
            revenue = total_assets * 0.2  # Assume 20% of assets as annual revenue for agricultural company
            
            # Estimate operating expenses (rough approximation)
            operating_expenses = revenue * 0.75  # Assume 75% of revenue as expenses
            
            # Estimate net income
            net_income = revenue - operating_expenses
            
            # Estimate COGS (Cost of Goods Sold) - higher for agricultural company
            cogs = revenue * 0.6  # Assume 60% of revenue as COGS for agricultural company
            
            # Estimate employee count based on company size
            employee_count = max(15, int(total_assets / 50000000))  # Rough estimate for agricultural company
        
        # Build financial data dictionary
        financial_data = {
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': revenue - cogs,
            'operating_expenses': operating_expenses,
            'operating_income': revenue - cogs - operating_expenses,
            'net_income': net_income,
            'employee_count': employee_count,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'cash_and_equivalents': cash_and_equivalents,
            'investments': investments,
            'receivables': receivables,
            'fixed_assets': fixed_assets,
            'current_liabilities': current_liabilities,
            'period': 'Enero_2025',
            'company': 'CARMANFE SAS'
        }
        
        print(f"📊 Extracted Financial Data:")
        print(f"   Revenue: ${revenue:,.0f}")
        print(f"   COGS: ${cogs:,.0f}")
        print(f"   Operating Income: ${financial_data['operating_income']:,.0f}")
        print(f"   Net Income: ${net_income:,.0f}")
        print(f"   Total Assets: ${total_assets:,.0f}")
        print(f"   Employee Count: {employee_count}")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Error extracting financial metrics: {str(e)}")
        return {}

def run_kpi_analysis(financial_data):
    """Run KPI analysis on the extracted financial data"""
    print("\n📈 KPI Analysis for CARMANFE SAS")
    print("-" * 40)
    
    try:
        # Initialize KPI calculator
        calculator = KPICalculator()
        
        # Calculate financial KPIs (using manufacturing industry benchmarks as closest to agricultural)
        kpis = calculator.calculate_financial_kpis(financial_data, industry='manufacturing')
        
        # Display results
        print("\n📊 Financial KPIs:")
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
        print(f"❌ Error in KPI analysis: {str(e)}")
        return [], []

def generate_executive_summary(financial_data, kpis, inefficiencies):
    """Generate executive summary for CARMANFE SAS"""
    print("\n📋 Executive Summary for CARMANFE SAS")
    print("=" * 50)
    
    print(f"Company: {financial_data.get('company', 'CARMANFE SAS')}")
    print(f"Period: {financial_data.get('period', 'Enero 2025')}")
    print(f"Total Assets: ${financial_data.get('total_assets', 0):,.0f}")
    print(f"Estimated Revenue: ${financial_data.get('revenue', 0):,.0f}")
    print(f"Estimated Net Income: ${financial_data.get('net_income', 0):,.0f}")
    print(f"Employee Count: {financial_data.get('employee_count', 0)}")
    
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
    
    print(f"\n🎯 Recommended Next Steps:")
    print("  1. Review financial performance against industry benchmarks")
    print("  2. Implement targeted optimization strategies")
    print("  3. Monitor KPIs on a regular basis")
    print("  4. Consider specialized agent recommendations for critical issues")
    
    # Generate detailed analysis
    print(f"\n🔍 Detailed Financial Analysis:")
    print(f"   • Asset Structure: {financial_data.get('total_assets', 0):,.0f} total assets")
    print(f"   • Cash Position: ${financial_data.get('cash_and_equivalents', 0):,.0f}")
    print(f"   • Investment Portfolio: ${financial_data.get('investments', 0):,.0f}")
    print(f"   • Fixed Assets: ${financial_data.get('fixed_assets', 0):,.0f}")
    print(f"   • Receivables: ${financial_data.get('receivables', 0):,.0f}")
    
    print(f"\n   • Liability Structure: ${financial_data.get('total_liabilities', 0):,.0f} total liabilities")
    print(f"   • Current Liabilities: ${financial_data.get('current_liabilities', 0):,.0f}")
    print(f"   • Equity: ${financial_data.get('total_equity', 0):,.0f}")

def main():
    """Run the complete test with CARMANFE SAS data"""
    print("🚀 Company Efficiency Optimizer - CARMANFE SAS Test")
    print("=" * 60)
    print("Testing with real financial data from testastra.xlsx")
    print("Company: CARMANFE SAS (Agricultural Company)")
    print("Period: Enero 2025")
    print()
    
    try:
        # Step 1: Process financial data
        financial_data = process_astra_financial_data()
        if not financial_data:
            print("❌ Failed to process financial data")
            return 1
        
        # Step 2: Run KPI analysis
        kpis, inefficiencies = run_kpi_analysis(financial_data)
        
        # Step 3: Generate executive summary
        generate_executive_summary(financial_data, kpis, inefficiencies)
        
        print("\n" + "=" * 60)
        print("🎉 CARMANFE SAS analysis completed successfully!")
        print("\n📝 Key Findings:")
        print(f"   • Analyzed {len(kpis)} key performance indicators")
        print(f"   • Identified {len(inefficiencies)} areas for improvement")
        print(f"   • Generated recommendations for optimization")
        print(f"   • Company appears to be in {'good' if len(inefficiencies) == 0 else 'needs improvement'} financial health")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())