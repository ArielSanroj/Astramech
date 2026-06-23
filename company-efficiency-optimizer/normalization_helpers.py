"""Helpers for sheet classification and heuristics."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def classify_sheet(sheet_name: str, df: pd.DataFrame) -> str:
    sheet_name_lower = sheet_name.lower()

    if any(keyword in sheet_name_lower for keyword in ["resultados", "pl", "profit", "income", "earnings"]):
        return "pl_statement"
    if any(keyword in sheet_name_lower for keyword in ["balance", "activo", "pasivo", "patrimonio", "assets", "liabilities"]):
        return "balance_sheet"
    if any(keyword in sheet_name_lower for keyword in ["hr", "empleado", "personal", "trabajador", "employee", "personnel"]):
        return "hr_data"

    content_text = " ".join([str(val) for val in df.values.flatten() if pd.notna(val)])
    content_lower = content_text.lower()

    if any(keyword in content_lower for keyword in ["revenue", "sales", "ventas", "ingresos", "utilidad", "profit"]):
        return "pl_statement"
    if any(keyword in content_lower for keyword in ["assets", "activos", "liabilities", "pasivos", "equity", "patrimonio"]):
        return "balance_sheet"

    return "unknown"


def classify_industry(financial_data: Dict[str, Any]) -> str:
    try:
        revenue = financial_data.get("revenue", 0)
        cogs = financial_data.get("cogs", 0)
        gross_margin = 0

        if revenue > 0:
            gross_margin = ((revenue - cogs) / revenue) * 100

        if gross_margin > 80:
            return "services"
        if gross_margin > 40:
            return "manufacturing"
        if financial_data.get("total_assets", 0) > revenue * 10:
            return "real_estate"
        return "retail"
    except Exception:
        return "services"


def estimate_employee_count(financial_data: Dict[str, Any]) -> int:
    try:
        revenue = financial_data.get("revenue", 0)
        industry = financial_data.get("industry", "services")

        if industry == "services":
            return max(5, int(revenue / 300000))
        if industry == "manufacturing":
            return max(10, int(revenue / 200000))
        if industry == "retail":
            return max(5, int(revenue / 100000))
        return max(5, int(revenue / 200000))
    except Exception:
        return 10
