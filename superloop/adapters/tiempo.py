"""ProveedorDeTiempo / ProveedorDeIdentidad."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..application.ports import ProveedorDeTiempo, ProveedorDeIdentidad


class TiempoUTC(ProveedorDeTiempo):
    def ahora(self) -> str:
        return datetime.now(timezone.utc).isoformat()


class IdentidadUUID(ProveedorDeIdentidad):
    def nuevo_id(self, prefijo: str) -> str:
        return f"{prefijo}_{uuid.uuid4().hex[:12]}"
