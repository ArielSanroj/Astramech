"""
Service wrapper to talk to the SuperVincent invoice + financial system.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, Optional


class SuperVincentService:
    _instance: Optional["SuperVincentService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        root = Path(__file__).resolve().parents[2]
        self.repo_path = root / "external_repos" / "supervincent"
        self._module = None
        self._agent = None

    def _ensure_repo_on_path(self):
        repo_str = str(self.repo_path)
        if repo_str not in sys.path:
            sys.path.insert(0, repo_str)

    def _load_module(self):
        if self._module is not None:
            return self._module
        self._ensure_repo_on_path()
        target = self.repo_path / "superbincent_integrated.py"
        spec = importlib.util.spec_from_file_location("superbincent_integrated", target)
        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        if loader is None:
            raise ImportError("Cannot load SuperVincent module")
        loader.exec_module(module)
        self._module = module
        return module

    def _get_agent(self):
        if self._agent is not None:
            return self._agent
        module = self._load_module()
        self._agent = module.SuperBincentIntegrated()
        return self._agent

    def get_status(self) -> Dict:
        agent = self._get_agent()
        try:
            status = agent.get_system_status()
            return {
                "status": "success",
                "system": status.get("system"),
                "version": status.get("version"),
                "timestamp": status.get("timestamp"),
                "reports": status.get("reports", {}),
                "financial_files": status.get("financial_files", {}),
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def run_analysis(self) -> Dict:
        agent = self._get_agent()
        try:
            analysis = agent.run_financial_analysis_only()
            status = agent.get_system_status()
            recommendations = agent._generate_recommendations(status, analysis)
            return {
                "status": analysis.get("status", "error"),
                "metrics": analysis.get("metrics", {}),
                "reports": analysis.get("reports", {}),
                "files_generated": analysis.get("files_generated", 0),
                "recommendations": recommendations,
                "timestamp": status.get("timestamp"),
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
