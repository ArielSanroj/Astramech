"""Finance Efficiency Engine: generate actions from finance KPIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FinanceAction:
    title: str
    description: str
    priority: str
    impact: str
    owner: str
    expected_impact: str
    timeframe: str


def analyze_finance_efficiency(finance_data: Dict[str, Any]) -> Dict[str, Any]:
    current_ratio = finance_data.get("current_ratio")
    quick_ratio = finance_data.get("quick_ratio")
    gross_margin_pct = finance_data.get("gross_margin_pct")
    net_margin_pct = finance_data.get("net_margin_pct")
    roe_pct = finance_data.get("roe_pct")
    debt_to_equity = finance_data.get("debt_to_equity")
    inventory_turnover = finance_data.get("inventory_turnover")
    ebitda = finance_data.get("ebitda")
    expense_execution_pct = finance_data.get("expense_execution_pct")
    revenue_execution_pct = finance_data.get("revenue_execution_pct")

    issues = []
    if current_ratio is not None and current_ratio < 1.5:
        issues.append({"type": "low_liquidity", "value": current_ratio})
    if quick_ratio is not None and quick_ratio < 1.0:
        issues.append({"type": "low_quick_ratio", "value": quick_ratio})
    if gross_margin_pct is not None and gross_margin_pct < 20:
        issues.append({"type": "low_gross_margin", "value": gross_margin_pct})
    if net_margin_pct is not None and net_margin_pct < 5:
        issues.append({"type": "low_net_margin", "value": net_margin_pct})
    if roe_pct is not None and roe_pct < 10:
        issues.append({"type": "low_roe", "value": roe_pct})
    if debt_to_equity is not None and debt_to_equity > 2:
        issues.append({"type": "high_leverage", "value": debt_to_equity})
    if inventory_turnover is not None and inventory_turnover < 4:
        issues.append({"type": "low_inventory_turnover", "value": inventory_turnover})
    if ebitda is not None and ebitda < 0:
        issues.append({"type": "negative_ebitda", "value": ebitda})
    if expense_execution_pct is not None and expense_execution_pct > 100:
        issues.append({"type": "over_budget_expenses", "value": expense_execution_pct})
    if revenue_execution_pct is not None and revenue_execution_pct < 80:
        issues.append({"type": "under_budget_revenue", "value": revenue_execution_pct})

    return {
        "issues": issues,
        "summary": {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "gross_margin_pct": gross_margin_pct,
            "net_margin_pct": net_margin_pct,
            "roe_pct": roe_pct,
            "debt_to_equity": debt_to_equity,
            "inventory_turnover": inventory_turnover,
            "ebitda": ebitda,
            "expense_execution_pct": expense_execution_pct,
            "revenue_execution_pct": revenue_execution_pct,
        },
    }


def generate_actions(analysis: Dict[str, Any]) -> List[FinanceAction]:
    actions: List[FinanceAction] = []
    issues = analysis.get("issues", [])

    for issue in issues:
        if issue["type"] == "low_liquidity":
            actions.append(
                FinanceAction(
                    title="Mejorar liquidez inmediata",
                    description="Acelerar cobranza, renegociar plazos y priorizar caja.",
                    priority="high",
                    impact="cash",
                    owner="Finanzas",
                    expected_impact="Subir current ratio 0.3-0.6",
                    timeframe="4-8 semanas",
                )
            )
        elif issue["type"] == "low_quick_ratio":
            actions.append(
                FinanceAction(
                    title="Fortalecer liquidez rápida",
                    description="Reducir inventarios lentos y convertir activos a caja.",
                    priority="high",
                    impact="cash",
                    owner="Finanzas + Operaciones",
                    expected_impact="Subir quick ratio 0.2-0.5",
                    timeframe="4-10 semanas",
                )
            )
        elif issue["type"] == "low_gross_margin":
            actions.append(
                FinanceAction(
                    title="Mejorar margen bruto",
                    description="Revisar costos directos, pricing y mix de productos.",
                    priority="high",
                    impact="profit",
                    owner="Finanzas + Comercial",
                    expected_impact="Subir margen bruto 2-5 pp",
                    timeframe="6-12 semanas",
                )
            )
        elif issue["type"] == "low_net_margin":
            actions.append(
                FinanceAction(
                    title="Revisar estructura de costos",
                    description="Identificar costos variables/indirectos y ajustar precios o mix.",
                    priority="high",
                    impact="profit",
                    owner="Finanzas + Operaciones",
                    expected_impact="Subir margen neto 2-4 pp",
                    timeframe="8-16 semanas",
                )
            )
        elif issue["type"] == "low_roe":
            actions.append(
                FinanceAction(
                    title="Mejorar retorno sobre patrimonio",
                    description="Reasignar capital a líneas con mayor rentabilidad.",
                    priority="medium",
                    impact="profit",
                    owner="Finanzas",
                    expected_impact="Subir ROE 3-6 pp",
                    timeframe="8-16 semanas",
                )
            )
        elif issue["type"] == "high_leverage":
            actions.append(
                FinanceAction(
                    title="Reducir apalancamiento",
                    description="Renegociar deuda y optimizar calendario de pagos.",
                    priority="high",
                    impact="risk",
                    owner="Finanzas",
                    expected_impact="Bajar deuda/patrimonio 0.3-0.7",
                    timeframe="6-16 semanas",
                )
            )
        elif issue["type"] == "low_inventory_turnover":
            actions.append(
                FinanceAction(
                    title="Aumentar rotación de inventario",
                    description="Depurar obsoletos, ajustar compras y mejorar forecast.",
                    priority="medium",
                    impact="cash",
                    owner="Supply Chain + Finanzas",
                    expected_impact="Subir rotación 1-2x",
                    timeframe="6-12 semanas",
                )
            )
        elif issue["type"] == "negative_ebitda":
            actions.append(
                FinanceAction(
                    title="Recuperar EBITDA",
                    description="Reducir costos fijos y priorizar unidades rentables.",
                    priority="high",
                    impact="profit",
                    owner="Finanzas + Operaciones",
                    expected_impact="EBITDA positivo en 1-2 trimestres",
                    timeframe="8-20 semanas",
                )
            )
        elif issue["type"] == "over_budget_expenses":
            actions.append(
                FinanceAction(
                    title="Controlar sobre-ejecución de gastos",
                    description="Revisar rubros con desvíos y congelar gastos no críticos.",
                    priority="medium",
                    impact="cost",
                    owner="Finanzas",
                    expected_impact="Reducir gasto 5-10%",
                    timeframe="4-10 semanas",
                )
            )
        elif issue["type"] == "under_budget_revenue":
            actions.append(
                FinanceAction(
                    title="Recuperar ejecución de ingresos",
                    description="Revisar forecast y plan comercial para cerrar brecha vs presupuesto.",
                    priority="medium",
                    impact="revenue",
                    owner="Ventas + Finanzas",
                    expected_impact="Cerrar brecha 10-20%",
                    timeframe="6-12 semanas",
                )
            )

    if not actions:
        actions.append(
            FinanceAction(
                title="Mantener salud financiera",
                description="Monitoreo mensual de liquidez, margen y presupuesto.",
                priority="low",
                impact="stability",
                owner="Finanzas",
                expected_impact="Estabilidad sostenida",
                timeframe="Continuo",
            )
        )

    return actions


def build_finance_plan(finance_data: Dict[str, Any]) -> Dict[str, Any]:
    analysis = analyze_finance_efficiency(finance_data)
    actions = generate_actions(analysis)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    actions_sorted = sorted(actions, key=lambda action: priority_order.get(action.priority, 3))
    return {
        "analysis": analysis,
        "actions": [action.__dict__ for action in actions_sorted],
    }
