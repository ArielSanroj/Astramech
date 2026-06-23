"""Extraction helpers for structured financial sheets."""

from __future__ import annotations

import re
from typing import Any, Dict, List

import pandas as pd


def extract_pl_data(df: pd.DataFrame, colombian_patterns: Dict[str, List[str]]) -> Dict[str, Any]:
    pl_data: Dict[str, Any] = {}

    try:
        def rightmost_numeric(series: pd.Series) -> float:
            for col in series.index[::-1]:
                try:
                    val = series[col]
                    if pd.isna(val):
                        continue
                    if series.index.get_loc(col) == 0:
                        continue
                    num = float(str(val).replace(",", "").replace(" ", ""))
                    return num
                except Exception:
                    continue
            return 0.0

        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            account_name = str(row.iloc[0]).strip()
            total_value = rightmost_numeric(row)
            if total_value == 0:
                continue

            for key, patterns in colombian_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, account_name, re.IGNORECASE):
                        if key == "operating_expenses":
                            pl_data[key] = abs(total_value)
                        else:
                            pl_data[key] = total_value
                        print(f"   Found {key}: ${total_value:,.0f}")
                        break

            if "revenue" not in pl_data and "VENTAS" in account_name and total_value > 0:
                pl_data["revenue"] = total_value
                print(f"   Found revenue (alternative): ${total_value:,.0f}")

        if "revenue" in pl_data and "cogs" in pl_data:
            pl_data["gross_profit"] = pl_data["revenue"] - pl_data["cogs"]
        elif "gross_profit" in pl_data and "revenue" in pl_data:
            pl_data["cogs"] = pl_data["revenue"] - pl_data["gross_profit"]

        return pl_data
    except Exception as exc:
        print(f"❌ Error extracting P&L data: {exc}")
        return {}


def extract_balance_sheet_data(df: pd.DataFrame) -> Dict[str, Any]:
    bs_data: Dict[str, Any] = {}
    try:
        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            account_name = str(row.iloc[3]).strip() if not pd.isna(row.iloc[3]) else ""
            final_balance = 0

            try:
                if not pd.isna(row.iloc[-1]):
                    final_balance = float(row.iloc[-1])
            except Exception:
                continue

            if "Activo" in account_name and "Clase" in str(row.iloc[0]):
                bs_data["total_assets"] = abs(final_balance)
                print(f"   Found Total Assets: ${final_balance:,.0f}")
            elif "Pasivo" in account_name and "Clase" in str(row.iloc[0]):
                bs_data["total_liabilities"] = abs(final_balance)
                print(f"   Found Total Liabilities: ${final_balance:,.0f}")
            elif "Patrimonio" in account_name and "Clase" in str(row.iloc[0]):
                bs_data["total_equity"] = abs(final_balance)
                print(f"   Found Total Equity: ${final_balance:,.0f}")
            elif "Efectivo y equivalentes" in account_name and "Grupo" in str(row.iloc[0]):
                bs_data["cash_and_equivalents"] = abs(final_balance)
                print(f"   Found Cash: ${final_balance:,.0f}")
            elif "Inversiones" in account_name and "Grupo" in str(row.iloc[0]):
                bs_data["investments"] = abs(final_balance)
                print(f"   Found Investments: ${final_balance:,.0f}")
            elif "Deudores comerciales" in account_name and "Grupo" in str(row.iloc[0]):
                bs_data["receivables"] = abs(final_balance)
                print(f"   Found Receivables: ${final_balance:,.0f}")
            elif "Propiedad planta y equipo" in account_name and "Grupo" in str(row.iloc[0]):
                bs_data["fixed_assets"] = abs(final_balance)
                print(f"   Found Fixed Assets: ${final_balance:,.0f}")

        return bs_data
    except Exception as exc:
        print(f"❌ Error extracting balance sheet data: {exc}")
        return {}


def extract_cash_flow_data(df: pd.DataFrame) -> Dict[str, Any]:
    cf_data: Dict[str, Any] = {}
    try:
        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            account_name = str(row.iloc[0]).strip()
            total_value = 0

            try:
                if not pd.isna(row.iloc[-1]):
                    total_value = float(row.iloc[-1])
            except Exception:
                continue

            if "flujo de efectivo" in account_name.lower():
                cf_data["net_cash_flow"] = total_value
                print(f"   Found Net Cash Flow: ${total_value:,.0f}")

        return cf_data
    except Exception as exc:
        print(f"❌ Error extracting cash flow data: {exc}")
        return {}


def extract_hr_data(df: pd.DataFrame) -> Dict[str, Any]:
    hr_data: Dict[str, Any] = {}
    try:
        employee_count = 0
        departments = []

        for _, row in df.iterrows():
            if pd.isna(row.iloc[0]):
                continue

            row_text = " ".join([str(val) for val in row if pd.notna(val)])

            if "empleado" in row_text.lower() or "trabajador" in row_text.lower():
                numbers = re.findall(r"\d+", row_text)
                if numbers:
                    employee_count = max(employee_count, int(numbers[0]))

            if "departamento" in row_text.lower() or "area" in row_text.lower():
                departments.append(row_text)

        hr_data = {"employee_count": employee_count, "departments": departments}

        if employee_count > 0:
            print(f"   Found Employee Count: {employee_count}")

        return hr_data
    except Exception as exc:
        print(f"❌ Error extracting HR data: {exc}")
        return {}


def extract_eri_data(df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
    eri_data: Dict[str, Any] = {}
    try:
        if "Codigo" in df.columns:
            revenue_row = df[df["Codigo"] == "4"]
            if not revenue_row.empty:
                month_columns = [col for col in df.columns if "2025" in str(col)]
                if month_columns:
                    latest_month = month_columns[-1]
                    eri_data["revenue_ytd"] = (
                        revenue_row[latest_month].iloc[0] if latest_month in revenue_row.columns else 0
                    )
                    print(
                        f"   📈 Revenue YTD ({latest_month}): ${eri_data['revenue_ytd']:,.0f} COP"
                    )

        if "Codigo" in df.columns:
            opex_rows = df[df["Codigo"].str.startswith("51", na=False)]
            if not opex_rows.empty:
                month_columns = [col for col in df.columns if "2025" in str(col)]
                if month_columns:
                    latest_month = month_columns[-1]
                    eri_data["opex_ytd"] = (
                        opex_rows[latest_month].sum() if latest_month in opex_rows.columns else 0
                    )
                    print(
                        f"   💰 Operating Expenses YTD ({latest_month}): ${eri_data['opex_ytd']:,.0f} COP"
                    )

        if "revenue_ytd" in eri_data and "opex_ytd" in eri_data:
            eri_data["net_profit_ytd"] = eri_data["revenue_ytd"] - eri_data["opex_ytd"]
            print(f"   💵 Net Profit YTD: ${eri_data['net_profit_ytd']:,.0f} COP")
    except Exception as exc:
        print(f"   ⚠️ Error extracting ERI data: {exc}")

    return eri_data


def calculate_ytd_metrics(ytd_data: Dict[str, Any]) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}

    if "revenue_ytd" in ytd_data:
        metrics["revenue"] = ytd_data["revenue_ytd"]
        metrics["revenue_ytd"] = ytd_data["revenue_ytd"]

    if "opex_ytd" in ytd_data:
        metrics["operating_expenses"] = ytd_data["opex_ytd"]
        metrics["operating_expenses_ytd"] = ytd_data["opex_ytd"]

    if "net_profit_ytd" in ytd_data:
        metrics["net_income"] = ytd_data["net_profit_ytd"]
        metrics["net_income_ytd"] = ytd_data["net_profit_ytd"]

    return metrics
