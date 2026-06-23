"""Memory integration for dynamic agent tool."""

from __future__ import annotations


def store_in_memory(report: str, analysis_result: dict) -> None:
    try:
        from memory_setup import HybridMemorySystem

        memory_system = HybridMemorySystem()

        memory_system.store_memory(
            report,
            {
                "type": "diagnostic_report",
                "period": "2025",
                "agents_created": len(analysis_result['recommended_agents']),
                "inefficiencies_found": len(analysis_result['inefficiencies']),
            },
        )

        for agent in analysis_result['recommended_agents']:
            memory_system.store_memory(
                f"Agent: {agent['type']} - Goal: {agent['goal']}",
                {
                    "type": "agent_configuration",
                    "agent_type": agent['type'],
                    "priority": agent.get('priority', 'medium'),
                },
            )

        print("💾 Stored analysis and agent configurations in memory system")
    except Exception as exc:
        print(f"⚠️ Memory storage failed: {exc}")
