"""
API routes for the Company Efficiency Optimizer
"""

from flask import Blueprint, jsonify, session, request, current_app
import logging
from sales_efficiency_engine import build_sales_plan
from ops_efficiency_engine import build_ops_plan
from finance_efficiency_engine import build_finance_plan
from marketing_efficiency_engine import build_marketing_plan
from hr_efficiency_engine import build_hr_plan
from app.db import insert_lead

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/analysis_status')
def analysis_status():
    """Get analysis status"""
    if session.get('analysis_results'):
        return jsonify({'status': 'completed'})
    return jsonify({'status': 'pending'})

@api_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Company Efficiency Optimizer'
    })


@api_bp.route('/quickstart', methods=['POST'])
def quickstart():
    """Store quickstart data from the landing modal."""
    payload = request.get_json(silent=True) or {}
    contact_info = {
        'name': payload.get('contact_name', ''),
        'email': payload.get('contact_email', ''),
        'phone': payload.get('contact_phone', ''),
        'location': payload.get('contact_location', ''),
    }
    areas = payload.get('areas') or []
    goal = payload.get('goal') or ''
    has_data = payload.get('has_data') or 'no'
    data_source = payload.get('data_source') or ''

    questionnaire_data = {
        'company_name': payload.get('company_name', 'Unknown Company'),
        'industry': payload.get('industry', 'services'),
        'company_size': payload.get('company_size', 'mid'),
        'revenue_range': payload.get('revenue_range', ''),
        'employee_count': payload.get('employee_count', ''),
        'current_challenges': goal,
        'goals': goal,
        'analysis_focus': areas,
    }

    session['questionnaire_data'] = questionnaire_data
    session['quickstart'] = {
        'contact': contact_info,
        'areas': areas,
        'goal': goal,
        'has_data': has_data,
        'data_source': data_source,
    }

    try:
        insert_lead(contact_info, session['quickstart'])
    except Exception as exc:
        current_app.logger.error(f"Lead insert failed: {exc}")

    if any(area.lower() == 'ventas' for area in areas):
        session['sales_plan'] = build_sales_plan({
            "conversion_by_stage": {
                "Lead": 0.12,
                "Demo": 0.28,
                "Proposal": 0.22,
                "Negotiation": 0.18,
            },
            "avg_cycle_days": 52,
            "win_rate": 0.18,
        })
    if any(area.lower() == 'operaciones' for area in areas):
        session['ops_plan'] = build_ops_plan({
            "cost_efficiency_ratio": 0.68,
            "opex_ratio": 0.42,
            "process_efficiency": 0.62,
            "on_time_delivery": 0.82,
            "cycle_time_days": 28,
            "rework_rate": 0.08,
            "capacity_utilization": 0.63,
            "inventory_turns": 3.2,
        })
    if any(area.lower() == 'finanzas' for area in areas):
        session['finance_plan'] = build_finance_plan({
            "current_ratio": 1.2,
            "quick_ratio": 0.8,
            "gross_margin_pct": 18,
            "net_margin_pct": 3.5,
            "roe_pct": 6.5,
            "debt_to_equity": 2.4,
            "inventory_turnover": 3.1,
            "ebitda": -120000,
            "expense_execution_pct": 112,
            "revenue_execution_pct": 74,
        })
    if any(area.lower() == 'marketing' for area in areas):
        session['marketing_plan'] = build_marketing_plan({
            "cac": 420,
            "ltv": 980,
            "ltv_cac": 2.3,
            "roas": 1.6,
            "conversion_rate": 0.015,
            "churn_rate": 0.07,
            "mql_to_sql": 0.22,
        })
    if any(area.lower() == 'rrhh' for area in areas):
        session['hr_plan'] = build_hr_plan({
            "turnover_rate": 0.22,
            "time_to_hire_days": 58,
            "absenteeism_rate": 0.04,
            "engagement_score": 62,
            "cost_per_hire": 4200,
            "revenue_per_employee": 72000,
        })

    next_url = '/upload' if has_data == 'yes' else None
    return jsonify({'status': 'ok', 'next_url': next_url})


@api_bp.route('/guided', methods=['POST'])
def guided_flow():
    """Capture guided onboarding inputs and build a checklist."""
    payload = request.form or {}
    goal = payload.get('goal', '')
    constraints = payload.get('constraints', '')
    available_data = payload.get('available_data', '')

    checklist = [
        "Estado de resultados (últimos 12 meses o YTD).",
        "Balance general (último mes).",
        "Listado de gastos operativos.",
        "Headcount actual y rotación.",
        "Top 5 productos/servicios y margen.",
    ]
    if available_data:
        checklist.append(f"Datos disponibles reportados: {available_data}")

    session['guided_flow'] = {
        'goal': goal,
        'constraints': constraints,
        'available_data': available_data,
        'checklist': checklist,
    }

    sales_plan = None
    ops_plan = None
    finance_plan = None
    marketing_plan = None
    hr_plan = None
    quickstart = session.get('quickstart', {})
    areas = quickstart.get('areas', [])
    if areas and any(area.lower() == 'operaciones' for area in areas):
        checklist.extend([
            "OTD (entregas a tiempo) por mes/semana.",
            "Tiempo de ciclo por proceso clave.",
            "Nivel de retrabajo o defectos.",
            "Utilización de capacidad (turnos, líneas, equipos).",
            "Rotación de inventario y stockouts.",
        ])
    if areas and any(area.lower() == 'finanzas' for area in areas):
        checklist.extend([
            "Estado de resultados (P&L) mensual o YTD.",
            "Balance general (último cierre).",
            "Flujo de caja real y proyectado.",
            "Ejecución presupuestal por rubro.",
            "Conciliación bancaria y cartera vencida.",
        ])
    if areas and any(area.lower() == 'marketing' for area in areas):
        checklist.extend([
            "CAC y LTV por canal.",
            "ROAS por campaña.",
            "Conversiones por etapa del funnel.",
            "Tasa de churn/retención.",
            "MQL→SQL y velocidad del pipeline.",
        ])
    if areas and any(area.lower() == 'rrhh' for area in areas):
        checklist.extend([
            "Rotación mensual/anual por equipo.",
            "Time-to-hire promedio.",
            "Costo por contratación.",
            "Ausentismo y licencias.",
            "Engagement y NPS interno.",
            "Ingresos por empleado.",
        ])
    if areas and any(area.lower() == 'ventas' for area in areas):
        sales_plan = build_sales_plan({
            "conversion_by_stage": {
                "Lead": 0.12,
                "Demo": 0.28,
                "Proposal": 0.22,
                "Negotiation": 0.18,
            },
            "avg_cycle_days": 52,
            "win_rate": 0.18,
        })
        session['sales_plan'] = sales_plan
    if areas and any(area.lower() == 'operaciones' for area in areas):
        ops_plan = build_ops_plan({
            "cost_efficiency_ratio": 0.68,
            "opex_ratio": 0.42,
            "process_efficiency": 0.62,
            "on_time_delivery": 0.82,
            "cycle_time_days": 28,
            "rework_rate": 0.08,
            "capacity_utilization": 0.63,
            "inventory_turns": 3.2,
        })
        session['ops_plan'] = ops_plan
    if areas and any(area.lower() == 'finanzas' for area in areas):
        finance_plan = build_finance_plan({
            "current_ratio": 1.2,
            "quick_ratio": 0.8,
            "gross_margin_pct": 18,
            "net_margin_pct": 3.5,
            "roe_pct": 6.5,
            "debt_to_equity": 2.4,
            "inventory_turnover": 3.1,
            "ebitda": -120000,
            "expense_execution_pct": 112,
            "revenue_execution_pct": 74,
        })
        session['finance_plan'] = finance_plan
    if areas and any(area.lower() == 'marketing' for area in areas):
        marketing_plan = build_marketing_plan({
            "cac": 420,
            "ltv": 980,
            "ltv_cac": 2.3,
            "roas": 1.6,
            "conversion_rate": 0.015,
            "churn_rate": 0.07,
            "mql_to_sql": 0.22,
        })
        session['marketing_plan'] = marketing_plan
    if areas and any(area.lower() == 'rrhh' for area in areas):
        hr_plan = build_hr_plan({
            "turnover_rate": 0.22,
            "time_to_hire_days": 58,
            "absenteeism_rate": 0.04,
            "engagement_score": 62,
            "cost_per_hire": 4200,
            "revenue_per_employee": 72000,
        })
        session['hr_plan'] = hr_plan

    return jsonify({
        'status': 'ok',
        'checklist': checklist,
        'sales_plan': sales_plan,
        'ops_plan': ops_plan,
        'finance_plan': finance_plan,
        'marketing_plan': marketing_plan,
        'hr_plan': hr_plan,
    })
