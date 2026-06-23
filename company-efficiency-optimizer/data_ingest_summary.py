"""Summaries for ingested data artifacts."""

from __future__ import annotations

import os
from typing import Any, Dict

import pandas as pd


def get_data_summary(data_dir: str) -> Dict[str, Any]:
    summary = {
        "hr_data": {"file": f"{data_dir}/hr_data.csv", "exists": False, "records": 0},
        "financial_data": {
            "file": f"{data_dir}/financial_data.csv",
            "exists": False,
            "records": 0,
        },
        "extracted_data": {
            "file": f"{data_dir}/extracted_financial_data.json",
            "exists": False,
        },
    }

    if os.path.exists(summary["hr_data"]["file"]):
        try:
            df = pd.read_csv(summary["hr_data"]["file"])
            summary["hr_data"]["exists"] = True
            summary["hr_data"]["records"] = len(df)
        except Exception:
            pass

    if os.path.exists(summary["financial_data"]["file"]):
        try:
            df = pd.read_csv(summary["financial_data"]["file"])
            summary["financial_data"]["exists"] = True
            summary["financial_data"]["records"] = len(df)
        except Exception:
            pass

    summary["extracted_data"]["exists"] = os.path.exists(summary["extracted_data"]["file"])

    return summary
