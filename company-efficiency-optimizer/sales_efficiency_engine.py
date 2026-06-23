"""Sales Efficiency Engine: generate actions from sales KPIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SalesAction:
    title: str
    description: str
    priority: str
    impact: str
    owner: str
    expected_impact: str
    timeframe: str


def analyze_sales_efficiency(sales_data: Dict[str, Any]) -> Dict[str, Any]:
    pipeline = sales_data.get("pipeline", [])
    conversion_by_stage = sales_data.get("conversion_by_stage", {})
    avg_cycle_days = sales_data.get("avg_cycle_days", 0)
    win_rate = sales_data.get("win_rate", 0)

    issues = []
    for stage, conv in conversion_by_stage.items():
        if conv < 0.15:
            issues.append({"type": "drop_off", "stage": stage, "value": conv})

    if avg_cycle_days and avg_cycle_days > 45:
        issues.append({"type": "long_cycle", "value": avg_cycle_days})

    if win_rate and win_rate < 0.2:
        issues.append({"type": "low_win_rate", "value": win_rate})

    return {
        "issues": issues,
        "summary": {
            "pipeline_count": len(pipeline),
            "avg_cycle_days": avg_cycle_days,
            "win_rate": win_rate,
        },
    }


def generate_actions(analysis: Dict[str, Any]) -> List[SalesAction]:
    actions: List[SalesAction] = []
    issues = analysis.get("issues", [])

    for issue in issues:
        if issue["type"] == "drop_off":
            actions.append(
                SalesAction(
                    title=f"Optimizar etapa {issue['stage']}",
                    description="Revisar criterios de calificación y mensajes de salida.",
                    priority="high",
                    impact="conversion",
                    owner="Sales Lead",
                    expected_impact="Subir conversión 5-10% en etapa",
                    timeframe="3-6 semanas",
                )
            )
        elif issue["type"] == "long_cycle":
            actions.append(
                SalesAction(
                    title="Reducir ciclo de ventas",
                    description="Implementar cadencias y alertas de deals estancados.",
                    priority="high",
                    impact="velocity",
                    owner="Sales Ops",
                    expected_impact="Reducir ciclo 15-25%",
                    timeframe="4-8 semanas",
                )
            )
        elif issue["type"] == "low_win_rate":
            actions.append(
                SalesAction(
                    title="Mejorar win rate",
                    description="Refinar playbooks, objeciones y demos por segmento.",
                    priority="medium",
                    impact="conversion",
                    owner="Sales Enablement",
                    expected_impact="Subir win rate 3-6 pp",
                    timeframe="4-10 semanas",
                )
            )

    if not actions:
        actions.append(
            SalesAction(
                title="Mantener performance",
                description="Revisión mensual de pipeline y criterios de calificación.",
                priority="low",
                impact="stability",
                owner="Sales Lead",
                expected_impact="Estabilidad sostenida",
                timeframe="Continuo",
            )
        )

    return actions


def build_sales_plan(sales_data: Dict[str, Any]) -> Dict[str, Any]:
    analysis = analyze_sales_efficiency(sales_data)
    actions = generate_actions(analysis)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    actions_sorted = sorted(actions, key=lambda action: priority_order.get(action.priority, 3))
    return {
        "analysis": analysis,
        "actions": [action.__dict__ for action in actions_sorted],
    }
