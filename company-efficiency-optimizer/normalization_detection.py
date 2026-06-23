"""Detection helpers for normalization layer."""

from __future__ import annotations

from typing import Dict

from normalization_models import AccountingStandard, FileFormat, Language, SchemaMapping


def detect_file_format(file_path: str) -> FileFormat:
    extension = file_path.rsplit(".", 1)[-1].lower()

    if extension in ["xlsx", "xls"]:
        return FileFormat.EXCEL
    if extension == "csv":
        return FileFormat.CSV
    if extension == "pdf":
        return FileFormat.PDF
    if extension == "json":
        return FileFormat.JSON
    raise ValueError(f"Unsupported file format: .{extension}")


def detect_language(text: str) -> Language:
    spanish_words = [
        "ingresos",
        "ventas",
        "utilidad",
        "gastos",
        "activos",
        "pasivos",
        "estado de resultados",
        "balance general",
    ]
    english_words = [
        "revenue",
        "sales",
        "profit",
        "expenses",
        "assets",
        "liabilities",
        "income statement",
        "balance sheet",
    ]
    portuguese_words = [
        "receita",
        "vendas",
        "lucro",
        "despesas",
        "ativo",
        "passivo",
        "balanco patrimonial",
    ]
    french_words = [
        "revenus",
        "ventes",
        "profit",
        "dépenses",
        "actifs",
        "passifs",
        "compte de resultat",
    ]

    text_lower = text.lower()

    counts = {
        Language.SPANISH: sum(1 for word in spanish_words if word in text_lower),
        Language.ENGLISH: sum(1 for word in english_words if word in text_lower),
        Language.PORTUGUESE: sum(1 for word in portuguese_words if word in text_lower),
        Language.FRENCH: sum(1 for word in french_words if word in text_lower),
    }

    return max(counts, key=counts.get)


def detect_accounting_standard(text: str, language: Language) -> AccountingStandard:
    text_lower = text.lower()

    if "niif" in text_lower or "ifrs" in text_lower or "nic" in text_lower:
        return AccountingStandard.IFRS
    if "gaap" in text_lower or "us gaap" in text_lower or "pcga" in text_lower:
        return AccountingStandard.US_GAAP
    if language == Language.SPANISH and ("colombia" in text_lower or "cop" in text_lower):
        return AccountingStandard.NIIF
    if language == Language.PORTUGUESE and ("cpc" in text_lower or "brasil" in text_lower):
        return AccountingStandard.IFRS
    return AccountingStandard.LOCAL


def detect_currency(text: str) -> str | None:
    text_lower = text.lower()
    if "cop" in text_lower or "colomb" in text_lower:
        return "COP"
    if "usd" in text_lower or "dollar" in text_lower:
        return "USD"
    if "eur" in text_lower or "euro" in text_lower:
        return "EUR"
    if "brl" in text_lower or "real" in text_lower:
        return "BRL"
    if "mxn" in text_lower or "mex" in text_lower:
        return "MXN"
    return None


def get_schema_mapping(
    schema_mappings: Dict[str, SchemaMapping],
    accounting_standard: AccountingStandard,
    language: Language,
) -> SchemaMapping:
    key = f"{accounting_standard.value}_{language.value.upper()}"
    if key in schema_mappings:
        return schema_mappings[key]
    return schema_mappings["IFRS_EN"]
