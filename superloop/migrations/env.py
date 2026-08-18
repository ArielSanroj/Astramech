"""Alembic env para el Superloop. Target = metadata de los modelos (única fuente)."""
from __future__ import annotations

import os
import sys

# Asegura que el root del repo esté en sys.path, independiente del CWD de invocación
# (env.py vive en superloop/migrations/ → el root está 3 niveles arriba).
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from alembic import context

from superloop.config.settings import SuperloopSettings
from superloop.adapters.persistence.models import Base

config = context.config
target_metadata = Base.metadata

# URL síncrona desde entorno (DATABASE_URL → psycopg2), nunca hardcodeada (R2).
DB_URL = SuperloopSettings.resolve(os.getenv("DATABASE_URL")).db_url


def run_migrations_offline() -> None:
    context.configure(url=DB_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine
    connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
    engine = create_engine(DB_URL, connect_args=connect_args)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
