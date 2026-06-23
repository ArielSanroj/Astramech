"""Department KPI calculations."""

from __future__ import annotations

from typing import Any, Dict, List

from tools.kpi_models import KPIMetrics
from tools.kpi_utils import get_status


def calculate_department_kpi_value(data: Dict[str, Any], department: str, kpi_name: str) -> float:
    financial_data = data.get("financial_data", {})
    department_data = data.get(f"{department}_data", {})

    if department == "marketing":
        if kpi_name == "marketing_roi":
            marketing_spend = department_data.get(
                "marketing_spend", financial_data.get("operating_expenses", 0) * 0.15
            )
            marketing_revenue = department_data.get(
                "marketing_revenue", financial_data.get("revenue", 0) * 0.3
            )
            return marketing_revenue / marketing_spend if marketing_spend > 0 else 0
        if kpi_name == "customer_acquisition_cost":
            return department_data.get("customer_acquisition_cost", 50000)
        if kpi_name == "conversion_rate":
            return department_data.get("conversion_rate", 2.5)

    if department == "it":
        if kpi_name == "system_uptime":
            return department_data.get("system_uptime", 99.9)
        if kpi_name == "response_time":
            return department_data.get("response_time", 200)
        if kpi_name == "security_incidents":
            return department_data.get("security_incidents", 0)

    if department == "r_d":
        if kpi_name == "innovation_index":
            return department_data.get("innovation_index", 0.8)
        if kpi_name == "r_d_investment_ratio":
            r_d_investment = department_data.get(
                "r_d_investment", financial_data.get("operating_expenses", 0) * 0.10
            )
            revenue = financial_data.get("revenue", 1)
            return r_d_investment / revenue if revenue > 0 else 0

    if department == "hr":
        if kpi_name == "employee_satisfaction":
            return department_data.get("employee_satisfaction", 4.0)
        if kpi_name == "training_hours_per_employee":
            return department_data.get("training_hours_per_employee", 40)

    return 0.0


def calculate_department_kpis(
    data: Dict[str, Any],
    department: str,
    department_kpis: Dict[str, Dict[str, Dict[str, Any]]],
) -> List[KPIMetrics]:
    kpis: List[KPIMetrics] = []

    if department not in department_kpis:
        return kpis

    dept_config = department_kpis[department]
    for kpi_name, config in dept_config.items():
        value = calculate_department_kpi_value(data, department, kpi_name)
        benchmark = config["benchmark"]
        status = get_status(value, benchmark, higher_is_better=True)
        kpis.append(
            KPIMetrics(
                name=kpi_name.replace("_", " ").title(),
                value=value,
                benchmark=benchmark,
                status=status,
                trend="stable",
                description=config["description"],
                formula=kpi_name,
                inputs={kpi_name: value},
            )
        )

    return kpis
