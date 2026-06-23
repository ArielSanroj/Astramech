"""superloop initial — Registro Canónico + Decision Ledger + Snapshot (§10, §11)

Crea las tablas desde la metadata de los modelos (única fuente de verdad), incluyendo
los CHECK constraints R6 (decide lleva respaldo) y R1 (Nivel>=3 aprobado lleva aprobador).

Revision ID: 0001_superloop
Revises:
Create Date: 2026-06-23
"""
from alembic import op

from superloop.adapters.persistence.models import Base

revision = "0001_superloop"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
