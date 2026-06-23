"""Marketing Efficiency Engine: generate actions from marketing KPIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class MarketingAction:
    title: str
    description: str
    priority: str
    impact: str
    owner: str
    expected_impact: str
    timeframe: str


def analyze_marketing_efficiency(marketing_data: Dict[str, Any]) -> Dict[str, Any]:
    cac = marketing_data.get("cac")
    ltv = marketing_data.get("ltv")
    ltv_cac = marketing_data.get("ltv_cac")
    roas = marketing_data.get("roas")
    conversion_rate = marketing_data.get("conversion_rate")
    churn_rate = marketing_data.get("churn_rate")
    mql_to_sql = marketing_data.get("mql_to_sql")

    issues = []
    if ltv_cac is not None and ltv_cac < 3:
        issues.append({"type": "low_ltv_cac", "value": ltv_cac})
    if roas is not None and roas < 2:
        issues.append({"type": "low_roas", "value": roas})
    if conversion_rate is not None and conversion_rate < 0.02:
        issues.append({"type": "low_conversion_rate", "value": conversion_rate})
    if churn_rate is not None and churn_rate > 0.05:
        issues.append({"type": "high_churn", "value": churn_rate})
    if mql_to_sql is not None and mql_to_sql < 0.3:
        issues.append({"type": "low_mql_to_sql", "value": mql_to_sql})
    if cac is not None and ltv is not None and cac > 0 and ltv / cac < 3:
        issues.append({"type": "high_cac", "value": cac})

    return {
        "issues": issues,
        "summary": {
            "cac": cac,
            "ltv": ltv,
            "ltv_cac": ltv_cac,
            "roas": roas,
            "conversion_rate": conversion_rate,
            "churn_rate": churn_rate,
            "mql_to_sql": mql_to_sql,
        },
    }


def generate_actions(analysis: Dict[str, Any]) -> List[MarketingAction]:
    actions: List[MarketingAction] = []
    issues = analysis.get("issues", [])

    for issue in issues:
        if issue["type"] == "low_ltv_cac":
            actions.append(
                MarketingAction(
                    title="Mejorar LTV/CAC",
                    description="Optimizar segmentación y subir ticket promedio con upsell.",
                    priority="high",
                    impact="profit",
                    owner="Marketing + Ventas",
                    expected_impact="Subir LTV/CAC a 3.0+",
                    timeframe="6-12 semanas",
                )
            )
        elif issue["type"] == "low_roas":
            actions.append(
                MarketingAction(
                    title="Optimizar ROAS",
                    description="Pausar campañas de bajo rendimiento y redistribuir presupuesto.",
                    priority="high",
                    impact="cost",
                    owner="Marketing",
                    expected_impact="Subir ROAS 0.5-1.0",
                    timeframe="3-6 semanas",
                )
            )
        elif issue["type"] == "low_conversion_rate":
            actions.append(
                MarketingAction(
                    title="Mejorar conversión",
                    description="Optimizar landing pages, mensajes y pruebas A/B.",
                    priority="medium",
                    impact="revenue",
                    owner="Marketing",
                    expected_impact="Subir conversión 20-40%",
                    timeframe="4-8 semanas",
                )
            )
        elif issue["type"] == "high_churn":
            actions.append(
                MarketingAction(
                    title="Reducir churn",
                    description="Mejorar onboarding y campañas de retención.",
                    priority="high",
                    impact="retention",
                    owner="Marketing + Customer Success",
                    expected_impact="Bajar churn 1-3 pp",
                    timeframe="6-12 semanas",
                )
            )
        elif issue["type"] == "low_mql_to_sql":
            actions.append(
                MarketingAction(
                    title="Alinear MQL→SQL",
                    description="Revisar scoring y definición de MQL con ventas.",
                    priority="medium",
                    impact="revenue",
                    owner="Marketing + Ventas",
                    expected_impact="Subir MQL→SQL 10-20 pp",
                    timeframe="4-8 semanas",
                )
            )
        elif issue["type"] == "high_cac":
            actions.append(
                MarketingAction(
                    title="Reducir CAC",
                    description="Optimizar canales, mejorar referidos y contenido orgánico.",
                    priority="high",
                    impact="cost",
                    owner="Marketing",
                    expected_impact="Reducir CAC 15-30%",
                    timeframe="6-12 semanas",
                )
            )

    if not actions:
        actions.append(
            MarketingAction(
                title="Mantener eficiencia de marketing",
                description="Monitoreo mensual de CAC, ROAS y conversiones.",
                priority="low",
                impact="stability",
                owner="Marketing",
                expected_impact="Estabilidad sostenida",
                timeframe="Continuo",
            )
        )

    return actions


def build_marketing_plan(marketing_data: Dict[str, Any]) -> Dict[str, Any]:
    analysis = analyze_marketing_efficiency(marketing_data)
    actions = generate_actions(analysis)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    actions_sorted = sorted(actions, key=lambda action: priority_order.get(action.priority, 3))
    return {
        "analysis": analysis,
        "actions": [action.__dict__ for action in actions_sorted],
    }
