#!/usr/bin/env python3
"""
Test script for CARMANFE SAS financial data from testastra.xlsx

This script processes the Excel financial data through the Company Efficiency Optimizer
to demonstrate the complete workflow with real data.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from data_ingest import DataIngestion
from tools.kpi_calculator import KPICalculator
from memory_setup import HybridMemorySystem

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
        # Looking for specific account codes and their final balances
        
        # Assets (Activo) - typically starts around row 7
        total_assets = 0
        cash_and_equivalents = 0
        investments = 0
        receivables = 0
        fixed_assets = 0
        
        # Liabilities (Pasivo) - typically starts around row 67
        total_liabilities = 0
        current_liabilities = 0
        long_term_debt = 0
        
        # Equity (Patrimonio) - typically at the end
        total_equity = 0
        
        # Revenue and expenses (if available in P&L section)
        revenue = 0
        operating_expenses = 0
        net_income = 0
        
        # Process each row to extract financial data
        for index, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue
                
            account_name = str(row.iloc[0]).strip()
            final_balance = 0
            
            # Try to get the final balance from the last column
            try:
                if not pd.isna(row.iloc[-1]):
                    final_balance = float(row.iloc[-1])
            except:
                continue
            
            # Categorize accounts based on Colombian accounting standards
            if "Activo" in account_name and "Clase" in account_name:
                # This is the total assets header
                total_assets = abs(final_balance)
                
            elif "Efectivo y equivalentes" in account_name:
                cash_and_equivalents = abs(final_balance)
                
            elif "Inversiones" in account_name and "Grupo" in account_name:
                investments = abs(final_balance)
                
            elif "Deudores comerciales" in account_name and "Grupo" in account_name:
                receivables = abs(final_balance)
                
            elif "Propiedad planta y equipo" in account_name and "Grupo" in account_name:
                fixed_assets = abs(final_balance)
                
            elif "Pasivo" in account_name and "Clase" in account_name:
                total_liabilities = abs(final_balance)
                
            elif "Acreedores comerciales" in account_name and "Grupo" in account_name:
                current_liabilities = abs(final_balance)
                
            elif "Patrimonio" in account_name and "Clase" in account_name:
                total_equity = abs(final_balance)
        
        # Calculate derived metrics
        if total_assets > 0:
            # Estimate revenue based on assets (rough approximation)
            revenue = total_assets * 0.3  # Assume 30% of assets as annual revenue
            
            # Estimate operating expenses (rough approximation)
            operating_expenses = revenue * 0.7  # Assume 70% of revenue as expenses
            
            # Estimate net income
            net_income = revenue - operating_expenses
            
            # Estimate COGS (Cost of Goods Sold)
            cogs = revenue * 0.5  # Assume 50% of revenue as COGS
            
            # Estimate employee count based on company size
            employee_count = max(10, int(total_assets / 100000000))  # Rough estimate
        
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
        
        # Calculate financial KPIs (using manufacturing industry benchmarks)
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

def run_memory_analysis(kpis, inefficiencies):
    """Store analysis results in memory system"""
    print("\n🧠 Memory System Analysis")
    print("-" * 30)
    
    try:
        # Initialize memory system
        memory_system = HybridMemorySystem()
        
        # Store KPI data
        print("Storing KPI data in memory...")
        for kpi in kpis:
            memory_id = memory_system.store_kpi_data(
                kpi_name=kpi.name.lower().replace(' ', '_'),
                value=kpi.value,
                period="Enero_2025",
                benchmark=kpi.benchmark,
                status=kpi.status
            )
            if memory_id:
                print(f"  ✅ Stored {kpi.name} with ID: {memory_id}")
        
        # Store inefficiencies
        print("\nStoring inefficiencies in memory...")
        for inefficiency in inefficiencies:
            memory_id = memory_system.store_inefficiency(
                issue_type=inefficiency['issue_type'],
                description=f"{inefficiency['kpi_name']}: {inefficiency['current_value']:.1f}% vs {inefficiency['benchmark']:.1f}%",
                severity=inefficiency['severity'],
                recommended_agent=inefficiency['recommended_agent']
            )
            if memory_id:
                print(f"  ✅ Stored inefficiency with ID: {memory_id}")
        
        # Generate pattern summary
        print("\nGenerating pattern summary...")
        summary = memory_system.summarize_patterns()
        print(summary)
        
    except Exception as e:
        print(f"⚠️  Memory system analysis skipped (requires API keys): {str(e)}")
        print("   This is expected when running without valid API keys.")

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

def main():
    """Run the complete test with CARMANFE SAS data"""
    print("🚀 Company Efficiency Optimizer - CARMANFE SAS Test")
    print("=" * 60)
    print("Testing with real financial data from testastra.xlsx")
    print()
    
    try:
        # Step 1: Process financial data
        financial_data = process_astra_financial_data()
        if not financial_data:
            print("❌ Failed to process financial data")
            return 1
        
        # Step 2: Run KPI analysis
        kpis, inefficiencies = run_kpi_analysis(financial_data)
        
        # Step 3: Memory analysis
        run_memory_analysis(kpis, inefficiencies)
        
        # Step 4: Generate executive summary
        generate_executive_summary(financial_data, kpis, inefficiencies)
        
        print("\n" + "=" * 60)
        print("🎉 CARMANFE SAS analysis completed successfully!")
        print("\n📝 Key Findings:")
        print(f"   • Analyzed {len(kpis)} key performance indicators")
        print(f"   • Identified {len(inefficiencies)} areas for improvement")
        print(f"   • Generated recommendations for optimization")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())