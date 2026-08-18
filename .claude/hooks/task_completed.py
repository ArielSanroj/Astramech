#!/usr/bin/env python3
"""Hook TaskCompleted (§20): rechaza tareas Superloop que no cumplan §16 (R6/R1/R3)."""
from _superloop_common import leer_payload, extraer_superloop, bloquear, ok
from superloop.domain import phase_done


def main() -> None:
    sl = extraer_superloop(leer_payload())
    if sl is None:
        ok()
    fase = sl.get("fase")
    if not fase:
        bloquear(["la tarea Superloop completada no declara 'fase'"])
    terminada, faltantes = phase_done.fase_terminada(fase, sl)
    if not terminada:
        bloquear([f"fase '{fase}' no terminada:"] + faltantes)
    ok()


if __name__ == "__main__":
    main()
