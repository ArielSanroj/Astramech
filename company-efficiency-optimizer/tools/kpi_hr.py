"""HR KPI calculations."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from tools.kpi_models import KPIMetrics
from tools.kpi_utils import get_status, to_dataframe
from tools.kpi_benchmarks import resolve_benchmark


def calculate_turnover_rate(hr_data: pd.DataFrame) -> float:
    try:
        current_date = pd.Timestamp.now()
        one_year_ago = current_date - pd.DateOffset(months=12)

        hr_data_copy = hr_data.copy()
        hr_data_copy["terminationDate"] = pd.to_datetime(
            hr_data_copy["terminationDate"], errors="coerce"
        )

        recent_terminations = hr_data_copy[
            (hr_data_copy["terminationDate"] >= one_year_ago)
            & (hr_data_copy["terminationDate"] <= current_date)
        ].shape[0]

        avg_headcount = len(hr_data_copy)
        return (recent_terminations / avg_headcount) * 100 if avg_headcount > 0 else 0
    except Exception as exc:
        print(f"❌ Error calculating turnover rate: {exc}")
        return 0.0


def calculate_department_turnover(hr_data: pd.DataFrame) -> Dict[str, float]:
    dept_turnover: Dict[str, float] = {}
    try:
        for dept in hr_data["department"].unique():
            dept_data = hr_data[hr_data["department"] == dept]
            dept_turnover[dept] = calculate_turnover_rate(dept_data)
    except Exception as exc:
        print(f"❌ Error calculating department turnover: {exc}")
    return dept_turnover


def calculate_hr_kpis(
    hr_data: pd.DataFrame,
    benchmarks: Dict[str, Dict[str, float]],
    industry: str = "services",
    context: Dict[str, str] | None = None,
) -> List[KPIMetrics]:
    kpis: List[KPIMetrics] = []

    if not isinstance(hr_data, pd.DataFrame):
        hr_data = to_dataframe(hr_data)
    if hr_data.empty:
        return kpis

    turnover_rate = calculate_turnover_rate(hr_data)
    benchmark = resolve_benchmark(
        "turnover_rate",
        industry,
        (context or {}).get("country", "CO"),
        (context or {}).get("size", "mid"),
        (context or {}).get("period", "annual"),
        15.0,
    )
    status = get_status(turnover_rate, benchmark, higher_is_better=False)

    kpis.append(
        KPIMetrics(
            name="Turnover Rate",
            value=turnover_rate,
            benchmark=benchmark,
            status=status,
            trend="stable",
            description=f"Annual turnover rate: {turnover_rate:.1f}% vs {benchmark}% benchmark",
            formula="terminations / avg_headcount",
            inputs={"turnover_rate": turnover_rate},
        )
    )

    if "department" in hr_data.columns:
        dept_turnover = calculate_department_turnover(hr_data)
        for dept, rate in dept_turnover.items():
            status = get_status(rate, benchmark, higher_is_better=False)
            kpis.append(
                KPIMetrics(
                    name=f"{dept} Turnover Rate",
                    value=rate,
                    benchmark=benchmark,
                    status=status,
                    trend="stable",
                    description=f"{dept} department turnover: {rate:.1f}%",
                )
            )

    return kpis
