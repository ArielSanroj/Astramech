from pathlib import Path
import sys
import importlib

from external_agents.base import (
    AgentCapability,
    AgentRunRequest,
    AgentRunResult,
    ExternalAgentAdapter,
)


class FinanceTaxAdapter(ExternalAgentAdapter):
    name = "finance_tax"
    domain = "Finanzas/Impuestos"
    source_repo = "https://github.com/ArielSanroj/supervincent"
    local_repo_path = "external_repos/supervincent"

    def capabilities(self):
        return [
            AgentCapability(
                name="financial_statements_analysis",
                description="Analiza estados financieros, calcula KPIs y sugiere ajustes",
                inputs=["financial_statements", "chart_of_accounts", "period"],
                outputs=["kpi_report", "anomaly_report", "recommendations"],
            ),
            AgentCapability(
                name="tax_planning",
                description="Calcula obligaciones fiscales y detecta oportunidades de optimizacion",
                inputs=["jurisdiction", "revenues", "expenses", "invoices"],
                outputs=["tax_obligations", "deadlines", "optimization_actions"],
            ),
        ]

    def required_credentials(self):
        return ["OPENAI_API_KEY", "ACCOUNTING_API_KEYS?", "DB_URI?"]

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

        # Look for an entrypoint we can later invoke.
        candidates = [
            target_repo / "tasks.py",
            target_repo / "financial_analysis.py",
            target_repo / "app.py",
            target_repo / "main.py",
            target_repo / "run.py",
        ]
        found = next((p for p in candidates if p.exists()), None)

        if not found:
            return AgentRunResult(
                success=False,
                output={},
                message=f"No known entrypoint found under {target_repo}",
            )

        # Short-circuit for discovery
        if request.options.get("dry_run", True) or "file_path" not in request.payload:
            return AgentRunResult(
                success=True,
                output={
                    "entrypoint": str(found),
                    "received_payload_keys": list(request.payload.keys()),
                    "note": "Dry-run mode; provide file_path and set dry_run=False to execute.",
                },
                message="FinanceTaxAdapter located repo; dry-run mode enabled.",
            )

        file_path = Path(request.payload["file_path"])
        if not file_path.exists():
            return AgentRunResult(
                success=False,
                output={"entrypoint": str(found)},
                message=f"Provided file_path not found: {file_path}",
            )

        # Add repo to sys.path for imports
        sys.path.insert(0, str(target_repo))
        try:
            module = importlib.import_module(found.stem)
            if hasattr(module, "FinancialAnalyzer"):
                analyzer = module.FinancialAnalyzer(downloads_dir=str(file_path.parent))
                analyzer.load_financial_data(str(file_path))
                metrics = analyzer.calculate_financial_metrics()
                recommendations = self._quick_recommendations(metrics)
                return AgentRunResult(
                    success=True,
                    output={
                        "entrypoint": str(found),
                        "metrics": metrics,
                        "recommendations": recommendations,
                    },
                    message="Financial analysis completed via FinancialAnalyzer",
                )
            else:
                return AgentRunResult(
                    success=False,
                    output={"entrypoint": str(found)},
                    message="financial_analysis module missing FinancialAnalyzer class",
                )
        except Exception as exc:
            return AgentRunResult(
                success=False,
                output={"entrypoint": str(found)},
                message=f"Finance execution failed: {exc}",
            )
        finally:
            if str(target_repo) in sys.path:
                sys.path.remove(str(target_repo))

    def _quick_recommendations(self, metrics):
        """Lightweight recommendations based on computed KPIs."""
        recs = []
        try:
            kpis = metrics.get("kpis", {})
            presupuesto = metrics.get("presupuesto_ejecutado", {})

            current_ratio = kpis.get("current_ratio", 0)
            if current_ratio < 1.5:
                recs.append("Current Ratio bajo (<1.5): revisar liquidez y pasivos corrientes.")
            elif current_ratio < 2.0:
                recs.append("Current Ratio moderado (<2.0): monitorear liquidez mensualmente.")

            margen_neto = kpis.get("margen_neto", 0)
            if margen_neto < 5:
                recs.append("Margen neto bajo (<5%): optimiza precios y costos operativos.")
            elif margen_neto < 10:
                recs.append("Margen neto moderado (<10%): ajustar mix de productos/servicios.")

            gastos_pct = presupuesto.get("gastos_pct", 0)
            if gastos_pct > 120:
                recs.append("Gastos >120% del presupuesto: aplicar recortes y renegociar proveedores.")
            elif gastos_pct > 100:
                recs.append("Gastos sobre presupuesto: priorizar spending y congelar rubros no esenciales.")

            if not recs:
                recs.append("Liquidez y márgenes estables: mantener monitoreo mensual y controles de gasto.")
        except Exception:
            recs.append("No se pudieron generar recomendaciones automáticas.")

        return recs
