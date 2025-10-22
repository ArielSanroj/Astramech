"""
Data models for analysis results
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class CompanyInfo:
    """Company information model"""
    name: str
    industry: str
    size: str
    employee_count: int
    revenue_range: Optional[str] = None
    current_challenges: Optional[str] = None
    goals: Optional[str] = None
    analysis_focus: Optional[List[str]] = None

@dataclass
class FinancialKPIs:
    """Financial KPI model"""
    gross_margin: float
    operating_margin: float
    net_margin: float
    revenue_per_employee: float
    return_on_assets: Optional[float] = None
    return_on_equity: Optional[float] = None

@dataclass
class HRKPIs:
    """HR KPI model"""
    turnover_rate: float
    total_employees: int
    employee_satisfaction: Optional[float] = None
    training_hours_per_employee: Optional[float] = None

@dataclass
class OperationalKPIs:
    """Operational KPI model"""
    cost_efficiency_ratio: float
    productivity_index: float
    process_efficiency: Optional[float] = None
    quality_score: Optional[float] = None

@dataclass
class AnalysisResults:
    """Complete analysis results model"""
    company_name: str
    kpi_results: Dict[str, Any]
    diagnostic_results: Dict[str, Any]
    file_summary: Dict[str, str]
    timestamp: datetime
    analysis_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()
