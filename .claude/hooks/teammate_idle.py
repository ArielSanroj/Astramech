#!/usr/bin/env python3
"""Hook TeammateIdle (§20/§19.1): recuerda procesar productos pendientes. No bloquea."""
import sys

from _superloop_common import leer_payload, extraer_superloop, ok


def main() -> None:
    sl = extraer_superloop(leer_payload())
    if sl is None:
        ok()
    pendientes = sl.get("portafolio_pendiente") or []
    if pendientes:
        print(f"↻ Superloop: {len(pendientes)} producto(s) sin procesar: "
              f"{', '.join(map(str, pendientes[:10]))} (§19.1).", file=sys.stderr)
    ok()


if __name__ == "__main__":
    main()
