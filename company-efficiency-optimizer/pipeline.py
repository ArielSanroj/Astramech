"""Pipeline orchestration for financial analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from data_ingest import EnhancedDataIngestion
from normalization_layer import NormalizationLayer
from data_ingest_validation import validate_financial_data
from data_enrich import enrich_financial_data
from data_quality import detect_anomalies
from scenario_simulator import run_simulation
from tools.kpi_calculator import KPICalculator


@dataclass
class PipelineResult:
    raw: Dict[str, Any]
    normalized: Dict[str, Any]
    validated: Dict[str, Any]
    enriched: Dict[str, Any]
    kpis: Dict[str, Any]


class FinancialPipeline:
    def __init__(self):
        self.ingestor = EnhancedDataIngestion()
        self.normalizer = NormalizationLayer()
        self.kpi_calculator = KPICalculator()

    def ingest(self, file_path: str, company_name: Optional[str] = None, department: str = "Finance") -> Dict[str, Any]:
        extension = Path(file_path).suffix.lower()
        if extension in {".xlsx", ".xls"}:
            return self.ingestor.process_excel_file(file_path, company_name or "Unknown Company", department)
        return self.normalizer.normalize_financial_data(file_path, company_name)

    def normalize(self, file_path: str, company_name: Optional[str] = None) -> Dict[str, Any]:
        return self.normalizer.normalize_financial_data(file_path, company_name)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        validate_financial_data(data)
        return data

    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return enrich_financial_data(data)

    def calculate_kpis(self, data: Dict[str, Any], department: str = "Finance") -> Dict[str, Any]:
        kpi_input = {
            "financial_data": {
                "revenue": data.get("revenue", 0),
                "cost_of_goods_sold": data.get("cogs", 0),
                "operating_expenses": data.get("operating_expenses", 0),
                "net_income": data.get("net_income", 0),
                "employee_count": data.get("employee_count", 10),
            },
            "hr_data": data.get("hr_data", {"total_employees": data.get("employee_count", 10)}),
            "operational_data": {"process_efficiency": 0.8},
            "industry": data.get("industry", "professional_services"),
            "country": data.get("country"),
            "company_size": data.get("company_size"),
            "period_type": data.get("period_type"),
        }
        return self.kpi_calculator.calculate_all_kpis(kpi_input, department)

    def simulate(self, data: Dict[str, Any], scenario: Dict[str, float]) -> Dict[str, Any]:
        industry = data.get("industry", "services")
        context = {
            "country": data.get("country", "CO"),
            "size": data.get("company_size", "mid"),
            "period": data.get("period_type", "annual"),
        }
        return run_simulation(data, scenario, industry, context)

    def run(self, file_path: str, company_name: Optional[str] = None, department: str = "Finance") -> PipelineResult:
        raw = self.ingest(file_path, company_name, department)
        extension = Path(file_path).suffix.lower()
        if extension in {".xlsx", ".xls"}:
            normalized = self.normalize(file_path, company_name)
        else:
            normalized = raw
        validated = self.validate(raw)
        enriched = self.enrich(validated)
        kpis = self.calculate_kpis(enriched, department)
        kpis["simulations"] = []
        anomalies = detect_anomalies(enriched)
        if anomalies:
            kpis["data_quality_issues"] = anomalies
        return PipelineResult(raw=raw, normalized=normalized, validated=validated, enriched=enriched, kpis=kpis)


def main() -> None:
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Run the Astramech financial pipeline")
    parser.add_argument("file", help="Path to financial file (Excel/PDF/CSV)")
    parser.add_argument("--company", default=None, help="Company name")
    parser.add_argument("--department", default="Finance", help="Department")
    args = parser.parse_args()

    pipeline = FinancialPipeline()
    result = pipeline.run(args.file, args.company, args.department)

    scenario = {
        "revenue_delta_pct": float(os.getenv("SCENARIO_REVENUE_PCT", "0") or 0),
        "cogs_delta_pct": float(os.getenv("SCENARIO_COGS_PCT", "0") or 0),
        "opex_delta_pct": float(os.getenv("SCENARIO_OPEX_PCT", "0") or 0),
        "headcount_delta_pct": float(os.getenv("SCENARIO_HEADCOUNT_PCT", "0") or 0),
    }
    if any(value != 0 for value in scenario.values()):
        simulation = pipeline.simulate(result.enriched, scenario)
        result.kpis["simulations"] = [simulation]

    print("\n✅ Pipeline completed")
    print(f"Company: {result.raw.get('company', 'Unknown')}")
    print(f"Revenue: {result.raw.get('revenue', 0)}")
    print(f"Net Income: {result.raw.get('net_income', 0)}")
    print(f"KPIs: {len(result.kpis.get('inefficiencies', []))} inefficiencies")
    if result.kpis.get("simulations"):
        print("Scenarios: 1 applied")


if __name__ == "__main__":
    main()
