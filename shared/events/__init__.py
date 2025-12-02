"""Event/topic definitions for RabbitMQ."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Topics:
    finance_invoice_received: str = "finance.invoice.received"
    finance_invoice_processed: str = "finance.invoice.processed"
    lead_created: str = "lead.created"
    buyer_signal_detected: str = "buyer_signal.detected"
    call_completed: str = "call.completed"
    burnout_risk: str = "burnout.risk.detected"
