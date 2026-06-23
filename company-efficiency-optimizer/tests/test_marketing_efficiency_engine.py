"""Tests for Marketing Efficiency Engine."""

from __future__ import annotations

from marketing_efficiency_engine import build_marketing_plan


def test_marketing_plan_flags_roi_and_funnel():
    marketing_data = {
        "cac": 420,
        "ltv": 980,
        "ltv_cac": 2.3,
        "roas": 1.6,
        "conversion_rate": 0.015,
        "churn_rate": 0.07,
        "mql_to_sql": 0.22,
    }
    plan = build_marketing_plan(marketing_data)
    assert plan["analysis"]["issues"]
    titles = [action["title"] for action in plan["actions"]]
    assert any("ROAS" in title or "roas" in title.lower() for title in titles)
    assert any("conversi" in title.lower() for title in titles)
