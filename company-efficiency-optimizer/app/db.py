"""
SQLite storage for lead capture.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict

from flask import current_app


def _resolve_db_path() -> Path:
    raw_path = current_app.config.get("LEADS_DB_PATH", "data/astramech.db")
    path = Path(raw_path)
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[1]
        path = repo_root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_resolve_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_leads_db() -> None:
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            name TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            areas TEXT,
            goal TEXT,
            has_data TEXT,
            data_source TEXT,
            raw_payload TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_lead(contact: Dict[str, Any], quickstart: Dict[str, Any]) -> None:
    conn = _get_connection()
    payload = {
        "contact": contact,
        "quickstart": quickstart,
    }
    conn.execute(
        """
        INSERT INTO leads (name, email, phone, location, areas, goal, has_data, data_source, raw_payload)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            contact.get("name"),
            contact.get("email"),
            contact.get("phone"),
            contact.get("location"),
            json.dumps(quickstart.get("areas", [])),
            quickstart.get("goal"),
            quickstart.get("has_data"),
            quickstart.get("data_source"),
            json.dumps(payload),
        ),
    )
    conn.commit()
    conn.close()
