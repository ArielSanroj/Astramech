"""Sheet classification helpers."""

from __future__ import annotations

import pandas as pd


def classify_sheet(sheet_name: str, df: pd.DataFrame) -> str:
    sheet_name_lower = sheet_name.lower()
    if any(keyword in sheet_name_lower for keyword in ["resultados", "pl", "profit", "income"]):
        return "pl_statement"
    if any(keyword in sheet_name_lower for keyword in ["balance", "activo", "pasivo", "patrimonio"]):
        return "balance_sheet"
    if any(keyword in sheet_name_lower for keyword in ["flujo", "cash", "efectivo"]):
        return "cash_flow"
    if any(keyword in sheet_name_lower for keyword in ["hr", "empleado", "personal", "trabajador"]):
        return "hr_data"

    content_text = " ".join([str(val) for val in df.values.flatten() if pd.notna(val)])
    content_lower = content_text.lower()

    if any(keyword in content_lower for keyword in ["ventas", "ingresos", "utilidad", "ganancia"]):
        return "pl_statement"
    if any(keyword in content_lower for keyword in ["activo", "pasivo", "patrimonio", "efectivo"]):
        return "balance_sheet"
    if any(keyword in content_lower for keyword in ["flujo", "efectivo", "cash"]):
        return "cash_flow"

    return "unknown"
