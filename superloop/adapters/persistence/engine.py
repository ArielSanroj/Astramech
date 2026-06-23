"""Engine + session factory SQLAlchemy. create_all idempotente (Postgres o SQLite)."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


def make_engine(db_url: str):
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, future=True, connect_args=connect_args)


def init_schema(engine) -> None:
    """Crea las tablas del Superloop si faltan. Idempotente."""
    Base.metadata.create_all(engine)


def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, future=True)
