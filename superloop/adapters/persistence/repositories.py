"""
Repos SQLAlchemy que implementan los puertos RegistroCanonico y DecisionLedger.

Append-only en el Ledger (§11). El Registro Canónico es upsert por producto (§10).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from ...application.ports import RegistroCanonico, DecisionLedger
from ...domain.entities import (
    Producto, DecisionRecomendada, RegistroCanonicoEntry, Aprendizaje,
)
from ...domain.enums import SiguienteMovimiento
from .models import ProductoRow, DecisionLedgerRow


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class RegistroCanonicoRepo(RegistroCanonico):
    def __init__(self, session_factory):
        self._sf = session_factory

    def upsert(self, entry: RegistroCanonicoEntry) -> None:
        with self._sf() as s:
            row = s.get(ProductoRow, entry.producto_id)
            if row is None:
                row = ProductoRow(producto_id=entry.producto_id, nombre=entry.nombre or entry.producto_id)
                s.add(row)
            row.nombre = entry.nombre or row.nombre
            row.tipo = entry.tipo
            row.estado_operativo = entry.estado_operativo
            row.estado_comercial = entry.estado_comercial
            row.confianza_estado = entry.confianza_estado
            row.metrica_principal = entry.metrica_principal
            row.kpis = json.dumps(entry.kpis)
            row.afirmaciones = json.dumps(entry.afirmaciones)
            row.hipotesis_vigente = entry.hipotesis_vigente
            row.decision_recomendada_ref = entry.decision_recomendada_ref
            row.estado_aprobacion = entry.estado_aprobacion
            row.proxima_mejor_accion = entry.proxima_mejor_accion
            row.updated_at = _utcnow()
            s.commit()

    def get(self, producto_id: str) -> RegistroCanonicoEntry | None:
        with self._sf() as s:
            row = s.get(ProductoRow, producto_id)
            if row is None:
                return None
            return RegistroCanonicoEntry(
                producto_id=row.producto_id, nombre=row.nombre, tipo=row.tipo or "dominio_kpi",
                estado_operativo=row.estado_operativo, estado_comercial=row.estado_comercial,
                confianza_estado=row.confianza_estado, metrica_principal=row.metrica_principal,
                kpis=json.loads(row.kpis or "{}"), afirmaciones=json.loads(row.afirmaciones or "[]"),
                hipotesis_vigente=row.hipotesis_vigente,
                decision_recomendada_ref=row.decision_recomendada_ref,
                estado_aprobacion=row.estado_aprobacion or "pendiente",
                proxima_mejor_accion=row.proxima_mejor_accion,
            )

    def list_productos(self) -> list[Producto]:
        with self._sf() as s:
            rows = s.execute(select(ProductoRow)).scalars().all()
            return [Producto(
                producto_id=r.producto_id, nombre=r.nombre, tipo=r.tipo or "dominio_kpi",
                owner=r.owner, proposito=r.proposito, cliente_ideal=r.cliente_ideal,
                modelo_ingresos=r.modelo_ingresos,
                expected_business_outcome=json.loads(r.expected_business_outcome or "{}"),
                source_ref=r.source_ref,
            ) for r in rows]

    def upsert_producto(self, producto: Producto) -> None:
        """Helper de seeding (no es parte del puerto)."""
        with self._sf() as s:
            row = s.get(ProductoRow, producto.producto_id)
            if row is None:
                row = ProductoRow(producto_id=producto.producto_id, nombre=producto.nombre)
                s.add(row)
            row.nombre = producto.nombre
            row.tipo = producto.tipo
            row.owner = producto.owner
            row.proposito = producto.proposito
            row.cliente_ideal = producto.cliente_ideal
            row.modelo_ingresos = producto.modelo_ingresos
            row.expected_business_outcome = json.dumps(producto.expected_business_outcome)
            row.source_ref = producto.source_ref
            row.updated_at = _utcnow()
            s.commit()


class DecisionLedgerRepo(DecisionLedger):
    def __init__(self, session_factory):
        self._sf = session_factory

    def registrar(self, decision: DecisionRecomendada) -> str:
        data = decision.to_row()
        data["created_at"] = _utcnow()
        with self._sf() as s:
            s.add(DecisionLedgerRow(**data))
            s.commit()
        return decision.decision_id

    def ultimos_aprendizajes(self, producto_id: str, limit: int = 5) -> list[Aprendizaje]:
        with self._sf() as s:
            rows = s.execute(
                select(DecisionLedgerRow)
                .where(DecisionLedgerRow.producto_id == producto_id)
                .where(DecisionLedgerRow.aprendizaje.is_not(None))
                .order_by(DecisionLedgerRow.fecha.desc())
                .limit(limit)
            ).scalars().all()
        out: list[Aprendizaje] = []
        for r in rows:
            try:
                mov = SiguienteMovimiento(r.siguiente_movimiento)
            except (ValueError, TypeError):
                mov = SiguienteMovimiento.HOLD
            out.append(Aprendizaje(
                producto_id=r.producto_id, hipotesis=r.hipotesis or "",
                resultado=r.resultado or "", aprendizaje=r.aprendizaje or "",
                siguiente_movimiento=mov, fecha=r.fecha or "",
            ))
        return out

    def actualizar_aprobacion(self, decision_id: str, estado: str, aprobador: str | None) -> None:
        with self._sf() as s:
            row = s.get(DecisionLedgerRow, decision_id)
            if row is not None:
                row.estado_aprobacion = estado
                row.aprobador = aprobador
                s.commit()
