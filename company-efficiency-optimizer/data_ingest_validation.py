"""Validation and estimation helpers for ingestion."""

from __future__ import annotations

from typing import Any, Dict


def classify_industry(financial_data: Dict[str, Any]) -> str:
    try:
        revenue = financial_data.get("revenue", 0)
        total_assets = financial_data.get("total_assets", 0)
        cogs = financial_data.get("cogs", 0)
        gross_margin = 0

        if revenue > 0:
            gross_margin = ((revenue - cogs) / revenue) * 100

        if gross_margin > 80:
            return "services"
        if gross_margin > 40:
            return "manufacturing"
        if total_assets > revenue * 10:
            return "real_estate"
        return "retail"
    except Exception as exc:
        print(f"❌ Error classifying industry: {exc}")
        return "services"


def estimate_employee_count(financial_data: Dict[str, Any]) -> int:
    try:
        revenue = financial_data.get("revenue", 0)
        total_assets = financial_data.get("total_assets", 0)
        industry = financial_data.get("industry", "services")

        if industry == "services":
            if revenue > 0:
                return max(5, int(revenue / 300000))
        elif industry == "manufacturing":
            if revenue > 0:
                return max(10, int(revenue / 200000))
        elif industry == "retail":
            if revenue > 0:
                return max(5, int(revenue / 100000))

        if total_assets > 0:
            return max(5, int(total_assets / 100000000))

        return 10
    except Exception as exc:
        print(f"❌ Error estimating employee count: {exc}")
        return 10


def estimate_employee_count_improved(financial_data: Dict[str, Any]) -> int:
    if "hr_data" in financial_data and "total_employees" in financial_data["hr_data"]:
        return financial_data["hr_data"]["total_employees"]

    opex = financial_data.get("operating_expenses", 0)
    opex_ytd = financial_data.get("operating_expenses_ytd", opex)

    if opex_ytd > 0:
        if opex_ytd > opex:
            months_passed = 5
            monthly_opex = opex_ytd / months_passed
        else:
            monthly_opex = opex

        monthly_payroll = monthly_opex * 0.6
        avg_monthly_salary = 1200000
        estimated_employees = int(monthly_payroll / avg_monthly_salary)

        if estimated_employees < 1:
            estimated_employees = 1
        elif estimated_employees > 1000:
            estimated_employees = 10

        print(f"   💼 Estimated from payroll: {estimated_employees} employees")
        return estimated_employees

    return 10


def validate_financial_data(financial_data: Dict[str, Any]) -> None:
    issues = []

    if financial_data.get("currency") != "COP":
        issues.append("Currency not set to COP")

    revenue = financial_data.get("revenue", 0)
    cogs = financial_data.get("cogs", 0)
    gross_profit = financial_data.get("gross_profit")
    operating_income = financial_data.get("operating_income")
    operating_expenses = financial_data.get("operating_expenses", 0)
    net_income = financial_data.get("net_income")
    total_assets = financial_data.get("total_assets")
    total_liabilities = financial_data.get("total_liabilities")
    total_equity = financial_data.get("total_equity")
    if revenue > 0:
        if revenue < 1000000:
            issues.append("Revenue seems too low for a company")
        elif revenue > 1000000000000:
            issues.append("Revenue seems too high, check for unit errors")
        if cogs and revenue < cogs:
            issues.append("COGS exceeds revenue")

    employees = financial_data.get("employee_count", 0)
    if employees > 0 and revenue > 0:
        revenue_per_employee = revenue / employees
        if revenue_per_employee < 50000000:
            issues.append("Revenue per employee seems low")
        elif revenue_per_employee > 2000000000:
            issues.append("Revenue per employee seems high")

    if gross_profit is not None and revenue > 0 and cogs is not None:
        expected = revenue - cogs
        if abs(gross_profit - expected) > max(1, abs(expected) * 0.02):
            issues.append("Gross profit does not match revenue - COGS")

    if operating_income is not None and revenue > 0 and operating_expenses is not None:
        expected = revenue - cogs - operating_expenses
        if abs(operating_income - expected) > max(1, abs(expected) * 0.03):
            issues.append("Operating income does not match revenue - COGS - opex")

    if net_income is not None and revenue > 0:
        net_margin = net_income / revenue
        if net_margin < -1 or net_margin > 1:
            issues.append("Net margin out of expected range")

    if total_assets and total_liabilities is not None and total_equity is not None:
        if abs(total_assets - (total_liabilities + total_equity)) > max(1, total_assets * 0.05):
            issues.append("Balance sheet equation mismatch")

    if issues:
        print(f"   ⚠️ Data validation issues: {', '.join(issues)}")
    else:
        print("   ✅ Data validation passed")
