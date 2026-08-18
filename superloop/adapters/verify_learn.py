"""
VERIFY + LEARN adapters (SUPERLOOP.md §6.6, §6.7) para Astramech.

VERIFY: re-observa el producto y compara el snapshot post-acción contra el baseline
del momento de la decisión (executed≠succeeded, R7). Sin datos post-acción → 'incierta'.
LEARN: deriva SCALE/ITERATE/HOLD/KILL y escribe aprendizaje + movimiento en el Ledger,
cerrando el loop para el próximo DECIDE (R8).
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import update

from ..domain import rules
from .persistence.models import DecisionLedgerRow


class VerificadorReobservacion:
    """Compara la métrica objetivo contra el baseline registrado en datos_usados."""

    def __init__(self, session_factory, fuente, registro):
        self._sf = session_factory
        self.fuente = fuente
        self.registro = registro

    def verificar(self, decision: dict[str, Any]) -> dict[str, Any]:
        producto_id = decision.get("producto_id")
        metrica = decision.get("metrica_objetivo")
        baseline = (json.loads(decision.get("datos_usados") or "{}")
                    .get("kpis", {}).get(metrica))

        actual = None
        productos = {p.producto_id: p for p in self.registro.list_productos()}
        prod = productos.get(producto_id)
        if prod is not None:
            try:
                snap = self.fuente.observar(prod)
                actual = snap.kpis.get(metrica)
            except Exception:
                actual = None

        if actual is None or baseline is None:
            estado = "incierta"
            sostuvo = None
            datos_suf = False
            resultado = f"sin datos post-acción para {metrica} (baseline={baseline}, actual={actual})"
        else:
            sostuvo = float(actual) >= float(baseline)
            estado = "sostuvo" if sostuvo else "fallo"
            datos_suf = True
            resultado = f"{metrica}: baseline={baseline} → actual={actual}"

        return {
            "decision_id": decision.get("decision_id"),
            "hipotesis_sostuvo": sostuvo,
            "estado_hipotesis": estado,
            "criterio_cumplido": sostuvo,
            "datos_suficientes": datos_suf,
            "resultado": resultado,
        }


class AprendizajeLedger:
    """Deriva el movimiento y cierra el loop escribiendo en el Ledger (R8)."""

    def __init__(self, session_factory):
        self._sf = session_factory

    def aprender(self, decision: dict[str, Any], verif: dict[str, Any]) -> dict[str, Any]:
        movimiento = rules.determinar_scale_iterate_hold_kill(
            hipotesis_sostuvo=verif.get("hipotesis_sostuvo"),
            criterio_cumplido=verif.get("criterio_cumplido"),
            datos_suficientes=bool(verif.get("datos_suficientes")),
        )
        resultado = verif.get("resultado", "")
        h = decision.get("hipotesis", "")
        if not verif.get("datos_suficientes"):
            aprendizaje = f"Sin datos suficientes para validar ('{h}'). Movimiento: HOLD."
        else:
            estado = "se sostuvo" if verif.get("hipotesis_sostuvo") else "no se sostuvo"
            aprendizaje = (f"La hipótesis ('{h}') {estado} ({resultado}). "
                           f"Movimiento: {movimiento.value.upper()}.")

        decision_id = decision.get("decision_id")
        with self._sf() as s:
            s.execute(update(DecisionLedgerRow)
                      .where(DecisionLedgerRow.decision_id == decision_id)
                      .values(resultado=resultado, aprendizaje=aprendizaje,
                              siguiente_movimiento=movimiento.value))
            s.commit()
        return {"decision_id": decision_id, "resultado": resultado,
                "aprendizaje": aprendizaje, "siguiente_movimiento": movimiento.value}
