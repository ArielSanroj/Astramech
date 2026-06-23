"""Models for normalization layer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class AccountingStandard(Enum):
    """Supported accounting standards."""

    NIIF = "NIIF"
    US_GAAP = "US_GAAP"
    IFRS = "IFRS"
    LOCAL = "LOCAL"


class FileFormat(Enum):
    """Supported file formats."""

    EXCEL = "excel"
    CSV = "csv"
    PDF = "pdf"
    JSON = "json"


class Language(Enum):
    """Supported languages."""

    SPANISH = "es"
    ENGLISH = "en"
    PORTUGUESE = "pt"
    FRENCH = "fr"


@dataclass
class SchemaMapping:
    """Schema mapping configuration."""

    revenue_patterns: List[str]
    cogs_patterns: List[str]
    gross_profit_patterns: List[str]
    operating_expenses_patterns: List[str]
    operating_income_patterns: List[str]
    net_income_patterns: List[str]
    total_assets_patterns: List[str]
    total_liabilities_patterns: List[str]
    total_equity_patterns: List[str]
    cash_patterns: List[str]
    employee_patterns: List[str]
