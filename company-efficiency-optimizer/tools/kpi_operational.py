"""Operational KPI calculations."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from tools.kpi_models import KPIMetrics
from tools.kpi_utils import get_status
from tools.kpi_benchmarks import resolve_benchmark


def calculate_operational_kpis(
    financial_data: Dict[str, float],
    hr_data: pd.DataFrame,
    benchmarks: Dict[str, Dict[str, float]],
    industry: str = "services",
    context: Dict[str, str] | None = None,
) -> List[KPIMetrics]:
    kpis: List[KPIMetrics] = []

    if "revenue" in financial_data and "operating_expenses" in financial_data:
        cost_efficiency = financial_data["operating_expenses"] / financial_data["revenue"]
        benchmark = resolve_benchmark(
            "cost_efficiency",
            industry,
            (context or {}).get("country", "CO"),
            (context or {}).get("size", "mid"),
            (context or {}).get("period", "annual"),
            0.80,
        )
        status = get_status(cost_efficiency, benchmark, higher_is_better=False)
        kpis.append(
            KPIMetrics(
                name="Cost Efficiency Ratio",
                value=cost_efficiency * 100,
                benchmark=benchmark * 100,
                status=status,
                trend="stable",
                description=(
                    f"Operating expenses as % of revenue: {cost_efficiency*100:.1f}% "
                    f"vs {benchmark*100:.1f}% benchmark"
                ),
                formula="operating_expenses / revenue",
                inputs={
                    "operating_expenses": financial_data["operating_expenses"],
                    "revenue": financial_data["revenue"],
                },
            )
        )

    if "revenue" in financial_data and "employee_count" in financial_data:
        current_productivity = financial_data["revenue"] / financial_data["employee_count"]
        kpis.append(
            KPIMetrics(
                name="Productivity Index",
                value=current_productivity,
                benchmark=current_productivity,
                status="good",
                trend="stable",
                description=(
                    f"Current productivity: ${current_productivity:,.0f} revenue per employee"
                ),
                formula="revenue / employee_count",
                inputs={
                    "revenue": financial_data["revenue"],
                    "employee_count": financial_data["employee_count"],
                },
            )
        )

    return kpis
