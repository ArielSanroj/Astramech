"""
KPI Calculator Tool for Company Efficiency Optimizer

Thin wrapper that delegates KPI calculations to helper modules.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from tools.kpi_aggregate import calculate_all_kpis as _calculate_all_kpis
from tools.kpi_benchmarks import BENCHMARKS, DEPARTMENT_KPIS, SEVERITY_WEIGHTS
from tools.kpi_department import (
    calculate_department_kpis as _calculate_department_kpis,
    calculate_department_kpi_value as _calculate_department_kpi_value,
)
from tools.kpi_financial import calculate_financial_kpis as _calculate_financial_kpis
from tools.kpi_hr import (
    calculate_department_turnover as _calculate_department_turnover,
    calculate_hr_kpis as _calculate_hr_kpis,
    calculate_turnover_rate as _calculate_turnover_rate,
)
from tools.kpi_models import KPIMetrics
from tools.kpi_operational import calculate_operational_kpis as _calculate_operational_kpis
from tools.kpi_report import (
    generate_kpi_report as _generate_kpi_report,
    identify_inefficiencies as _identify_inefficiencies,
)
from tools.kpi_utils import (
    calculate_gap,
    coerce_number,
    determine_trend,
    extract_previous_entry,
    get_status,
    label_urgency,
    normalize_snapshot,
    score_issue,
    to_dataframe,
)


class KPICalculator:
    """Calculator for various business KPIs."""

    def __init__(self):
        self.benchmarks = BENCHMARKS
        self.department_kpis = DEPARTMENT_KPIS
        self._severity_weights = SEVERITY_WEIGHTS

    def _coerce_number(self, value: Any, default: float = 0.0) -> float:
        return coerce_number(value, default)

    def _determine_trend(self, current: Optional[float], previous: Optional[float], tolerance: float = 0.01) -> str:
        return determine_trend(current, previous, tolerance)

    def _calculate_gap(self, value: Optional[float], benchmark: Optional[float], higher_is_better: bool = True) -> float:
        return calculate_gap(value, benchmark, higher_is_better)

    def _score_issue(self, severity: str, gap: float, trend: str) -> float:
        return score_issue(severity, gap, trend, self._severity_weights)

    def _label_urgency(self, score: float) -> str:
        return label_urgency(score)

    def _normalize_snapshot(self, record: Optional[Dict[str, Any]], keys: Tuple[str, ...]) -> Dict[str, float]:
        return normalize_snapshot(record, keys)

    def _extract_previous_entry(self, data: Dict[str, Any], keys: Tuple[str, ...]) -> Dict[str, float]:
        return extract_previous_entry(data, keys)

    def calculate_all_kpis(self, data: Dict[str, Any], department: str = "Finance") -> Dict[str, Any]:
        return _calculate_all_kpis(self, data, department)

    def _to_dataframe(self, data) -> pd.DataFrame:
        return to_dataframe(data)

    def calculate_financial_kpis(
        self,
        financial_data: Dict[str, float],
        industry: str = "retail",
        context: Optional[Dict[str, str]] = None,
    ) -> List[KPIMetrics]:
        return _calculate_financial_kpis(financial_data, industry, self.benchmarks, context)

    def calculate_hr_kpis(
        self,
        hr_data: pd.DataFrame,
        industry: str = "services",
        context: Optional[Dict[str, str]] = None,
    ) -> List[KPIMetrics]:
        return _calculate_hr_kpis(hr_data, self.benchmarks, industry, context)

    def calculate_operational_kpis(
        self,
        financial_data: Dict[str, float],
        hr_data: pd.DataFrame,
        industry: str = "services",
        context: Optional[Dict[str, str]] = None,
    ) -> List[KPIMetrics]:
        return _calculate_operational_kpis(financial_data, hr_data, self.benchmarks, industry, context)

    def _calculate_turnover_rate(self, hr_data: pd.DataFrame) -> float:
        return _calculate_turnover_rate(hr_data)

    def _calculate_department_turnover(self, hr_data: pd.DataFrame) -> Dict[str, float]:
        return _calculate_department_turnover(hr_data)

    def _get_status(self, value: float, benchmark: float, higher_is_better: bool = True) -> str:
        return get_status(value, benchmark, higher_is_better)

    def generate_kpi_report(self, kpis: List[KPIMetrics]) -> str:
        return _generate_kpi_report(kpis)

    def identify_inefficiencies(self, kpis: List[KPIMetrics]) -> List[Dict[str, Any]]:
        return _identify_inefficiencies(kpis)

    def calculate_department_kpis(self, data: Dict[str, Any], department: str) -> List[KPIMetrics]:
        return _calculate_department_kpis(data, department, self.department_kpis)

    def _calculate_department_kpi_value(self, data: Dict[str, Any], department: str, kpi_name: str) -> float:
        return _calculate_department_kpi_value(data, department, kpi_name)


kpi_calculator = KPICalculator()


def get_kpi_calculator() -> KPICalculator:
    return kpi_calculator
