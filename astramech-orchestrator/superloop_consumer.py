"""
SuperloopConsumer (SUPERLOOP.md §6.4→§6.5) — escucha decision.approved y cierra el loop.

Cuando un humano aprueba una decisión (vía el endpoint del gateway, que actualiza el
Ledger y publica decision.approved), este consumidor dispara ORCHESTRATE→VERIFY→LEARN
a través del SuperloopRunner. El gate humano NO se delega (R1/§19.5): el consumer solo
actúa sobre decisiones que YA tienen aprobador en el Ledger; el ejecutor es gated.

Arranque (junto al EventConsumer legacy, additivo):
    SuperloopConsumer(SuperloopRunner()).start()
"""
from __future__ import annotations

import json
import logging
import os

logger = logging.getLogger(__name__)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


class SuperloopConsumer:
    def __init__(self, runner=None, rabbitmq_url: str = RABBITMQ_URL):
        if runner is None:
            from superloop_runner import SuperloopRunner
            runner = SuperloopRunner()
        self.runner = runner
        self.url = rabbitmq_url

    def _on_message(self, ch, method, properties, body) -> None:
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}
        logger.info("🔔 decision.approved recibido: %s", payload.get("decision_id"))
        try:
            self.runner.close_approved()
        except Exception as exc:
            logger.error("Superloop close_approved falló: %s", exc)
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self) -> None:
        """Bloquea consumiendo decision.approved. Requiere RabbitMQ vivo."""
        import pika
        from shared.events import Topics
        conn = pika.BlockingConnection(pika.URLParameters(self.url))
        ch = conn.channel()
        queue = "superloop.decision.approved"
        ch.queue_declare(queue=queue, durable=True)
        ch.queue_bind(exchange="", queue=queue, routing_key=Topics.decision_approved)
        ch.basic_consume(queue=queue, on_message_callback=self._on_message)
        logger.info("🚀 SuperloopConsumer escuchando %s", Topics.decision_approved)
        ch.start_consuming()
