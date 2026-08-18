"""
Superloop facade (SUPERLOOP.md §1, §12) — punto de entrada único en Astramech.

Construye la máquina con persistencia SQLAlchemy (Postgres en prod, SQLite en test) y
la fuente de los *_efficiency_engine.py. Corre el loop read-only OBSERVE→DIAGNOSE→DECIDE
deteniéndose en APPROVE (R1). Renderiza Business Card + Evidence Pack (§12).
"""
from __future__ import annotations

from typing import Any

from .config.settings import SuperloopSettings
from .adapters.persistence.engine import make_engine, init_schema, make_session_factory
from .adapters.persistence.repositories import RegistroCanonicoRepo, DecisionLedgerRepo
from .adapters.fuentes.efficiency_engine_source import EfficiencyEngineSource
from .adapters.tiempo import TiempoUTC, IdentidadUUID
from .adapters.ejecutor import EjecutorGated
from .adapters.verify_learn import VerificadorReobservacion, AprendizajeLedger
from .application.state_machine import SuperloopStateMachine, CicloResultado, PhaseNotDone
from .application.use_cases import ObservarProducto, DiagnosticarProducto, DecidirProximaAccion
from .application.closing import OrquestarAccionAprobada, VerificarResultado, RegistrarAprendizaje
from .domain import phase_done
from .domain.entities import Producto


# Los 6 dominios KPI = productos por defecto (§2).
_DOMINIOS = ["finance", "hr", "marketing", "ops", "sales"]


class SuperloopFacade:
    def __init__(self, db_url: str | None = None, datos_por_dominio: dict | None = None):
        self.settings = SuperloopSettings.resolve(db_url)
        self.engine = make_engine(self.settings.db_url)
        init_schema(self.engine)
        self._sf = make_session_factory(self.engine)

        self.registro = RegistroCanonicoRepo(self._sf)
        self.ledger = DecisionLedgerRepo(self._sf)
        self.fuente = EfficiencyEngineSource(datos_por_dominio)
        self.tiempo = TiempoUTC()
        self.identidad = IdentidadUUID()

        use_cases = {
            "observe": ObservarProducto(self.fuente),
            "diagnose": DiagnosticarProducto(self.registro),
            "decide": DecidirProximaAccion(self.registro, self.ledger, self.tiempo, self.identidad),
        }
        self.machine = SuperloopStateMachine(use_cases, detener_en=self.settings.detener_en)

        # Fase 3 — cierre del loop (post-aprobación humana).
        self.ejecutor = EjecutorGated(self._sf, crew_dispatch=None)
        self._orquestar = OrquestarAccionAprobada(self.ejecutor)
        self._verificar = VerificarResultado(
            VerificadorReobservacion(self._sf, self.fuente, self.registro))
        self._aprender = RegistrarAprendizaje(AprendizajeLedger(self._sf))

    def aprobar(self, decision_id: str, aprobador: str) -> None:
        """Registra una aprobación HUMANA en el Ledger (R1)."""
        if not aprobador:
            raise ValueError("aprobador humano requerido (R1)")
        self.ledger.actualizar_aprobacion(decision_id, "aprobado", aprobador)

    def resume_aprobados(self) -> list[dict[str, Any]]:
        """ORCHESTRATE→VERIFY→LEARN sobre decisiones aprobadas (cadencia REPEAT, R8)."""
        from sqlalchemy import select
        from .adapters.persistence.models import DecisionLedgerRow
        with self._sf() as s:
            rows = s.execute(
                select(DecisionLedgerRow)
                .where(DecisionLedgerRow.estado_aprobacion == "aprobado")
                .where(DecisionLedgerRow.aprendizaje.is_(None))
            ).scalars().all()
            decisiones = [self._row_to_dict(r) for r in rows]
        return [self._cerrar_ciclo(d) for d in decisiones]

    @staticmethod
    def _row_to_dict(r) -> dict[str, Any]:
        return {c.name: getattr(r, c.name) for c in r.__table__.columns}

    def _cerrar_ciclo(self, decision: dict[str, Any]) -> dict[str, Any]:
        ctx: dict[str, Any] = {}
        orq = self._orquestar(decision, ctx)
        ok, faltan = phase_done.orchestrate_done({**decision, **orq})
        if not ok:
            return {"decision_id": decision.get("decision_id"), "fase": "orchestrate",
                    "ok": False, "faltan": faltan, "detalle": orq}
        ver = self._verificar(decision, ctx)
        ok, faltan = phase_done.verify_done(ver)
        if not ok:
            return {"decision_id": decision.get("decision_id"), "fase": "verify",
                    "ok": False, "faltan": faltan, "detalle": ver}
        learn = self._aprender(decision, ctx)
        ok, faltan = phase_done.learn_done(learn)
        return {"decision_id": decision.get("decision_id"),
                "fase": "learn" if ok else "learn_incompleto", "ok": ok, "faltan": faltan,
                "siguiente_movimiento": learn.get("siguiente_movimiento"),
                "aprendizaje": learn.get("aprendizaje")}

    def seed_productos_dominios(self) -> int:
        creados = 0
        for d in _DOMINIOS:
            self.registro.upsert_producto(Producto(
                producto_id=f"prod_{d}", nombre=f"{d.capitalize()} Domain", tipo="dominio_kpi",
                owner="company", proposito=f"Eficiencia del dominio {d}.",
                modelo_ingresos="b2b", source_ref=d,
                expected_business_outcome={"tipo": "cost_saving", "metrica_norte": "efficiency_score"},
            ))
            creados += 1
        return creados

    def run_producto(self, producto: Producto) -> dict[str, Any]:
        try:
            return self._render(producto, self.machine.run(producto), None)
        except PhaseNotDone as exc:
            return self._render(producto, None, str(exc))

    def run_todos(self) -> list[dict[str, Any]]:
        productos = self.registro.list_productos()[: self.settings.max_productos]
        return [self.run_producto(p) for p in productos]

    def _render(self, producto: Producto, resultado: CicloResultado | None,
                error: str | None) -> dict[str, Any]:
        if error or resultado is None:
            return {"producto": producto.nombre, "error": error,
                    "business_card": None, "evidence_pack": None}
        diag = resultado.registros.get("diagnose", {})
        decide = resultado.registros.get("decide", {})
        observe = resultado.registros.get("observe", {})
        business_card = {
            "producto": producto.nombre,
            "estado_operativo": diag.get("estado_operativo"),
            "estado_comercial": diag.get("estado_comercial"),
            "confianza": diag.get("confianza"),
            "problema_principal": (diag.get("anomalias") or ["—"])[0],
            "metrica_principal": diag.get("metrica_principal"),
            "decision_recomendada": decide.get("decision_recomendada"),
            "riesgo": "medio" if decide.get("requiere_aprobacion") else "bajo",
            "nivel_autonomia": decide.get("nivel_autonomia"),
            "requiere_aprobacion": decide.get("requiere_aprobacion"),
            "proxima_accion": decide.get("decision_recomendada"),
        }
        evidence_pack = {
            "resumen_ejecutivo": (f"{producto.nombre}: operativo={diag.get('estado_operativo')}, "
                                  f"comercial={diag.get('estado_comercial')}."),
            "afirmaciones": diag.get("afirmaciones", []),
            "kpis": diag.get("kpis", {}),
            "hipotesis": decide.get("hipotesis"),
            "plan_de_accion": {
                "metrica_objetivo": decide.get("metrica_objetivo"),
                "criterio_exito": decide.get("criterio_exito"),
                "ventana_medicion": decide.get("ventana_medicion"),
            },
            "fuentes_consultadas": observe.get("fuentes_consultadas", []),
            "fuentes_inaccesibles": observe.get("fuentes_inaccesibles", []),
            "decision_ledger_ref": decide.get("decision_id"),
            "registro_canonico_ref": producto.producto_id,
            "aprendizajes_consultados": decide.get("aprendizajes_consultados", 0),
            "detenido_en": resultado.detenido_en,
            "siguiente_movimiento": "HOLD (pendiente de aprobación humana)",
        }
        return {"producto": producto.nombre, "error": None,
                "business_card": business_card, "evidence_pack": evidence_pack}
