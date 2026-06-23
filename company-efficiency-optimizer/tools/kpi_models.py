"""Models for KPI calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class KPIMetrics:
    """Data class for KPI metrics."""

    name: str
    value: float
    benchmark: float
    status: str  # 'excellent', 'good', 'warning', 'critical'
    trend: str   # 'improving', 'stable', 'declining'
    description: str
    formula: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
