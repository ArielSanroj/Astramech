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
    x_comment_posted: str = "x.comment.posted"
    x_engagement_detected: str = "x.engagement.detected"
    # Superloop — eventos de fase del loop de negocio (ver SUPERLOOP.md §6).
    decision_observation_recorded: str = "decision.observation.recorded"
    decision_diagnosed: str = "decision.diagnosed"
    decision_proposed: str = "decision.proposed"
    decision_approved: str = "decision.approved"
    decision_rejected: str = "decision.rejected"
    decision_executed: str = "decision.executed"
    decision_verified: str = "decision.verified"
    decision_learned: str = "decision.learned"
