"""LLM-assisted parsing helpers for Excel content."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import pandas as pd


def excel_to_text(file_path: str) -> str:
    try:
        xl = pd.ExcelFile(file_path)
        parts: List[str] = []
        for sheet in xl.sheet_names:
            try:
                df = xl.parse(sheet)
                parts.append(f"SHEET: {sheet}\n{df.to_string(index=False)}\n")
            except Exception:
                continue
        return "\n".join(parts)
    except Exception:
        return ""


def generalized_parse_excel(document_text: str) -> Dict[str, Any]:
    if not document_text:
        return {}
    prompt = (
        "Eres un experto en extracción de datos financieros de archivos Excel, independientemente del formato o idioma. "
        "Analiza la descripción de un archivo Excel (texto con sheets y rows) y extrae un JSON SOLO con estas claves: "
        "revenue, cogs, opex, operating_income, net_income, total_assets, cash, investments, fixed_assets, liabilities, equity, estimated_employees, currency, period. "
        "Si un dato no aparece, usa \"N/A\". Usa COP como moneda por defecto.\n\n"
        "Descripcion:\n" + document_text + "\n\nDevuelve solo JSON válido."
    )
    try:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.2,
        )
        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else str(response)
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            payload = text[first_brace : last_brace + 1]
            return json.loads(payload)
    except Exception:
        pass
    return {}
