"""Data models for financial ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FinancialSnapshot:
    company: str = "Unknown Company"
    currency: str = "COP"
    period: str = "Unknown"
    department: str = "Finance"
    sheets_processed: List[str] = field(default_factory=list)
    ytd_data: Dict[str, Any] = field(default_factory=dict)
    hr_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    sources: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    source_rank: Dict[str, int] = field(default_factory=dict)

    def set_metric(self, key: str, value: Any, source: str, allow_overwrite: bool = False) -> None:
        if value in (None, "", "N/A"):
            return
        ranks = {
            "structured": 3,
            "universal": 2,
            "llm": 1,
            "fallback": 0,
        }
        incoming_rank = ranks.get(source, 0)
        current_rank = self.source_rank.get(key, -1)
        current_value = self.metrics.get(key)

        if allow_overwrite or current_value in (None, "", 0):
            if current_value in (None, "", 0) or incoming_rank >= current_rank:
                self.metrics[key] = value
                self.source_rank[key] = incoming_rank
        elif incoming_rank > current_rank and value not in (None, "", 0):
            self.metrics[key] = value
            self.source_rank[key] = incoming_rank

        self.sources.setdefault(key, [])
        self.sources[key].append({"source": source, "value": value})

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "company": self.company,
            "currency": self.currency,
            "period": self.period,
            "department": self.department,
            "sheets_processed": self.sheets_processed,
            "ytd_data": self.ytd_data,
            "hr_data": self.hr_data,
            "_sources": self.sources,
            "_source_rank": self.source_rank,
        }
        payload.update(self.metrics)
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialSnapshot":
        snapshot = cls(
            company=data.get("company", "Unknown Company"),
            currency=data.get("currency", "COP"),
            period=data.get("period", "Unknown"),
            department=data.get("department", "Finance"),
            sheets_processed=list(data.get("sheets_processed", [])),
            ytd_data=dict(data.get("ytd_data", {})),
            hr_data=dict(data.get("hr_data", {})),
        )
        snapshot.metrics = {k: v for k, v in data.items() if k not in {
            "company", "currency", "period", "department", "sheets_processed", "ytd_data", "hr_data", "_sources", "_source_rank",
        }}
        snapshot.sources = dict(data.get("_sources", {}))
        snapshot.source_rank = dict(data.get("_source_rank", {}))
        return snapshot
