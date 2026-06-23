"""
Normalization Layer for Company Efficiency Optimizer.

Thin wrapper around helpers to normalize diverse financial data sources.
"""

from __future__ import annotations

from typing import Any, Dict

import logging
import pandas as pd

from normalization_detection import (
    detect_accounting_standard,
    detect_currency,
    detect_file_format,
    detect_language,
    get_schema_mapping,
)
from normalization_extractors import (
    extract_balance_sheet_data,
    extract_hr_data,
    extract_pl_data,
)
from normalization_helpers import (
    classify_industry,
    classify_sheet,
    estimate_employee_count,
)
from normalization_loaders import (
    extract_text_content,
    load_csv_data,
    load_excel_data,
    load_json_data,
    load_pdf_data,
)
from normalization_mappings import define_unified_schema, load_schema_mappings
from normalization_models import AccountingStandard, FileFormat, Language, SchemaMapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NormalizationLayer:
    """Normalization layer for diverse file formats and accounting standards."""

    def __init__(self):
        self.schema_mappings = load_schema_mappings()
        self.unified_schema = define_unified_schema()

    def detect_file_format(self, file_path: str) -> FileFormat:
        return detect_file_format(file_path)

    def detect_language(self, text: str) -> Language:
        return detect_language(text)

    def detect_accounting_standard(self, text: str, language: Language) -> AccountingStandard:
        return detect_accounting_standard(text, language)

    def get_schema_mapping(
        self, accounting_standard: AccountingStandard, language: Language
    ) -> SchemaMapping:
        return get_schema_mapping(self.schema_mappings, accounting_standard, language)

    def normalize_financial_data(self, file_path: str, company_name: str = None) -> Dict[str, Any]:
        try:
            file_format = self.detect_file_format(file_path)
            logger.info(f"Detected file format: {file_format.value}")

            if file_format == FileFormat.EXCEL:
                data = load_excel_data(file_path)
            elif file_format == FileFormat.CSV:
                data = load_csv_data(file_path)
            elif file_format == FileFormat.PDF:
                data = load_pdf_data(file_path)
            elif file_format == FileFormat.JSON:
                data = load_json_data(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")

            text_content = extract_text_content(data)
            language = self.detect_language(text_content)
            accounting_standard = self.detect_accounting_standard(text_content, language)
            detected_currency = detect_currency(text_content)

            logger.info(f"Detected language: {language.value}")
            logger.info(f"Detected accounting standard: {accounting_standard.value}")

            schema_mapping = self.get_schema_mapping(accounting_standard, language)
            normalized_data = self._normalize_data(data, schema_mapping, company_name)

            normalized_data["metadata"] = {
                "file_format": file_format.value,
                "language": language.value,
                "accounting_standard": accounting_standard.value,
                "detected_currency": detected_currency,
                "normalization_timestamp": pd.Timestamp.now().isoformat(),
            }

            if detected_currency and not normalized_data.get("currency"):
                normalized_data["currency"] = detected_currency

            return normalized_data
        except Exception as exc:
            logger.error(f"Error normalizing financial data: {exc}")
            return {}

    def _normalize_data(
        self, data: Dict[str, pd.DataFrame], schema_mapping: SchemaMapping, company_name: str = None
    ) -> Dict[str, Any]:
        normalized_data = {
            "company": company_name or "Unknown Company",
            "currency": "USD",
            "period": "Unknown",
            "sheets_processed": [],
        }

        for sheet_name, df in data.items():
            logger.info(f"Processing sheet: {sheet_name}")
            sheet_type = classify_sheet(sheet_name, df)

            if sheet_type == "pl_statement":
                pl_data = extract_pl_data(df, schema_mapping)
                normalized_data.update(pl_data)
                normalized_data["sheets_processed"].append(f"{sheet_name} (P&L)")
            elif sheet_type == "balance_sheet":
                bs_data = extract_balance_sheet_data(df, schema_mapping)
                normalized_data.update(bs_data)
                normalized_data["sheets_processed"].append(f"{sheet_name} (Balance Sheet)")
            elif sheet_type == "hr_data":
                hr_data = extract_hr_data(df, schema_mapping)
                normalized_data["hr_data"] = hr_data
                normalized_data["sheets_processed"].append(f"{sheet_name} (HR)")

        industry = classify_industry(normalized_data)
        normalized_data["industry"] = industry

        if "employee_count" not in normalized_data or normalized_data["employee_count"] == 0:
            normalized_data["employee_count"] = estimate_employee_count(normalized_data)

        return normalized_data


normalization_layer = NormalizationLayer()


def get_normalization_layer() -> NormalizationLayer:
    return normalization_layer
