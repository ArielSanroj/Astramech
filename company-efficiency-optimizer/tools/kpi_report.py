"""KPI reporting and inefficiency detection."""

from __future__ import annotations

from typing import Any, Dict, List

from tools.kpi_models import KPIMetrics


def generate_kpi_report(kpis: List[KPIMetrics]) -> str:
    report = "📊 KPI Analysis Report\n"
    report += "=" * 50 + "\n\n"

    status_groups = {
        "excellent": [],
        "good": [],
        "warning": [],
        "critical": [],
    }

    for kpi in kpis:
        status_groups[kpi.status].append(kpi)

    for status in ["critical", "warning", "good", "excellent"]:
        if status_groups[status]:
            status_emoji = {
                "excellent": "🟢",
                "good": "🟡",
                "warning": "🟠",
                "critical": "🔴",
            }

            report += f"{status_emoji[status]} {status.title()} Performance:\n"
            for kpi in status_groups[status]:
                report += f"   • {kpi.name}: {kpi.description}\n"
            report += "\n"

    return report


def identify_inefficiencies(kpis: List[KPIMetrics]) -> List[Dict[str, Any]]:
    inefficiencies: List[Dict[str, Any]] = []
    min_gap_ratio = 0.05
    min_gap_absolute = 50000

    for kpi in kpis:
        if kpi.status in ["warning", "critical"]:
            if kpi.benchmark in (None, 0):
                continue
            gap = kpi.value - kpi.benchmark
            gap_ratio = abs(gap) / abs(kpi.benchmark) if kpi.benchmark else 0
            if gap_ratio < min_gap_ratio:
                continue
            if "revenue per employee" in kpi.name.lower() and abs(gap) < min_gap_absolute:
                continue
            if "turnover" in kpi.name.lower():
                recommended_agent = "hr_optimizer"
                issue_type = "high_turnover"
            elif "margin" in kpi.name.lower() or "revenue" in kpi.name.lower():
                recommended_agent = "financial_optimizer"
                issue_type = "financial_performance"
            elif "cost" in kpi.name.lower() or "efficiency" in kpi.name.lower():
                recommended_agent = "operations_optimizer"
                issue_type = "operational_efficiency"
            else:
                recommended_agent = "diagnostic_agent"
                issue_type = "general_performance"

            inefficiencies.append(
                {
                    "issue_type": issue_type,
                    "kpi_name": kpi.name,
                    "current_value": kpi.value,
                    "benchmark": kpi.benchmark,
                    "severity": kpi.status,
                    "description": kpi.description,
                    "recommended_agent": recommended_agent,
                }
            )

    return inefficiencies
