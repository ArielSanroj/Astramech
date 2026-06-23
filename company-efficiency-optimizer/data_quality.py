"""Data quality checks and anomaly detection."""

from __future__ import annotations

from typing import Any, Dict, List


def detect_anomalies(financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    revenue = financial_data.get("revenue") or 0
    cogs = financial_data.get("cogs") or 0
    operating_expenses = financial_data.get("operating_expenses") or 0
    net_income = financial_data.get("net_income")
    employee_count = financial_data.get("employee_count") or 0

    if revenue and cogs and cogs > revenue:
        issues.append({
            "type": "consistency",
            "field": "cogs",
            "message": "COGS exceeds revenue",
        })

    if revenue and operating_expenses and operating_expenses > revenue:
        issues.append({
            "type": "consistency",
            "field": "operating_expenses",
            "message": "Operating expenses exceed revenue",
        })

    if net_income is not None and revenue:
        net_margin = net_income / revenue
        if net_margin < -0.5:
            issues.append({
                "type": "outlier",
                "field": "net_margin",
                "message": "Net margin below -50%",
            })
        if net_margin > 0.7:
            issues.append({
                "type": "outlier",
                "field": "net_margin",
                "message": "Net margin above 70%",
            })

    if employee_count and revenue:
        revenue_per_employee = revenue / employee_count
        if revenue_per_employee < 100000:
            issues.append({
                "type": "outlier",
                "field": "revenue_per_employee",
                "message": "Revenue per employee unusually low",
            })
        if revenue_per_employee > 5000000:
            issues.append({
                "type": "outlier",
                "field": "revenue_per_employee",
                "message": "Revenue per employee unusually high",
            })

    return issues
