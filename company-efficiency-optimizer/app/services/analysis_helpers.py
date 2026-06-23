"""Helper functions for analysis workflows."""

from __future__ import annotations

from typing import Any, Dict, Optional


def _to_number(value: Any) -> Optional[float]:
    if value in (None, "", "N/A"):
        return None
    try:
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if not cleaned:
                return None
            return float(cleaned)
        if isinstance(value, (int, float)):
            return float(value)
    except (TypeError, ValueError):
        return None
    return None


def _to_int(value: Any, default: int = 0) -> int:
    number = _to_number(value)
    if number is None:
        return default
    try:
        return int(number)
    except (TypeError, ValueError):
        return default


def _extract_financial_metrics(data: list) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    for record in data:
        if isinstance(record, dict):
            for key, value in record.items():
                if isinstance(value, (int, float)) and value > 0:
                    metrics[key.lower().replace(" ", "_")] = value
    return metrics


def _extract_hr_metrics(data: list) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    for record in data:
        if isinstance(record, dict):
            for key, value in record.items():
                if isinstance(value, (int, float)) and value > 0:
                    metrics[key.lower().replace(" ", "_")] = value
    return metrics


def create_sample_data_from_inputs(questionnaire_data: Dict[str, Any], file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create sample data structure from questionnaire and file inputs."""

    revenue_ranges = {
        "under_1m": 500000,
        "1m_10m": 5000000,
        "10m_50m": 25000000,
        "50m_100m": 75000000,
        "over_100m": 150000000,
    }
    base_revenue = revenue_ranges.get(questionnaire_data.get("revenue_range", "1m_10m"), 5000000)
    baseline_employee_count = _to_int(questionnaire_data.get("employee_count"), 50) or 50

    financial_data = {
        "revenue": base_revenue,
        "cost_of_goods_sold": base_revenue * 0.6,
        "operating_expenses": base_revenue * 0.25,
        "net_income": base_revenue * 0.15,
    }
    hr_data = {
        "total_employees": baseline_employee_count,
        "departments": {
            "engineering": int(baseline_employee_count * 0.4),
            "sales": int(baseline_employee_count * 0.2),
            "marketing": int(baseline_employee_count * 0.1),
            "operations": int(baseline_employee_count * 0.2),
            "admin": int(baseline_employee_count * 0.1),
        },
    }
    operational_data = {
        "projects_completed": 25,
        "customer_satisfaction": 4.2,
        "process_efficiency": 0.78,
    }

    detected_industry = questionnaire_data.get("industry", "Unknown") or "Unknown"
    employee_count = baseline_employee_count

    def merge_financial_from_dict(source: Dict[str, Any]) -> None:
        if not isinstance(source, dict):
            return
        normalized = {}
        for key, value in source.items():
            if isinstance(key, str):
                normalized[key.lower().strip()] = value
        key_map = {
            "revenue": "revenue",
            "sales": "revenue",
            "cogs": "cost_of_goods_sold",
            "cost_of_goods_sold": "cost_of_goods_sold",
            "gross_profit": "gross_profit",
            "operating_expenses": "operating_expenses",
            "opex": "operating_expenses",
            "operating_income": "operating_income",
            "ebit": "operating_income",
            "net_income": "net_income",
        }
        for alias, target in key_map.items():
            if alias in normalized:
                num_value = _to_number(normalized[alias])
                if num_value is not None:
                    financial_data[target] = num_value
                    if target == "cost_of_goods_sold":
                        financial_data["cogs"] = num_value

    for _, data in file_data.items():
        if isinstance(data, dict):
            detected_industry = data.get("industry") or detected_industry
            if data.get("employee_count"):
                employee_count = _to_int(data.get("employee_count"), employee_count)
            merge_financial_from_dict(data)
            if isinstance(data.get("financial_data"), dict):
                merge_financial_from_dict(data["financial_data"])
            if isinstance(data.get("hr_data"), dict):
                hr_data.update({k: v for k, v in data["hr_data"].items() if v not in (None, "")})
            if isinstance(data.get("operational_data"), dict):
                operational_data.update({k: v for k, v in data["operational_data"].items() if v not in (None, "")})
            continue

        if isinstance(data, list) and data:
            header_str = str(data[0]).lower()
            if "revenue" in header_str or "income" in header_str:
                financial_data.update(_extract_financial_metrics(data))
            elif "employee" in header_str or "hr" in header_str:
                hr_data.update(_extract_hr_metrics(data))

    if not employee_count:
        employee_count = baseline_employee_count
    hr_data["total_employees"] = employee_count

    return {
        "financial_data": financial_data,
        "hr_data": hr_data,
        "operational_data": operational_data,
        "industry": detected_industry,
        "employee_count": employee_count,
        "company_name": questionnaire_data.get("company_name", "Unknown"),
        "company_info": {
            "name": questionnaire_data.get("company_name", "Unknown"),
            "industry": detected_industry,
            "size": questionnaire_data.get("company_size", "Unknown"),
            "employee_count": employee_count,
        },
    }


def describe_file_payload(payload: Any) -> str:
    """Provide a human-friendly summary for processed files."""
    try:
        if isinstance(payload, list):
            return f"{len(payload)} records"
        if isinstance(payload, dict):
            sheets = payload.get("sheets_processed")
            if isinstance(sheets, list) and sheets:
                return f"{len(sheets)} sheets parsed"
            metrics = [key for key in ("revenue", "operating_income", "employee_count") if payload.get(key)]
            if metrics:
                return f"Extracted {len(metrics)} metrics"
            return f"{len(payload.keys())} fields extracted"
    except Exception:
        pass
    return "Processed"


def generate_summary_message(company_name: str, kpi_results: Dict[str, Any], financial_data: Dict[str, Any]) -> str:
    """Generate intelligent summary message based on real KPIs."""
    try:
        financial = kpi_results.get("financial", {})
        operating_margin = financial.get("operating_margin", 0) * 100 if financial.get("operating_margin") else 0
        total_assets = financial_data.get("total_assets", 0)
        monthly_revenue = financial_data.get("revenue", 0) / 12 if financial_data.get("revenue") else 0

        if operating_margin > 15:
            margin_msg = f"Excelente rentabilidad ({operating_margin:.1f}% operating margin)"
        elif operating_margin > 10:
            margin_msg = f"Buena rentabilidad ({operating_margin:.1f}% operating margin)"
        else:
            margin_msg = f"Rentabilidad mejorable ({operating_margin:.1f}% operating margin)"

        if total_assets > monthly_revenue * 100:
            asset_msg = (
                f"pero estás sentado sobre ${total_assets/1e9:.1f}B en activos que generan "
                f"solo ${monthly_revenue/1e6:.1f}M/mes. Vamos a escalar esto."
            )
        elif total_assets > monthly_revenue * 50:
            asset_msg = (
                f"con buen uso de activos (${total_assets/1e9:.1f}B generando ${monthly_revenue/1e6:.1f}M/mes). "
                "Podemos optimizar más."
            )
        else:
            asset_msg = "con uso eficiente de activos. Enfoquémonos en crecimiento."

        return f"{margin_msg}, {asset_msg}"
    except Exception:
        return f"Análisis completado para {company_name}. Revisa los KPIs detallados abajo."
