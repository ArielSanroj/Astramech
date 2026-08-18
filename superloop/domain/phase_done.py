"""
Superloop "definición de terminado" por fase (SUPERLOOP.md §16) — predicados puros.

ESTA es la única fuente de verdad de "¿la fase está terminada?". La usan tanto la
máquina de estados (R5: no avanzar sin cumplir la fase) como los hooks de enforcement
(§20: TaskCompleted sale con exit code 2 si esto devuelve incompleto).

Cada predicado recibe un dict plano (un "registro de fase") y devuelve
(ok: bool, faltantes: list[str]). Trabajan sobre dicts — no sobre entidades — para
que los hooks puedan llamarlos con el JSON crudo de una tarea sin instanciar el dominio.

Valida también las reglas duras:
  R3 — afirmaciones etiquetadas HECHO/INFERENCIA/SUPUESTO/PREGUNTA
  R6 — toda decisión lleva hipótesis + métrica + criterio de éxito + ventana
  R1 — toda acción Nivel >= 3 lleva un aprobador humano registrado
"""
from __future__ import annotations

from typing import Any

ETIQUETAS_VALIDAS = {"HECHO", "INFERENCIA", "SUPUESTO", "PREGUNTA"}


def _afirmaciones_etiquetadas(afirmaciones: Any) -> tuple[bool, list[str]]:
    """R3 — toda afirmación debe llevar una etiqueta válida."""
    faltantes: list[str] = []
    if not isinstance(afirmaciones, list):
        return False, ["afirmaciones no es una lista"]
    for i, a in enumerate(afirmaciones):
        etiqueta = a.get("etiqueta") if isinstance(a, dict) else None
        if etiqueta not in ETIQUETAS_VALIDAS:
            faltantes.append(f"afirmacion[{i}] sin etiqueta válida (R3): {etiqueta!r}")
    return (not faltantes), faltantes


def observe_done(reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """§16 OBSERVE done: snapshot actualizado, fuentes consultadas/inaccesibles,
    datos faltantes registrados como PREGUNTA."""
    faltan: list[str] = []
    if not reg.get("snapshot_fecha"):
        faltan.append("falta snapshot actualizado")
    if not reg.get("fuentes_consultadas") and not reg.get("fuentes_inaccesibles"):
        faltan.append("ninguna fuente consultada ni marcada inaccesible")
    ok_af, faltan_af = _afirmaciones_etiquetadas(reg.get("afirmaciones", []))
    faltan += faltan_af
    return (not faltan), faltan


def diagnose_done(reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """§16 DIAGNOSE done: KPIs, estado operativo y comercial, métrica principal,
    afirmaciones etiquetadas (R3)."""
    faltan: list[str] = []
    if not reg.get("estado_operativo"):
        faltan.append("falta estado_operativo")
    if not reg.get("estado_comercial"):
        faltan.append("falta estado_comercial")
    if not reg.get("metrica_principal"):
        faltan.append("falta metrica_principal")
    ok_af, faltan_af = _afirmaciones_etiquetadas(reg.get("afirmaciones", []))
    faltan += faltan_af
    return (not faltan), faltan


def decide_done(reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """§16 DECIDE done + R6: hipótesis, métrica, criterio de éxito, ventana,
    nivel de autonomía."""
    faltan: list[str] = []
    for campo in ("hipotesis", "metrica_objetivo", "criterio_exito", "ventana_medicion"):
        if not reg.get(campo):
            faltan.append(f"falta {campo} (R6)")
    if reg.get("nivel_autonomia") is None:
        faltan.append("falta nivel_autonomia")
    return (not faltan), faltan


def approve_done(reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """§16 APPROVE done + R1: estado de aprobación resuelto; ninguna acción
    Nivel >= 3 avanza sin aprobador humano."""
    faltan: list[str] = []
    estado = reg.get("estado_aprobacion")
    if estado not in ("aprobado", "rechazado", "requiere_cambios"):
        faltan.append("estado_aprobacion sigue pendiente (no puede avanzar)")
    nivel = reg.get("nivel_autonomia")
    try:
        nivel_i = int(nivel) if nivel is not None else 0
    except (TypeError, ValueError):
        nivel_i = 0
    if nivel_i >= 3 and estado == "aprobado" and not reg.get("aprobador"):
        faltan.append("acción Nivel >= 3 aprobada sin aprobador humano (R1)")
    return (not faltan), faltan


def orchestrate_done(reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """§16 ORCHESTRATE done: acción ejecutada/preparada/bloqueada con alcance
    documentado; Nivel >= 3 exige aprobador (R1)."""
    faltan: list[str] = []
    if not reg.get("accion_ejecutada") and not reg.get("bloqueada_razon"):
        faltan.append("acción ni ejecutada ni marcada como bloqueada")
    nivel = reg.get("nivel_autonomia")
    try:
        nivel_i = int(nivel) if nivel is not None else 0
    except (TypeError, ValueError):
        nivel_i = 0
    if nivel_i >= 3 and not reg.get("aprobador"):
        faltan.append("orquestar Nivel >= 3 sin aprobador humano (R1)")
    return (not faltan), faltan


def verify_done(reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """§16 VERIFY done: gate evaluado contra datos, baseline + ventana, hipótesis
    sostuvo/falló/incierta.

    El estado de la hipótesis se registra de forma explícita (tri-estado): un
    `estado_hipotesis` en {sostuvo, fallo, incierta}, o un `hipotesis_sostuvo` booleano.
    'incierta' es un estado VÁLIDO (no es lo mismo que no haberlo registrado).
    """
    faltan: list[str] = []
    estado = reg.get("estado_hipotesis")
    if estado not in ("sostuvo", "fallo", "incierta") and reg.get("hipotesis_sostuvo") is None:
        faltan.append("no se registró si la hipótesis sostuvo/falló/incierta")
    if not reg.get("resultado"):
        faltan.append("falta resultado medido")
    return (not faltan), faltan


def learn_done(reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """§16 LEARN done: ciclo registrado, registro canónico actualizado, siguiente
    movimiento definido."""
    faltan: list[str] = []
    if reg.get("siguiente_movimiento") not in ("scale", "iterate", "hold", "kill"):
        faltan.append("siguiente_movimiento debe ser scale/iterate/hold/kill")
    if not reg.get("aprendizaje"):
        faltan.append("falta aprendizaje registrado (R8)")
    return (not faltan), faltan


# Mapa fase → predicado, para la máquina de estados y los hooks.
PREDICADOS = {
    "observe": observe_done,
    "diagnose": diagnose_done,
    "decide": decide_done,
    "approve": approve_done,
    "orchestrate": orchestrate_done,
    "verify": verify_done,
    "learn": learn_done,
}


def fase_terminada(fase: str, reg: dict[str, Any]) -> tuple[bool, list[str]]:
    """Dispatcher: ¿la `fase` está terminada según su registro `reg`?"""
    pred = PREDICADOS.get(fase)
    if pred is None:
        return False, [f"fase desconocida: {fase!r}"]
    return pred(reg)
