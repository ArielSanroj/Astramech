"""Utility helpers for KPI calculations."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pandas as pd


def coerce_number(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return default
            return float(cleaned.replace(",", ""))
        return float(value)
    except (TypeError, ValueError):
        return default


def determine_trend(current: Optional[float], previous: Optional[float], tolerance: float = 0.01) -> str:
    if previous in (None, 0):
        return "stable"
    if current is None:
        return "stable"
    delta = (current - previous) / abs(previous)
    if delta >= tolerance:
        return "improving"
    if delta <= -tolerance:
        return "declining"
    return "stable"


def calculate_gap(value: Optional[float], benchmark: Optional[float], higher_is_better: bool = True) -> float:
    if value is None or benchmark in (None, 0):
        return 0.0
    diff = value - benchmark
    gap = diff / abs(benchmark) if benchmark else 0.0
    return gap if higher_is_better else -gap


def score_issue(severity: str, gap: float, trend: str, severity_weights: Dict[str, float]) -> float:
    weight = severity_weights.get(severity, 0.0)
    score = weight * 0.7 + min(1.0, max(0.0, abs(gap))) * 0.3
    if trend == "declining":
        score += 0.1
    elif trend == "improving":
        score -= 0.1
    return max(0.0, min(1.2, score))


def label_urgency(score: float) -> str:
    if score >= 0.85:
        return "very_high"
    if score >= 0.6:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


def normalize_snapshot(record: Optional[Dict[str, Any]], keys: Tuple[str, ...]) -> Dict[str, float]:
    if not isinstance(record, dict):
        return {}
    normalized: Dict[str, float] = {}
    for key in keys:
        normalized[key] = coerce_number(record.get(key))
    return normalized


def extract_previous_entry(data: Dict[str, Any], keys: Tuple[str, ...]) -> Dict[str, float]:
    candidates = []
    previous = data.get("previous_period")
    if isinstance(previous, dict):
        candidates.append(previous)
    historical = data.get("historical") or data.get("history")
    if isinstance(historical, list) and len(historical) >= 2:
        candidates.append(historical[-2])

    for candidate in candidates:
        normalized = normalize_snapshot(candidate, keys)
        if any(value for value in normalized.values()):
            return normalized
    return {}


def to_dataframe(data: Any) -> pd.DataFrame:
    if data is None:
        return pd.DataFrame()
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        return pd.DataFrame([data])
    raise ValueError("Unsupported data format for DataFrame conversion")


def get_status(value: float, benchmark: float, higher_is_better: bool = True) -> str:
    if higher_is_better:
        if value >= benchmark * 1.1:
            return "excellent"
        if value >= benchmark:
            return "good"
        if value >= benchmark * 0.8:
            return "warning"
        return "critical"

    if value <= benchmark * 0.9:
        return "excellent"
    if value <= benchmark:
        return "good"
    if value <= benchmark * 1.2:
        return "warning"
    return "critical"
