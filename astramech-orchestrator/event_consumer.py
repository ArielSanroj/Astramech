"""RabbitMQ event consumer for Astramech orchestrator."""

from __future__ import annotations

import json
from typing import Any

import pika
from loguru import logger


class EventConsumer:
    """RabbitMQ event consumer."""

    def __init__(self, supervisor, rabbitmq_url: str, topics: Any):
        self.supervisor = supervisor
        self.rabbitmq_url = rabbitmq_url
        self.topics = topics
        self.connection = None
        self.channel = None

    def connect(self) -> None:
        """Connect to RabbitMQ and declare queues."""
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            self.channel = self.connection.channel()

            self.channel.queue_declare(queue=self.topics.buyer_signal_detected, durable=True)
            self.channel.queue_declare(queue=self.topics.burnout_risk, durable=True)

            logger.info("✅ Connected to RabbitMQ")
        except Exception as exc:
            logger.error(f"❌ Failed to connect to RabbitMQ: {exc}")
            raise

    def start_consuming(self) -> None:
        """Start consuming events."""
        self.channel.basic_consume(
            queue=self.topics.buyer_signal_detected,
            on_message_callback=self._on_buyer_signal,
            auto_ack=True,
        )

        self.channel.basic_consume(
            queue=self.topics.burnout_risk,
            on_message_callback=self._on_burnout_risk,
            auto_ack=True,
        )

        logger.info("🎧 Starting to consume events...")
        logger.info(f"   Listening to: {self.topics.buyer_signal_detected}")
        logger.info(f"   Listening to: {self.topics.burnout_risk}")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("🛑 Stopping consumer...")
            self.channel.stop_consuming()
            self.connection.close()

    def _on_buyer_signal(self, ch, method, properties, body) -> None:
        """Handle buyer_signal.detected event."""
        try:
            data = json.loads(body)
            self.supervisor.handle_buyer_signal(data)
        except Exception as exc:
            logger.error(f"❌ Error handling buyer signal: {exc}")

    def _on_burnout_risk(self, ch, method, properties, body) -> None:
        """Handle burnout.risk.detected event."""
        try:
            data = json.loads(body)
            self.supervisor.handle_burnout_risk(data)
        except Exception as exc:
            logger.error(f"❌ Error handling burnout risk: {exc}")
