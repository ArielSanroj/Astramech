"""
KPI MCP Server

Exposes KPI calculations via a simple HTTP interface compatible with MCP.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from tools.kpi_calculator import KPICalculator


app = Flask(__name__)
calculator = KPICalculator()


@app.route("/health", methods=["GET"])
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@app.route("/kpi", methods=["POST"])
def calculate_kpis() -> tuple:
    payload = request.get_json(force=True, silent=True) or {}
    industry = payload.get("industry", "retail")
    financial_data = payload.get("financial_data", {})
    hr_records = payload.get("hr_data", [])

    kpis = calculator.calculate_financial_kpis(financial_data, industry)
    hr_kpis = []
    if hr_records:
        hr_kpis = calculator.calculate_hr_kpis(calculator._to_dataframe(hr_records))  # type: ignore[attr-defined]

    inefficiencies = calculator.identify_inefficiencies(kpis + hr_kpis)

    return (jsonify({
        "financial_kpis": [kpi.__dict__ for kpi in kpis],
        "hr_kpis": [kpi.__dict__ for kpi in hr_kpis],
        "inefficiencies": inefficiencies,
    }), 200)


def run(host: str = "127.0.0.1", port: int = 5004) -> None:
    app.run(host=host, port=port)


if __name__ == "__main__":
    run()
