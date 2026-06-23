"""Tests for Sales Efficiency Engine."""

from __future__ import annotations

from sales_efficiency_engine import build_sales_plan


def test_sales_plan_flags_drop_off():
    sales_data = {
        "conversion_by_stage": {"Lead": 0.1, "Demo": 0.3},
        "avg_cycle_days": 30,
        "win_rate": 0.25,
    }
    plan = build_sales_plan(sales_data)
    assert plan["analysis"]["issues"]
    assert any("Optimizar etapa" in action["title"] for action in plan["actions"])
