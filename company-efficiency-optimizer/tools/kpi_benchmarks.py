"""Benchmark constants for KPI calculations."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

BENCHMARKS: Dict[str, Dict[str, float]] = {
    "gross_margin": {
        "retail": 30.0,
        "manufacturing": 25.0,
        "services": 40.0,
        "professional_services": 35.0,
        "technology": 45.0,
        "healthcare": 38.0,
    },
    "operating_margin": {
        "retail": 8.0,
        "manufacturing": 12.0,
        "services": 15.0,
        "professional_services": 9.8,
        "technology": 18.0,
        "healthcare": 12.0,
    },
    "net_margin": {
        "retail": 5.0,
        "manufacturing": 8.0,
        "services": 10.0,
        "professional_services": 6.5,
        "technology": 15.0,
        "healthcare": 8.0,
    },
    "turnover_rate": {
        "retail": 15.0,
        "manufacturing": 12.0,
        "services": 18.0,
        "professional_services": 14.0,
        "technology": 20.0,
        "healthcare": 16.0,
    },
    "revenue_per_employee": {
        "retail": 200000,
        "manufacturing": 250000,
        "services": 300000,
        "professional_services": 794000000,
        "technology": 500000000,
        "healthcare": 400000000,
    },
    "cost_efficiency": {
        "retail": 0.85,
        "manufacturing": 0.80,
        "services": 0.75,
        "professional_services": 0.82,
        "technology": 0.70,
        "healthcare": 0.78,
    },
    "revenue_growth_rate": {
        "retail": 5.0,
        "manufacturing": 4.0,
        "services": 7.0,
        "professional_services": 6.0,
        "technology": 12.0,
        "healthcare": 8.0,
    },
}

BENCHMARKS_CONTEXT: Dict[str, Any] = {
    "gross_margin": {
        "CO": {
            "small": {"annual": {"retail": 28.0, "manufacturing": 23.0, "services": 38.0}},
            "mid": {"annual": {"retail": 30.0, "manufacturing": 25.0, "services": 40.0}},
            "large": {"annual": {"retail": 32.0, "manufacturing": 27.0, "services": 42.0}},
        },
        "US": {
            "small": {"annual": {"retail": 30.0, "manufacturing": 24.0, "services": 40.0}},
            "mid": {"annual": {"retail": 32.0, "manufacturing": 26.0, "services": 42.0}},
            "large": {"annual": {"retail": 34.0, "manufacturing": 28.0, "services": 45.0}},
        },
    },
    "operating_margin": {
        "CO": {
            "small": {"annual": {"retail": 6.0, "manufacturing": 10.0, "services": 13.0}},
            "mid": {"annual": {"retail": 8.0, "manufacturing": 12.0, "services": 15.0}},
            "large": {"annual": {"retail": 9.0, "manufacturing": 13.0, "services": 16.0}},
        }
    },
    "net_margin": {
        "CO": {
            "small": {"annual": {"retail": 4.0, "manufacturing": 7.0, "services": 9.0}},
            "mid": {"annual": {"retail": 5.0, "manufacturing": 8.0, "services": 10.0}},
            "large": {"annual": {"retail": 6.0, "manufacturing": 9.0, "services": 11.0}},
        }
    },
    "turnover_rate": {
        "CO": {
            "small": {"annual": {"retail": 18.0, "manufacturing": 14.0, "services": 20.0}},
            "mid": {"annual": {"retail": 15.0, "manufacturing": 12.0, "services": 18.0}},
            "large": {"annual": {"retail": 13.0, "manufacturing": 10.0, "services": 16.0}},
        }
    },
    "revenue_per_employee": {
        "CO": {
            "small": {"annual": {"retail": 150000, "manufacturing": 200000, "services": 250000}},
            "mid": {"annual": {"retail": 200000, "manufacturing": 250000, "services": 300000}},
            "large": {"annual": {"retail": 240000, "manufacturing": 300000, "services": 360000}},
        }
    },
    "cost_efficiency": {
        "CO": {
            "small": {"annual": {"retail": 0.88, "manufacturing": 0.83, "services": 0.78}},
            "mid": {"annual": {"retail": 0.85, "manufacturing": 0.80, "services": 0.75}},
            "large": {"annual": {"retail": 0.82, "manufacturing": 0.78, "services": 0.72}},
        }
    },
    "revenue_growth_rate": {
        "CO": {
            "small": {"annual": {"retail": 4.0, "manufacturing": 3.5, "services": 6.0}},
            "mid": {"annual": {"retail": 5.0, "manufacturing": 4.0, "services": 7.0}},
            "large": {"annual": {"retail": 6.0, "manufacturing": 4.5, "services": 8.0}},
        }
    },
}


_BENCHMARK_OVERRIDES: Dict[str, Any] = {}


def load_benchmark_overrides(path: str) -> None:
    if not path or not os.path.exists(path):
        return
    try:
        if path.lower().endswith((".yml", ".yaml")):
            try:
                import yaml
            except Exception:
                return
            with open(path, "r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        else:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle) or {}
        if isinstance(data, dict):
            _BENCHMARK_OVERRIDES.update(data)
    except Exception:
        return


def _get_override(metric: str) -> Dict[str, Any]:
    return _BENCHMARK_OVERRIDES.get(metric, {})


def resolve_benchmark(
    metric: str,
    industry: str,
    country: str = "CO",
    size: str = "mid",
    period: str = "annual",
    default: float | None = None,
) -> float:
    industry_key = (industry or "services").lower()
    country_key = (country or "CO").upper()
    size_key = (size or "mid").lower()
    period_key = (period or "annual").lower()

    override_context = _get_override(metric)
    context = override_context or BENCHMARKS_CONTEXT.get(metric, {})
    country_block = context.get(country_key) or context.get("GLOBAL") or {}
    size_block = country_block.get(size_key) or country_block.get("mid") or {}
    period_block = size_block.get(period_key) or size_block.get("annual") or {}
    if industry_key in period_block:
        return period_block[industry_key]

    fallback = BENCHMARKS.get(metric, {}).get(industry_key)
    if fallback is not None:
        return fallback

    if default is not None:
        return default
    return 0.0


if os.getenv("BENCHMARKS_CONFIG"):
    load_benchmark_overrides(os.getenv("BENCHMARKS_CONFIG"))
DEPARTMENT_KPIS = {
    "marketing": {
        "marketing_roi": {
            "benchmark": 5.0,
            "description": "Revenue generated per marketing spend",
        },
        "customer_acquisition_cost": {
            "benchmark": 50000,
            "description": "Cost to acquire one customer (COP)",
        },
        "customer_lifetime_value": {
            "benchmark": 500000,
            "description": "Total value of a customer (COP)",
        },
        "conversion_rate": {
            "benchmark": 2.5,
            "description": "Percentage of leads that convert",
        },
        "marketing_spend_ratio": {
            "benchmark": 0.15,
            "description": "Marketing spend as % of revenue",
        },
    },
    "it": {
        "system_uptime": {
            "benchmark": 99.9,
            "description": "System availability percentage",
        },
        "response_time": {
            "benchmark": 200,
            "description": "Average response time (ms)",
        },
        "security_incidents": {
            "benchmark": 0,
            "description": "Number of security incidents",
        },
        "project_delivery_time": {
            "benchmark": 0.9,
            "description": "Projects delivered on time ratio",
        },
        "it_cost_ratio": {
            "benchmark": 0.05,
            "description": "IT costs as % of revenue",
        },
    },
    "r_d": {
        "innovation_index": {
            "benchmark": 0.8,
            "description": "New products/features per year",
        },
        "research_efficiency": {
            "benchmark": 0.75,
            "description": "Successful projects ratio",
        },
        "patent_filing_rate": {
            "benchmark": 2.0,
            "description": "Patents filed per year",
        },
        "r_d_investment_ratio": {
            "benchmark": 0.10,
            "description": "R&D investment as % of revenue",
        },
        "time_to_market": {
            "benchmark": 12,
            "description": "Months from concept to launch",
        },
    },
    "hr": {
        "employee_satisfaction": {
            "benchmark": 4.0,
            "description": "Employee satisfaction score (1-5)",
        },
        "training_hours_per_employee": {
            "benchmark": 40,
            "description": "Annual training hours per employee",
        },
        "internal_promotion_rate": {
            "benchmark": 0.15,
            "description": "Internal promotions ratio",
        },
        "diversity_index": {
            "benchmark": 0.6,
            "description": "Workforce diversity score",
        },
        "hr_cost_per_employee": {
            "benchmark": 500000,
            "description": "HR costs per employee (COP)",
        },
    },
}

SEVERITY_WEIGHTS = {
    "critical": 1.0,
    "warning": 0.6,
    "good": 0.25,
    "excellent": 0.0,
}
