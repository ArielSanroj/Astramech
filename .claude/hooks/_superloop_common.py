"""Helpers compartidos por los hooks del Superloop (SUPERLOOP.md §20)."""
from __future__ import annotations

import json
import os
import sys

# Permite importar superloop.domain.phase_done (paquete top-level del repo).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def leer_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def extraer_superloop(payload: dict) -> dict | None:
    if not isinstance(payload, dict):
        return None
    task = payload.get("task") if isinstance(payload.get("task"), dict) else {}
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    for c in (payload.get("superloop"), task.get("superloop"),
              (task.get("metadata") or {}).get("superloop"), meta.get("superloop")):
        if isinstance(c, dict):
            return c
    return None


def bloquear(faltantes: list[str]) -> None:
    print("⛔ Superloop bloqueó esta acción (SUPERLOOP.md §16/§20):", file=sys.stderr)
    for f in faltantes:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(2)


def ok() -> None:
    sys.exit(0)
