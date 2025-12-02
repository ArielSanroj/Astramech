"""
Thin wrapper for the Clio Alpha backend so Astramech can surface HR insights.
"""

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any


class ClioService:
    def __init__(self):
        repo_root = Path(__file__).resolve().parents[2]
        self.repo_path = repo_root / "external_repos" / "clioalphamodel"
        self.module = None

    def _ensure_loaded(self):
        if self.module:
            return self.module

        target = self.repo_path / "backend" / "main.py"
        if not target.exists():
            raise FileNotFoundError("Clio backend module missing")

        if str(self.repo_path) not in sys.path:
            sys.path.insert(0, str(self.repo_path))

        spec = importlib.util.spec_from_file_location("clio_backend_main", target)
        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        if loader is None:
            raise ImportError("Cannot load Clio backend module")
        loader.exec_module(module)
        self.module = module
        return module

    async def _run_async(self, func, *args, **kwargs):
        return await func(*args, **kwargs)

    def get_team_overview(self) -> Dict[str, Any]:
        module = self._ensure_loaded()
        try:
            return asyncio.run(self._run_async(module.get_team_data))
        except Exception as exc:
            return {"error": str(exc)}

    def get_risk_analysis(self) -> Dict[str, Any]:
        module = self._ensure_loaded()
        try:
            return asyncio.run(self._run_async(module.get_risk_analysis))
        except Exception as exc:
            return {"error": str(exc)}

    def analyze_composition(self, members: Dict[str, Any]) -> Dict[str, Any]:
        module = self._ensure_loaded()
        try:
            return asyncio.run(self._run_async(module.analyze_team_composition, members))
        except Exception as exc:
            return {"error": str(exc)}
