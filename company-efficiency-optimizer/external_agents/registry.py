from typing import Dict, List, Optional

from external_agents.adapters.crm_email import CRMEmailAdapter
from external_agents.adapters.finance_tax import FinanceTaxAdapter
from external_agents.adapters.linkedin_commenter import LinkedInCommenterAdapter
from external_agents.adapters.marketing_google_ads import MarketingGoogleAdsAdapter
from external_agents.adapters.marketing_tiktok import MarketingTikTokAdapter
from external_agents.adapters.outbound_calls import OutboundCallsAdapter
from external_agents.base import ExternalAgentAdapter
from external_agents.adapters.hr_clio import HRAgentClioAdapter


def _build_registry() -> Dict[str, ExternalAgentAdapter]:
    # Instantiate adapters without hitting external dependencies.
    adapters: List[ExternalAgentAdapter] = [
        FinanceTaxAdapter(),
        MarketingTikTokAdapter(),
        MarketingGoogleAdsAdapter(),
        OutboundCallsAdapter(),
        LinkedInCommenterAdapter(),
        CRMEmailAdapter(),
        HRAgentClioAdapter(),
    ]
    return {adapter.name: adapter for adapter in adapters}


REGISTRY: Dict[str, ExternalAgentAdapter] = _build_registry()


def get_adapter(name: str) -> Optional[ExternalAgentAdapter]:
    return REGISTRY.get(name)


def list_adapters() -> List[ExternalAgentAdapter]:
    return list(REGISTRY.values())
