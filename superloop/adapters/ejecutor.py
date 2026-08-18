"""
ORCHESTRATE adapter (SUPERLOOP.md §6.5, R1) — EjecutorDeAcciones SIEMPRE gated.

Rehúsa actuar salvo que la fila del Decision Ledger esté `aprobado` y, para
nivel_autonomia >= 3, tenga `aprobador` humano (R1).

  - Nivel 0-2: registra orquestación interna (sin blast radius).
  - Nivel >= 3: entrega al supervisor CrewAI existente (inyectado) — que aplica sus
    propios controles; nunca ejecuta directamente. Si no hay supervisor inyectado o
    falta el mapeo, queda BLOQUEADA con razón registrada (no improvisa, §6.5).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy import update, select

from ..application.ports import EjecutorDeAcciones
from .persistence.models import DecisionLedgerRow


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class EjecutorGated(EjecutorDeAcciones):
    def __init__(self, session_factory, crew_dispatch: Callable[[dict], str] | None = None):
        self._sf = session_factory
        # crew_dispatch: callable opcional que entrega la acción al orquestador CrewAI.
        self._crew_dispatch = crew_dispatch

    def ejecutar(self, decision: dict[str, Any]) -> dict[str, Any]:
        decision_id = decision.get("decision_id")
        with self._sf() as s:
            row = s.get(DecisionLedgerRow, decision_id) if decision_id else None
            if row is None:
                return self._bloquear(decision_id, "decisión no encontrada en el Ledger")
            nivel = int(row.nivel_autonomia or 0)
            estado = row.estado_aprobacion

            # --- GATE R1 ---
            if estado != "aprobado":
                return self._bloquear(decision_id, f"no aprobada (estado={estado}); no se orquesta (R1)")
            if nivel >= 3 and not row.aprobador:
                return self._bloquear(decision_id, "Nivel >= 3 sin aprobador humano (R1)")

            if nivel < 3:
                accion = f"Preparada/registrada acción interna: {row.decision_recomendada}"
                row.accion_ejecutada = f"[{_utcnow()}] (interno) {accion}"
                s.commit()
                return {"decision_id": decision_id, "estado": "ejecutada_interna",
                        "accion_ejecutada": accion, "aprobador": row.aprobador}

            # Nivel >= 3: handoff gated a CrewAI.
            datos = json.loads(row.datos_usados or "{}")
            mapeo = datos.get("accion_externa")
            if not (mapeo and self._crew_dispatch):
                return self._bloquear(
                    decision_id,
                    "Nivel >= 3 aprobada pero sin dispatch CrewAI o sin mapeo de acción; "
                    "regresa a DECIDE (§6.5). No se improvisa.")
            try:
                ref = self._crew_dispatch(mapeo)
            except Exception as exc:
                return self._bloquear(decision_id, f"handoff CrewAI falló: {exc}")
            accion = f"Despachada a CrewAI (ref={ref})"
            row.accion_ejecutada = f"[{_utcnow()}] (externo_gated) {accion}"
            s.commit()
            return {"decision_id": decision_id, "estado": "despachada_crew",
                    "accion_ejecutada": accion, "ref": ref, "aprobador": row.aprobador}

    def _bloquear(self, decision_id: str | None, razon: str) -> dict[str, Any]:
        if decision_id:
            with self._sf() as s:
                s.execute(update(DecisionLedgerRow)
                          .where(DecisionLedgerRow.decision_id == decision_id)
                          .values(accion_ejecutada=f"[BLOQUEADA {_utcnow()}] {razon}"))
                s.commit()
        return {"decision_id": decision_id, "estado": "bloqueada",
                "bloqueada_razon": razon, "accion_ejecutada": None}
