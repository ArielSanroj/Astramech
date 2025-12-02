from pathlib import Path
import sys
import importlib

from external_agents.base import (
    AgentCapability,
    AgentRunRequest,
    AgentRunResult,
    ExternalAgentAdapter,
)


class MarketingTikTokAdapter(ExternalAgentAdapter):
    name = "marketing_tiktok_ads"
    domain = "Marketing - TikTok Ads"
    source_repo = "https://github.com/ArielSanroj/marketingagentcompanies"
    local_repo_path = "external_repos/marketingagentcompanies"

    def capabilities(self):
        return [
            AgentCapability(
                name="campaign_optimization",
                description="Optimiza campañas de TikTok Ads, presupuesto y creatividades",
                inputs=["account_credentials", "campaigns", "goals"],
                outputs=["budget_changes", "targeting_updates", "creative_suggestions"],
            ),
            AgentCapability(
                name="performance_reporting",
                description="Genera reportes de performance y alertas de desviaciones",
                inputs=["campaigns", "time_window"],
                outputs=["kpi_report", "alerts", "next_actions"],
            ),
        ]

    def required_credentials(self):
        return ["TIKTOK_ADS_TOKEN", "OPENAI_API_KEY?"]

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        repo_root = Path(__file__).resolve().parents[1]
        target_repo = repo_root.parent / self.local_repo_path
        # Fallback to monorepo root (one level up) when adapters are used from inside subfolder.
        if not target_repo.exists():
            alt_repo = repo_root.parent.parent / self.local_repo_path
            if alt_repo.exists():
                target_repo = alt_repo
            else:
                return AgentRunResult(
                    success=False,
                    output={},
                    message=f"Repository not found at {target_repo}",
                )

        candidates = [
            target_repo / "main.py",
            target_repo / "app.py",
            target_repo / "run.py",
        ]
        found = next((p for p in candidates if p.exists()), None)

        if not found:
            return AgentRunResult(
                success=False,
                output={},
                message=(
                    f"No executable entrypoint detected under {target_repo}; "
                    "add one or update adapter mapping."
                ),
            )

        if request.options.get("dry_run", True):
            return AgentRunResult(
                success=True,
                output={
                    "entrypoint": str(found),
                    "received_payload_keys": list(request.payload.keys()),
                    "note": "Dry-run mode; set dry_run=False to execute.",
                },
                message="TikTok adapter ready; dry-run mode enabled.",
            )

        sys.path.insert(0, str(target_repo))
        try:
            module = importlib.import_module(found.stem)
            runner = None
            for candidate in ("run", "optimize_campaigns", "main"):
                if hasattr(module, candidate):
                    runner = getattr(module, candidate)
                    break
            if runner is None:
                return AgentRunResult(
                    success=False,
                    output={"entrypoint": str(found)},
                    message="No callable entrypoint (run/optimize_campaigns/main) found in module",
                )

            result = runner(request.payload)
            return AgentRunResult(
                success=True,
                output={"entrypoint": str(found), "result": result},
                message="TikTok adapter executed entrypoint successfully.",
            )
        except Exception as exc:
            return AgentRunResult(
                success=False,
                output={"entrypoint": str(found)},
                message=f"TikTok execution failed: {exc}",
            )
        finally:
            if str(target_repo) in sys.path:
                sys.path.remove(str(target_repo))
