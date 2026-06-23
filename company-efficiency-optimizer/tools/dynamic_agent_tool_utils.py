"""Utility helpers for dynamic agent tool."""

from __future__ import annotations

from typing import List

from tools.dynamic_agent_tool_templates import (
    BACKSTORIES,
    CAPABILITY_TEMPLATES,
    DEFAULT_CAPABILITIES,
    DEFAULT_METRICS,
    METRICS_TEMPLATES,
)


def get_fallback_backstory(agent_type: str, goal: str) -> str:
    base = BACKSTORIES.get(agent_type)
    if base:
        return f"{base} Goal: {goal}"
    return f"Experienced business optimization specialist with expertise in {agent_type.lower()}. Goal: {goal}"


def generate_capabilities(agent_type: str, focus_areas: List[str]) -> List[str]:
    base_capabilities = CAPABILITY_TEMPLATES.get(agent_type, DEFAULT_CAPABILITIES)
    focus_capabilities = []
    for area in focus_areas:
        if "Revenue" in area:
            focus_capabilities.append(f"{area} optimization and analysis")
        elif "Margin" in area:
            focus_capabilities.append(f"{area} improvement strategies")
        elif "Growth" in area:
            focus_capabilities.append(f"{area} acceleration techniques")
        else:
            focus_capabilities.append(f"{area} management and optimization")
    return base_capabilities + focus_capabilities


def generate_success_metrics(agent_type: str) -> List[str]:
    return METRICS_TEMPLATES.get(agent_type, DEFAULT_METRICS)
