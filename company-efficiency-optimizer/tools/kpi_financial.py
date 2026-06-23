"""Financial KPI calculations."""

from __future__ import annotations

from typing import Dict, List

from tools.kpi_models import KPIMetrics
from tools.kpi_utils import get_status
from tools.kpi_benchmarks import resolve_benchmark


def calculate_financial_kpis(
    financial_data: Dict[str, float],
    industry: str,
    benchmarks: Dict[str, Dict[str, float]],
    context: Dict[str, str] | None = None,
) -> List[KPIMetrics]:
    kpis: List[KPIMetrics] = []

    if "revenue" in financial_data and "cogs" in financial_data:
        gross_margin = ((financial_data["revenue"] - financial_data["cogs"]) / financial_data["revenue"]) * 100
        benchmark = resolve_benchmark(
            "gross_margin",
            industry,
            (context or {}).get("country", "CO"),
            (context or {}).get("size", "mid"),
            (context or {}).get("period", "annual"),
            30.0,
        )
        status = get_status(gross_margin, benchmark, higher_is_better=True)
        kpis.append(
            KPIMetrics(
                name="Gross Margin",
                value=gross_margin,
                benchmark=benchmark,
                status=status,
                trend="stable",
                description=f"Gross profit margin: {gross_margin:.1f}% vs {benchmark}% benchmark",
                formula="(revenue - cogs) / revenue",
                inputs={"revenue": financial_data["revenue"], "cogs": financial_data["cogs"]},
            )
        )

    if "revenue" in financial_data and "operating_income" in financial_data:
        operating_margin = (financial_data["operating_income"] / financial_data["revenue"]) * 100
        benchmark = resolve_benchmark(
            "operating_margin",
            industry,
            (context or {}).get("country", "CO"),
            (context or {}).get("size", "mid"),
            (context or {}).get("period", "annual"),
            10.0,
        )
        status = get_status(operating_margin, benchmark, higher_is_better=True)
        kpis.append(
            KPIMetrics(
                name="Operating Margin",
                value=operating_margin,
                benchmark=benchmark,
                status=status,
                trend="stable",
                description=f"Operating profit margin: {operating_margin:.1f}% vs {benchmark}% benchmark",
                formula="operating_income / revenue",
                inputs={
                    "operating_income": financial_data["operating_income"],
                    "revenue": financial_data["revenue"],
                },
            )
        )

    if "revenue" in financial_data and "net_income" in financial_data:
        net_margin = (financial_data["net_income"] / financial_data["revenue"]) * 100
        benchmark = resolve_benchmark(
            "net_margin",
            industry,
            (context or {}).get("country", "CO"),
            (context or {}).get("size", "mid"),
            (context or {}).get("period", "annual"),
            8.0,
        )
        status = get_status(net_margin, benchmark, higher_is_better=True)
        kpis.append(
            KPIMetrics(
                name="Net Margin",
                value=net_margin,
                benchmark=benchmark,
                status=status,
                trend="stable",
                description=f"Net profit margin: {net_margin:.1f}% vs {benchmark}% benchmark",
                formula="net_income / revenue",
                inputs={"net_income": financial_data["net_income"], "revenue": financial_data["revenue"]},
            )
        )

    if "revenue" in financial_data and "employee_count" in financial_data:
        revenue_per_employee = financial_data["revenue"] / financial_data["employee_count"]
        benchmark = resolve_benchmark(
            "revenue_per_employee",
            industry,
            (context or {}).get("country", "CO"),
            (context or {}).get("size", "mid"),
            (context or {}).get("period", "annual"),
            250000,
        )
        status = get_status(revenue_per_employee, benchmark, higher_is_better=True)
        kpis.append(
            KPIMetrics(
                name="Revenue per Employee",
                value=revenue_per_employee,
                benchmark=benchmark,
                status=status,
                trend="stable",
                description=(
                    f"Revenue per employee: ${revenue_per_employee:,.0f} vs ${benchmark:,.0f} benchmark"
                ),
                formula="revenue / employee_count",
                inputs={"revenue": financial_data["revenue"], "employee_count": financial_data["employee_count"]},
            )
        )

    return kpis
