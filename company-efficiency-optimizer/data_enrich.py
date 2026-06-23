"""Enrichment utilities for financial data."""

from __future__ import annotations

from typing import Any, Dict


def enrich_financial_data(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    revenue = financial_data.get("revenue") or 0
    cogs = financial_data.get("cogs") or 0
    operating_expenses = financial_data.get("operating_expenses") or 0

    if revenue and cogs and financial_data.get("gross_profit") in (None, "", 0):
        financial_data["gross_profit"] = revenue - cogs

    if revenue and operating_expenses and financial_data.get("operating_income") in (None, "", 0):
        financial_data["operating_income"] = revenue - cogs - operating_expenses

    if financial_data.get("net_income") in (None, "") and financial_data.get("operating_income") not in (None, ""):
        financial_data["net_income"] = financial_data.get("operating_income")

    total_assets = financial_data.get("total_assets") or 0
    total_liabilities = financial_data.get("total_liabilities") or 0
    total_equity = financial_data.get("total_equity") or 0
    if total_assets and total_liabilities and not total_equity:
        financial_data["total_equity"] = total_assets - total_liabilities

    if not financial_data.get("country"):
        currency = (financial_data.get("currency") or "").upper()
        currency_map = {
            "COP": "CO",
            "USD": "US",
            "BRL": "BR",
            "EUR": "EU",
            "MXN": "MX",
            "ARS": "AR",
        }
        if currency in currency_map:
            financial_data["country"] = currency_map[currency]

    if not financial_data.get("company_size"):
        employee_count = financial_data.get("employee_count") or 0
        if employee_count >= 250:
            financial_data["company_size"] = "large"
        elif employee_count >= 50:
            financial_data["company_size"] = "mid"
        else:
            financial_data["company_size"] = "small"

    if not financial_data.get("period_type"):
        period = str(financial_data.get("period", "")).upper()
        if "Q" in period or "QUARTER" in period:
            financial_data["period_type"] = "quarterly"
        elif "MONTH" in period or "M" in period:
            financial_data["period_type"] = "monthly"
        else:
            financial_data["period_type"] = "annual"

    return financial_data
