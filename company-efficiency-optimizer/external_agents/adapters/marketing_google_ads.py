from external_agents.base import (
    AgentCapability,
    AgentRunRequest,
    AgentRunResult,
    ExternalAgentAdapter,
)


class MarketingGoogleAdsAdapter(ExternalAgentAdapter):
    name = "marketing_google_ads"
    domain = "Marketing - Google Ads"
    source_repo = "https://github.com/ArielSanroj/marketingagent"
    local_repo_path = "external_repos/marketingagent"

    def capabilities(self):
        return [
            AgentCapability(
                name="campaign_optimization",
                description="Optimiza campañas y estructura de cuentas de Google Ads",
                inputs=["account_credentials", "campaigns", "goals"],
                outputs=["budget_recommendations", "bidding_strategy", "keyword_actions"],
            ),
            AgentCapability(
                name="creative_guidance",
                description="Sugerencias de anuncios y extensiones segun performance",
                inputs=["campaigns", "assets", "conversion_data"],
                outputs=["ad_copy_suggestions", "asset_scores", "experiments"],
            ),
        ]

    def required_credentials(self):
        return ["GOOGLE_ADS_TOKEN", "OPENAI_API_KEY?"]

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        return AgentRunResult(
            success=False,
            output={},
            message="Hook into marketingagent entrypoint after adding the submodule.",
        )

