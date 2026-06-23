"""Core processing for enhanced data ingestion."""

from __future__ import annotations

import os
from typing import Any, Dict

import pandas as pd

from data_ingest_extractors import (
    calculate_ytd_metrics,
    extract_balance_sheet_data,
    extract_cash_flow_data,
    extract_eri_data,
    extract_hr_data,
    extract_pl_data,
)
from data_ingest_cache import load_cached_result, save_cached_result
from models_financial import FinancialSnapshot
from data_ingest_llm import excel_to_text, generalized_parse_excel
from data_ingest_merge import merge_financial_metrics
from data_ingest_sheet import classify_sheet
from data_ingest_validation import (
    classify_industry,
    estimate_employee_count_improved,
    validate_financial_data,
)


def process_excel_file(
    ingestor,
    file_path: str,
    company_name: str = None,
    department: str = "Finance",
) -> Dict[str, Any]:
    enable_cache = os.getenv("ENABLE_INGEST_CACHE", "1") == "1"
    if enable_cache:
        cached = load_cached_result(file_path)
        if cached:
            print("⚡ Using cached ingestion result")
            return cached

    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"📊 Found {len(sheet_names)} sheets: {sheet_names}")

        snapshot = FinancialSnapshot(
            company=company_name or "Unknown Company",
            currency="COP",
            period="Unknown",
            department=department,
        )

        for sheet_name in sheet_names:
            print(f"\n📋 Processing sheet: {sheet_name}")
            try:
                preview = excel_file.parse(sheet_name, nrows=1)
                columns = list(preview.columns)
                if columns:
                    base_cols = columns[:6]
                    last_col = columns[-1]
                    usecols = base_cols + ([last_col] if last_col not in base_cols else [])
                    df = excel_file.parse(sheet_name, usecols=usecols)
                else:
                    df = excel_file.parse(sheet_name)
            except Exception:
                df = excel_file.parse(sheet_name)

            sheet_type = classify_sheet(sheet_name, df)
            print(f"   Sheet type: {sheet_type}")

            if sheet_type == "pl_statement":
                pl_data = extract_pl_data(df, ingestor.colombian_patterns)
                for key, value in pl_data.items():
                    snapshot.set_metric(key, value, "structured")
                snapshot.sheets_processed.append(f"{sheet_name} (P&L)")
            elif sheet_type == "balance_sheet":
                bs_data = extract_balance_sheet_data(df)
                for key, value in bs_data.items():
                    snapshot.set_metric(key, value, "structured")
                snapshot.sheets_processed.append(f"{sheet_name} (Balance Sheet)")
            elif sheet_type == "cash_flow":
                cf_data = extract_cash_flow_data(df)
                for key, value in cf_data.items():
                    snapshot.set_metric(key, value, "structured")
                snapshot.sheets_processed.append(f"{sheet_name} (Cash Flow)")
            elif sheet_type == "hr_data":
                hr_data = extract_hr_data(df)
                snapshot.hr_data = hr_data
                snapshot.sheets_processed.append(f"{sheet_name} (HR)")
            elif "ERI" in sheet_name.upper():
                eri_data = extract_eri_data(df, sheet_name)
                snapshot.ytd_data.update(eri_data)
                snapshot.sheets_processed.append(f"{sheet_name} (ERI - YTD)")

        if snapshot.ytd_data:
            ytd_metrics = calculate_ytd_metrics(snapshot.ytd_data)
            for key, value in ytd_metrics.items():
                snapshot.set_metric(key, value, "structured")

        financial_data = snapshot.to_dict()
        industry = classify_industry(financial_data)
        snapshot.set_metric("industry", industry, "fallback", True)
        print(f"\n🏭 Classified industry: {industry}")

        financial_data = snapshot.to_dict()
        estimated_employees = estimate_employee_count_improved(financial_data)
        snapshot.set_metric("employee_count", estimated_employees, "fallback", True)
        print(f"👥 Estimated employee count: {estimated_employees}")

        def missing_core_metrics() -> bool:
            current = snapshot.to_dict()
            return not current.get("revenue") or not current.get("operating_income")

        force_llm = os.getenv("FORCE_LLM_PARSE", "0") == "1"
        if force_llm or missing_core_metrics():
            try:
                print("   ⚙️  Structured parse incomplete → invoking Ollama fallback parser...")
                document_text = excel_to_text(file_path)
                llm_parsed = generalized_parse_excel(document_text)
                if isinstance(llm_parsed, dict) and llm_parsed:
                    mapped = {
                        "revenue": llm_parsed.get("revenue"),
                        "cogs": llm_parsed.get("cogs"),
                        "operating_expenses": llm_parsed.get("opex"),
                        "operating_income": llm_parsed.get("operating_income"),
                        "net_income": llm_parsed.get("net_income"),
                        "total_assets": llm_parsed.get("total_assets"),
                        "cash_and_equivalents": llm_parsed.get("cash"),
                        "investments": llm_parsed.get("investments"),
                        "fixed_assets": llm_parsed.get("fixed_assets"),
                        "total_liabilities": llm_parsed.get("liabilities"),
                        "total_equity": llm_parsed.get("equity"),
                    }
                    print(f"   🤖 LLM parsed raw: {llm_parsed}")
                    for key, value in mapped.items():
                        snapshot.set_metric(key, value, "llm")
                    if llm_parsed.get("estimated_employees") not in (None, "N/A", ""):
                        snapshot.set_metric(
                            "employee_count",
                            int(float(llm_parsed.get("estimated_employees"))),
                            "llm",
                            True,
                        )
                    if llm_parsed.get("currency"):
                        snapshot.currency = llm_parsed.get("currency")
                    if llm_parsed.get("period"):
                        snapshot.period = llm_parsed.get("period")
            except Exception:
                pass

        if missing_core_metrics():
            try:
                universal_metrics = ingestor.universal_parser.parse(file_path)
                if universal_metrics:
                    print("   🔍 Universal parser extracted metrics:", universal_metrics)
                    def set_metric(store, key, value, source, allow_overwrite):
                        if key == "company":
                            snapshot.company = value
                            return
                        if key == "currency":
                            snapshot.currency = value
                            return
                        if key == "period":
                            snapshot.period = value
                            return
                        snapshot.set_metric(key, value, source, allow_overwrite)

                    merge_financial_metrics(
                        financial_data,
                        universal_metrics,
                        set_metric=set_metric,
                        source="universal",
                    )
            except Exception as parse_err:
                print(f"   ⚠️ Universal parser failed: {parse_err}")

        financial_data = snapshot.to_dict()
        validate_financial_data(financial_data)
        if enable_cache:
            save_cached_result(file_path, financial_data)
        return financial_data
    except Exception as exc:
        print(f"❌ Error processing Excel file: {exc}")
        import traceback
        traceback.print_exc()
        return {}
