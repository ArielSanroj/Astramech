"""Tests for Finance Efficiency Engine."""

from __future__ import annotations

from finance_efficiency_engine import build_finance_plan


def test_finance_plan_flags_liquidity_and_budget():
    finance_data = {
        "current_ratio": 1.1,
        "quick_ratio": 0.7,
        "gross_margin_pct": 15,
        "net_margin_pct": 3.2,
        "roe_pct": 6.0,
        "debt_to_equity": 2.5,
        "inventory_turnover": 3.0,
        "ebitda": -50000,
        "expense_execution_pct": 112,
        "revenue_execution_pct": 74,
    }
    plan = build_finance_plan(finance_data)
    assert plan["analysis"]["issues"]
    titles = [action["title"] for action in plan["actions"]]
    assert any("liquidez" in title.lower() for title in titles)
    assert any("gastos" in title.lower() for title in titles)
    assert any("margen" in title.lower() for title in titles)
    assert any("apalancamiento" in title.lower() for title in titles)
