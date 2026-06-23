#!/usr/bin/env python3
"""Hook TaskCreated (§20): rechaza tareas Superloop sin producto/fase/nivel_autonomia."""
from _superloop_common import leer_payload, extraer_superloop, bloquear, ok


def main() -> None:
    sl = extraer_superloop(leer_payload())
    if sl is None:
        ok()
    faltantes = []
    if not sl.get("producto"):
        faltantes.append("la tarea Superloop no declara 'producto'")
    if not sl.get("fase"):
        faltantes.append("la tarea Superloop no declara 'fase'")
    if sl.get("nivel_autonomia") is None:
        faltantes.append("la tarea Superloop no declara 'nivel_autonomia'")
    if faltantes:
        bloquear(faltantes)
    ok()


if __name__ == "__main__":
    main()
