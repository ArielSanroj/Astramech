"""Sample data providers for interactive flow."""

from __future__ import annotations

from typing import Dict


def get_retail_sample_data() -> Dict[str, float]:
    return {
        "revenue": 2000000,
        "cogs": 1400000,
        "gross_profit": 600000,
        "operating_expenses": 400000,
        "operating_income": 200000,
        "net_income": 160000,
        "employee_count": 25,
        "period": "Q4_2024",
        "company_type": "Retail",
    }


def get_manufacturing_sample_data() -> Dict[str, float]:
    return {
        "revenue": 5000000,
        "cogs": 3750000,
        "gross_profit": 1250000,
        "operating_expenses": 800000,
        "operating_income": 450000,
        "net_income": 360000,
        "employee_count": 100,
        "period": "Q4_2024",
        "company_type": "Manufacturing",
    }


def get_services_sample_data() -> Dict[str, float]:
    return {
        "revenue": 800000,
        "cogs": 200000,
        "gross_profit": 600000,
        "operating_expenses": 700000,
        "operating_income": -100000,
        "net_income": -120000,
        "employee_count": 15,
        "period": "Q4_2024",
        "company_type": "Services",
    }


def get_default_sample_data() -> Dict[str, float]:
    return {
        "revenue": 1000000,
        "cogs": 700000,
        "gross_profit": 300000,
        "operating_expenses": 200000,
        "operating_income": 100000,
        "net_income": 80000,
        "employee_count": 50,
        "period": "Q4_2024",
        "company_type": "Mixed",
    }
