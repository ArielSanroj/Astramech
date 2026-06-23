"""Merge utilities for parsed financial metrics."""

from __future__ import annotations

from typing import Any, Dict, Optional, Callable


def merge_financial_metrics(
    financial_data: Dict[str, Any],
    parsed_metrics: Dict[str, Any],
    set_metric: Optional[Callable[[Dict[str, Any], str, Any, str, bool], None]] = None,
    source: str = "universal",
) -> None:
    mapping = {
        "revenue": "revenue",
        "cogs": "cogs",
        "opex": "operating_expenses",
        "operating_income": "operating_income",
        "net_income": "net_income",
        "total_assets": "total_assets",
        "cash": "cash_and_equivalents",
        "estimated_employees": "employee_count",
    }

    for source_key, target_key in mapping.items():
        value = parsed_metrics.get(source_key)
        if value in (None, "", "N/A"):
            continue
        if target_key == "cash_and_equivalents":
            value = abs(float(value))
        if set_metric:
            allow_overwrite = target_key == "employee_count"
            set_metric(financial_data, target_key, value, source, allow_overwrite)
            continue
        if target_key == "employee_count":
            financial_data[target_key] = value
            continue
        if not financial_data.get(target_key):
            financial_data[target_key] = value

    if parsed_metrics.get("company"):
        if set_metric:
            set_metric(financial_data, "company", parsed_metrics["company"], source, True)
        else:
            financial_data["company"] = parsed_metrics["company"]
    if parsed_metrics.get("period"):
        if set_metric:
            set_metric(financial_data, "period", parsed_metrics["period"], source, True)
        else:
            financial_data["period"] = parsed_metrics["period"]
    if parsed_metrics.get("currency"):
        if set_metric:
            set_metric(financial_data, "currency", parsed_metrics["currency"], source, True)
        else:
            financial_data["currency"] = parsed_metrics["currency"]
