#!/usr/bin/env python3
"""
Corrected test script for CARMANFE SAS financial data from testastra.xlsx

This script properly processes the Excel financial data using the correct P&L statement
and appropriate industry benchmarks for professional services.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from tools.kpi_calculator import KPICalculator

def process_astra_financial_data_corrected():
    """Process the CARMANFE SAS financial data from Excel using correct P&L data"""
    print("🏢 Processing CARMANFE SAS Financial Data (Corrected)")
    print("=" * 60)
    
    try:
        # Read the P&L statement sheet
        pl_df = pd.read_excel('/Users/arielsanroj/Downloads/testastra.xlsx', sheet_name='ESTADO DE RESULTADOS')
        print(f"✅ Loaded P&L statement: {pl_df.shape[0]} rows, {pl_df.shape[1]} columns")
        
        # Read the balance sheet for assets
        bs_df = pd.read_excel('/Users/arielsanroj/Downloads/testastra.xlsx', sheet_name='BALANCE DE PRUEBA ENERO')
        print(f"✅ Loaded balance sheet: {bs_df.shape[0]} rows, {bs_df.shape[1]} columns")
        
        # Extract financial data from both sheets
        financial_data = extract_financial_metrics_corrected(pl_df, bs_df)
        print(f"✅ Extracted financial metrics: {len(financial_data)} key figures")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
        return None

def extract_financial_metrics_corrected(pl_df, bs_df):
    """Extract key financial metrics from P&L and balance sheet"""
    financial_data = {}
    
    try:
        # Extract P&L data
        revenue = 0
        cogs = 0
        gross_profit = 0
        operating_expenses = 0
        operating_income = 0
        net_income = 0
        
        # Process P&L statement
        for index, row in pl_df.iterrows():
            if pd.isna(row.iloc[0]):
                continue
                
            account_name = str(row.iloc[0]).strip()
            total_value = 0
            
            # Get the total value from the last column
            try:
                if not pd.isna(row.iloc[-1]):
                    total_value = float(row.iloc[-1])
            except:
                continue
            
            # Extract key P&L figures
            if "INGRESOS ORDINARIOS" in account_name:
                revenue = total_value
                print(f"Found Revenue: ${revenue:,.0f} COP")
                
            elif "COSTO DE LA MERCANCIA VENDIDA" in account_name or "COSTO DE VENTAS" in account_name:
                cogs = total_value
                print(f"Found COGS: ${cogs:,.0f} COP")
                
            elif "UTILIDAD BRUTA" in account_name:
                gross_profit = total_value
                print(f"Found Gross Profit: ${gross_profit:,.0f} COP")
                
            elif "TOTAL GASTOS OPERACIONALES" in account_name:
                operating_expenses = abs(total_value)  # Make positive for calculation
                print(f"Found Operating Expenses: ${operating_expenses:,.0f} COP")
                
            elif "RESULTADO OPERACIONAL" in account_name:
                operating_income = total_value
                print(f"Found Operating Income: ${operating_income:,.0f} COP")
                
            elif "RESULTADO DEL EJERCICIO" in account_name and "UTILIDAD/PERDIDA" in account_name:
                net_income = total_value
                print(f"Found Net Income: ${net_income:,.0f} COP")
        
        # Extract balance sheet data
        total_assets = 0
        total_liabilities = 0
        total_equity = 0
        cash_and_equivalents = 0
        
        # Process balance sheet
        for index, row in bs_df.iterrows():
            if pd.isna(row.iloc[0]):
                continue
                
            account_name = str(row.iloc[3]).strip() if not pd.isna(row.iloc[3]) else ""
            final_balance = 0
            
            # Get the final balance from the last column
            try:
                if not pd.isna(row.iloc[-1]):
                    final_balance = float(row.iloc[-1])
            except:
                continue
            
            # Extract key balance sheet figures
            if "Activo" in account_name and "Clase" in str(row.iloc[0]):
                total_assets = abs(final_balance)
                print(f"Found Total Assets: ${total_assets:,.0f} COP")
                
            elif "Pasivo" in account_name and "Clase" in str(row.iloc[0]):
                total_liabilities = abs(final_balance)
                print(f"Found Total Liabilities: ${total_liabilities:,.0f} COP")
                
            elif "Patrimonio" in account_name and "Clase" in str(row.iloc[0]):
                total_equity = abs(final_balance)
                print(f"Found Total Equity: ${total_equity:,.0f} COP")
                
            elif "Efectivo y equivalentes" in account_name and "Grupo" in str(row.iloc[0]):
                cash_and_equivalents = abs(final_balance)
                print(f"Found Cash and Equivalents: ${cash_and_equivalents:,.0f} COP")
        
        # Estimate employee count based on company size and industry
        # For a professional services company with ~$20M revenue, estimate 10-20 employees
        employee_count = 15  # Conservative estimate for professional services
        
        # Build financial data dictionary
        financial_data = {
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'operating_expenses': operating_expenses,
            'operating_income': operating_income,
            'net_income': net_income,
            'employee_count': employee_count,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'cash_and_equivalents': cash_and_equivalents,
            'period': 'Mayo_2025',
            'company': 'CARMANFE SAS',
            'currency': 'COP'
        }
        
        print(f"\n📊 Corrected Financial Data:")
        print(f"   Revenue: ${revenue:,.0f} COP")
        print(f"   COGS: ${cogs:,.0f} COP")
        print(f"   Gross Profit: ${gross_profit:,.0f} COP")
        print(f"   Operating Expenses: ${operating_expenses:,.0f} COP")
        print(f"   Operating Income: ${operating_income:,.0f} COP")
        print(f"   Net Income: ${net_income:,.0f} COP")
        print(f"   Total Assets: ${total_assets:,.0f} COP")
        print(f"   Employee Count: {employee_count} (estimated)")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Error extracting financial metrics: {str(e)}")
        return {}

def run_kpi_analysis_corrected(financial_data):
    """Run KPI analysis using professional services benchmarks"""
    print("\n📈 KPI Analysis for CARMANFE SAS (Professional Services)")
    print("-" * 60)
    
    try:
        # Initialize KPI calculator
        calculator = KPICalculator()
        
        # Calculate financial KPIs using professional services benchmarks
        kpis = calculator.calculate_financial_kpis(financial_data, industry='services')
        
        # Display results
        print("\n📊 Financial KPIs (Professional Services Benchmarks):")
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

def generate_executive_summary_corrected(financial_data, kpis, inefficiencies):
    """Generate executive summary for CARMANFE SAS"""
    print("\n📋 Executive Summary for CARMANFE SAS (Corrected)")
    print("=" * 60)
    
    print(f"Company: {financial_data.get('company', 'CARMANFE SAS')}")
    print(f"Period: {financial_data.get('period', 'Mayo 2025')}")
    print(f"Currency: {financial_data.get('currency', 'COP')}")
    print(f"Total Assets: ${financial_data.get('total_assets', 0):,.0f} COP")
    print(f"Revenue: ${financial_data.get('revenue', 0):,.0f} COP")
    print(f"Net Income: ${financial_data.get('net_income', 0):,.0f} COP")
    print(f"Employee Count: {financial_data.get('employee_count', 0)} (estimated)")
    
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
    print("  1. Review financial performance against professional services benchmarks")
    print("  2. Implement targeted optimization strategies")
    print("  3. Monitor KPIs on a regular basis")
    print("  4. Consider specialized agent recommendations for critical issues")
    
    # Generate detailed analysis
    print(f"\n🔍 Detailed Financial Analysis:")
    print(f"   • Revenue: ${financial_data.get('revenue', 0):,.0f} COP")
    print(f"   • Gross Profit: ${financial_data.get('gross_profit', 0):,.0f} COP")
    print(f"   • Operating Income: ${financial_data.get('operating_income', 0):,.0f} COP")
    print(f"   • Net Income: ${financial_data.get('net_income', 0):,.0f} COP")
    print(f"   • Total Assets: ${financial_data.get('total_assets', 0):,.0f} COP")
    print(f"   • Cash Position: ${financial_data.get('cash_and_equivalents', 0):,.0f} COP")

def main():
    """Run the corrected test with CARMANFE SAS data"""
    print("🚀 Company Efficiency Optimizer - CARMANFE SAS Test (Corrected)")
    print("=" * 70)
    print("Testing with real financial data from testastra.xlsx")
    print("Company: CARMANFE SAS (Professional Services)")
    print("Period: Mayo 2025")
    print("Currency: Colombian Pesos (COP)")
    print()
    
    try:
        # Step 1: Process financial data correctly
        financial_data = process_astra_financial_data_corrected()
        if not financial_data:
            print("❌ Failed to process financial data")
            return 1
        
        # Step 2: Run KPI analysis with correct benchmarks
        kpis, inefficiencies = run_kpi_analysis_corrected(financial_data)
        
        # Step 3: Generate executive summary
        generate_executive_summary_corrected(financial_data, kpis, inefficiencies)
        
        print("\n" + "=" * 70)
        print("🎉 CARMANFE SAS analysis completed successfully!")
        print("\n📝 Key Findings:")
        print(f"   • Analyzed {len(kpis)} key performance indicators")
        print(f"   • Identified {len(inefficiencies)} areas for improvement")
        print(f"   • Used professional services industry benchmarks")
        print(f"   • Corrected data extraction from P&L statement")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())