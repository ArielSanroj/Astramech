from external_agents.base import (
    AgentCapability,
    AgentRunRequest,
    AgentRunResult,
    ExternalAgentAdapter,
)


class CRMEmailAdapter(ExternalAgentAdapter):
    name = "crm_email"
    domain = "Ventas/CRM"
    source_repo = "https://github.com/ArielSanroj/mailicpagent"
    local_repo_path = "external_repos/mailicpagent"

    def capabilities(self):
        return [
            AgentCapability(
                name="sequencing",
                description="Genera y ejecuta secuencias de emails/outreach",
                inputs=["lead_list", "segments", "playbooks"],
                outputs=["email_sequences", "send_plan", "followups"],
            ),
            AgentCapability(
                name="lead_scoring",
                description="Prioriza leads y recomienda acciones",
                inputs=["crm_data", "engagement_events"],
                outputs=["lead_scores", "next_actions", "cadence_adjustments"],
            ),
        ]

    def required_credentials(self):
        return ["EMAIL_PROVIDER_KEY?", "CRM_API_KEY?", "OPENAI_API_KEY?"]

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        return AgentRunResult(
            success=False,
            output={},
            message="Hook this adapter to mailicpagent once the submodule is synced.",
        )

