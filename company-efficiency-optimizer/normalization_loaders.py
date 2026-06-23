"""Loaders for normalization layer."""

from __future__ import annotations

import json
from typing import Dict

import pandas as pd


def load_excel_data(file_path: str) -> Dict[str, pd.DataFrame]:
    try:
        excel_file = pd.ExcelFile(file_path)
        data: Dict[str, pd.DataFrame] = {}
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            data[sheet_name] = df
        return data
    except Exception as exc:
        print(f"Error loading Excel file: {exc}")
        return {}


def load_csv_data(file_path: str) -> Dict[str, pd.DataFrame]:
    try:
        df = pd.read_csv(file_path)
        return {"main": df}
    except Exception as exc:
        print(f"Error loading CSV file: {exc}")
        return {}


def load_pdf_data(file_path: str) -> Dict[str, pd.DataFrame]:
    try:
        return {}
    except Exception as exc:
        print(f"Error loading PDF file: {exc}")
        return {}


def load_json_data(file_path: str) -> Dict[str, pd.DataFrame]:
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame()

        return {"main": df}
    except Exception as exc:
        print(f"Error loading JSON file: {exc}")
        return {}


def extract_text_content(data: Dict[str, pd.DataFrame]) -> str:
    text_parts = []
    for sheet_name, df in data.items():
        text_parts.append(f"Sheet: {sheet_name}")
        text_parts.append(df.to_string())
    return " ".join(text_parts)
