"""Scenario simulation utilities."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from tools.kpi_calculator import KPICalculator


def apply_scenario(financial_data: Dict[str, Any], scenario: Dict[str, float]) -> Dict[str, Any]:
    updated = deepcopy(financial_data)

    def apply_pct(key: str, pct: float) -> None:
        if key in updated and updated[key] not in (None, ""):
            updated[key] = updated[key] * (1 + pct)

    apply_pct("revenue", scenario.get("revenue_delta_pct", 0))
    apply_pct("cogs", scenario.get("cogs_delta_pct", 0))
    apply_pct("operating_expenses", scenario.get("opex_delta_pct", 0))
    apply_pct("net_income", scenario.get("net_income_delta_pct", 0))
    apply_pct("employee_count", scenario.get("headcount_delta_pct", 0))

    return updated


def run_simulation(
    financial_data: Dict[str, Any],
    scenario: Dict[str, float],
    industry: str = "services",
    context: Dict[str, str] | None = None,
) -> Dict[str, Any]:
    simulator = KPICalculator()
    updated = apply_scenario(financial_data, scenario)

    kpis = simulator.calculate_financial_kpis(updated, industry, context)
    return {
        "scenario": scenario,
        "updated_financials": updated,
        "kpis": [kpi.__dict__ for kpi in kpis],
    }
