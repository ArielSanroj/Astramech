from external_agents.base import (
    AgentCapability,
    AgentRunRequest,
    AgentRunResult,
    ExternalAgentAdapter,
)


class OutboundCallsAdapter(ExternalAgentAdapter):
    name = "outbound_calls"
    domain = "Ventas - Outbound"
    source_repo = "https://github.com/ArielSanroj/callagent"
    local_repo_path = "external_repos/callagent"

    def capabilities(self):
        return [
            AgentCapability(
                name="call_campaigns",
                description="Gestiona campañas de llamadas, scripts y resultados",
                inputs=["lead_list", "scripts", "schedules"],
                outputs=["call_outcomes", "next_steps", "pipeline_updates"],
            ),
            AgentCapability(
                name="script_generation",
                description="Genera y adapta guiones para llamadas outbound",
                inputs=["product", "audience", "objections"],
                outputs=["scripts", "talking_points", "objection_handling"],
            ),
        ]

    def required_credentials(self):
        return ["TELEPHONY_API_KEY?", "CRM_API_KEY?"]

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        return AgentRunResult(
            success=False,
            output={},
            message="Wire to callagent runner after the submodule is present.",
        )

