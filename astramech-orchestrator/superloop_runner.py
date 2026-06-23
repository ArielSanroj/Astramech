"""
SuperloopRunner (SUPERLOOP.md §6, §19.0) — corre el loop de negocio y publica eventos.

El estado vive en el Registro Canónico + Decision Ledger (única fuente de verdad, §19.0);
RabbitMQ es solo el spine de coordinación. Publica eventos decision.* en cada transición.
La conexión a RabbitMQ es perezosa y best-effort: si el broker no está, el loop igual
persiste su estado (no se pierde nada).
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


class SuperloopRunner:
    def __init__(self, facade=None, crew_dispatch=None):
        # facade inyectable para test; por defecto construye uno con DATABASE_URL.
        if facade is None:
            from superloop.facade import SuperloopFacade
            facade = SuperloopFacade()
        self.facade = facade
        if crew_dispatch is not None:
            self.facade.ejecutor._crew_dispatch = crew_dispatch

    def run_proposal_cycle(self, seed: bool = True) -> list[dict[str, Any]]:
        """OBSERVE→DIAGNOSE→DECIDE (se detiene en APPROVE). Publica decision.proposed."""
        if seed:
            self.facade.seed_productos_dominios()
        cards = self.facade.run_todos()
        from shared.events import Topics
        for c in cards:
            if c.get("error") is None and c.get("evidence_pack"):
                self._publish(Topics.decision_proposed, {
                    "producto": c["producto"],
                    "decision_ledger_ref": c["evidence_pack"].get("decision_ledger_ref"),
                    "requiere_aprobacion": c["business_card"].get("requiere_aprobacion"),
                })
        return cards

    def close_approved(self) -> list[dict[str, Any]]:
        """ORCHESTRATE→VERIFY→LEARN sobre aprobadas. Publica executed/verified/learned."""
        from shared.events import Topics
        salidas = self.facade.resume_aprobados()
        for s in salidas:
            if s.get("ok"):
                self._publish(Topics.decision_executed, {"decision_id": s["decision_id"]})
                self._publish(Topics.decision_verified, {"decision_id": s["decision_id"]})
                self._publish(Topics.decision_learned, {
                    "decision_id": s["decision_id"],
                    "siguiente_movimiento": s.get("siguiente_movimiento"),
                })
        return salidas

    def _publish(self, routing_key: str, data: dict[str, Any]) -> None:
        try:
            import pika
            conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            ch = conn.channel()
            ch.basic_publish(exchange="", routing_key=routing_key, body=json.dumps(data))
            conn.close()
            logger.info("📤 Superloop event: %s", routing_key)
        except Exception as exc:
            logger.warning("Superloop event %s no publicado (broker?): %s", routing_key, exc)
