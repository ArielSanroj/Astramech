"""Aggregate KPI calculations."""
from __future__ import annotations
from typing import Any, Dict
import numpy as np
import pandas as pd
from tools.kpi_models import KPIMetrics
from tools.kpi_benchmarks import resolve_benchmark
def calculate_all_kpis(calculator, data: Dict[str, Any], department: str = "Finance") -> Dict[str, Any]:
    def _to_number(value, default: float = 0.0) -> float:
        return calculator._coerce_number(value, default)

    industry_key = str(
        data.get("industry") or data.get("company_info", {}).get("industry") or "services"
    ).lower()
    context = {
        "country": data.get("country") or data.get("company_info", {}).get("country") or "CO",
        "size": data.get("company_size") or data.get("company_info", {}).get("size") or "mid",
        "period": data.get("period_type") or "annual",
    }
    financial_data = data.get("financial_data") or {}
    hr_input = data.get("hr_data")
    operational_input = data.get("operational_data") or {}

    baseline_revenue = 1_000_000.0
    baseline_employees = 50

    revenue = _to_number(financial_data.get("revenue"))
    cogs_value = financial_data.get("cogs", financial_data.get("cost_of_goods_sold"))
    cogs = _to_number(cogs_value)
    operating_expenses = _to_number(financial_data.get("operating_expenses"))
    gross_profit_value = financial_data.get("gross_profit")
    if gross_profit_value is None and revenue and cogs:
        gross_profit_value = revenue - cogs
    gross_profit = _to_number(gross_profit_value)

    operating_income_value = financial_data.get("operating_income")
    if operating_income_value is None and revenue:
        operating_income_value = revenue - cogs - operating_expenses
    operating_income = _to_number(operating_income_value)

    net_income = _to_number(financial_data.get("net_income"))

    missing_financials = not any(
        [
            financial_data.get("revenue"),
            financial_data.get("cogs"),
            financial_data.get("cost_of_goods_sold"),
            financial_data.get("operating_income"),
            financial_data.get("net_income"),
        ]
    )
    if missing_financials:
        revenue = baseline_revenue
        cogs = baseline_revenue * 0.7
        operating_expenses = baseline_revenue * 0.2
        gross_profit = revenue - cogs
        operating_income = revenue - cogs - operating_expenses
        net_income = baseline_revenue * 0.15

    hr_total_employees = None
    hr_turnover_rate = None
    hr_df = None

    if isinstance(hr_input, dict):
        records = None
        if isinstance(hr_input.get("records"), (list, pd.DataFrame)):
            records = hr_input["records"]
        elif isinstance(hr_input.get("data"), (list, pd.DataFrame)):
            records = hr_input["data"]

        if records is not None:
            hr_df = calculator._to_dataframe(records)
        else:
            hr_total_employees = _to_number(
                hr_input.get("total_employees") or hr_input.get("employee_count")
            )
            turnover_candidate = hr_input.get("turnover_rate") or hr_input.get("attrition_rate")
            if turnover_candidate is not None:
                hr_turnover_rate = _to_number(turnover_candidate)
    elif hr_input is not None:
        try:
            hr_df = calculator._to_dataframe(hr_input)
        except ValueError:
            hr_df = None

    if hr_df is not None and not hr_df.empty:
        hr_total_employees = hr_total_employees or hr_df.shape[0]
        if "terminationDate" in hr_df.columns:
            turnover_pct = calculator._calculate_turnover_rate(hr_df)
            hr_turnover_rate = turnover_pct / 100.0

    if hr_turnover_rate is not None and hr_turnover_rate > 1.0:
        hr_turnover_rate = hr_turnover_rate / 100.0
    hr_total_employees = int(hr_total_employees) if hr_total_employees not in (None, "") else 0
    if not hr_total_employees:
        hr_total_employees = baseline_employees

    employee_count = financial_data.get("employee_count")
    if employee_count in (None, ""):
        employee_count = data.get("employee_count")
    if employee_count in (None, ""):
        employee_count = hr_total_employees
    employee_count = _to_number(employee_count)
    employee_count = int(employee_count) if employee_count else 0
    if not employee_count and hr_total_employees:
        employee_count = hr_total_employees

    revenue_per_employee = revenue / employee_count if employee_count else 0.0

    gross_margin_ratio = (gross_profit / revenue) if revenue else 0.0
    operating_margin_ratio = (operating_income / revenue) if revenue else 0.0
    net_margin_ratio = (net_income / revenue) if revenue else 0.0

    cost_efficiency_ratio = 1.0 - (operating_expenses / revenue) if revenue else None
    process_efficiency = _to_number(operational_input.get("process_efficiency"))
    if process_efficiency:
        cost_efficiency_ratio = max(cost_efficiency_ratio or 0.0, process_efficiency)
    cost_efficiency_ratio = max(cost_efficiency_ratio or 0.0, 0.0)

    rev_emp_benchmark = resolve_benchmark(
        "revenue_per_employee",
        industry_key,
        context["country"],
        context["size"],
        context["period"],
        calculator.benchmarks["revenue_per_employee"].get("services", 300000),
    )
    productivity_index = (
        (revenue_per_employee / rev_emp_benchmark)
        if (rev_emp_benchmark and employee_count)
        else None
    )

    financial_metric_input = {
        "revenue": revenue,
        "cogs": cogs,
        "operating_income": operating_income,
        "net_income": net_income,
    }
    if employee_count:
        financial_metric_input["employee_count"] = employee_count

    financial_kpis = (
        calculator.calculate_financial_kpis(financial_metric_input, industry_key, context) if revenue else []
    )
    hr_kpis = (
        calculator.calculate_hr_kpis(hr_df, industry_key, context)
        if hr_df is not None and not hr_df.empty
        else []
    )
    operational_input_for_calc = {
        "revenue": revenue,
        "operating_expenses": operating_expenses,
    }
    if employee_count:
        operational_input_for_calc["employee_count"] = employee_count

    operational_kpis = (
        calculator.calculate_operational_kpis(
            operational_input_for_calc,
            hr_df if hr_df is not None else pd.DataFrame(),
            industry_key,
            context,
        )
        if (revenue and operating_expenses)
        else []
    )

    dept_key = (department or "").lower() if department else ""
    department_kpis = calculator.calculate_department_kpis(data, dept_key) if dept_key else []

    inefficiencies = calculator.identify_inefficiencies(
        financial_kpis + hr_kpis + operational_kpis + department_kpis
    )

    def _clean_value(value):
        if isinstance(value, np.generic):
            return float(value)
        return value

    def _clean_dict(obj: KPIMetrics) -> Dict[str, Any]:
        return {key: _clean_value(val) for key, val in obj.__dict__.items()}

    cleaned_inefficiencies = [
        {key: _clean_value(val) for key, val in issue.items()} for issue in inefficiencies
    ]

    financial_benchmarks = {
        "gross_margin": resolve_benchmark("gross_margin", industry_key, **context),
        "operating_margin": resolve_benchmark("operating_margin", industry_key, **context),
        "net_margin": resolve_benchmark("net_margin", industry_key, **context),
        "revenue_per_employee": rev_emp_benchmark,
    }

    hr_benchmark = resolve_benchmark("turnover_rate", industry_key, **context, default=0.0) / 100.0

    weights = {
        "gross_margin": 0.30,
        "operating_margin": 0.25,
        "net_margin": 0.20,
        "revenue_per_employee": 0.15,
        "cost_efficiency": 0.10,
    }

    available_weights = 0.0
    score_accum = 0.0

    def get_benchmark(kpi_name: str) -> float:
        if kpi_name == "gross_margin":
            return resolve_benchmark("gross_margin", industry_key, **context, default=30.0) / 100.0
        if kpi_name == "operating_margin":
            return resolve_benchmark("operating_margin", industry_key, **context, default=10.0) / 100.0
        if kpi_name == "net_margin":
            return resolve_benchmark("net_margin", industry_key, **context, default=8.0) / 100.0
        if kpi_name == "revenue_per_employee":
            return rev_emp_benchmark
        if kpi_name == "cost_efficiency":
            return resolve_benchmark("cost_efficiency", industry_key, **context, default=0.75)
        return 0.0

    if revenue:
        if gross_margin_ratio is not None:
            benchmark = get_benchmark("gross_margin")
            if benchmark > 0:
                ratio = gross_margin_ratio / benchmark
                if ratio >= 1.0:
                    performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                else:
                    performance = ratio
                available_weights += weights["gross_margin"]
                score_accum += weights["gross_margin"] * performance

        if operating_margin_ratio is not None:
            benchmark = get_benchmark("operating_margin")
            if benchmark > 0:
                ratio = operating_margin_ratio / benchmark
                if ratio >= 1.0:
                    performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                else:
                    performance = ratio
                available_weights += weights["operating_margin"]
                score_accum += weights["operating_margin"] * performance

        if net_margin_ratio is not None:
            benchmark = get_benchmark("net_margin")
            if benchmark > 0:
                ratio = net_margin_ratio / benchmark
                if ratio >= 1.0:
                    performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                else:
                    performance = ratio
                available_weights += weights["net_margin"]
                score_accum += weights["net_margin"] * performance

        if revenue_per_employee and rev_emp_benchmark:
            benchmark = get_benchmark("revenue_per_employee")
            if benchmark > 0:
                ratio = revenue_per_employee / benchmark
                if ratio >= 1.0:
                    performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                else:
                    performance = ratio
                available_weights += weights["revenue_per_employee"]
                score_accum += weights["revenue_per_employee"] * performance

        if cost_efficiency_ratio is not None:
            benchmark = get_benchmark("cost_efficiency")
            if benchmark > 0:
                ratio = cost_efficiency_ratio / benchmark
                if ratio >= 1.0:
                    performance = min(1.0 + (ratio - 1.0) ** 0.5 * 0.3, 1.3)
                else:
                    performance = ratio
                available_weights += weights["cost_efficiency"]
                score_accum += weights["cost_efficiency"] * performance

    efficiency_score = None
    if available_weights > 0:
        efficiency_score = round(min((score_accum / available_weights) * 100, 100), 1)

    department_summary = {
        "name": department or "Finance",
        "kpis": {kpi.name: kpi.value for kpi in department_kpis},
        "benchmarks": {kpi.name: kpi.benchmark for kpi in department_kpis},
    }

    return {
        "financial": {
            "gross_margin": gross_margin_ratio,
            "operating_margin": operating_margin_ratio,
            "net_margin": net_margin_ratio,
            "revenue_per_employee": revenue_per_employee,
            "benchmarks": financial_benchmarks,
        },
        "hr": {
            "turnover_rate": hr_turnover_rate,
            "total_employees": hr_total_employees,
            "benchmark_turnover_rate": hr_benchmark,
        },
        "operational": {
            "cost_efficiency_ratio": cost_efficiency_ratio,
            "productivity_index": productivity_index,
            "customer_satisfaction": _to_number(operational_input.get("customer_satisfaction")),
            "projects_completed": int(_to_number(operational_input.get("projects_completed")))
            if operational_input.get("projects_completed") is not None
            else None,
        },
        "department": department_summary,
        "efficiency_score": efficiency_score,
        "inefficiencies": cleaned_inefficiencies,
        "raw_kpis": {
            "financial": [_clean_dict(kpi) for kpi in financial_kpis],
            "hr": [_clean_dict(kpi) for kpi in hr_kpis],
            "operational": [_clean_dict(kpi) for kpi in operational_kpis],
            "department": [_clean_dict(kpi) for kpi in department_kpis],
        },
    }
