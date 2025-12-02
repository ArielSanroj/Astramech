from external_agents.base import (
    AgentCapability,
    AgentRunRequest,
    AgentRunResult,
    ExternalAgentAdapter,
)


class LinkedInCommenterAdapter(ExternalAgentAdapter):
    name = "linkedin_commenter"
    domain = "Marketing - LinkedIn"
    source_repo = "https://github.com/ArielSanroj/linkedinposting"
    local_repo_path = "external_repos/linkedinposting"

    def capabilities(self):
        return [
            AgentCapability(
                name="post_commenting",
                description="Publica comentarios en posts de LinkedIn segun estrategia",
                inputs=["profiles", "posts", "tone_guidelines"],
                outputs=["scheduled_comments", "posted_comments", "engagement"],
            ),
            AgentCapability(
                name="content_rules",
                description="Define reglas de contenido y revisiones antes de publicar",
                inputs=["brand_voice", "compliance_rules"],
                outputs=["approved_comments", "blocked_comments"],
            ),
        ]

    def required_credentials(self):
        return ["LINKEDIN_COOKIES/SESSION", "OPENAI_API_KEY?"]

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        return AgentRunResult(
            success=False,
            output={},
            message="Connect to linkedinposting workflow once the submodule is available.",
        )

