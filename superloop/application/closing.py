"""ORCHESTRATE / VERIFY / LEARN use cases (SUPERLOOP.md §6.5-6.7) — cierre del loop."""
from __future__ import annotations

from typing import Any


class OrquestarAccionAprobada:
    def __init__(self, ejecutor):
        self.ejecutor = ejecutor

    def __call__(self, decision: dict[str, Any], contexto: dict[str, Any]) -> dict[str, Any]:
        res = self.ejecutor.ejecutar(decision)
        contexto["orquestacion"] = res
        return {
            "accion_ejecutada": res.get("accion_ejecutada"),
            "bloqueada_razon": res.get("bloqueada_razon"),
            "nivel_autonomia": decision.get("nivel_autonomia"),
            "aprobador": res.get("aprobador") or decision.get("aprobador"),
        }


class VerificarResultado:
    def __init__(self, verificador):
        self.verificador = verificador

    def __call__(self, decision: dict[str, Any], contexto: dict[str, Any]) -> dict[str, Any]:
        verif = self.verificador.verificar(decision)
        contexto["verificacion"] = verif
        return {
            "hipotesis_sostuvo": verif.get("hipotesis_sostuvo"),
            "estado_hipotesis": verif.get("estado_hipotesis"),
            "resultado": verif.get("resultado"),
        }


class RegistrarAprendizaje:
    def __init__(self, aprendiz):
        self.aprendiz = aprendiz

    def __call__(self, decision: dict[str, Any], contexto: dict[str, Any]) -> dict[str, Any]:
        res = self.aprendiz.aprender(decision, contexto.get("verificacion", {}))
        return {
            "aprendizaje": res.get("aprendizaje"),
            "siguiente_movimiento": res.get("siguiente_movimiento"),
        }
