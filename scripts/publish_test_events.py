#!/usr/bin/env python3
"""
Utility script to publish test events to RabbitMQ
Useful for testing the orchestrator workflows
"""
import os
import json
import sys
import pika
from datetime import datetime

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
from events import Topics

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def publish_buyer_signal(lead_id: str = "lead_123", company_id: str = "company_456", strength: str = "high"):
    """Publish a test buyer_signal.detected event"""
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    
    event_data = {
        "lead_id": lead_id,
        "company_id": company_id,
        "strength": strength,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "test_script"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key=Topics.buyer_signal_detected,
        body=json.dumps(event_data)
    )
    
    connection.close()
    print(f"✅ Published buyer_signal.detected: {event_data}")


def publish_burnout_risk(team_id: str = "team_789", user_id: str = "user_101", burnout_probability: float = 0.65):
    """Publish a test burnout.risk.detected event"""
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    
    event_data = {
        "team_id": team_id,
        "user_id": user_id,
        "burnout_probability": burnout_probability,
        "archetype": "Avoidant",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "test_script"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key=Topics.burnout_risk,
        body=json.dumps(event_data)
    )
    
    connection.close()
    print(f"✅ Published burnout.risk.detected: {event_data}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Publish test events to RabbitMQ")
    parser.add_argument("event_type", choices=["buyer_signal", "burnout_risk"], help="Type of event to publish")
    parser.add_argument("--lead-id", default="lead_123", help="Lead ID for buyer signal")
    parser.add_argument("--company-id", default="company_456", help="Company ID for buyer signal")
    parser.add_argument("--strength", default="high", choices=["low", "medium", "high"], help="Signal strength")
    parser.add_argument("--team-id", default="team_789", help="Team ID for burnout risk")
    parser.add_argument("--user-id", default="user_101", help="User ID for burnout risk")
    parser.add_argument("--burnout-prob", type=float, default=0.65, help="Burnout probability (0-1)")
    
    args = parser.parse_args()
    
    try:
        if args.event_type == "buyer_signal":
            publish_buyer_signal(
                lead_id=args.lead_id,
                company_id=args.company_id,
                strength=args.strength
            )
        elif args.event_type == "burnout_risk":
            publish_burnout_risk(
                team_id=args.team_id,
                user_id=args.user_id,
                burnout_probability=args.burnout_prob
            )
    except Exception as e:
        print(f"❌ Error publishing event: {e}")
        sys.exit(1)

