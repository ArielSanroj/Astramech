"""Tests for scenario simulation."""

from __future__ import annotations

from scenario_simulator import run_simulation


def test_run_simulation_changes_revenue():
    data = {
        "revenue": 1000,
        "cogs": 400,
        "operating_expenses": 300,
        "net_income": 200,
        "employee_count": 10,
        "industry": "services",
    }
    scenario = {"revenue_delta_pct": 0.1}
    result = run_simulation(data, scenario, "services", {"country": "CO", "size": "mid", "period": "annual"})

    assert result["updated_financials"]["revenue"] == 1100
    assert result["kpis"]
