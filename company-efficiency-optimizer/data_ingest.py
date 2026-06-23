"""
Enhanced Data Ingestion Module for Company Efficiency Optimizer.

Thin wrapper around helper modules to keep the public API stable.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from dotenv import load_dotenv

from data_ingest_core import process_excel_file
from data_ingest_extractors import (
    calculate_ytd_metrics,
    extract_balance_sheet_data,
    extract_cash_flow_data,
    extract_eri_data,
    extract_hr_data,
    extract_pl_data,
)
from data_ingest_llm import excel_to_text, generalized_parse_excel
from data_ingest_merge import merge_financial_metrics
from data_ingest_sheet import classify_sheet
from data_ingest_summary import get_data_summary
from data_ingest_validation import (
    classify_industry,
    estimate_employee_count_improved,
    validate_financial_data,
)
from universal_excel_parser import UniversalExcelParser

load_dotenv()


class EnhancedDataIngestion:
    """Enhanced data ingestion handler for various data sources and formats."""

    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.colombian_patterns = {
            "revenue": [
                r"INGRESOS ORDINARIOS",
                r"VENTAS BRUTAS",
                r"INGRESOS OPERACIONALES",
            ],
            "cogs": [
                r"COSTO DE LA MERCANCIA VENDIDA",
                r"COSTO DE VENTAS",
                r"COSTO DE VENTA",
            ],
            "gross_profit": [r"UTILIDAD BRUTA", r"GANANCIA BRUTA"],
            "operating_expenses": [
                r"TOTAL GASTOS OPERACIONALES",
                r"GASTOS DE ADMINISTRACION",
                r"GASTOS OPERACIONALES",
            ],
            "operating_income": [r"RESULTADO OPERACIONAL", r"UTILIDAD OPERACIONAL"],
            "net_income": [
                r"RESULTADO DEL EJERCICIO",
                r"UTILIDAD NETA",
                r"GANANCIA NETA",
            ],
        }
        self.universal_parser = UniversalExcelParser()

    def process_excel_file(self, file_path: str, company_name: str = None, department: str = "Finance") -> Dict[str, Any]:
        return process_excel_file(self, file_path, company_name, department)

    def _merge_financial_metrics(self, financial_data: Dict[str, Any], parsed_metrics: Dict[str, Any]) -> None:
        merge_financial_metrics(financial_data, parsed_metrics)

    def _excel_to_text(self, file_path: str) -> str:
        return excel_to_text(file_path)

    def generalized_parse_excel(self, document_text: str) -> Dict[str, Any]:
        return generalized_parse_excel(document_text)

    def _classify_sheet(self, sheet_name: str, df):
        return classify_sheet(sheet_name, df)

    def _extract_pl_data(self, df):
        return extract_pl_data(df, self.colombian_patterns)

    def _extract_balance_sheet_data(self, df):
        return extract_balance_sheet_data(df)

    def _extract_cash_flow_data(self, df):
        return extract_cash_flow_data(df)

    def _extract_hr_data(self, df):
        return extract_hr_data(df)

    def _classify_industry(self, financial_data: Dict[str, Any]) -> str:
        return classify_industry(financial_data)

    def _estimate_employee_count(self, financial_data: Dict[str, Any]) -> int:
        return estimate_employee_count_improved(financial_data)

    def get_data_summary(self) -> Dict[str, Any]:
        return get_data_summary(self.data_dir)

    def _extract_eri_data(self, df, sheet_name: str) -> Dict[str, Any]:
        return extract_eri_data(df, sheet_name)

    def _calculate_ytd_metrics(self, ytd_data: Dict[str, Any]) -> Dict[str, Any]:
        return calculate_ytd_metrics(ytd_data)

    def _estimate_employee_count_improved(self, financial_data: Dict[str, Any]) -> int:
        return estimate_employee_count_improved(financial_data)

    def _validate_financial_data(self, financial_data: Dict[str, Any]) -> None:
        return validate_financial_data(financial_data)


enhanced_data_ingestion = EnhancedDataIngestion()


def get_enhanced_data_ingestion() -> EnhancedDataIngestion:
    return enhanced_data_ingestion
