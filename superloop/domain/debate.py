"""
DIAGNOSE como debate — hipótesis en competencia (SUPERLOOP.md §19.2).

Para diagnósticos ambiguos o de alto impacto, un solo razonamiento halla una explicación
plausible y deja de buscar (sesgo de anclaje). Este módulo genera VARIAS hipótesis rivales
sobre POR QUÉ un producto está en su estado, las confronta contra las señales (evidencia a
favor / en contra) y las rankea. El resultado sube la fiabilidad del diagnóstico y se
registra como `opciones_consideradas` en el Decision Ledger (R3/§19.2).

Puro: sin IO. La versión con agent-teams (ConsensusEngine) es una estrategia de runtime
por encima de esta lógica (§19.4) — esta es la fuente de verdad del scoring.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .enums import EstadoOperativo, EstadoComercial, EtiquetaAfirmacion
from .entities import Afirmacion


@dataclass
class Hipotesis:
    """Una explicación rival de por qué el producto está como está."""
    nombre: str
    explicacion: str
    evidencia_a_favor: list[str] = field(default_factory=list)
    evidencia_en_contra: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        """Fuerza de la hipótesis: evidencia a favor neta, normalizada a 0-1."""
        f, c = len(self.evidencia_a_favor), len(self.evidencia_en_contra)
        if f + c == 0:
            return 0.0
        return round(f / (f + c), 3)

    def etiqueta(self) -> EtiquetaAfirmacion:
        """HECHO si domina la evidencia, INFERENCIA si compite, SUPUESTO si débil."""
        s = self.score
        if s >= 0.75 and self.evidencia_a_favor:
            return EtiquetaAfirmacion.HECHO
        if s >= 0.4:
            return EtiquetaAfirmacion.INFERENCIA
        return EtiquetaAfirmacion.SUPUESTO


# Cada generador propone una hipótesis (o None si no aplica) a partir de las señales.
def _h_estacional(s: dict[str, Any]) -> Hipotesis | None:
    delta = s.get("uso_30d_vs_anterior_pct")
    if delta is None:
        return None
    h = Hipotesis("estacional", "La variación de uso es estacional, no estructural.")
    if s.get("mes_estacional"):
        h.evidencia_a_favor.append("el periodo coincide con estacionalidad conocida")
    else:
        h.evidencia_en_contra.append("no hay marca de estacionalidad en las señales")
    if isinstance(delta, (int, float)) and abs(delta) < 15:
        h.evidencia_a_favor.append("la magnitud del cambio es moderada")
    return h


def _h_churn(s: dict[str, Any]) -> Hipotesis | None:
    churn = s.get("churn_risk")
    if churn is None:
        return None
    h = Hipotesis("churn", "La caída se explica por abandono real de cuentas (churn).")
    if isinstance(churn, (int, float)) and churn >= 0.5:
        h.evidencia_a_favor.append("churn_risk alto")
    else:
        h.evidencia_en_contra.append("churn_risk no es alto")
    if s.get("clientes_activos") == 0:
        h.evidencia_a_favor.append("clientes_activos = 0")
    return h


def _h_data_gap(s: dict[str, Any]) -> Hipotesis | None:
    h = Hipotesis("data_gap", "El estado aparente es un artefacto de datos faltantes.")
    faltan = s.get("_datos_faltantes") or []
    if faltan:
        h.evidencia_a_favor.append(f"hay {len(faltan)} dato(s) faltante(s)")
    if not s or len([k for k in s if not k.startswith("_")]) <= 1:
        h.evidencia_a_favor.append("casi no hay KPIs medidos")
    else:
        h.evidencia_en_contra.append("hay KPIs medidos suficientes para clasificar")
    return h


def _h_monetizacion(s: dict[str, Any]) -> Hipotesis | None:
    if not (s.get("monetizacion_baja") or s.get("uso_sin_venta")):
        return None
    h = Hipotesis("monetizacion", "Hay uso pero la monetización/conversión está rezagada.")
    if s.get("monetizacion_baja"):
        h.evidencia_a_favor.append("señal de monetización baja")
    if s.get("uso_sin_venta"):
        h.evidencia_a_favor.append("uso sin venta")
    if s.get("revenue"):
        h.evidencia_en_contra.append("hay revenue registrado")
    return h


_GENERADORES: list[Callable[[dict[str, Any]], Hipotesis | None]] = [
    _h_estacional, _h_churn, _h_data_gap, _h_monetizacion,
]


def debatir(senales: dict[str, Any], datos_faltantes: list[str] | None = None) -> list[Hipotesis]:
    """Genera y rankea hipótesis rivales (de mayor a menor score). §19.2."""
    ctx = dict(senales)
    ctx["_datos_faltantes"] = datos_faltantes or []
    hipotesis = [h for gen in _GENERADORES if (h := gen(ctx)) is not None]
    return sorted(hipotesis, key=lambda h: h.score, reverse=True)


def opciones_consideradas(hipotesis: list[Hipotesis]) -> list[dict[str, Any]]:
    """Serializa el debate para `opciones_consideradas` del Decision Ledger (§11)."""
    return [{
        "hipotesis": h.nombre,
        "explicacion": h.explicacion,
        "score": h.score,
        "elegida": i == 0,
        "evidencia_a_favor": h.evidencia_a_favor,
        "evidencia_en_contra": h.evidencia_en_contra,
    } for i, h in enumerate(hipotesis)]


def afirmaciones_del_debate(hipotesis: list[Hipotesis], top: int = 3) -> list[Afirmacion]:
    """Convierte el debate en afirmaciones etiquetadas (R3)."""
    out: list[Afirmacion] = []
    for h in hipotesis[:top]:
        out.append(Afirmacion(
            f"Hipótesis '{h.nombre}' (score {h.score}): {h.explicacion}",
            h.etiqueta(),
        ))
    return out
