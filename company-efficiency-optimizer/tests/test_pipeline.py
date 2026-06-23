"""Basic tests for financial pipeline."""

from __future__ import annotations

from pipeline import FinancialPipeline


def test_pipeline_enrich_and_kpis_with_minimal_data(tmp_path):
    # Create a tiny CSV with minimal columns for normalization path
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("revenue,cogs,operating_expenses,net_income,employee_count\n1000000,400000,300000,200000,10\n")

    pipeline = FinancialPipeline()
    result = pipeline.run(str(csv_path), company_name="TestCo")

    assert result.raw
    assert result.validated
    assert result.kpis
