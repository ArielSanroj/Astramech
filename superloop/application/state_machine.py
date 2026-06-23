"""
Superloop state machine (SUPERLOOP.md §6, §16) — orquestador del loop.

Avanza OBSERVE → DIAGNOSE → DECIDE → APPROVE → ORCHESTRATE → VERIFY → LEARN
SOLO cuando la fase actual cumple su "definición de terminado" (R5). Cualquier
intento de saltar una fase incompleta levanta PhaseNotDone.

En el MVP la máquina corre en modo read-only: OBSERVE→DIAGNOSE→DECIDE y se DETIENE
en APPROVE (R1/R2: blast radius cero). Las fases posteriores se inyectan vía use
cases en fases posteriores del roadmap.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ..domain.enums import Fase
from ..domain import phase_done


class PhaseNotDone(Exception):
    """Se intentó avanzar de fase sin cumplir su definición de terminado (R5)."""

    def __init__(self, fase: str, faltantes: list[str]):
        self.fase = fase
        self.faltantes = faltantes
        super().__init__(f"Fase '{fase}' no terminada: {'; '.join(faltantes)}")


@dataclass
class CicloResultado:
    """Resultado de una vuelta (parcial) del loop."""
    producto_id: str
    fase_alcanzada: str
    registros: dict[str, dict[str, Any]] = field(default_factory=dict)
    detenido_en: str | None = None
    motivo_detencion: str | None = None

    @property
    def registro_actual(self) -> dict[str, Any]:
        return self.registros.get(self.fase_alcanzada, {})


class SuperloopStateMachine:
    """Secuencia las fases, validando cada transición con phase_done (R5).

    `use_cases` es un dict fase->callable. Cada callable recibe (producto, contexto)
    y devuelve el "registro" plano de esa fase (el mismo shape que validan los
    predicados de phase_done). El contexto acumula los registros previos.
    """

    def __init__(self, use_cases: dict[str, Callable[[Any, dict], dict[str, Any]]],
                 detener_en: str | None = Fase.APPROVE.value):
        self.use_cases = use_cases
        # Por defecto la máquina se detiene ANTES de APPROVE (gate humano, R1).
        self.detener_en = detener_en

    def run(self, producto: Any) -> CicloResultado:
        contexto: dict[str, Any] = {"registros": {}}
        resultado = CicloResultado(
            producto_id=getattr(producto, "producto_id", str(producto)),
            fase_alcanzada=Fase.OBSERVE.value,
        )

        for fase in Fase.orden():
            fase_val = fase.value

            # Gate de detención (MVP: parar en APPROVE — no ejecutar nada gated).
            if self.detener_en and fase_val == self.detener_en:
                resultado.detenido_en = fase_val
                resultado.motivo_detencion = (
                    f"Gate humano: el loop se detiene en {fase_val} (R1)."
                )
                break

            use_case = self.use_cases.get(fase_val)
            if use_case is None:
                resultado.detenido_en = fase_val
                resultado.motivo_detencion = f"Sin use case para {fase_val} (no implementado)."
                break

            registro = use_case(producto, contexto)
            contexto["registros"][fase_val] = registro
            resultado.registros[fase_val] = registro
            resultado.fase_alcanzada = fase_val

            # R5 — no avanzar si la fase no está terminada.
            ok, faltantes = phase_done.fase_terminada(fase_val, registro)
            if not ok:
                raise PhaseNotDone(fase_val, faltantes)

        return resultado
