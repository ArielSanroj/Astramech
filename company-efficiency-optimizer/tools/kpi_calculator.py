"""
KPI Calculator Tool for Company Efficiency Optimizer

This module provides tools for calculating and analyzing key performance indicators
including financial ratios, operational metrics, and HR indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Union, Optional
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
        """Initialize the KPI calculator with 2025 industry benchmarks"""
        # Updated 2025 benchmarks for Colombia and global markets
        self.benchmarks = {
            'gross_margin': {
                'retail': 30.0, 'manufacturing': 25.0, 'services': 40.0, 
                'professional_services': 35.0, 'technology': 45.0, 'healthcare': 38.0
            },
            'operating_margin': {
                'retail': 8.0, 'manufacturing': 12.0, 'services': 15.0,
                'professional_services': 9.8, 'technology': 18.0, 'healthcare': 12.0
            },
            'net_margin': {
                'retail': 5.0, 'manufacturing': 8.0, 'services': 10.0,
                'professional_services': 6.5, 'technology': 15.0, 'healthcare': 8.0
            },
            'turnover_rate': {
                'retail': 15.0, 'manufacturing': 12.0, 'services': 18.0,
                'professional_services': 14.0, 'technology': 20.0, 'healthcare': 16.0
            },
            'revenue_per_employee': {
                'retail': 200000, 'manufacturing': 250000, 'services': 300000,
                'professional_services': 794000000, 'technology': 500000000, 'healthcare': 400000000
            },
            'cost_efficiency': {
                'retail': 0.85, 'manufacturing': 0.80, 'services': 0.75,
                'professional_services': 0.82, 'technology': 0.70, 'healthcare': 0.78
            },
            'revenue_growth_rate': {
                'retail': 5.0, 'manufacturing': 4.0, 'services': 7.0,
                'professional_services': 6.0, 'technology': 12.0, 'healthcare': 8.0
            }
        }
        
        # Department-specific KPIs and benchmarks
        self.department_kpis = {
            'marketing': {
                'marketing_roi': {'benchmark': 5.0, 'description': 'Revenue generated per marketing spend'},
                'customer_acquisition_cost': {'benchmark': 50000, 'description': 'Cost to acquire one customer (COP)'},
                'customer_lifetime_value': {'benchmark': 500000, 'description': 'Total value of a customer (COP)'},
                'conversion_rate': {'benchmark': 2.5, 'description': 'Percentage of leads that convert'},
                'marketing_spend_ratio': {'benchmark': 0.15, 'description': 'Marketing spend as % of revenue'}
            },
            'it': {
                'system_uptime': {'benchmark': 99.9, 'description': 'System availability percentage'},
                'response_time': {'benchmark': 200, 'description': 'Average response time (ms)'},
                'security_incidents': {'benchmark': 0, 'description': 'Number of security incidents'},
                'project_delivery_time': {'benchmark': 0.9, 'description': 'Projects delivered on time ratio'},
                'it_cost_ratio': {'benchmark': 0.05, 'description': 'IT costs as % of revenue'}
            },
            'r_d': {
                'innovation_index': {'benchmark': 0.8, 'description': 'New products/features per year'},
                'research_efficiency': {'benchmark': 0.75, 'description': 'Successful projects ratio'},
                'patent_filing_rate': {'benchmark': 2.0, 'description': 'Patents filed per year'},
                'r_d_investment_ratio': {'benchmark': 0.10, 'description': 'R&D investment as % of revenue'},
                'time_to_market': {'benchmark': 12, 'description': 'Months from concept to launch'}
            },
            'hr': {
                'employee_satisfaction': {'benchmark': 4.0, 'description': 'Employee satisfaction score (1-5)'},
                'training_hours_per_employee': {'benchmark': 40, 'description': 'Annual training hours per employee'},
                'internal_promotion_rate': {'benchmark': 0.15, 'description': 'Internal promotions ratio'},
                'diversity_index': {'benchmark': 0.6, 'description': 'Workforce diversity score'},
                'hr_cost_per_employee': {'benchmark': 500000, 'description': 'HR costs per employee (COP)'}
            }
        }

        self._severity_weights = {
            'critical': 1.0,
            'warning': 0.6,
            'good': 0.25,
            'excellent': 0.0
        }

    def _coerce_number(self, value: Any, default: float = 0.0) -> float:
        if value is None:
            return default
        try:
            if isinstance(value, str):
                cleaned = value.strip()
                if not cleaned:
                    return default
                return float(cleaned.replace(',', ''))
            return float(value)
        except (TypeError, ValueError):
            return default

    def _determine_trend(self, current: Optional[float], previous: Optional[float], tolerance: float = 0.01) -> str:
        if previous in (None, 0):
            return 'stable'
        if current is None:
            return 'stable'
        delta = (current - previous) / abs(previous)
        if delta >= tolerance:
            return 'improving'
        if delta <= -tolerance:
            return 'declining'
        return 'stable'

    def _calculate_gap(self, value: Optional[float], benchmark: Optional[float], higher_is_better: bool = True) -> float:
        if value is None or benchmark in (None, 0):
            return 0.0
        diff = value - benchmark
        gap = diff / abs(benchmark) if benchmark else 0.0
        return gap if higher_is_better else -gap

    def _score_issue(self, severity: str, gap: float, trend: str) -> float:
        weight = self._severity_weights.get(severity, 0.0)
        score = weight * 0.7 + min(1.0, max(0.0, abs(gap))) * 0.3
        if trend == 'declining':
            score += 0.1
        elif trend == 'improving':
            score -= 0.1
        return max(0.0, min(1.2, score))

    def _label_urgency(self, score: float) -> str:
        if score >= 0.85:
            return 'very_high'
        if score >= 0.6:
            return 'high'
        if score >= 0.35:
            return 'medium'
        return 'low'

    def _normalize_snapshot(self, record: Optional[Dict[str, Any]], keys: Tuple[str, ...]) -> Dict[str, float]:
        if not isinstance(record, dict):
            return {}
        normalized: Dict[str, float] = {}
        for key in keys:
            normalized[key] = self._coerce_number(record.get(key))
        return normalized

    def _extract_previous_entry(self, data: Dict[str, Any], keys: Tuple[str, ...]) -> Dict[str, float]:
        candidates: List[Dict[str, Any]] = []
        previous = data.get('previous_period')
        if isinstance(previous, dict):
            candidates.append(previous)
        historical = data.get('historical') or data.get('history')
        if isinstance(historical, list) and len(historical) >= 2:
            candidates.append(historical[-2])

        for candidate in candidates:
            normalized = self._normalize_snapshot(candidate, keys)
            if any(value for value in normalized.values()):
                return normalized
        return {}
    
    def calculate_all_kpis(self, data: Dict[str, Any], department: str = 'Finance') -> Dict[str, Any]:
        """Aggregate financial, HR, operational, and department KPIs from heterogeneous inputs"""

        def _to_number(value, default: float = 0.0) -> float:
            return self._coerce_number(value, default)

        industry_key = str(
            data.get('industry')
            or data.get('company_info', {}).get('industry')
            or 'services'
        ).lower()
        financial_data = data.get('financial_data') or {}
        hr_input = data.get('hr_data')
        operational_input = data.get('operational_data') or {}

        baseline_revenue = 1_000_000.0
        baseline_employees = 50

        revenue = _to_number(financial_data.get('revenue'))
        cogs_value = financial_data.get('cogs', financial_data.get('cost_of_goods_sold'))
        cogs = _to_number(cogs_value)
        operating_expenses = _to_number(financial_data.get('operating_expenses'))
        gross_profit_value = financial_data.get('gross_profit')
        if gross_profit_value is None and revenue and cogs:
            gross_profit_value = revenue - cogs
        gross_profit = _to_number(gross_profit_value)

        operating_income_value = financial_data.get('operating_income')
        if operating_income_value is None and revenue:
            operating_income_value = revenue - cogs - operating_expenses
        operating_income = _to_number(operating_income_value)

        net_income = _to_number(financial_data.get('net_income'))

        missing_financials = not any([
            financial_data.get('revenue'),
            financial_data.get('cogs'),
            financial_data.get('cost_of_goods_sold'),
            financial_data.get('operating_income'),
            financial_data.get('net_income')
        ])
        if missing_financials:
            revenue = baseline_revenue
            cogs = baseline_revenue * 0.7
            operating_expenses = baseline_revenue * 0.2
            gross_profit = revenue - cogs
            operating_income = revenue - cogs - operating_expenses
            net_income = baseline_revenue * 0.15

        hr_total_employees = None
        hr_turnover_rate = None
        hr_df = None

        if isinstance(hr_input, dict):
            records = None
            if isinstance(hr_input.get('records'), (list, pd.DataFrame)):
                records = hr_input['records']
            elif isinstance(hr_input.get('data'), (list, pd.DataFrame)):
                records = hr_input['data']

            if records is not None:
                hr_df = self._to_dataframe(records)
            else:
                hr_total_employees = _to_number(
                    hr_input.get('total_employees') or hr_input.get('employee_count')
                )
                turnover_candidate = hr_input.get('turnover_rate') or hr_input.get('attrition_rate')
                if turnover_candidate is not None:
                    hr_turnover_rate = _to_number(turnover_candidate)
        elif hr_input is not None:
            try:
                hr_df = self._to_dataframe(hr_input)
            except ValueError:
                hr_df = None

        if hr_df is not None and not hr_df.empty:
            hr_total_employees = hr_total_employees or hr_df.shape[0]
            if 'terminationDate' in hr_df.columns:
                turnover_pct = self._calculate_turnover_rate(hr_df)
                hr_turnover_rate = turnover_pct / 100.0

        if hr_turnover_rate is not None and hr_turnover_rate > 1.0:
            hr_turnover_rate = hr_turnover_rate / 100.0
        hr_total_employees = int(hr_total_employees) if hr_total_employees not in (None, '') else 0
        if not hr_total_employees:
            hr_total_employees = baseline_employees

        employee_count = financial_data.get('employee_count')
        if employee_count in (None, ''):
            employee_count = data.get('employee_count')
        if employee_count in (None, ''):
            employee_count = hr_total_employees
        employee_count = _to_number(employee_count)
        employee_count = int(employee_count) if employee_count else 0
        if not employee_count and hr_total_employees:
            employee_count = hr_total_employees

        revenue_per_employee = revenue / employee_count if employee_count else 0.0

        gross_margin_ratio = (gross_profit / revenue) if revenue else 0.0
        operating_margin_ratio = (operating_income / revenue) if revenue else 0.0
        net_margin_ratio = (net_income / revenue) if revenue else 0.0

        cost_efficiency_ratio = 1.0 - (operating_expenses / revenue) if revenue else None
        process_efficiency = _to_number(operational_input.get('process_efficiency'))
        if process_efficiency:
            cost_efficiency_ratio = max(cost_efficiency_ratio or 0.0, process_efficiency)
        cost_efficiency_ratio = max(cost_efficiency_ratio or 0.0, 0.0)

        rev_emp_benchmark = self.benchmarks['revenue_per_employee'].get(
            industry_key, self.benchmarks['revenue_per_employee'].get('services', 300000)
        )
        productivity_index = (
            (revenue_per_employee / rev_emp_benchmark)
            if (rev_emp_benchmark and employee_count)
            else None
        )

        financial_metric_input = {
            'revenue': revenue,
            'cogs': cogs,
            'operating_income': operating_income,
            'net_income': net_income
        }
        if employee_count:
            financial_metric_input['employee_count'] = employee_count

        financial_kpis = self.calculate_financial_kpis(financial_metric_input, industry_key) if revenue else []
        hr_kpis = self.calculate_hr_kpis(hr_df) if hr_df is not None and not hr_df.empty else []
        operational_input_for_calc = {
            'revenue': revenue,
            'operating_expenses': operating_expenses
        }
        if employee_count:
            operational_input_for_calc['employee_count'] = employee_count

        operational_kpis = self.calculate_operational_kpis(
            operational_input_for_calc,
            hr_df if hr_df is not None else pd.DataFrame()
        ) if (revenue and operating_expenses) else []

        dept_key = (department or '').lower() if department else ''
        department_kpis = self.calculate_department_kpis(data, dept_key) if dept_key else []

        inefficiencies = self.identify_inefficiencies(
            financial_kpis + hr_kpis + operational_kpis + department_kpis
        )

        def _clean_value(value):
            if isinstance(value, np.generic):
                return float(value)
            return value

        def _clean_dict(obj: KPIMetrics) -> Dict[str, Any]:
            return {key: _clean_value(val) for key, val in obj.__dict__.items()}

        cleaned_inefficiencies = [
            {key: _clean_value(val) for key, val in issue.items()}
            for issue in inefficiencies
        ]

        financial_benchmarks = {
            'gross_margin': self.benchmarks['gross_margin'].get(industry_key),
            'operating_margin': self.benchmarks['operating_margin'].get(industry_key),
            'net_margin': self.benchmarks['net_margin'].get(industry_key),
            'revenue_per_employee': rev_emp_benchmark
        }

        hr_benchmark = self.benchmarks['turnover_rate'].get(industry_key, 0.0) / 100.0

        # Compute weighted efficiency score comparing against benchmarks (honest scoring)
        weights = {
            'gross_margin': 0.30,
            'operating_margin': 0.25,
            'net_margin': 0.20,
            'revenue_per_employee': 0.15,
            'cost_efficiency': 0.10
        }

        available_weights = 0.0
        score_accum = 0.0

        def get_benchmark(kpi_name: str) -> float:
            """Get benchmark value for a KPI"""
            if kpi_name == 'gross_margin':
                return self.benchmarks['gross_margin'].get(industry_key, 30.0) / 100.0
            elif kpi_name == 'operating_margin':
                return self.benchmarks['operating_margin'].get(industry_key, 10.0) / 100.0
            elif kpi_name == 'net_margin':
                return self.benchmarks['net_margin'].get(industry_key, 8.0) / 100.0
            elif kpi_name == 'revenue_per_employee':
                return rev_emp_benchmark
            elif kpi_name == 'cost_efficiency':
                return self.benchmarks['cost_efficiency'].get(industry_key, 0.75)
            return 0.0

        if revenue:
            if gross_margin_ratio is not None:
                benchmark = get_benchmark('gross_margin')
                if benchmark > 0:
                    # Use conservative scaling: 1.0 = benchmark, max 1.3x for excellent performance
                    ratio = gross_margin_ratio / benchmark
                    if ratio >= 1.0:
                        # Cap excellent performance at 1.3x benchmark (max 130% score contribution)
                        # Use square root scaling to prevent inflation
                        performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                    else:
                        # Below benchmark: linear scale
                        performance = ratio
                    available_weights += weights['gross_margin']
                    score_accum += weights['gross_margin'] * performance
            
            if operating_margin_ratio is not None:
                benchmark = get_benchmark('operating_margin')
                if benchmark > 0:
                    ratio = operating_margin_ratio / benchmark
                    if ratio >= 1.0:
                        performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                    else:
                        performance = ratio
                    available_weights += weights['operating_margin']
                    score_accum += weights['operating_margin'] * performance
            
            if net_margin_ratio is not None:
                benchmark = get_benchmark('net_margin')
                if benchmark > 0:
                    ratio = net_margin_ratio / benchmark
                    if ratio >= 1.0:
                        performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                    else:
                        performance = ratio
                    available_weights += weights['net_margin']
                    score_accum += weights['net_margin'] * performance
            
            if revenue_per_employee and rev_emp_benchmark:
                benchmark = get_benchmark('revenue_per_employee')
                if benchmark > 0:
                    ratio = revenue_per_employee / benchmark
                    if ratio >= 1.0:
                        performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                    else:
                        performance = ratio
                    available_weights += weights['revenue_per_employee']
                    score_accum += weights['revenue_per_employee'] * performance
            
            if cost_efficiency_ratio is not None:
                benchmark = get_benchmark('cost_efficiency')
                if benchmark > 0:
                    ratio = cost_efficiency_ratio / benchmark
                    if ratio >= 1.0:
                        performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                    else:
                        performance = ratio
                    available_weights += weights['cost_efficiency']
                    score_accum += weights['cost_efficiency'] * performance

        efficiency_score = None
        if available_weights > 0:
            # Normalize to 0-100 scale (max 100 = excellent performance)
            efficiency_score = round(min((score_accum / available_weights) * 100, 100), 1)

        department_summary = {
            'name': department or 'Finance',
            'kpis': {kpi.name: kpi.value for kpi in department_kpis},
            'benchmarks': {kpi.name: kpi.benchmark for kpi in department_kpis}
        }

        return {
            'financial': {
                'gross_margin': gross_margin_ratio,
                'operating_margin': operating_margin_ratio,
                'net_margin': net_margin_ratio,
                'revenue_per_employee': revenue_per_employee,
                'benchmarks': financial_benchmarks
            },
            'hr': {
                'turnover_rate': hr_turnover_rate,
                'total_employees': hr_total_employees,
                'benchmark_turnover_rate': hr_benchmark
            },
            'operational': {
                'cost_efficiency_ratio': cost_efficiency_ratio,
                'productivity_index': productivity_index,
                'customer_satisfaction': _to_number(operational_input.get('customer_satisfaction')),
                'projects_completed': int(_to_number(operational_input.get('projects_completed'))) if operational_input.get('projects_completed') is not None else None
            },
            'department': department_summary,
            'efficiency_score': efficiency_score,
            'inefficiencies': cleaned_inefficiencies,
            'raw_kpis': {
                'financial': [_clean_dict(kpi) for kpi in financial_kpis],
                'hr': [_clean_dict(kpi) for kpi in hr_kpis],
                'operational': [_clean_dict(kpi) for kpi in operational_kpis],
                'department': [_clean_dict(kpi) for kpi in department_kpis]
            }
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
            
            # Create a copy to avoid SettingWithCopyWarning
            hr_data_copy = hr_data.copy()
            
            # Convert termination dates
            hr_data_copy['terminationDate'] = pd.to_datetime(hr_data_copy['terminationDate'], errors='coerce')
            
            # Count terminations in last 12 months
            recent_terminations = hr_data_copy[
                (hr_data_copy['terminationDate'] >= one_year_ago) & 
                (hr_data_copy['terminationDate'] <= current_date)
            ].shape[0]
            
            # Calculate average headcount
            avg_headcount = len(hr_data_copy)
            
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
    
    def calculate_department_kpis(self, data: Dict[str, Any], department: str) -> List[KPIMetrics]:
        """Calculate department-specific KPIs"""
        kpis = []
        
        if department not in self.department_kpis:
            return kpis
        
        dept_config = self.department_kpis[department]
        
        for kpi_name, config in dept_config.items():
            value = self._calculate_department_kpi_value(data, department, kpi_name)
            benchmark = config['benchmark']
            status = self._get_status(value, benchmark, higher_is_better=True)
            
            kpis.append(KPIMetrics(
                name=kpi_name.replace('_', ' ').title(),
                value=value,
                benchmark=benchmark,
                status=status,
                trend='stable',
                description=config['description']
            ))
        
        return kpis
    
    def _calculate_department_kpi_value(self, data: Dict[str, Any], department: str, kpi_name: str) -> float:
        """Calculate specific department KPI values"""
        financial_data = data.get('financial_data', {})
        department_data = data.get(f'{department}_data', {})
        
        if department == 'marketing':
            if kpi_name == 'marketing_roi':
                marketing_spend = department_data.get('marketing_spend', financial_data.get('operating_expenses', 0) * 0.15)
                marketing_revenue = department_data.get('marketing_revenue', financial_data.get('revenue', 0) * 0.3)
                return marketing_revenue / marketing_spend if marketing_spend > 0 else 0
            
            elif kpi_name == 'customer_acquisition_cost':
                return department_data.get('customer_acquisition_cost', 50000)
            
            elif kpi_name == 'conversion_rate':
                return department_data.get('conversion_rate', 2.5)
        
        elif department == 'it':
            if kpi_name == 'system_uptime':
                return department_data.get('system_uptime', 99.9)
            
            elif kpi_name == 'response_time':
                return department_data.get('response_time', 200)
            
            elif kpi_name == 'security_incidents':
                return department_data.get('security_incidents', 0)
        
        elif department == 'r_d':
            if kpi_name == 'innovation_index':
                return department_data.get('innovation_index', 0.8)
            
            elif kpi_name == 'r_d_investment_ratio':
                r_d_investment = department_data.get('r_d_investment', financial_data.get('operating_expenses', 0) * 0.10)
                revenue = financial_data.get('revenue', 1)
                return r_d_investment / revenue if revenue > 0 else 0
        
        elif department == 'hr':
            if kpi_name == 'employee_satisfaction':
                return department_data.get('employee_satisfaction', 4.0)
            
            elif kpi_name == 'training_hours_per_employee':
                return department_data.get('training_hours_per_employee', 40)
        
        return 0.0
    

# Global KPI calculator instance
kpi_calculator = KPICalculator()

def get_kpi_calculator() -> KPICalculator:
    """Get the global KPI calculator instance"""
    return kpi_calculator
