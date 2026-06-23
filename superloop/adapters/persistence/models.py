"""
SQLAlchemy models — Registro Canónico (§10), Decision Ledger (§11), Snapshot.

Base propia (no shared.db.Base) para no acoplar al engine asyncpg de legacy. Tipos
genéricos → funciona en Postgres (prod) y SQLite (test). Los CheckConstraint imponen
R6 (DECIDE lleva respaldo) y R1 (Nivel >=3 aprobado lleva aprobador) a nivel de DB,
como defensa en profundidad junto a los hooks.
"""
from __future__ import annotations

from sqlalchemy import (
    Column, String, Integer, Float, Text, CheckConstraint, Index,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ProductoRow(Base):
    __tablename__ = "superloop_producto"
    producto_id = Column(String, primary_key=True)
    tipo = Column(String, default="dominio_kpi")          # dominio_kpi | agente
    nombre = Column(String, nullable=False)
    owner = Column(String)
    proposito = Column(Text)
    cliente_ideal = Column(String)
    modelo_ingresos = Column(String)
    expected_business_outcome = Column(Text, default="{}")
    source_ref = Column(String)
    estado_operativo = Column(String)
    estado_comercial = Column(String)
    confianza_estado = Column(Float)
    metrica_principal = Column(String)
    kpis = Column(Text, default="{}")
    afirmaciones = Column(Text, default="[]")
    hipotesis_vigente = Column(Text)
    decision_recomendada_ref = Column(String)
    estado_aprobacion = Column(String, default="pendiente")
    proxima_mejor_accion = Column(Text)
    updated_at = Column(String)


class SnapshotRow(Base):
    __tablename__ = "superloop_snapshot"
    snapshot_id = Column(String, primary_key=True)
    producto_id = Column(String, nullable=False, index=True)
    fecha = Column(String)
    fuentes_consultadas = Column(Text, default="[]")
    fuentes_inaccesibles = Column(Text, default="[]")
    datos_faltantes = Column(Text, default="[]")
    raw_kpis = Column(Text, default="{}")
    afirmaciones = Column(Text, default="[]")


class DecisionLedgerRow(Base):
    __tablename__ = "superloop_decision_ledger"
    decision_id = Column(String, primary_key=True)
    producto_id = Column(String, nullable=False, index=True)
    fecha = Column(String)
    fase_origen = Column(String)
    decision_recomendada = Column(Text)
    opciones_consideradas = Column(Text, default="[]")
    razonamiento = Column(Text)
    datos_usados = Column(Text, default="{}")
    afirmaciones = Column(Text, default="[]")
    hipotesis = Column(Text)
    metrica_objetivo = Column(String)
    segmento = Column(String)
    impacto_esperado = Column(String)
    esfuerzo_estimado = Column(String)
    riesgo = Column(String)
    nivel_autonomia = Column(Integer, default=0)
    criterio_exito = Column(Text)
    ventana_medicion = Column(String)
    aprobador = Column(String)
    estado_aprobacion = Column(String, default="pendiente")
    accion_ejecutada = Column(Text)
    resultado = Column(Text)
    aprendizaje = Column(Text)
    siguiente_movimiento = Column(String)
    ciclo_id = Column(String)
    created_at = Column(String)

    __table_args__ = (
        # R6 — una decisión de DECIDE lleva hipótesis + métrica + criterio + ventana.
        CheckConstraint(
            "fase_origen != 'decide' OR ("
            "hipotesis IS NOT NULL AND metrica_objetivo IS NOT NULL AND "
            "criterio_exito IS NOT NULL AND ventana_medicion IS NOT NULL)",
            name="ck_superloop_decide_respaldo_r6",
        ),
        # R1 — Nivel >= 3 aprobado lleva aprobador humano.
        CheckConstraint(
            "nivel_autonomia < 3 OR estado_aprobacion != 'aprobado' OR aprobador IS NOT NULL",
            name="ck_superloop_nivel3_aprobador_r1",
        ),
        Index("idx_superloop_ledger_fase", "fase_origen", "estado_aprobacion"),
    )
