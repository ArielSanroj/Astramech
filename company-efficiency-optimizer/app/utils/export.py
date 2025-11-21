"""
Export utilities for analysis results
"""

import csv
import json
from typing import Dict, Any
from io import StringIO
from datetime import datetime


def _safe_format_percent(value: Any, default: str = 'N/A') -> str:
    """Safely format a percentage value, handling None"""
    if value is None:
        return default
    try:
        return f"{float(value) * 100:.1f}"
    except (TypeError, ValueError):
        return default

def _safe_format_number(value: Any, default: str = 'N/A') -> str:
    """Safely format a number value, handling None"""
    if value is None:
        return default
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return default

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
            financial = kpis['financial']
            writer.writerow(['Gross Margin', _safe_format_percent(financial.get('gross_margin')), '%'])
            writer.writerow(['Operating Margin', _safe_format_percent(financial.get('operating_margin')), '%'])
            writer.writerow(['Net Margin', _safe_format_percent(financial.get('net_margin')), '%'])
            rev_per_emp = financial.get('revenue_per_employee')
            writer.writerow(['Revenue per Employee', f"${_safe_format_number(rev_per_emp)}" if rev_per_emp is not None else 'N/A', 'COP'])
        writer.writerow([])
        
        # HR KPIs
        writer.writerow(['HR KPIs'])
        writer.writerow(['Metric', 'Value', 'Unit'])
        if 'hr' in kpis:
            hr = kpis['hr']
            writer.writerow(['Turnover Rate', _safe_format_percent(hr.get('turnover_rate')), '%'])
            total_emp = hr.get('total_employees')
            writer.writerow(['Total Employees', str(total_emp) if total_emp is not None else 'N/A', 'count'])
        writer.writerow([])
        
        # Operational KPIs
        writer.writerow(['OPERATIONAL KPIs'])
        writer.writerow(['Metric', 'Value', 'Unit'])
        if 'operational' in kpis:
            operational = kpis['operational']
            writer.writerow(['Cost Efficiency Ratio', _safe_format_percent(operational.get('cost_efficiency_ratio')), '%'])
            writer.writerow(['Productivity Index', _safe_format_percent(operational.get('productivity_index')), '%'])
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

