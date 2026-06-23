"""Operations Efficiency Engine: generate actions from ops KPIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class OpsAction:
    title: str
    description: str
    priority: str
    impact: str
    owner: str
    expected_impact: str
    timeframe: str


def analyze_ops_efficiency(ops_data: Dict[str, Any]) -> Dict[str, Any]:
    cost_efficiency = ops_data.get("cost_efficiency_ratio")
    opex_ratio = ops_data.get("opex_ratio")
    process_efficiency = ops_data.get("process_efficiency")
    on_time_delivery = ops_data.get("on_time_delivery")
    cycle_time_days = ops_data.get("cycle_time_days")
    rework_rate = ops_data.get("rework_rate")
    capacity_utilization = ops_data.get("capacity_utilization")
    inventory_turns = ops_data.get("inventory_turns")

    issues = []
    if cost_efficiency is not None and cost_efficiency < 0.75:
        issues.append({"type": "low_cost_efficiency", "value": cost_efficiency})
    if opex_ratio is not None and opex_ratio > 0.4:
        issues.append({"type": "high_opex_ratio", "value": opex_ratio})
    if process_efficiency is not None and process_efficiency < 0.7:
        issues.append({"type": "low_process_efficiency", "value": process_efficiency})
    if on_time_delivery is not None and on_time_delivery < 0.9:
        issues.append({"type": "low_on_time_delivery", "value": on_time_delivery})
    if cycle_time_days is not None and cycle_time_days > 20:
        issues.append({"type": "high_cycle_time", "value": cycle_time_days})
    if rework_rate is not None and rework_rate > 0.05:
        issues.append({"type": "high_rework_rate", "value": rework_rate})
    if capacity_utilization is not None and capacity_utilization < 0.7:
        issues.append({"type": "low_capacity_utilization", "value": capacity_utilization})
    if inventory_turns is not None and inventory_turns < 4:
        issues.append({"type": "low_inventory_turns", "value": inventory_turns})

    return {
        "issues": issues,
        "summary": {
            "cost_efficiency": cost_efficiency,
            "opex_ratio": opex_ratio,
            "process_efficiency": process_efficiency,
            "on_time_delivery": on_time_delivery,
            "cycle_time_days": cycle_time_days,
            "rework_rate": rework_rate,
            "capacity_utilization": capacity_utilization,
            "inventory_turns": inventory_turns,
        },
    }


def generate_actions(analysis: Dict[str, Any]) -> List[OpsAction]:
    actions: List[OpsAction] = []
    issues = analysis.get("issues", [])

    for issue in issues:
        if issue["type"] == "low_cost_efficiency":
            actions.append(
                OpsAction(
                    title="Reducir costos operativos",
                    description="Auditar costos por proceso, eliminar desperdicios y renegociar insumos críticos.",
                    priority="high",
                    impact="cost",
                    owner="Líder de Operaciones",
                    expected_impact="Reducir costos 5-10%",
                    timeframe="6-12 semanas",
                )
            )
        elif issue["type"] == "high_opex_ratio":
            actions.append(
                OpsAction(
                    title="Optimizar OPEX",
                    description="Renegociar contratos y automatizar tareas repetitivas.",
                    priority="high",
                    impact="cost",
                    owner="Operaciones + Finanzas",
                    expected_impact="Reducir OPEX 3-7%",
                    timeframe="4-10 semanas",
                )
            )
        elif issue["type"] == "low_process_efficiency":
            actions.append(
                OpsAction(
                    title="Mejorar eficiencia de procesos",
                    description="Mapear procesos críticos, eliminar cuellos de botella y definir SLAs internos.",
                    priority="medium",
                    impact="throughput",
                    owner="Operaciones",
                    expected_impact="Subir eficiencia 10-20%",
                    timeframe="4-12 semanas",
                )
            )
        elif issue["type"] == "low_on_time_delivery":
            actions.append(
                OpsAction(
                    title="Aumentar entregas a tiempo",
                    description="Implementar control de promesas, buffers y seguimiento diario de atrasos.",
                    priority="high",
                    impact="service",
                    owner="Logística",
                    expected_impact="Subir OTD 5-10 pp",
                    timeframe="4-8 semanas",
                )
            )
        elif issue["type"] == "high_cycle_time":
            actions.append(
                OpsAction(
                    title="Reducir tiempo de ciclo",
                    description="Simplificar pasos, estandarizar handoffs y automatizar aprobaciones.",
                    priority="high",
                    impact="throughput",
                    owner="Operaciones",
                    expected_impact="Reducir ciclo 15-30%",
                    timeframe="4-10 semanas",
                )
            )
        elif issue["type"] == "high_rework_rate":
            actions.append(
                OpsAction(
                    title="Disminuir retrabajo",
                    description="Inspección en origen, checklists de calidad y capacitación focalizada.",
                    priority="medium",
                    impact="quality",
                    owner="Calidad",
                    expected_impact="Reducir retrabajo 20-40%",
                    timeframe="6-12 semanas",
                )
            )
        elif issue["type"] == "low_capacity_utilization":
            actions.append(
                OpsAction(
                    title="Alinear capacidad y demanda",
                    description="Rebalancear turnos, nivelar carga y priorizar mix rentable.",
                    priority="medium",
                    impact="cost",
                    owner="Operaciones",
                    expected_impact="Subir utilización 10-15%",
                    timeframe="4-10 semanas",
                )
            )
        elif issue["type"] == "low_inventory_turns":
            actions.append(
                OpsAction(
                    title="Mejorar rotación de inventario",
                    description="Definir mínimos/máximos, revisar obsolescencia y ajustar reposición.",
                    priority="medium",
                    impact="cash",
                    owner="Supply Chain",
                    expected_impact="Subir rotación 1-2x",
                    timeframe="6-12 semanas",
                )
            )

    if not actions:
        actions.append(
            OpsAction(
                title="Mantener eficiencia",
                description="Revisión mensual de costos, tiempos de ciclo y calidad.",
                priority="low",
                impact="stability",
                owner="Líder de Operaciones",
                expected_impact="Estabilidad sostenida",
                timeframe="Continuo",
            )
        )

    return actions


def build_ops_plan(ops_data: Dict[str, Any]) -> Dict[str, Any]:
    analysis = analyze_ops_efficiency(ops_data)
    actions = generate_actions(analysis)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    actions_sorted = sorted(actions, key=lambda action: priority_order.get(action.priority, 3))
    return {
        "analysis": analysis,
        "actions": [action.__dict__ for action in actions_sorted],
    }
