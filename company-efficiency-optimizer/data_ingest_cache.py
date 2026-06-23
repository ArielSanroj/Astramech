"""Lightweight cache for ingestion results."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, Optional


CACHE_DIR = ".cache/ingest"


def _ensure_cache_dir() -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return CACHE_DIR


def _cache_key(file_path: str) -> str:
    stat = os.stat(file_path)
    payload = f"{file_path}|{stat.st_size}|{int(stat.st_mtime)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_cached_result(file_path: str) -> Optional[Dict[str, Any]]:
    cache_dir = _ensure_cache_dir()
    key = _cache_key(file_path)
    cache_path = os.path.join(cache_dir, f"{key}.json")
    if not os.path.exists(cache_path):
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def save_cached_result(file_path: str, result: Dict[str, Any]) -> None:
    cache_dir = _ensure_cache_dir()
    key = _cache_key(file_path)
    cache_path = os.path.join(cache_dir, f"{key}.json")

    try:
        with open(cache_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return
