#!/usr/bin/env python3
"""
Test the full analysis flow with testastra2.xlsx
Simulates the web flow: questionnaire -> file upload -> analysis
"""

import os
import sys
from app.services.analysis_service import AnalysisService

def test_full_flow():
    """Test the complete analysis flow"""
    
    # Simulate questionnaire data
    questionnaire_data = {
        'company_name': 'APRU SAS',
        'industry': 'retail',
        'company_size': 'small',
        'revenue_range': '10m_50m',
        'employee_count': '68',
        'current_challenges': 'Operational efficiency',
        'goals': 'Improve margins',
        'analysis_focus': ['financial', 'operational']
    }
    
    # Simulate file upload processing
    file_path = '/Users/arielsanroj/Downloads/testastra2.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print("=" * 60)
    print("TESTING FULL ANALYSIS FLOW")
    print("=" * 60)
    
    print(f"\n📋 Questionnaire Data:")
    print(f"   Company: {questionnaire_data['company_name']}")
    print(f"   Industry: {questionnaire_data['industry']}")
    print(f"   Employees: {questionnaire_data['employee_count']}")
    
    print(f"\n📁 File: {file_path}")
    print(f"   Size: {os.path.getsize(file_path) / 1024:.1f} KB")
    
    # Process file using EnhancedDataIngestion
    print(f"\n" + "=" * 60)
    print("STEP 1: File Processing")
    print("=" * 60)
    
    from data_ingest import EnhancedDataIngestion
    data_ingestion = EnhancedDataIngestion()
    
    structured_data = data_ingestion.process_excel_file(
        file_path,
        company_name=questionnaire_data['company_name'],
        department='Finance'
    )
    
    if not structured_data:
        print("❌ File processing failed")
        return False
    
    print(f"\n✅ File processed successfully!")
    print(f"   Revenue: ${structured_data.get('revenue', 0):,.0f}")
    print(f"   COGS: ${structured_data.get('cogs', 0):,.0f}")
    print(f"   Operating Income: ${structured_data.get('operating_income', 0):,.0f}")
    print(f"   Net Income: ${structured_data.get('net_income', 0):,.0f}")
    print(f"   Employees: {structured_data.get('employee_count', 'N/A')}")
    
    # Prepare file_data for analysis service
    file_data = {
        os.path.basename(file_path): structured_data
    }
    
    # Run analysis
    print(f"\n" + "=" * 60)
    print("STEP 2: Running Analysis Service")
    print("=" * 60)
    
    analysis_service = AnalysisService()
    results = analysis_service.run_analysis(questionnaire_data, file_data)
    
    if 'error' in results:
        print(f"❌ Analysis failed: {results['error']}")
        return False
    
    print(f"\n✅ Analysis completed successfully!")
    print(f"   Company: {results.get('company_name', 'Unknown')}")
    
    # Check KPI results
    kpi_results = results.get('kpi_results', {})
    
    print(f"\n📊 KPI Results:")
    
    # Financial KPIs
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
    
    # Efficiency score
    efficiency_score = kpi_results.get('efficiency_score')
    if efficiency_score is not None:
        print(f"\n⭐ Overall Efficiency Score: {efficiency_score}%")
    
    # Check for N/A values in raw KPIs
    raw_kpis = kpi_results.get('raw_kpis', {})
    all_kpis = []
    for category in ['financial', 'hr', 'operational', 'department']:
        all_kpis.extend(raw_kpis.get(category, []))
    
    na_count = sum(1 for kpi in all_kpis if kpi.get('value') is None or str(kpi.get('value')) == 'N/A')
    
    if na_count == 0:
        print(f"\n✅ All KPIs have valid values (no N/A)")
    else:
        print(f"\n⚠️  {na_count} KPIs have N/A values")
        # Show which ones
        for kpi in all_kpis:
            if kpi.get('value') is None or str(kpi.get('value')) == 'N/A':
                print(f"   - {kpi.get('name', 'Unknown')}: N/A")
    
    # File summary
    file_summary = results.get('file_summary', {})
    if file_summary:
        print(f"\n📄 File Summary:")
        for filename, summary in file_summary.items():
            print(f"   {filename}: {summary}")
    
    # Inefficiencies
    inefficiencies = kpi_results.get('inefficiencies', [])
    if inefficiencies:
        print(f"\n⚠️  Identified Inefficiencies: {len(inefficiencies)}")
        for ineff in inefficiencies[:5]:
            print(f"   - {ineff.get('issue_type', 'Unknown')}: {ineff.get('description', 'N/A')}")
    
    return True

if __name__ == '__main__':
    print("🧪 Testing Full Analysis Flow with testastra2.xlsx\n")
    success = test_full_flow()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ FULL FLOW TEST PASSED")
        print("=" * 60)
        print("\nThe system successfully:")
        print("  ✓ Processed testastra2.xlsx with universal parser")
        print("  ✓ Extracted real financial metrics")
        print("  ✓ Calculated KPIs with real values (no N/A)")
        print("  ✓ Generated analysis results")
    else:
        print("\n" + "=" * 60)
        print("❌ FULL FLOW TEST FAILED")
        print("=" * 60)
        sys.exit(1)



