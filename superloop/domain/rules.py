"""
Superloop domain rules — reglas puras de negocio (SUPERLOOP.md §4.2, §8).

Sin IO. Operan sobre dicts de KPIs / señales y devuelven clasificaciones,
anomalías y el siguiente movimiento. Reutilizadas por la máquina de estados
y por los hooks de enforcement.
"""
from __future__ import annotations

from typing import Any

from .enums import EstadoOperativo, EstadoComercial, SiguienteMovimiento


def _num(d: dict[str, Any], key: str, default: float | None = None) -> float | None:
    v = d.get(key, default)
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def clasificar_estado_operativo(senales: dict[str, Any]) -> tuple[EstadoOperativo, float]:
    """§8.1 — salud de uso. Devuelve (estado, confianza 0-1).

    Señales esperadas (cualquiera puede faltar):
      dias_desde_ultimo_uso, uso_30d_vs_anterior_pct, clientes_activos,
      revenue, churn_risk, owner_activo
    """
    dias = _num(senales, "dias_desde_ultimo_uso")
    delta = _num(senales, "uso_30d_vs_anterior_pct")
    activos = _num(senales, "clientes_activos")
    revenue = _num(senales, "revenue")
    churn = _num(senales, "churn_risk")
    owner = senales.get("owner_activo")

    # Sin ninguna señal de uso → no fingir certeza (R3 / §7)
    if dias is None and delta is None and activos is None:
        return EstadoOperativo.DESCONOCIDO, 0.2

    if dias is not None and dias > 180 and (revenue in (None, 0)) and owner is False:
        return EstadoOperativo.ABANDONADO, 0.8
    if dias is not None and dias > 45 and (activos in (None, 0)):
        return EstadoOperativo.DORMIDO, 0.75
    if delta is not None and delta > 20 and (churn is None or churn < 0.2):
        return EstadoOperativo.CRECIENDO, 0.8
    if delta is not None and -10 <= delta <= 10:
        return EstadoOperativo.ESTANCADO, 0.65
    if activos is not None and activos > 0:
        return EstadoOperativo.SALUDABLE, 0.6
    return EstadoOperativo.ESTANCADO, 0.4


def clasificar_estado_comercial(senales: dict[str, Any]) -> tuple[EstadoComercial, float]:
    """§8.2 — oportunidad de negocio. Devuelve (estado, confianza 0-1)."""
    uso_pasado = senales.get("uso_pasado")
    uso_actual_bajo = senales.get("uso_actual_bajo")
    revenue = _num(senales, "revenue")
    churn = _num(senales, "churn_risk")
    clientes_valiosos = senales.get("clientes_valiosos")
    monetizacion_baja = senales.get("monetizacion_baja")
    senales_demanda = senales.get("señales_de_demanda") or senales.get("senales_de_demanda")

    if clientes_valiosos and churn is not None and churn >= 0.5:
        return EstadoComercial.DEFENDER, 0.75
    if uso_pasado and uso_actual_bajo:
        return EstadoComercial.REACTIVAR, 0.7
    if senales_demanda:
        return EstadoComercial.ALTA_OPORTUNIDAD, 0.7
    if monetizacion_baja:
        return EstadoComercial.OPTIMIZAR, 0.6
    if (revenue in (None, 0)) and uso_actual_bajo:
        return EstadoComercial.CERRAR, 0.55
    return EstadoComercial.DESCONOCIDO, 0.3


def detectar_anomalias(senales: dict[str, Any]) -> list[str]:
    """§6.2 — anomalías / triggers (§15) detectadas en las señales."""
    out: list[str] = []
    delta = _num(senales, "uso_30d_vs_anterior_pct")
    churn = _num(senales, "churn_risk")
    dias = _num(senales, "dias_desde_ultimo_uso")
    venta_sin_uso = senales.get("venta_sin_uso")
    uso_sin_venta = senales.get("uso_sin_venta")

    if delta is not None and delta < -30:
        out.append("caida_uso_>30%")
    if churn is not None and churn >= 0.5:
        out.append("churn_risk_alto")
    if dias is not None and dias > 14 and senales.get("cliente_estrategico"):
        out.append("cliente_estrategico_inactivo_>14d")
    if venta_sin_uso:
        out.append("venta_sin_uso")
    if uso_sin_venta:
        out.append("uso_sin_venta")
    return out


def recomendar_siguiente_movimiento(
    estado_operativo: EstadoOperativo,
    estado_comercial: EstadoComercial,
) -> str:
    """§6.3 — próxima mejor acción (texto corto). No ejecuta nada."""
    if estado_comercial == EstadoComercial.REACTIVAR:
        return "Preparar campaña de reactivación segmentada"
    if estado_comercial == EstadoComercial.CERRAR:
        return "Evaluar cierre/reposicionamiento del producto"
    if estado_comercial == EstadoComercial.DEFENDER:
        return "Plan de retención para cuentas valiosas en riesgo"
    if estado_comercial == EstadoComercial.ALTA_OPORTUNIDAD:
        return "Diseñar experimento de adquisición sobre el segmento con demanda"
    if estado_comercial == EstadoComercial.OPTIMIZAR:
        return "Revisar pricing/packaging para subir monetización"
    if estado_operativo == EstadoOperativo.CRECIENDO:
        return "Registrar la palanca de crecimiento y evaluar SCALE"
    return "Recolectar más señales antes de decidir (HOLD)"


def determinar_scale_iterate_hold_kill(
    hipotesis_sostuvo: bool | None,
    criterio_cumplido: bool | None,
    datos_suficientes: bool,
) -> SiguienteMovimiento:
    """§6.7 — movimiento tras VERIFY."""
    if not datos_suficientes:
        return SiguienteMovimiento.HOLD
    if criterio_cumplido and hipotesis_sostuvo:
        return SiguienteMovimiento.SCALE
    if criterio_cumplido or hipotesis_sostuvo:
        return SiguienteMovimiento.ITERATE
    return SiguienteMovimiento.KILL
