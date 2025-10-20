"""
HR Analysis MCP Server

Provides HR-related analytics based on existing data ingestion utilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from data_ingest import DataIngestion


app = Flask(__name__)
ingestion = DataIngestion()


@app.route("/health", methods=["GET"])
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@app.route("/hr/turnover", methods=["GET"])
def turnover() -> tuple:
    hr_df = ingestion.fetch_hr_data()
    rate = ingestion.calculate_turnover_rate(hr_df)
    return jsonify({
        "turnover_rate": rate,
        "records": len(hr_df.index),
    }), 200


def run(host: str = "127.0.0.1", port: int = 5005) -> None:
    app.run(host=host, port=port)


if __name__ == "__main__":
    run()
