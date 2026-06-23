"""
FuenteDeDatos adapter — lee los *_efficiency_engine.py legacy. Read-only (R2).

Para un producto de tipo dominio_kpi (finance/hr/marketing/ops/sales) llama
analyze_<dominio>_efficiency(datos) e interpreta su salida {issues, summary} como
señales del Snapshot. Best-effort: si el engine no está, marca la fuente inaccesible
y los datos faltantes como PREGUNTA (R3/§7).

`producto.source_ref` lleva los datos de entrada del dominio (dict) o queda vacío.
"""
from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import Any, Callable

from ...application.ports import FuenteDeDatos
from ...domain.entities import Producto, Snapshot, Afirmacion
from ...domain.enums import EtiquetaAfirmacion


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# dominio → (módulo, función). Los módulos viven en company-efficiency-optimizer/.
_ENGINES: dict[str, tuple[str, str]] = {
    "finance": ("finance_efficiency_engine", "analyze_finance_efficiency"),
    "hr": ("hr_efficiency_engine", "analyze_hr_efficiency"),
    "marketing": ("marketing_efficiency_engine", "analyze_marketing_efficiency"),
    "ops": ("ops_efficiency_engine", "analyze_ops_efficiency"),
    "sales": ("sales_efficiency_engine", "analyze_sales_efficiency"),
}


class EfficiencyEngineSource(FuenteDeDatos):
    def __init__(self, datos_por_dominio: dict[str, dict] | None = None):
        # datos_por_dominio: {"finance": {...kpis...}, ...}. Inyectables para test.
        self.datos = datos_por_dominio or {}

    def _resolver_engine(self, dominio: str) -> Callable | None:
        spec = _ENGINES.get(dominio)
        if not spec:
            return None
        mod_name, fn_name = spec
        try:
            mod = importlib.import_module(mod_name)
            return getattr(mod, fn_name, None)
        except Exception:
            return None

    def observar(self, producto: Producto) -> Snapshot:
        dominio = (producto.source_ref or producto.nombre or "").lower()
        # normaliza: "finance" de "prod_finance" o "Finance Domain"
        for key in _ENGINES:
            if key in dominio:
                dominio = key
                break

        fuentes_ok: list[str] = []
        fuentes_ko: list[str] = []
        faltantes: list[str] = []
        kpis: dict[str, Any] = {}
        afirmaciones: list[Afirmacion] = []

        engine = self._resolver_engine(dominio)
        datos = self.datos.get(dominio, {})

        if engine is None:
            fuentes_ko.append(f"{dominio}_efficiency_engine")
            faltantes.append(f"{dominio}_engine_inaccesible")
        else:
            try:
                resultado = engine(datos)
                fuentes_ok.append(f"{dominio}_efficiency_engine")
                summary = resultado.get("summary", {})
                for k, v in summary.items():
                    if v is not None:
                        kpis[k] = v
                        afirmaciones.append(Afirmacion(f"KPI {k} = {v}.", EtiquetaAfirmacion.HECHO))
                for issue in resultado.get("issues", []):
                    afirmaciones.append(Afirmacion(
                        f"Issue {issue.get('type')} (valor {issue.get('value')}).",
                        EtiquetaAfirmacion.HECHO))
                # Señal derivada para clasificación operativa/comercial.
                if resultado.get("issues"):
                    kpis["monetizacion_baja"] = True
                    kpis["uso_actual_bajo"] = True
            except Exception as exc:
                fuentes_ko.append(f"{dominio}_efficiency_engine")
                faltantes.append(f"{dominio}_engine_error:{type(exc).__name__}")

        if not kpis:
            faltantes.append("sin_kpis_para_clasificar")
            afirmaciones.append(Afirmacion(
                f"No se obtuvieron KPIs para {producto.nombre}; baja confianza.",
                EtiquetaAfirmacion.PREGUNTA))

        if producto.expected_business_outcome.get("metrica_norte"):
            kpis.setdefault("metrica_principal", producto.expected_business_outcome["metrica_norte"])

        return Snapshot(
            producto_id=producto.producto_id, fecha=_utcnow(),
            fuentes_consultadas=fuentes_ok, fuentes_inaccesibles=fuentes_ko,
            datos_faltantes=faltantes, kpis=kpis, afirmaciones=afirmaciones,
        )
