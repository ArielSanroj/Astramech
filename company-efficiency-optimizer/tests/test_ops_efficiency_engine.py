"""Tests for Operations Efficiency Engine."""

from __future__ import annotations

from ops_efficiency_engine import build_ops_plan


def test_ops_plan_flags_low_efficiency():
    ops_data = {
        "cost_efficiency_ratio": 0.65,
        "opex_ratio": 0.45,
        "process_efficiency": 0.6,
        "on_time_delivery": 0.82,
        "cycle_time_days": 26,
        "rework_rate": 0.08,
        "capacity_utilization": 0.6,
        "inventory_turns": 3,
    }
    plan = build_ops_plan(ops_data)
    assert plan["analysis"]["issues"]
    titles = [action["title"] for action in plan["actions"]]
    assert any("Optimizar" in title or "Reducir" in title for title in titles)
    assert any("entregas" in title.lower() for title in titles)
    assert any("ciclo" in title.lower() for title in titles)
