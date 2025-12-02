from pathlib import Path

from external_agents.base import (
    AgentCapability,
    AgentRunRequest,
    AgentRunResult,
    ExternalAgentAdapter,
)


class HRAgentClioAdapter(ExternalAgentAdapter):
    name = "hr_clioalpha"
    domain = "Recursos Humanos"
    source_repo = "https://github.com/ArielSanroj/clioalphamodel"
    local_repo_path = "external_repos/clioalphamodel"

    def capabilities(self):
        return [
            AgentCapability(
                name="team_psychometrics",
                description="Analiza arquetipos y métricas de equipo (Clio Alpha dashboards)",
                inputs=["team_id", "db_path", "ml_service_url"],
                outputs=["team_profile", "risk_scenarios", "recommendations"],
            ),
            AgentCapability(
                name="risk_detection",
                description="Detecta riesgos de comunicación/conflicto y propone acciones",
                inputs=["team_composition", "assessments"],
                outputs=["risk_matrix", "action_items"],
            ),
        ]

    def required_credentials(self):
        return ["DB_PATH", "ML_SERVICE_URL"]

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        repo_root = Path(__file__).resolve().parents[1]
        target_repo = repo_root.parent / self.local_repo_path
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

        backend_main = target_repo / "backend" / "main.py"
        if not backend_main.exists():
            return AgentRunResult(
                success=False,
                output={},
                message=f"No backend/main.py found under {target_repo}",
            )

        # For now, return discovery info and let caller orchestrate FastAPI start or direct function usage.
        return AgentRunResult(
            success=True,
            output={
                "entrypoint": str(backend_main),
                "recommended_run": "Launch FastAPI (uvicorn backend.main:app) or call exported endpoints.",
                "received_payload_keys": list(request.payload.keys()),
            },
            message="HR Clio adapter ready (dry-run). Wire to FastAPI app or callable for execution.",
        )

