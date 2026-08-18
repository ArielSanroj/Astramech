"""
Superloop use cases (SUPERLOOP.md §4.2 puertos inbound) — MVP: OBSERVE, DIAGNOSE, DECIDE.

Cada use case es un callable (producto, contexto) -> registro_de_fase (dict plano que
valida phase_done). El contexto acumula entidades entre fases.
"""
from __future__ import annotations

from typing import Any

from .ports import (
    FuenteDeDatos, RegistroCanonico, DecisionLedger,
    ProveedorDeTiempo, ProveedorDeIdentidad,
)
from ..domain import rules, debate
from ..domain.entities import (
    Producto, Snapshot, Diagnostico, DecisionRecomendada, Afirmacion, RegistroCanonicoEntry,
)
from ..domain.enums import (
    EtiquetaAfirmacion, EstadoComercial, NivelAutonomia, EstadoAprobacion,
)


class ObservarProducto:
    def __init__(self, fuente: FuenteDeDatos):
        self.fuente = fuente

    def __call__(self, producto: Producto, contexto: dict[str, Any]) -> dict[str, Any]:
        snapshot = self.fuente.observar(producto)
        contexto["snapshot"] = snapshot
        return {
            "snapshot_fecha": snapshot.fecha,
            "fuentes_consultadas": snapshot.fuentes_consultadas,
            "fuentes_inaccesibles": snapshot.fuentes_inaccesibles,
            "datos_faltantes": snapshot.datos_faltantes,
            "afirmaciones": [a.to_dict() for a in snapshot.afirmaciones],
            "kpis": snapshot.kpis,
        }


class DiagnosticarProducto:
    def __init__(self, registro: RegistroCanonico):
        self.registro = registro

    def __call__(self, producto: Producto, contexto: dict[str, Any]) -> dict[str, Any]:
        snapshot: Snapshot = contexto["snapshot"]
        senales = dict(snapshot.kpis)

        estado_op, conf_op = rules.clasificar_estado_operativo(senales)
        estado_com, conf_com = rules.clasificar_estado_comercial(senales)
        anomalias = rules.detectar_anomalias(senales)
        confianza = round((conf_op + conf_com) / 2, 2)
        metrica_principal = senales.get("metrica_principal") or (
            producto.expected_business_outcome.get("metrica_norte") or "kpi_principal"
        )

        # §19.2 — DIAGNOSE como debate (hipótesis rivales).
        hipotesis = debate.debatir(senales, snapshot.datos_faltantes)
        contexto["debate_opciones"] = debate.opciones_consideradas(hipotesis)

        afirmaciones: list[Afirmacion] = list(snapshot.afirmaciones)
        afirmaciones.append(Afirmacion(
            f"Estado operativo {estado_op.value} (confianza {conf_op}).",
            EtiquetaAfirmacion.INFERENCIA))
        afirmaciones.append(Afirmacion(
            f"Estado comercial {estado_com.value} (confianza {conf_com}).",
            EtiquetaAfirmacion.INFERENCIA))
        for a in anomalias:
            afirmaciones.append(Afirmacion(f"Anomalía: {a}.", EtiquetaAfirmacion.HECHO))
        afirmaciones.extend(debate.afirmaciones_del_debate(hipotesis))
        if snapshot.datos_faltantes:
            afirmaciones.append(Afirmacion(
                f"Datos faltantes: {', '.join(snapshot.datos_faltantes)}.",
                EtiquetaAfirmacion.PREGUNTA))

        contexto["diagnostico"] = Diagnostico(
            producto_id=producto.producto_id, estado_operativo=estado_op,
            estado_comercial=estado_com, confianza=confianza,
            metrica_principal=metrica_principal, kpis=senales,
            anomalias=anomalias, afirmaciones=afirmaciones,
        )
        self.registro.upsert(RegistroCanonicoEntry(
            producto_id=producto.producto_id, nombre=producto.nombre, tipo=producto.tipo,
            estado_operativo=estado_op.value, estado_comercial=estado_com.value,
            confianza_estado=confianza, metrica_principal=metrica_principal,
            kpis=senales, afirmaciones=[a.to_dict() for a in afirmaciones],
        ))
        return {
            "estado_operativo": estado_op.value,
            "estado_comercial": estado_com.value,
            "confianza": confianza,
            "metrica_principal": metrica_principal,
            "anomalias": anomalias,
            "afirmaciones": [a.to_dict() for a in afirmaciones],
            "kpis": senales,
        }


_NIVEL_POR_ESTADO = {
    EstadoComercial.REACTIVAR: NivelAutonomia.EXTERNAL_ACTION,
    EstadoComercial.ALTA_OPORTUNIDAD: NivelAutonomia.EXTERNAL_ACTION,
    EstadoComercial.DEFENDER: NivelAutonomia.EXTERNAL_ACTION,
    EstadoComercial.CERRAR: NivelAutonomia.BUSINESS_CRITICAL,
    EstadoComercial.OPTIMIZAR: NivelAutonomia.DRAFT,
    EstadoComercial.DESCONOCIDO: NivelAutonomia.READ_ONLY,
}


class DecidirProximaAccion:
    def __init__(self, registro: RegistroCanonico, ledger: DecisionLedger,
                 tiempo: ProveedorDeTiempo, identidad: ProveedorDeIdentidad):
        self.registro = registro
        self.ledger = ledger
        self.tiempo = tiempo
        self.identidad = identidad

    def __call__(self, producto: Producto, contexto: dict[str, Any]) -> dict[str, Any]:
        diag: Diagnostico = contexto["diagnostico"]
        # R8 — consultar aprendizaje previo ANTES de decidir.
        aprendizajes = self.ledger.ultimos_aprendizajes(producto.producto_id, limit=5)

        accion = rules.recomendar_siguiente_movimiento(diag.estado_operativo, diag.estado_comercial)
        nivel = _NIVEL_POR_ESTADO.get(diag.estado_comercial, NivelAutonomia.DRAFT)

        decision = DecisionRecomendada(
            decision_id=self.identidad.nuevo_id("dec"),
            producto_id=producto.producto_id, fecha=self.tiempo.ahora(),
            fase_origen="decide", decision_recomendada=accion,
            hipotesis=self._hipotesis(diag.estado_comercial),
            metrica_objetivo=diag.metrica_principal or "kpi_principal",
            criterio_exito=self._criterio(diag.estado_comercial),
            ventana_medicion="14 días", nivel_autonomia=nivel,
            segmento=producto.cliente_ideal, impacto_esperado="medio",
            esfuerzo_estimado="bajo",
            riesgo="medio" if nivel.requiere_aprobacion_humana else "bajo",
            razonamiento=(f"operativo={diag.estado_operativo.value}, "
                          f"comercial={diag.estado_comercial.value}. "
                          f"{len(aprendizajes)} aprendizaje(s) previo(s) consultado(s) (R8)."),
            opciones_consideradas=contexto.get("debate_opciones") or [
                {"opcion": accion, "elegida": True}, {"opcion": "HOLD", "elegida": False}],
            datos_usados={"kpis": diag.kpis, "anomalias": diag.anomalias},
            afirmaciones=diag.afirmaciones,
            estado_aprobacion=EstadoAprobacion.PENDIENTE,
        )
        contexto["decision"] = decision
        self.ledger.registrar(decision)
        self.registro.upsert(RegistroCanonicoEntry(
            producto_id=producto.producto_id, nombre=producto.nombre, tipo=producto.tipo,
            estado_operativo=diag.estado_operativo.value,
            estado_comercial=diag.estado_comercial.value,
            confianza_estado=diag.confianza, metrica_principal=diag.metrica_principal,
            kpis=diag.kpis, afirmaciones=[a.to_dict() for a in diag.afirmaciones],
            hipotesis_vigente=decision.hipotesis, decision_recomendada_ref=decision.decision_id,
            estado_aprobacion="pendiente", proxima_mejor_accion=accion,
        ))
        return {
            "decision_id": decision.decision_id,
            "decision_recomendada": accion,
            "hipotesis": decision.hipotesis,
            "metrica_objetivo": decision.metrica_objetivo,
            "criterio_exito": decision.criterio_exito,
            "ventana_medicion": decision.ventana_medicion,
            "nivel_autonomia": int(nivel.value),
            "requiere_aprobacion": decision.requiere_aprobacion,
            "aprendizajes_consultados": len(aprendizajes),
        }

    @staticmethod
    def _hipotesis(com: EstadoComercial) -> str:
        return {
            EstadoComercial.REACTIVAR: "Una reactivación segmentada recupera uso dormido.",
            EstadoComercial.ALTA_OPORTUNIDAD: "El segmento con demanda convierte sobre baseline.",
            EstadoComercial.OPTIMIZAR: "Ajustar la palanca operativa sube la eficiencia sin romper nada.",
        }.get(com, "Recolectar más señal reduce la incertidumbre antes de invertir.")

    @staticmethod
    def _criterio(com: EstadoComercial) -> str:
        return {
            EstadoComercial.REACTIVAR: "+10% reactivación en 14 días",
            EstadoComercial.ALTA_OPORTUNIDAD: "5 oportunidades calificadas en 30 días",
            EstadoComercial.OPTIMIZAR: "+15% en el KPI objetivo vs baseline",
        }.get(com, "Confianza de clasificación >= 0.6")
