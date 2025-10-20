#!/usr/bin/env python3
"""
Universal File Processor for Company Efficiency Optimizer

This script demonstrates how users can upload any file format and the system will
automatically detect, normalize, and analyze the financial data regardless of:
- File format (Excel, CSV, PDF, JSON)
- Language (Spanish, English, Portuguese, French)
- Accounting standard (NIIF, US GAAP, IFRS, Local)
- Company size or industry
"""

import os
import sys
import argparse
from typing import Dict, Any
from dotenv import load_dotenv
from normalization_layer import NormalizationLayer
from tools.kpi_calculator import KPICalculator

def process_any_financial_file(file_path: str, company_name: str = None) -> Dict[str, Any]:
    """
    Process any financial file and return comprehensive analysis
    
    Args:
        file_path: Path to the financial file
        company_name: Optional company name
        
    Returns:
        Dict: Comprehensive financial analysis
    """
    print(f"🚀 Processing Financial File: {file_path}")
    print("=" * 60)
    
    try:
        # Initialize normalization layer
        normalization = NormalizationLayer()
        
        # Normalize the data
        print("📊 Step 1: Normalizing data...")
        normalized_data = normalization.normalize_financial_data(file_path, company_name)
        
        if not normalized_data:
            print("❌ Failed to normalize data")
            return {}
        
        # Show detection results
        metadata = normalized_data.get('metadata', {})
        print(f"✅ File Format: {metadata.get('file_format', 'Unknown')}")
        print(f"✅ Language: {metadata.get('language', 'Unknown')}")
        print(f"✅ Accounting Standard: {metadata.get('accounting_standard', 'Unknown')}")
        print(f"✅ Industry: {normalized_data.get('industry', 'Unknown')}")
        print(f"✅ Sheets Processed: {len(normalized_data.get('sheets_processed', []))}")
        
        # Run KPI analysis
        print(f"\n📈 Step 2: Running KPI analysis...")
        calculator = KPICalculator()
        kpis = calculator.calculate_financial_kpis(
            normalized_data, 
            industry=normalized_data.get('industry', 'services')
        )
        
        # Identify inefficiencies
        inefficiencies = calculator.identify_inefficiencies(kpis)
        
        # Generate comprehensive report
        report = {
            'company': normalized_data.get('company', 'Unknown'),
            'industry': normalized_data.get('industry', 'Unknown'),
            'metadata': metadata,
            'financial_data': {
                'revenue': normalized_data.get('revenue', 0),
                'net_income': normalized_data.get('net_income', 0),
                'total_assets': normalized_data.get('total_assets', 0),
                'employee_count': normalized_data.get('employee_count', 0)
            },
            'kpis': [
                {
                    'name': kpi.name,
                    'value': kpi.value,
                    'benchmark': kpi.benchmark,
                    'status': kpi.status,
                    'description': kpi.description
                }
                for kpi in kpis
            ],
            'inefficiencies': inefficiencies,
            'sheets_processed': normalized_data.get('sheets_processed', [])
        }
        
        return report
        
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return {}

def display_analysis_report(report: Dict[str, Any]):
    """Display a comprehensive analysis report"""
    if not report:
        print("❌ No analysis report available")
        return
    
    print(f"\n📋 Comprehensive Analysis Report")
    print("=" * 70)
    
    # Company information
    print(f"🏢 Company: {report['company']}")
    print(f"🏭 Industry: {report['industry'].title()}")
    print(f"📊 File Format: {report['metadata'].get('file_format', 'Unknown')}")
    print(f"🌍 Language: {report['metadata'].get('language', 'Unknown')}")
    print(f"📋 Accounting Standard: {report['metadata'].get('accounting_standard', 'Unknown')}")
    
    # Financial overview
    financial_data = report['financial_data']
    print(f"\n💰 Financial Overview:")
    print(f"   • Revenue: ${financial_data['revenue']:,.0f}")
    print(f"   • Net Income: ${financial_data['net_income']:,.0f}")
    print(f"   • Total Assets: ${financial_data['total_assets']:,.0f}")
    print(f"   • Employee Count: {financial_data['employee_count']}")
    
    # KPI analysis
    print(f"\n📊 Key Performance Indicators:")
    for kpi in report['kpis']:
        status_emoji = {
            'excellent': '🟢',
            'good': '🟡',
            'warning': '🟠',
            'critical': '🔴'
        }
        emoji = status_emoji.get(kpi['status'], '⚪')
        print(f"   {emoji} {kpi['name']}: {kpi['value']:.1f}% (Benchmark: {kpi['benchmark']:.1f}%)")
        print(f"      Status: {kpi['status'].upper()}")
        print(f"      Description: {kpi['description']}")
        print()
    
    # Inefficiencies
    inefficiencies = report['inefficiencies']
    if inefficiencies:
        print(f"⚠️  Critical Issues Identified ({len(inefficiencies)}):")
        for i, inefficiency in enumerate(inefficiencies, 1):
            print(f"   {i}. {inefficiency['kpi_name']}: {inefficiency['severity']} severity")
            print(f"      Current: {inefficiency['current_value']:.1f}% vs Benchmark: {inefficiency['benchmark']:.1f}%")
            print(f"      Recommended agent: {inefficiency['recommended_agent']}")
            print(f"      Issue type: {inefficiency['issue_type']}")
            print()
    else:
        print("✅ No critical inefficiencies found!")
    
    # Processed sheets
    if report['sheets_processed']:
        print(f"📋 Processed Financial Statements:")
        for sheet in report['sheets_processed']:
            print(f"   • {sheet}")
    
    # Recommendations
    print(f"\n🎯 Recommendations:")
    print("   1. Review financial performance against industry benchmarks")
    print("   2. Implement targeted optimization strategies")
    print("   3. Monitor KPIs on a regular basis")
    print("   4. Consider specialized agent recommendations for critical issues")
    print("   5. Leverage multi-sheet analysis for comprehensive insights")

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Universal File Processor for Company Efficiency Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python universal_file_processor.py /path/to/financial_data.xlsx
  python universal_file_processor.py /path/to/financial_data.csv --company "My Company"
  python universal_file_processor.py /path/to/financial_data.pdf --company "Tech Corp"
        """
    )
    
    parser.add_argument(
        'file_path',
        help='Path to the financial file (Excel, CSV, PDF, or JSON)'
    )
    
    parser.add_argument(
        '--company',
        help='Company name (optional)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path for JSON report (optional)'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.file_path):
        print(f"❌ File not found: {args.file_path}")
        return 1
    
    # Process the file
    report = process_any_financial_file(args.file_path, args.company)
    
    if not report:
        print("❌ Failed to process file")
        return 1
    
    # Display the report
    display_analysis_report(report)
    
    # Save to file if requested
    if args.output:
        import json
        try:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n💾 Report saved to: {args.output}")
        except Exception as e:
            print(f"❌ Error saving report: {str(e)}")
    
    print(f"\n🎉 Analysis completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())