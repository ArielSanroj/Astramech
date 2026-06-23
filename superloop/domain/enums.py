"""Superloop domain enums (SUPERLOOP.md §6, §8, §9, §3)."""
from __future__ import annotations

from enum import Enum


class Fase(str, Enum):
    """Fases del loop operativo (§6)."""
    OBSERVE = "observe"
    DIAGNOSE = "diagnose"
    DECIDE = "decide"
    APPROVE = "approve"
    ORCHESTRATE = "orchestrate"
    VERIFY = "verify"
    LEARN = "learn"

    @classmethod
    def orden(cls) -> list["Fase"]:
        return [cls.OBSERVE, cls.DIAGNOSE, cls.DECIDE, cls.APPROVE,
                cls.ORCHESTRATE, cls.VERIFY, cls.LEARN]

    def siguiente(self) -> "Fase | None":
        orden = self.orden()
        i = orden.index(self)
        return orden[i + 1] if i + 1 < len(orden) else None


class EtiquetaAfirmacion(str, Enum):
    """R3 — toda afirmación lleva una de estas etiquetas."""
    HECHO = "HECHO"
    INFERENCIA = "INFERENCIA"
    SUPUESTO = "SUPUESTO"
    PREGUNTA = "PREGUNTA"


class EstadoOperativo(str, Enum):
    """§8.1 — salud de uso del producto."""
    CRECIENDO = "creciendo"
    SALUDABLE = "saludable"
    ESTANCADO = "estancado"
    DORMIDO = "dormido"
    ABANDONADO = "abandonado"
    DESCONOCIDO = "desconocido"


class EstadoComercial(str, Enum):
    """§8.2 — oportunidad de negocio."""
    ALTA_OPORTUNIDAD = "alta_oportunidad"
    DEFENDER = "defender"
    OPTIMIZAR = "optimizar"
    REACTIVAR = "reactivar"
    CERRAR = "cerrar"
    DESCONOCIDO = "desconocido"


class NivelAutonomia(int, Enum):
    """§9 — niveles de autonomía por riesgo de la acción."""
    READ_ONLY = 0
    DRAFT = 1
    INTERNAL_WRITE = 2
    EXTERNAL_ACTION = 3
    BUSINESS_CRITICAL = 4

    @property
    def requiere_aprobacion_humana(self) -> bool:
        """Nivel 3-4 siempre requiere un humano aprobador (R1)."""
        return self.value >= 3


class EstadoAprobacion(str, Enum):
    """§6.4 — resultado del gate de aprobación."""
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    REQUIERE_CAMBIOS = "requiere_cambios"


class SiguienteMovimiento(str, Enum):
    """§6.7 — movimiento tras verificar."""
    SCALE = "scale"
    ITERATE = "iterate"
    HOLD = "hold"
    KILL = "kill"
