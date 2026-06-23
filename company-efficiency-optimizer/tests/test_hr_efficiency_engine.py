"""Tests for HR Efficiency Engine."""

from __future__ import annotations

from hr_efficiency_engine import build_hr_plan


def test_hr_plan_flags_turnover_and_engagement():
    hr_data = {
        "turnover_rate": 0.22,
        "time_to_hire_days": 58,
        "absenteeism_rate": 0.04,
        "engagement_score": 62,
        "cost_per_hire": 4200,
        "revenue_per_employee": 72000,
    }
    plan = build_hr_plan(hr_data)
    assert plan["analysis"]["issues"]
    titles = [action["title"] for action in plan["actions"]]
    assert any("rotaci" in title.lower() for title in titles)
    assert any("engagement" in title.lower() for title in titles)
