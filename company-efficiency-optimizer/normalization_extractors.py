"""Extraction helpers for normalization layer."""

from __future__ import annotations

import re
from typing import Any, Dict, List

import pandas as pd

from normalization_models import SchemaMapping


def match_pattern(text: str, patterns: List[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def extract_pl_data(df: pd.DataFrame, schema_mapping: SchemaMapping) -> Dict[str, Any]:
    pl_data: Dict[str, Any] = {}
    try:
        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]) and (len(row) < 2 or pd.isna(row.iloc[1])):
                continue

            account_name = ""
            total_value = 0

            if not pd.isna(row.iloc[0]) and str(row.iloc[0]).strip():
                account_name = str(row.iloc[0]).strip()
                try:
                    if not pd.isna(row.iloc[2]):
                        total_value = float(row.iloc[2])
                except Exception:
                    pass
            elif not pd.isna(row.iloc[1]) and str(row.iloc[1]).strip():
                account_name = str(row.iloc[1]).strip()
                try:
                    if not pd.isna(row.iloc[3]):
                        total_value = float(row.iloc[3])
                except Exception:
                    pass
            else:
                account_name = str(row.iloc[0]).strip()
                try:
                    if not pd.isna(row.iloc[-1]):
                        total_value = float(row.iloc[-1])
                except Exception:
                    continue

            if match_pattern(account_name, schema_mapping.revenue_patterns):
                pl_data["revenue"] = total_value
            elif match_pattern(account_name, schema_mapping.cogs_patterns):
                pl_data["cogs"] = total_value
            elif match_pattern(account_name, schema_mapping.gross_profit_patterns):
                pl_data["gross_profit"] = total_value
            elif match_pattern(account_name, schema_mapping.operating_expenses_patterns):
                pl_data["operating_expenses"] = abs(total_value)
            elif match_pattern(account_name, schema_mapping.operating_income_patterns):
                pl_data["operating_income"] = total_value
            elif match_pattern(account_name, schema_mapping.net_income_patterns):
                pl_data["net_income"] = total_value

            if "INGRESOS ORDINARIOS" in account_name and total_value > 0:
                pl_data["revenue"] = total_value
            elif "VENTAS BRUTAS" in account_name and total_value > 0:
                pl_data["revenue"] = total_value
            elif "TOTAL GASTOS OPERACIONALES" in account_name and total_value != 0:
                pl_data["operating_expenses"] = abs(total_value)
            elif "RESULTADO OPERACIONAL" in account_name and total_value != 0:
                pl_data["operating_income"] = total_value
            elif "RESULTADO DEL EJERCICIO" in account_name and "UTILIDAD" in account_name and total_value != 0:
                pl_data["net_income"] = total_value
            elif "Ingresos de Actividades Ordinarias" in account_name and total_value > 0:
                pl_data["revenue"] = total_value
            elif "Costos de Ventas" in account_name and total_value > 0:
                pl_data["cogs"] = total_value
            elif "MARGEN BRUTO" in account_name and total_value > 0:
                pl_data["gross_profit"] = total_value
            elif "Gastos de Ventas" in account_name and total_value > 0:
                pl_data.setdefault("operating_expenses", 0)
                pl_data["operating_expenses"] += total_value
            elif "Gastos de Administración" in account_name and total_value > 0:
                pl_data.setdefault("operating_expenses", 0)
                pl_data["operating_expenses"] += total_value
            elif "RESULTADO OPERACIONAL" in account_name and total_value != 0:
                pl_data["operating_income"] = total_value

        return pl_data
    except Exception as exc:
        print(f"Error extracting P&L data: {exc}")
        return {}


def extract_balance_sheet_data(df: pd.DataFrame, schema_mapping: SchemaMapping) -> Dict[str, Any]:
    bs_data: Dict[str, Any] = {}
    try:
        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            account_name = (
                str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else str(row.iloc[0]).strip()
            )
            final_balance = 0

            try:
                if not pd.isna(row.iloc[-1]):
                    final_balance = float(row.iloc[-1])
            except Exception:
                continue

            if match_pattern(account_name, schema_mapping.total_assets_patterns):
                bs_data["total_assets"] = abs(final_balance)
            elif match_pattern(account_name, schema_mapping.total_liabilities_patterns):
                bs_data["total_liabilities"] = abs(final_balance)
            elif match_pattern(account_name, schema_mapping.total_equity_patterns):
                bs_data["total_equity"] = abs(final_balance)
            elif match_pattern(account_name, schema_mapping.cash_patterns):
                bs_data["cash_and_equivalents"] = abs(final_balance)

            if "Activo" in account_name and "Clase" in str(row.iloc[0]):
                bs_data["total_assets"] = abs(final_balance)
            elif "Pasivo" in account_name and "Clase" in str(row.iloc[0]):
                bs_data["total_liabilities"] = abs(final_balance)
            elif "Patrimonio" in account_name and "Clase" in str(row.iloc[0]):
                bs_data["total_equity"] = abs(final_balance)
            elif "Efectivo y equivalentes" in account_name and "Grupo" in str(row.iloc[0]):
                bs_data["cash_and_equivalents"] = abs(final_balance)
            elif "ACTIVOS TOTALES" in account_name and final_balance > 0:
                bs_data["total_assets"] = abs(final_balance)
            elif "PASIVOS TOTALES" in account_name and final_balance > 0:
                bs_data["total_liabilities"] = abs(final_balance)
            elif "PATRIMONIO TOTAL" in account_name and final_balance > 0:
                bs_data["total_equity"] = abs(final_balance)
            elif "Efectivo y equivalentes" in account_name and final_balance > 0:
                bs_data["cash_and_equivalents"] = abs(final_balance)

        return bs_data
    except Exception as exc:
        print(f"Error extracting balance sheet data: {exc}")
        return {}


def extract_hr_data(df: pd.DataFrame, schema_mapping: SchemaMapping) -> Dict[str, Any]:
    hr_data: Dict[str, Any] = {}
    try:
        employee_count = 0

        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            row_text = " ".join([str(val) for val in row if pd.notna(val)])

            if match_pattern(row_text, schema_mapping.employee_patterns):
                numbers = re.findall(r"\d+", row_text)
                if numbers:
                    employee_count = max(employee_count, int(numbers[0]))

        hr_data = {"employee_count": employee_count}
        return hr_data
    except Exception as exc:
        print(f"Error extracting HR data: {exc}")
        return {}
