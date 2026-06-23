"""Report exporter utilities (JSON/CSV/PDF)."""

from __future__ import annotations

import csv
import json
from typing import Any, Dict, List


def export_json(report: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, default=str)


def export_csv(report: Dict[str, Any], path: str) -> None:
    financial_data = report.get("financial_data", {})
    inefficiencies = report.get("inefficiencies") or report.get("kpis", [])
    kpis = report.get("kpis", [])

    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["section", "key", "value"])
        for key, value in financial_data.items():
            writer.writerow(["financial", key, value])
        writer.writerow([])
        writer.writerow(["kpis", "name", "value", "benchmark", "formula"])
        for kpi in kpis:
            kpi_data = kpi.__dict__ if hasattr(kpi, "__dict__") else kpi
            writer.writerow([
                "kpi",
                kpi_data.get("name", ""),
                kpi_data.get("value", ""),
                kpi_data.get("benchmark", ""),
                kpi_data.get("formula", ""),
            ])
        writer.writerow([])
        writer.writerow(["inefficiencies", "kpi_name", "severity"])
        for issue in inefficiencies:
            writer.writerow([
                "inefficiency",
                issue.get("kpi_name", issue.get("name", "")),
                issue.get("severity", issue.get("status", "")),
            ])


def export_pdf(report: Dict[str, Any], path: str) -> None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception as exc:
        raise RuntimeError("reportlab is required for PDF export") from exc

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Astramech Report")
    y -= 30

    financial_data = report.get("financial_data", {})
    c.setFont("Helvetica", 10)
    for key, value in financial_data.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 14
        if y < 80:
            c.showPage()
            y = height - 50

    inefficiencies = report.get("inefficiencies") or []
    if inefficiencies:
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Inefficiencies")
        y -= 20
        c.setFont("Helvetica", 10)
        for issue in inefficiencies:
            name = issue.get("kpi_name", issue.get("name", ""))
            severity = issue.get("severity", issue.get("status", ""))
            c.drawString(50, y, f"- {name} ({severity})")
            y -= 14
            if y < 80:
                c.showPage()
                y = height - 50

    c.save()
