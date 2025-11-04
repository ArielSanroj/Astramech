"""
Export utilities for analysis results
"""

import csv
import json
from typing import Dict, Any
from io import StringIO
from datetime import datetime


def export_results_to_csv(results: Dict[str, Any]) -> str:
    """
    Export analysis results to CSV format
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        CSV string
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['AstraMech Analysis Report'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Company:', results.get('company_name', 'Unknown')])
    writer.writerow([])
    
    if 'kpi_results' in results:
        kpis = results['kpi_results']
        
        # Financial KPIs
        writer.writerow(['FINANCIAL KPIs'])
        writer.writerow(['Metric', 'Value', 'Unit'])
        if 'financial' in kpis:
            writer.writerow(['Gross Margin', f"{kpis['financial'].get('gross_margin', 0) * 100:.1f}", '%'])
            writer.writerow(['Operating Margin', f"{kpis['financial'].get('operating_margin', 0) * 100:.1f}", '%'])
            writer.writerow(['Net Margin', f"{kpis['financial'].get('net_margin', 0) * 100:.1f}", '%'])
            writer.writerow(['Revenue per Employee', f"${kpis['financial'].get('revenue_per_employee', 0):,.0f}", 'USD'])
        writer.writerow([])
        
        # HR KPIs
        writer.writerow(['HR KPIs'])
        writer.writerow(['Metric', 'Value', 'Unit'])
        if 'hr' in kpis:
            writer.writerow(['Turnover Rate', f"{kpis['hr'].get('turnover_rate', 0) * 100:.1f}", '%'])
            writer.writerow(['Total Employees', f"{kpis['hr'].get('total_employees', 0)}", 'count'])
        writer.writerow([])
        
        # Operational KPIs
        writer.writerow(['OPERATIONAL KPIs'])
        writer.writerow(['Metric', 'Value', 'Unit'])
        if 'operational' in kpis:
            writer.writerow(['Cost Efficiency Ratio', f"{kpis['operational'].get('cost_efficiency_ratio', 0) * 100:.1f}", '%'])
            writer.writerow(['Productivity Index', f"{kpis['operational'].get('productivity_index', 0) * 100:.1f}", '%'])
        writer.writerow([])
    
    # Recommendations
    writer.writerow(['RECOMMENDATIONS'])
    writer.writerow(['1. Implement cost reduction strategies in operational expenses'])
    writer.writerow(['2. Develop employee retention programs'])
    writer.writerow(['3. Automate routine tasks and optimize workflows'])
    writer.writerow(['4. Regular monitoring of KPIs for continuous improvement'])
    
    return output.getvalue()


def export_results_to_json(results: Dict[str, Any]) -> str:
    """
    Export analysis results to JSON format
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        JSON string
    """
    export_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'company_name': results.get('company_name', 'Unknown'),
            'version': '1.0'
        },
        'kpi_results': results.get('kpi_results', {}),
        'diagnostic_results': results.get('diagnostic_results', {}),
        'file_summary': results.get('file_summary', {})
    }
    
    return json.dumps(export_data, indent=2, default=str)

