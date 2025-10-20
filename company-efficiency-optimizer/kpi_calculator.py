"""
KPI Calculator for Company Efficiency Optimizer
Calculates financial KPIs and compares against industry benchmarks
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class KPICalculator:
    """Calculate and analyze financial KPIs"""
    
    def __init__(self):
        self.industry_benchmarks = {
            'manufacturing': {
                'gross_margin': 25.0,
                'operating_margin': 12.0,
                'net_margin': 8.0,
                'revenue_per_employee': 250000,
                'asset_turnover': 1.2,
                'debt_to_equity': 0.6
            },
            'services': {
                'gross_margin': 40.0,
                'operating_margin': 15.0,
                'net_margin': 10.0,
                'revenue_per_employee': 300000,
                'asset_turnover': 1.5,
                'debt_to_equity': 0.4
            },
            'retail': {
                'gross_margin': 30.0,
                'operating_margin': 8.0,
                'net_margin': 5.0,
                'revenue_per_employee': 200000,
                'asset_turnover': 2.0,
                'debt_to_equity': 0.8
            },
            'technology': {
                'gross_margin': 70.0,
                'operating_margin': 25.0,
                'net_margin': 15.0,
                'revenue_per_employee': 500000,
                'asset_turnover': 1.0,
                'debt_to_equity': 0.3
            },
            'healthcare': {
                'gross_margin': 50.0,
                'operating_margin': 18.0,
                'net_margin': 12.0,
                'revenue_per_employee': 400000,
                'asset_turnover': 1.3,
                'debt_to_equity': 0.5
            },
            'finance': {
                'gross_margin': 60.0,
                'operating_margin': 20.0,
                'net_margin': 12.0,
                'revenue_per_employee': 600000,
                'asset_turnover': 0.8,
                'debt_to_equity': 0.9
            },
            'construction': {
                'gross_margin': 20.0,
                'operating_margin': 8.0,
                'net_margin': 5.0,
                'revenue_per_employee': 180000,
                'asset_turnover': 1.5,
                'debt_to_equity': 0.7
            },
            'agriculture': {
                'gross_margin': 25.0,
                'operating_margin': 10.0,
                'net_margin': 6.0,
                'revenue_per_employee': 150000,
                'asset_turnover': 1.0,
                'debt_to_equity': 0.5
            },
            'education': {
                'gross_margin': 35.0,
                'operating_margin': 12.0,
                'net_margin': 8.0,
                'revenue_per_employee': 250000,
                'asset_turnover': 1.2,
                'debt_to_equity': 0.4
            },
            'hospitality': {
                'gross_margin': 30.0,
                'operating_margin': 10.0,
                'net_margin': 6.0,
                'revenue_per_employee': 120000,
                'asset_turnover': 1.8,
                'debt_to_equity': 0.6
            }
        }
    
    def calculate_financial_kpis(self, financial_data: Dict[str, Any], industry: str = 'services') -> List[Dict[str, Any]]:
        """Calculate financial KPIs and compare against industry benchmarks"""
        
        kpis = []
        
        # Get industry benchmarks
        benchmarks = self.industry_benchmarks.get(industry.lower(), self.industry_benchmarks['services'])
        
        # Extract financial data
        revenue = financial_data.get('revenue', 0)
        net_income = financial_data.get('net_income', 0)
        total_assets = financial_data.get('total_assets', 0)
        employee_count = financial_data.get('employee_count', 1)
        gross_profit = financial_data.get('gross_profit', 0)
        operating_income = financial_data.get('operating_income', 0)
        operating_expenses = financial_data.get('operating_expenses', 0)
        total_liabilities = financial_data.get('total_liabilities', 0)
        total_equity = financial_data.get('total_equity', 0)
        
        # Calculate KPIs
        if revenue > 0:
            # Gross Margin
            if gross_profit > 0:
                gross_margin = (gross_profit / revenue) * 100
                kpis.append(self._create_kpi(
                    'Gross Margin',
                    gross_margin,
                    benchmarks['gross_margin'],
                    f'Gross profit margin: {gross_margin:.1f}% vs {benchmarks["gross_margin"]:.1f}% benchmark'
                ))
            
            # Operating Margin
            if operating_income != 0:
                operating_margin = (operating_income / revenue) * 100
                kpis.append(self._create_kpi(
                    'Operating Margin',
                    operating_margin,
                    benchmarks['operating_margin'],
                    f'Operating profit margin: {operating_margin:.1f}% vs {benchmarks["operating_margin"]:.1f}% benchmark'
                ))
            
            # Net Margin
            if net_income != 0:
                net_margin = (net_income / revenue) * 100
                kpis.append(self._create_kpi(
                    'Net Margin',
                    net_margin,
                    benchmarks['net_margin'],
                    f'Net profit margin: {net_margin:.1f}% vs {benchmarks["net_margin"]:.1f}% benchmark'
                ))
            
            # Revenue per Employee
            if employee_count > 0:
                revenue_per_employee = revenue / employee_count
                kpis.append(self._create_kpi(
                    'Revenue per Employee',
                    revenue_per_employee,
                    benchmarks['revenue_per_employee'],
                    f'Revenue per employee: ${revenue_per_employee:,.0f} vs ${benchmarks["revenue_per_employee"]:,.0f} benchmark'
                ))
        
        # Asset Turnover
        if total_assets > 0 and revenue > 0:
            asset_turnover = revenue / total_assets
            kpis.append(self._create_kpi(
                'Asset Turnover',
                asset_turnover,
                benchmarks['asset_turnover'],
                f'Asset turnover: {asset_turnover:.2f} vs {benchmarks["asset_turnover"]:.2f} benchmark'
            ))
        
        # Debt to Equity Ratio
        if total_equity > 0 and total_liabilities > 0:
            debt_to_equity = total_liabilities / total_equity
            kpis.append(self._create_kpi(
                'Debt to Equity Ratio',
                debt_to_equity,
                benchmarks['debt_to_equity'],
                f'Debt to equity ratio: {debt_to_equity:.2f} vs {benchmarks["debt_to_equity"]:.2f} benchmark'
            ))
        
        # Return on Assets (ROA)
        if total_assets > 0 and net_income != 0:
            roa = (net_income / total_assets) * 100
            kpis.append(self._create_kpi(
                'Return on Assets (ROA)',
                roa,
                8.0,  # General benchmark for ROA
                f'Return on assets: {roa:.1f}% vs 8.0% benchmark'
            ))
        
        # Return on Equity (ROE)
        if total_equity > 0 and net_income != 0:
            roe = (net_income / total_equity) * 100
            kpis.append(self._create_kpi(
                'Return on Equity (ROE)',
                roe,
                15.0,  # General benchmark for ROE
                f'Return on equity: {roe:.1f}% vs 15.0% benchmark'
            ))
        
        return kpis
    
    def _create_kpi(self, name: str, value: float, benchmark: float, description: str) -> Dict[str, Any]:
        """Create a KPI dictionary with status assessment"""
        
        # Calculate performance vs benchmark
        if benchmark == 0:
            performance_ratio = 1.0
        else:
            performance_ratio = value / benchmark
        
        # Determine status
        if performance_ratio >= 1.2:
            status = 'EXCELLENT'
        elif performance_ratio >= 1.0:
            status = 'GOOD'
        elif performance_ratio >= 0.8:
            status = 'AVERAGE'
        elif performance_ratio >= 0.6:
            status = 'POOR'
        else:
            status = 'CRITICAL'
        
        return {
            'name': name,
            'value': value,
            'benchmark': benchmark,
            'performance_ratio': performance_ratio,
            'status': status,
            'description': description
        }
    
    def get_industry_benchmarks(self, industry: str) -> Dict[str, float]:
        """Get industry-specific benchmarks"""
        return self.industry_benchmarks.get(industry.lower(), self.industry_benchmarks['services'])
    
    def calculate_custom_kpi(self, name: str, value: float, benchmark: float, description: str) -> Dict[str, Any]:
        """Calculate a custom KPI"""
        return self._create_kpi(name, value, benchmark, description)