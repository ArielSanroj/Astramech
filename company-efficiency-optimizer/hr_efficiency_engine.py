"""HR Efficiency Engine: generate actions from HR KPIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class HRAction:
    title: str
    description: str
    priority: str
    impact: str
    owner: str
    expected_impact: str
    timeframe: str


def analyze_hr_efficiency(hr_data: Dict[str, Any]) -> Dict[str, Any]:
    turnover_rate = hr_data.get("turnover_rate")
    time_to_hire_days = hr_data.get("time_to_hire_days")
    absenteeism_rate = hr_data.get("absenteeism_rate")
    engagement_score = hr_data.get("engagement_score")
    cost_per_hire = hr_data.get("cost_per_hire")
    revenue_per_employee = hr_data.get("revenue_per_employee")

    issues = []
    if turnover_rate is not None and turnover_rate > 0.15:
        issues.append({"type": "high_turnover", "value": turnover_rate})
    if time_to_hire_days is not None and time_to_hire_days > 45:
        issues.append({"type": "slow_hiring", "value": time_to_hire_days})
    if absenteeism_rate is not None and absenteeism_rate > 0.03:
        issues.append({"type": "high_absenteeism", "value": absenteeism_rate})
    if engagement_score is not None and engagement_score < 70:
        issues.append({"type": "low_engagement", "value": engagement_score})
    if cost_per_hire is not None and cost_per_hire > 3500:
        issues.append({"type": "high_cost_per_hire", "value": cost_per_hire})
    if revenue_per_employee is not None and revenue_per_employee < 80000:
        issues.append({"type": "low_productivity", "value": revenue_per_employee})

    return {
        "issues": issues,
        "summary": {
            "turnover_rate": turnover_rate,
            "time_to_hire_days": time_to_hire_days,
            "absenteeism_rate": absenteeism_rate,
            "engagement_score": engagement_score,
            "cost_per_hire": cost_per_hire,
            "revenue_per_employee": revenue_per_employee,
        },
    }


def generate_actions(analysis: Dict[str, Any]) -> List[HRAction]:
    actions: List[HRAction] = []
    issues = analysis.get("issues", [])

    for issue in issues:
        if issue["type"] == "high_turnover":
            actions.append(
                HRAction(
                    title="Reducir rotación",
                    description="Analizar causas por equipo, ajustar compensación crítica y activar planes de carrera.",
                    priority="high",
                    impact="retention",
                    owner="RRHH",
                    expected_impact="Bajar rotación 3-6 pp en 90 días",
                    timeframe="4-12 semanas",
                )
            )
        elif issue["type"] == "slow_hiring":
            actions.append(
                HRAction(
                    title="Acelerar contratación",
                    description="Estandarizar entrevistas, reducir rondas y fijar SLA de aprobación.",
                    priority="medium",
                    impact="throughput",
                    owner="RRHH + Hiring Managers",
                    expected_impact="Reducir time-to-hire 10-20 días",
                    timeframe="2-8 semanas",
                )
            )
        elif issue["type"] == "high_absenteeism":
            actions.append(
                HRAction(
                    title="Reducir ausentismo",
                    description="Revisar turnos, lanzar programas de bienestar y alertas tempranas.",
                    priority="medium",
                    impact="productivity",
                    owner="RRHH",
                    expected_impact="Bajar ausentismo 1-2 pp",
                    timeframe="4-10 semanas",
                )
            )
        elif issue["type"] == "low_engagement":
            actions.append(
                HRAction(
                    title="Mejorar engagement",
                    description="Encuestas cortas mensuales, feedback continuo y plan de reconocimiento.",
                    priority="high",
                    impact="culture",
                    owner="RRHH + Líderes",
                    expected_impact="Subir engagement 8-12 pts",
                    timeframe="6-12 semanas",
                )
            )
        elif issue["type"] == "high_cost_per_hire":
            actions.append(
                HRAction(
                    title="Optimizar costo por contratación",
                    description="Potenciar referidos, optimizar canales y reducir uso de agencias.",
                    priority="medium",
                    impact="cost",
                    owner="RRHH",
                    expected_impact="Reducir costo por hire 15-25%",
                    timeframe="4-12 semanas",
                )
            )
        elif issue["type"] == "low_productivity":
            actions.append(
                HRAction(
                    title="Subir productividad por empleado",
                    description="Capacitación focalizada, automatización y revisión de cargas.",
                    priority="high",
                    impact="revenue",
                    owner="RRHH + Operaciones",
                    expected_impact="Mejorar ingresos/empleado 8-15%",
                    timeframe="6-16 semanas",
                )
            )

    if not actions:
        actions.append(
            HRAction(
                title="Mantener salud de RRHH",
                description="Monitoreo mensual de rotación, engagement y productividad.",
                priority="low",
                impact="stability",
                owner="RRHH",
                expected_impact="Estabilidad sostenida",
                timeframe="Continuo",
            )
        )

    return actions


def build_hr_plan(hr_data: Dict[str, Any]) -> Dict[str, Any]:
    analysis = analyze_hr_efficiency(hr_data)
    actions = generate_actions(analysis)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    actions_sorted = sorted(actions, key=lambda action: priority_order.get(action.priority, 3))
    return {
        "analysis": analysis,
        "actions": [action.__dict__ for action in actions_sorted],
    }
