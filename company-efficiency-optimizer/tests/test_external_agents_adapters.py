import sys
from pathlib import Path

# Ensure project root is on path for adapter imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from external_agents.adapters.finance_tax import FinanceTaxAdapter
from external_agents.adapters.marketing_tiktok import MarketingTikTokAdapter
from external_agents.adapters.hr_clio import HRAgentClioAdapter
from external_agents.base import AgentRunRequest


def test_finance_tax_adapter_detects_entrypoint():
    adapter = FinanceTaxAdapter()
    request = AgentRunRequest(payload={"sample": "data"})
    result = adapter.run(request)

    assert result.success is True
    assert "entrypoint" in result.output
    assert result.output["entrypoint"].endswith(
        ("tasks.py", "financial_analysis.py", "app.py", "main.py", "run.py")
    )
    assert "note" in result.output


def test_marketing_tiktok_adapter_handles_missing_entrypoint():
    adapter = MarketingTikTokAdapter()
    request = AgentRunRequest(payload={"sample": "data"})
    result = adapter.run(request)

    assert result.success is True
    assert "entrypoint" in result.output
    assert result.output["entrypoint"].endswith(("main.py", "app.py", "run.py"))
    assert "dry-run" in result.message.lower()


def test_hr_clio_adapter_finds_backend():
    adapter = HRAgentClioAdapter()
    request = AgentRunRequest(payload={"team_id": "global_aseguradora"})
    result = adapter.run(request)

    assert result.success is True
    assert "entrypoint" in result.output
    assert result.output["entrypoint"].endswith("backend/main.py")
