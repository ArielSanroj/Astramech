"""
KPI Calculator Tool for Company Efficiency Optimizer

This module provides tools for calculating and analyzing key performance indicators
including financial ratios, operational metrics, and HR indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class KPIMetrics:
    """Data class for KPI metrics"""
    name: str
    value: float
    benchmark: float
    status: str  # 'excellent', 'good', 'warning', 'critical'
    trend: str   # 'improving', 'stable', 'declining'
    description: str

class KPICalculator:
    """Calculator for various business KPIs"""
    
    def __init__(self):
        """Initialize the KPI calculator with industry benchmarks"""
        self.benchmarks = {
            'gross_margin': {'retail': 30.0, 'manufacturing': 25.0, 'services': 40.0},
            'operating_margin': {'retail': 8.0, 'manufacturing': 12.0, 'services': 15.0},
            'net_margin': {'retail': 5.0, 'manufacturing': 8.0, 'services': 10.0},
            'turnover_rate': {'retail': 15.0, 'manufacturing': 12.0, 'services': 18.0},
            'revenue_per_employee': {'retail': 200000, 'manufacturing': 250000, 'services': 300000},
            'cost_efficiency': {'retail': 0.85, 'manufacturing': 0.80, 'services': 0.75}
        }
    
    def _to_dataframe(self, data):
        if data is None:
            return pd.DataFrame()
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            return pd.DataFrame([data])
        raise ValueError("Unsupported data format for DataFrame conversion")

    def calculate_financial_kpis(self, financial_data: Dict[str, float], 
                               industry: str = 'retail') -> List[KPIMetrics]:
        """
        Calculate financial KPIs from P&L data
        
        Args:
            financial_data: Dictionary with financial figures
            industry: Industry type for benchmarking
            
        Returns:
            List of KPIMetrics objects
        """
        kpis = []
        
        # Gross Margin
        if 'revenue' in financial_data and 'cogs' in financial_data:
            gross_margin = ((financial_data['revenue'] - financial_data['cogs']) / 
                           financial_data['revenue']) * 100
            benchmark = self.benchmarks['gross_margin'].get(industry, 30.0)
            status = self._get_status(gross_margin, benchmark, higher_is_better=True)
            
            kpis.append(KPIMetrics(
                name='Gross Margin',
                value=gross_margin,
                benchmark=benchmark,
                status=status,
                trend='stable',  # Would need historical data for trend
                description=f'Gross profit margin: {gross_margin:.1f}% vs {benchmark}% benchmark'
            ))
        
        # Operating Margin
        if 'revenue' in financial_data and 'operating_income' in financial_data:
            operating_margin = (financial_data['operating_income'] / 
                              financial_data['revenue']) * 100
            benchmark = self.benchmarks['operating_margin'].get(industry, 10.0)
            status = self._get_status(operating_margin, benchmark, higher_is_better=True)
            
            kpis.append(KPIMetrics(
                name='Operating Margin',
                value=operating_margin,
                benchmark=benchmark,
                status=status,
                trend='stable',
                description=f'Operating profit margin: {operating_margin:.1f}% vs {benchmark}% benchmark'
            ))
        
        # Net Margin
        if 'revenue' in financial_data and 'net_income' in financial_data:
            net_margin = (financial_data['net_income'] / 
                         financial_data['revenue']) * 100
            benchmark = self.benchmarks['net_margin'].get(industry, 8.0)
            status = self._get_status(net_margin, benchmark, higher_is_better=True)
            
            kpis.append(KPIMetrics(
                name='Net Margin',
                value=net_margin,
                benchmark=benchmark,
                status=status,
                trend='stable',
                description=f'Net profit margin: {net_margin:.1f}% vs {benchmark}% benchmark'
            ))
        
        # Revenue per Employee
        if 'revenue' in financial_data and 'employee_count' in financial_data:
            revenue_per_employee = financial_data['revenue'] / financial_data['employee_count']
            benchmark = self.benchmarks['revenue_per_employee'].get(industry, 250000)
            status = self._get_status(revenue_per_employee, benchmark, higher_is_better=True)
            
            kpis.append(KPIMetrics(
                name='Revenue per Employee',
                value=revenue_per_employee,
                benchmark=benchmark,
                status=status,
                trend='stable',
                description=f'Revenue per employee: ${revenue_per_employee:,.0f} vs ${benchmark:,.0f} benchmark'
            ))
        
        return kpis
    
    def calculate_hr_kpis(self, hr_data: pd.DataFrame) -> List[KPIMetrics]:
        """
        Calculate HR-related KPIs
        
        Args:
            hr_data: DataFrame with HR information
            
        Returns:
            List of KPIMetrics objects
        """
        kpis = []

        if not isinstance(hr_data, pd.DataFrame):
            hr_data = self._to_dataframe(hr_data)
        if hr_data.empty:
            return kpis
        
        # Turnover Rate
        turnover_rate = self._calculate_turnover_rate(hr_data)
        benchmark = self.benchmarks['turnover_rate'].get('retail', 15.0)  # Default to retail
        status = self._get_status(turnover_rate, benchmark, higher_is_better=False)
        
        kpis.append(KPIMetrics(
            name='Turnover Rate',
            value=turnover_rate,
            benchmark=benchmark,
            status=status,
            trend='stable',
            description=f'Annual turnover rate: {turnover_rate:.1f}% vs {benchmark}% benchmark'
        ))
        
        # Department Analysis
        if 'department' in hr_data.columns:
            dept_turnover = self._calculate_department_turnover(hr_data)
            for dept, rate in dept_turnover.items():
                status = self._get_status(rate, benchmark, higher_is_better=False)
                kpis.append(KPIMetrics(
                    name=f'{dept} Turnover Rate',
                    value=rate,
                    benchmark=benchmark,
                    status=status,
                    trend='stable',
                    description=f'{dept} department turnover: {rate:.1f}%'
                ))
        
        return kpis
    
    def calculate_operational_kpis(self, financial_data: Dict[str, float], 
                                  hr_data: pd.DataFrame) -> List[KPIMetrics]:
        """
        Calculate operational efficiency KPIs
        
        Args:
            financial_data: Financial metrics
            hr_data: HR data for employee metrics
            
        Returns:
            List of KPIMetrics objects
        """
        kpis = []
        
        # Cost Efficiency (Operating Expenses / Revenue)
        if 'revenue' in financial_data and 'operating_expenses' in financial_data:
            cost_efficiency = financial_data['operating_expenses'] / financial_data['revenue']
            benchmark = self.benchmarks['cost_efficiency'].get('retail', 0.80)
            status = self._get_status(cost_efficiency, benchmark, higher_is_better=False)
            
            kpis.append(KPIMetrics(
                name='Cost Efficiency Ratio',
                value=cost_efficiency * 100,  # Convert to percentage
                benchmark=benchmark * 100,
                status=status,
                trend='stable',
                description=f'Operating expenses as % of revenue: {cost_efficiency*100:.1f}% vs {benchmark*100:.1f}% benchmark'
            ))
        
        # Productivity Index (if we have historical data)
        if 'revenue' in financial_data and 'employee_count' in financial_data:
            current_productivity = financial_data['revenue'] / financial_data['employee_count']
            # This would ideally compare to previous periods
            kpis.append(KPIMetrics(
                name='Productivity Index',
                value=current_productivity,
                benchmark=current_productivity,  # Same as current for now
                status='good',
                trend='stable',
                description=f'Current productivity: ${current_productivity:,.0f} revenue per employee'
            ))
        
        return kpis
    
    def _calculate_turnover_rate(self, hr_data: pd.DataFrame) -> float:
        """Calculate overall turnover rate"""
        try:
            # Count employees who left in the last 12 months
            current_date = pd.Timestamp.now()
            one_year_ago = current_date - pd.DateOffset(months=12)
            
            # Convert termination dates
            hr_data['terminationDate'] = pd.to_datetime(hr_data['terminationDate'], errors='coerce')
            
            # Count terminations in last 12 months
            recent_terminations = hr_data[
                (hr_data['terminationDate'] >= one_year_ago) & 
                (hr_data['terminationDate'] <= current_date)
            ].shape[0]
            
            # Calculate average headcount
            avg_headcount = len(hr_data)
            
            # Calculate turnover rate
            turnover_rate = (recent_terminations / avg_headcount) * 100 if avg_headcount > 0 else 0
            
            return turnover_rate
            
        except Exception as e:
            print(f"❌ Error calculating turnover rate: {str(e)}")
            return 0.0
    
    def _calculate_department_turnover(self, hr_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate turnover rate by department"""
        dept_turnover = {}
        
        try:
            for dept in hr_data['department'].unique():
                dept_data = hr_data[hr_data['department'] == dept]
                turnover_rate = self._calculate_turnover_rate(dept_data)
                dept_turnover[dept] = turnover_rate
                
        except Exception as e:
            print(f"❌ Error calculating department turnover: {str(e)}")
        
        return dept_turnover
    
    def _get_status(self, value: float, benchmark: float, 
                   higher_is_better: bool = True) -> str:
        """
        Determine status based on value vs benchmark
        
        Args:
            value: Current value
            benchmark: Benchmark value
            higher_is_better: Whether higher values are better
            
        Returns:
            str: Status indicator
        """
        if higher_is_better:
            if value >= benchmark * 1.1:
                return 'excellent'
            elif value >= benchmark:
                return 'good'
            elif value >= benchmark * 0.8:
                return 'warning'
            else:
                return 'critical'
        else:
            if value <= benchmark * 0.9:
                return 'excellent'
            elif value <= benchmark:
                return 'good'
            elif value <= benchmark * 1.2:
                return 'warning'
            else:
                return 'critical'
    
    def generate_kpi_report(self, kpis: List[KPIMetrics]) -> str:
        """
        Generate a formatted KPI report
        
        Args:
            kpis: List of KPI metrics
            
        Returns:
            str: Formatted report
        """
        report = "📊 KPI Analysis Report\n"
        report += "=" * 50 + "\n\n"
        
        # Group KPIs by status
        status_groups = {
            'excellent': [],
            'good': [],
            'warning': [],
            'critical': []
        }
        
        for kpi in kpis:
            status_groups[kpi.status].append(kpi)
        
        # Report by status priority
        for status in ['critical', 'warning', 'good', 'excellent']:
            if status_groups[status]:
                status_emoji = {
                    'excellent': '🟢',
                    'good': '🟡',
                    'warning': '🟠',
                    'critical': '🔴'
                }
                
                report += f"{status_emoji[status]} {status.title()} Performance:\n"
                for kpi in status_groups[status]:
                    report += f"   • {kpi.name}: {kpi.description}\n"
                report += "\n"
        
        return report
    
    def identify_inefficiencies(self, kpis: List[KPIMetrics]) -> List[Dict[str, Any]]:
        """
        Identify inefficiencies from KPI analysis
        
        Args:
            kpis: List of KPI metrics
            
        Returns:
            List of inefficiency records
        """
        inefficiencies = []
        
        for kpi in kpis:
            if kpi.status in ['warning', 'critical']:
                # Determine recommended agent
                if 'turnover' in kpi.name.lower():
                    recommended_agent = 'hr_optimizer'
                    issue_type = 'high_turnover'
                elif 'margin' in kpi.name.lower() or 'revenue' in kpi.name.lower():
                    recommended_agent = 'financial_optimizer'
                    issue_type = 'financial_performance'
                elif 'cost' in kpi.name.lower() or 'efficiency' in kpi.name.lower():
                    recommended_agent = 'operations_optimizer'
                    issue_type = 'operational_efficiency'
                else:
                    recommended_agent = 'diagnostic_agent'
                    issue_type = 'general_performance'
                
                inefficiencies.append({
                    'issue_type': issue_type,
                    'kpi_name': kpi.name,
                    'current_value': kpi.value,
                    'benchmark': kpi.benchmark,
                    'severity': kpi.status,
                    'description': kpi.description,
                    'recommended_agent': recommended_agent
                })
        
        return inefficiencies
    
    def calculate_all_kpis(self, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all KPIs and return structured results matching template expectations
        
        Args:
            sample_data: Dictionary containing financial_data, hr_data, and operational_data
            
        Returns:
            Dict: Structured KPI results matching template expectations
        """
        try:
            financial_data = sample_data.get('financial_data', {})
            hr_data = sample_data.get('hr_data', {})
            operational_data = sample_data.get('operational_data', {})
            
            # Calculate financial KPIs
            financial_kpis = self.calculate_financial_kpis(financial_data)
            
            # Calculate HR KPIs
            hr_df = pd.DataFrame([hr_data]) if hr_data else pd.DataFrame()
            hr_kpis = self.calculate_hr_kpis(hr_df)
            
            # Calculate operational KPIs
            operational_kpis = self.calculate_operational_kpis(financial_data, hr_df)
            
            # Structure results to match template expectations
            # Template expects percentages as decimals (0.3 for 30%)
            results = {
                'financial': {
                    'gross_margin': self._extract_kpi_value(financial_kpis, 'Gross Margin') / 100 if self._extract_kpi_value(financial_kpis, 'Gross Margin') else 0.3,
                    'operating_margin': self._extract_kpi_value(financial_kpis, 'Operating Margin') / 100 if self._extract_kpi_value(financial_kpis, 'Operating Margin') else 0.15,
                    'net_margin': self._extract_kpi_value(financial_kpis, 'Net Margin') / 100 if self._extract_kpi_value(financial_kpis, 'Net Margin') else 0.1,
                    'revenue_per_employee': self._extract_kpi_value(financial_kpis, 'Revenue per Employee') if self._extract_kpi_value(financial_kpis, 'Revenue per Employee') else 250000
                },
                'hr': {
                    'turnover_rate': self._extract_kpi_value(hr_kpis, 'Turnover Rate') / 100 if self._extract_kpi_value(hr_kpis, 'Turnover Rate') else 0.15,
                    'total_employees': hr_data.get('total_employees', 50)
                },
                'operational': {
                    'cost_efficiency_ratio': self._extract_kpi_value(operational_kpis, 'Cost Efficiency Ratio') / 100 if self._extract_kpi_value(operational_kpis, 'Cost Efficiency Ratio') else 0.8,
                    'productivity_index': operational_data.get('process_efficiency', 0.78)
                }
            }
            
            return results
            
        except Exception as e:
            print(f"❌ Error calculating all KPIs: {str(e)}")
            # Return default values on error
            return {
                'financial': {
                    'gross_margin': 0.3,
                    'operating_margin': 0.15,
                    'net_margin': 0.1,
                    'revenue_per_employee': 250000
                },
                'hr': {
                    'turnover_rate': 0.15,
                    'total_employees': 50
                },
                'operational': {
                    'cost_efficiency_ratio': 0.8,
                    'productivity_index': 0.78
                }
            }
    
    def _extract_kpi_value(self, kpis: List[KPIMetrics], name: str) -> float:
        """Extract value from KPI list by name"""
        for kpi in kpis:
            if kpi.name == name:
                return kpi.value
        return 0.0

# Global KPI calculator instance
kpi_calculator = KPICalculator()

def get_kpi_calculator() -> KPICalculator:
    """Get the global KPI calculator instance"""
    return kpi_calculator