"""Keyword-driven Excel parser for heterogeneous NIIF layouts."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import pandas as pd


class UniversalExcelParser:
    """Keyword-driven Excel parser for heterogeneous NIIF layouts."""

    def __init__(self):
        self.revenue_keywords = [
            "INGRESOS DE ACTIVIDADES ORDINARIAS",
            "INGRESOS ORDINARIOS",
            "VENTAS BRUTAS",
            "REVENUE",
            "SALES",
            "INGRESOS OPERACIONALES",
        ]
        self.cogs_keywords = [
            "COSTO DE VENTAS",
            "COSTO DE LA MERCANCIA VENDIDA",
            "COST OF SALES",
            "COGS",
        ]
        self.opex_keywords = [
            "GASTOS DE ADMINISTRACION",
            "GASTOS OPERATIVOS",
            "OPERATING EXPENSES",
            "GASTOS DE OPERACION",
        ]
        self.operating_income_keywords = [
            "RESULTADO OPERACIONAL",
            "UTILIDAD OPERATIVA",
            "OPERATING INCOME",
        ]
        self.net_income_keywords = [
            "RESULTADO DEL EJERCICIO",
            "UTILIDAD NETA",
            "NET INCOME",
            "RESULTADO INTEGRAL",
        ]
        self.total_assets_keywords = ["TOTAL ACTIVO", "TOTAL DE ACTIVOS", "TOTAL ASSETS"]
        self.cash_keywords = [
            "EFECTIVO Y EQUIVALENTES",
            "CASH AND CASH EQUIVALENTS",
            "DISPONIBILIDADES",
        ]
        self.payroll_keywords = ["GASTOS DE PERSONAL", "SUELDOS", "PAYROLL", "SALARIOS"]
        self.company_markers = ["APRU", "CARMANFE", "SAS", "S.A.S.", "LTDA"]

    def parse(self, file_path: str) -> Dict[str, Any]:
        workbook = pd.ExcelFile(file_path)
        result: Dict[str, Any] = {
            "company": None,
            "period": None,
            "currency": "COP",
            "revenue": None,
            "cogs": None,
            "opex": None,
            "operating_income": None,
            "net_income": None,
            "total_assets": None,
            "cash": None,
            "estimated_employees": None,
        }

        for sheet in workbook.sheet_names:
            df = workbook.parse(sheet, header=None)
            text_blob = " ".join(df.astype(str).fillna("").values.flatten())
            company_match = next(
                (marker for marker in self.company_markers if marker in text_blob.upper()), None
            )
            if company_match and not result["company"]:
                result["company"] = company_match
            period_match = re.search(
                r"(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[A-Za-z\s]*\d{4}",
                text_blob,
                re.IGNORECASE,
            )
            if period_match and not result["period"]:
                result["period"] = period_match.group(0)

            result["revenue"] = result["revenue"] or self._find_value_in_df(
                df, self.revenue_keywords
            )
            result["cogs"] = result["cogs"] or self._find_value_in_df(df, self.cogs_keywords)
            result["opex"] = result["opex"] or self._find_value_in_df(df, self.opex_keywords)
            result["operating_income"] = result["operating_income"] or self._find_value_in_df(
                df, self.operating_income_keywords
            )
            result["net_income"] = result["net_income"] or self._find_value_in_df(
                df, self.net_income_keywords
            )
            result["total_assets"] = result["total_assets"] or self._find_value_in_df(
                df, self.total_assets_keywords, min_abs=1000
            )
            result["cash"] = result["cash"] or self._find_value_in_df(
                df, self.cash_keywords, min_abs=1000
            )

            payroll_value = self._find_value_in_df(df, self.payroll_keywords, min_abs=1000)
            if payroll_value and not result["estimated_employees"]:
                result["estimated_employees"] = max(1, round(payroll_value / 940000))

        return result

    def _find_value_in_df(
        self, df: pd.DataFrame, keywords: List[str], min_abs: float = 1.0
    ) -> Optional[float]:
        if df.empty:
            return None
        normalized = df.astype(str).fillna("")
        for keyword in keywords:
            keyword_mask = normalized.apply(lambda col: col.str.contains(keyword, case=False, na=False))
            row_matches = keyword_mask.any(axis=1)
            if not row_matches.any():
                continue
            row_idx = row_matches[row_matches].index[0]
            row_values = df.loc[row_idx]
            for raw_value in reversed(row_values.dropna().values):
                numeric = self._clean_numeric(raw_value)
                if numeric is not None and abs(numeric) >= min_abs:
                    return numeric
        return None

    def _clean_numeric(self, value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            numeric = float(value)
            return numeric if abs(numeric) >= 1 else None
        if isinstance(value, str):
            stripped = re.sub(r"[^\d\-,.]", "", value)
            stripped = stripped.replace(",", "")
            try:
                numeric = float(stripped)
                return numeric if abs(numeric) >= 1 else None
            except ValueError:
                return None
        return None
