"""
Superloop settings (SUPERLOOP.md §4.4, R2) — config desde entorno, sin secretos hardcoded.

Resuelve una URL SQLAlchemy SÍNCRONA. Corrige el bug latente de shared/db (driver
asyncpg sobre engine sync): si DATABASE_URL trae asyncpg, lo cambia a psycopg2. Para
desarrollo/test cae a un SQLite local (no requiere docker/Postgres).
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _sync_url(raw: str | None) -> str:
    if not raw:
        # Dev/test: SQLite local. Prod inyecta DATABASE_URL (Postgres).
        return os.getenv("SUPERLOOP_DB_URL", "sqlite:///superloop_dev.db")
    # Engine SÍNCRONO: nunca asyncpg.
    raw = raw.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    raw = raw.replace("postgres+asyncpg://", "postgresql+psycopg2://")
    if raw.startswith("postgresql://"):
        raw = raw.replace("postgresql://", "postgresql+psycopg2://", 1)
    return raw


@dataclass
class SuperloopSettings:
    db_url: str
    detener_en: str = "approve"   # MVP: gate humano en APPROVE (R1)
    max_productos: int = int(os.getenv("SUPERLOOP_MAX_PRODUCTOS", "50"))

    @classmethod
    def resolve(cls, db_url: str | None = None) -> "SuperloopSettings":
        return cls(db_url=_sync_url(db_url or os.getenv("DATABASE_URL")))
