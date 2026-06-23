#!/usr/bin/env python3
"""
Dynamic Agent Creator Tool

This tool generates specialized AI agent configurations based on identified 
inefficiencies using NVIDIA LLM. It creates detailed agent profiles with
roles, goals, backstories, and capabilities tailored to specific business needs.
"""

import yaml
import os
from typing import Dict, List, Any
from datetime import datetime

try:
    from crewai.tools import BaseTool
except ImportError:
    class BaseTool:  # type: ignore[override]
        name: str = ""
        description: str = ""

        def __call__(self, *args, **kwargs):
            return self._run(*args, **kwargs)

        def _run(self, *args, **kwargs):
            raise NotImplementedError

from tools.dynamic_agent_tool_memory import store_in_memory
from tools.dynamic_agent_tool_report import generate_diagnostic_report
from tools.dynamic_agent_tool_utils import (
    generate_capabilities,
    generate_success_metrics,
    get_fallback_backstory,
)

class DynamicAgentCreator(BaseTool):
    name: str = "Dynamic Agent Creator"
    description: str = "Generates specialized AI agent configurations based on identified inefficiencies using NVIDIA LLM."

    def _run(self, analysis_result: dict) -> str:
        """
        Generate specialized AI agent configurations based on analysis results.
        
        Args:
            analysis_result: Dictionary containing KPIs, inefficiencies, and recommended agents
        
        Returns:
            String containing the generated report and agent configurations
        """
        
        try:
            # Initialize Ollama LLM
            from langchain_ollama import ChatOllama
            
            model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            # For langchain-ollama, we don't need the ollama/ prefix
            
            llm = ChatOllama(
                model=model_name,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.7
            )
            
            print("🤖 Generating specialized AI agents using Ollama LLM...")
            
            # Generate agent configurations
            agent_configs = {}
            agent_descriptions = []
            
            for agent in analysis_result['recommended_agents']:
                agent_type = agent['type']
                goal = agent['goal']
                priority = agent.get('priority', 'medium')
                focus_areas = agent.get('focus_areas', [])
                
                print(f"   Creating {agent_type}...")
                
                # Generate detailed backstory using Ollama LLM
                backstory = self._generate_agent_backstory(llm, agent_type, goal, priority, focus_areas)
                
                # Create agent configuration
                agent_key = agent_type.lower().replace(' ', '_').replace('-', '_')
                agent_configs[agent_key] = {
                    'role': agent_type,
                    'goal': goal,
                    'backstory': backstory,
                    'priority': priority,
                    'focus_areas': focus_areas,
                    'capabilities': generate_capabilities(agent_type, focus_areas),
                    'success_metrics': generate_success_metrics(agent_type),
                    'allow_delegation': True,
                    'verbose': True,
                    'memory': True,
                    'created_at': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                agent_descriptions.append({
                    'type': agent_type,
                    'goal': goal,
                    'priority': priority,
                    'capabilities': agent_configs[agent_key]['capabilities']
                })
            
            # Save to dynamic_agents.yaml
            self._save_agent_configs(agent_configs)
            
            # Generate comprehensive report
            report = generate_diagnostic_report(analysis_result, agent_descriptions)
            
            # Store in memory system
            store_in_memory(report, analysis_result)
            
            print(f"✅ Successfully created {len(agent_configs)} specialized agents")
            return report
            
        except Exception as e:
            print(f"❌ Error creating agents: {str(e)}")
            # Fallback to basic agent creation without LLM
            return self._create_fallback_agents(analysis_result)

    def _generate_agent_backstory(self, llm, agent_type: str, goal: str, priority: str, focus_areas: List[str]) -> str:
        """Generate detailed backstory using Ollama LLM."""
        
        focus_areas_str = ", ".join(focus_areas) if focus_areas else "general business optimization"
        
        prompt = f"""
        Create a detailed backstory for an AI agent with the following specifications:
        
        Agent Type: {agent_type}
        Primary Goal: {goal}
        Priority Level: {priority}
        Focus Areas: {focus_areas_str}
        
        The backstory should include:
        1. Professional background and expertise
        2. Personality traits and working style
        3. Specific skills and methodologies
        4. Experience with similar business challenges
        5. Approach to problem-solving
        6. Communication style and preferences
        
        Make it engaging, professional, and specific to the agent's role.
        Keep it concise but detailed (2-3 paragraphs).
        """
        
        try:
            response = llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"⚠️ LLM generation failed for {agent_type}: {str(e)}")
            return get_fallback_backstory(agent_type, goal)


    def _save_agent_configs(self, agent_configs: Dict[str, Any]) -> None:
        """Save agent configurations to YAML file."""
        
        # Ensure config directory exists
        os.makedirs('config', exist_ok=True)
        
        # Save to dynamic_agents.yaml
        with open('config/dynamic_agents.yaml', 'w') as f:
            yaml.dump(agent_configs, f, default_flow_style=False, indent=2)
        
        print(f"💾 Saved {len(agent_configs)} agent configurations to config/dynamic_agents.yaml")

    def _create_fallback_agents(self, analysis_result: dict) -> str:
        """Create basic agents when LLM is unavailable."""
        
        print("⚠️ Using fallback agent creation (LLM unavailable)")
        
        agent_configs = {}
        for agent in analysis_result['recommended_agents']:
            agent_key = agent['type'].lower().replace(' ', '_').replace('-', '_')
            agent_configs[agent_key] = {
                'role': agent['type'],
                'goal': agent['goal'],
                'backstory': f"Specialized AI agent focused on {agent['type'].lower()} to achieve: {agent['goal']}",
                'priority': agent.get('priority', 'medium'),
                'focus_areas': agent.get('focus_areas', []),
                'capabilities': ['Business analysis', 'Optimization strategies', 'Performance improvement'],
                'success_metrics': ['KPI improvement', 'Goal achievement', 'Performance gains'],
                'allow_delegation': True,
                'verbose': True,
                'memory': True,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
        
        self._save_agent_configs(agent_configs)
        
        return f"Created {len(agent_configs)} fallback agents due to LLM unavailability."
