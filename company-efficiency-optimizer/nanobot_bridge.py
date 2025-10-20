"""Nanobot Bridge utilities."""

import os
import subprocess
from pathlib import Path
from typing import Dict, List

import yaml


class NanobotBridge:
    def __init__(self, configuration_path: str):
        self.config_path = Path(configuration_path)

    def sync_agents(self, analysis: Dict) -> None:
        if not analysis:
            return
        config = self._load_config()
        textagents = config.setdefault("textagents", {})

        for agent in analysis.get("recommended_agents", []):
            agent_key = self._slugify(agent.get("type", "dynamic_agent"))
            textagents[agent_key] = {
                "name": agent.get("type", "Dynamic Agent"),
                "model": os.getenv("NANOBOT_DYNAMIC_MODEL", "gpt-4o"),
                "mcpServers": self._resolve_servers(agent.get("type", "")),
                "metadata": {
                    "goal": agent.get("goal", ""),
                    "priority": agent.get("priority", "medium"),
                    "focus_areas": agent.get("focus_areas", []),
                },
            }

        self._save_config(config)

    def run_session(self) -> int:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Nanobot configuration not found: {self.config_path}")
        result = subprocess.run(
            ["nanobot", "run", str(self.config_path)],
            check=False,
            env=os.environ.copy(),
        )
        return result.returncode

    def _load_config(self) -> Dict:
        if self.config_path.exists():
            return yaml.safe_load(self.config_path.read_text()) or {}
        return {}

    def _save_config(self, config: Dict) -> None:
        self.config_path.write_text(yaml.safe_dump(config, sort_keys=False))

    def _slugify(self, value: str) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_") or "dynamic_agent"

    def _resolve_servers(self, agent_type: str) -> List[str]:
        lowered = agent_type.lower()
        if "hr" in lowered:
            return ["hr_analysis_mcp"]
        return ["kpi_mcp"]
