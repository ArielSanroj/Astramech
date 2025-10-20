#!/usr/bin/env python3
"""
Dynamic Agent Creator Tool

This tool generates specialized AI agent configurations based on identified 
inefficiencies using NVIDIA LLM. It creates detailed agent profiles with
roles, goals, backstories, and capabilities tailored to specific business needs.
"""

from crewai.tools import BaseTool
import yaml
import os
import json
from typing import Dict, List, Any
from datetime import datetime

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
                    'capabilities': self._generate_capabilities(agent_type, focus_areas),
                    'success_metrics': self._generate_success_metrics(agent_type, goal),
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
            report = self._generate_diagnostic_report(analysis_result, agent_descriptions)
            
            # Store in memory system
            self._store_in_memory(report, analysis_result)
            
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
            return self._get_fallback_backstory(agent_type, goal)

    def _get_fallback_backstory(self, agent_type: str, goal: str) -> str:
        """Fallback backstory when LLM is unavailable."""
        
        backstories = {
            'Pricing Optimizer': f"Expert pricing strategist with 10+ years of experience in dynamic pricing, market analysis, and revenue optimization. Specializes in data-driven pricing decisions and competitive positioning. Known for analytical rigor and creative solutions to pricing challenges. Goal: {goal}",
            
            'Operations Optimizer': f"Process improvement specialist with extensive experience in lean methodologies, Six Sigma, and operational excellence. Expert in identifying bottlenecks, streamlining workflows, and implementing efficiency improvements. Known for systematic approach and measurable results. Goal: {goal}",
            
            'Financial Optimizer': f"Strategic financial analyst with deep expertise in P&L optimization, cost management, and profitability improvement. Specializes in financial modeling, scenario analysis, and strategic planning. Known for data-driven insights and actionable recommendations. Goal: {goal}",
            
            'Cost Management Agent': f"Cost reduction specialist with proven track record in expense optimization and budget management. Expert in identifying cost-saving opportunities, negotiating contracts, and implementing cost controls. Known for attention to detail and persistent optimization. Goal: {goal}",
            
            'Supply Chain Optimizer': f"Supply chain expert with extensive experience in procurement, vendor management, and logistics optimization. Specializes in reducing COGS, improving supplier relationships, and streamlining supply chain processes. Known for strategic thinking and operational excellence. Goal: {goal}",
            
            'Sales Growth Agent': f"Revenue growth specialist with proven success in market expansion, sales optimization, and customer acquisition. Expert in sales strategy, market analysis, and growth planning. Known for innovative approaches and results-driven execution. Goal: {goal}",
            
            'Productivity Optimizer': f"Workforce productivity expert with deep understanding of human resources, performance management, and organizational development. Specializes in employee engagement, retention strategies, and productivity improvement. Known for people-focused solutions and sustainable improvements. Goal: {goal}",
            
            'Process Optimization Agent': f"Process improvement expert with extensive experience in operational efficiency and resource optimization. Specializes in workflow analysis, automation, and continuous improvement. Known for systematic approach and measurable results. Goal: {goal}",
            
            'HR Retention Specialist': f"Human resources specialist with deep expertise in employee retention, engagement, and talent management. Expert in retention strategies, employee satisfaction, and organizational culture. Known for empathetic approach and data-driven HR solutions. Goal: {goal}",
            
            'Cash Flow Manager': f"Financial management expert with extensive experience in cash flow optimization, working capital management, and financial planning. Specializes in liquidity management, expense control, and revenue acceleration. Known for strategic financial thinking and crisis management. Goal: {goal}",
            
            'Growth Strategy Agent': f"Strategic growth consultant with proven success in market expansion, business development, and revenue growth. Expert in growth strategy, market analysis, and competitive positioning. Known for innovative thinking and execution excellence. Goal: {goal}"
        }
        
        return backstories.get(agent_type, f"Experienced business optimization specialist with expertise in {agent_type.lower()}. Goal: {goal}")

    def _generate_capabilities(self, agent_type: str, focus_areas: List[str]) -> List[str]:
        """Generate agent capabilities based on type and focus areas."""
        
        capability_templates = {
            'Pricing Optimizer': [
                'Dynamic pricing analysis and optimization',
                'Market research and competitive analysis',
                'Price elasticity modeling',
                'Revenue optimization strategies',
                'Customer segmentation for pricing'
            ],
            'Operations Optimizer': [
                'Process mapping and analysis',
                'Lean methodology implementation',
                'Workflow optimization',
                'Resource allocation optimization',
                'Performance metrics development'
            ],
            'Financial Optimizer': [
                'Financial modeling and analysis',
                'Cost-benefit analysis',
                'Profitability optimization',
                'Budget planning and control',
                'Financial forecasting'
            ],
            'Cost Management Agent': [
                'Expense analysis and optimization',
                'Vendor negotiation and management',
                'Budget control and monitoring',
                'Cost reduction strategies',
                'Spend analysis and reporting'
            ],
            'Supply Chain Optimizer': [
                'Supplier relationship management',
                'Procurement optimization',
                'Inventory management',
                'Logistics optimization',
                'Vendor performance analysis'
            ],
            'Sales Growth Agent': [
                'Market analysis and research',
                'Sales strategy development',
                'Customer acquisition strategies',
                'Revenue growth planning',
                'Competitive analysis'
            ],
            'Productivity Optimizer': [
                'Workforce analysis and optimization',
                'Performance management systems',
                'Employee engagement strategies',
                'Training and development programs',
                'Productivity measurement and improvement'
            ],
            'Process Optimization Agent': [
                'Process mapping and documentation',
                'Workflow analysis and improvement',
                'Automation opportunities identification',
                'Efficiency measurement and optimization',
                'Continuous improvement implementation'
            ],
            'HR Retention Specialist': [
                'Employee satisfaction analysis',
                'Retention strategy development',
                'Engagement program design',
                'Exit interview analysis',
                'Talent management optimization'
            ],
            'Cash Flow Manager': [
                'Cash flow analysis and forecasting',
                'Working capital optimization',
                'Expense reduction strategies',
                'Revenue acceleration techniques',
                'Financial crisis management'
            ],
            'Growth Strategy Agent': [
                'Market opportunity analysis',
                'Growth strategy development',
                'Business model optimization',
                'Market expansion planning',
                'Competitive positioning strategies'
            ]
        }
        
        base_capabilities = capability_templates.get(agent_type, [
            'Business analysis and optimization',
            'Data-driven decision making',
            'Strategic planning and execution',
            'Performance measurement and improvement',
            'Cross-functional collaboration'
        ])
        
        # Add focus area specific capabilities
        focus_capabilities = []
        for area in focus_areas:
            if 'Revenue' in area:
                focus_capabilities.append(f'{area} optimization and analysis')
            elif 'Margin' in area:
                focus_capabilities.append(f'{area} improvement strategies')
            elif 'Growth' in area:
                focus_capabilities.append(f'{area} acceleration techniques')
            else:
                focus_capabilities.append(f'{area} management and optimization')
        
        return base_capabilities + focus_capabilities

    def _generate_success_metrics(self, agent_type: str, goal: str) -> List[str]:
        """Generate success metrics for the agent."""
        
        metrics_templates = {
            'Pricing Optimizer': [
                'Gross margin improvement percentage',
                'Revenue growth rate',
                'Price optimization ROI',
                'Customer acquisition cost reduction'
            ],
            'Operations Optimizer': [
                'Operating margin improvement',
                'Process efficiency gains',
                'Cost reduction percentage',
                'Time-to-completion improvements'
            ],
            'Financial Optimizer': [
                'Net margin improvement',
                'ROI on optimization initiatives',
                'Cash flow improvement',
                'Profitability growth rate'
            ],
            'Cost Management Agent': [
                'Expense reduction percentage',
                'Cost savings achieved',
                'Budget variance improvement',
                'Spend efficiency gains'
            ],
            'Supply Chain Optimizer': [
                'COGS reduction percentage',
                'Supplier performance improvements',
                'Inventory turnover optimization',
                'Procurement cost savings'
            ],
            'Sales Growth Agent': [
                'Revenue growth rate',
                'Market share increase',
                'Customer acquisition rate',
                'Sales conversion improvements'
            ],
            'Productivity Optimizer': [
                'Revenue per employee improvement',
                'Employee satisfaction scores',
                'Productivity metrics gains',
                'Retention rate improvements'
            ],
            'Process Optimization Agent': [
                'Process efficiency improvements',
                'Automation implementation rate',
                'Resource utilization optimization',
                'Quality metrics improvements'
            ],
            'HR Retention Specialist': [
                'Employee retention rate',
                'Turnover reduction percentage',
                'Employee satisfaction scores',
                'Engagement metrics improvements'
            ],
            'Cash Flow Manager': [
                'Cash flow improvement percentage',
                'Working capital optimization',
                'Liquidity ratio improvements',
                'Financial stability metrics'
            ],
            'Growth Strategy Agent': [
                'Revenue growth acceleration',
                'Market expansion success rate',
                'New customer acquisition',
                'Market share growth'
            ]
        }
        
        return metrics_templates.get(agent_type, [
            'KPI improvement percentage',
            'Goal achievement rate',
            'Performance optimization gains',
            'Business impact metrics'
        ])

    def _save_agent_configs(self, agent_configs: Dict[str, Any]) -> None:
        """Save agent configurations to YAML file."""
        
        # Ensure config directory exists
        os.makedirs('config', exist_ok=True)
        
        # Save to dynamic_agents.yaml
        with open('config/dynamic_agents.yaml', 'w') as f:
            yaml.dump(agent_configs, f, default_flow_style=False, indent=2)
        
        print(f"💾 Saved {len(agent_configs)} agent configurations to config/dynamic_agents.yaml")

    def _generate_diagnostic_report(self, analysis_result: dict, agent_descriptions: List[dict]) -> str:
        """Generate comprehensive diagnostic report."""
        
        report = f"""# 🚀 Company Efficiency Diagnostic Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Executive Summary
{analysis_result['data_confirmation']}

**Key Findings:**
- Total Inefficiencies: {analysis_result['summary']['total_inefficiencies']}
- Critical Issues: {analysis_result['summary']['critical_issues']}
- Warning Issues: {analysis_result['summary']['warning_issues']}
- AI Agents Deployed: {analysis_result['summary']['agents_needed']}

## 📈 KPI Analysis

| KPI | Current Value | Benchmark | Status |
|-----|---------------|-----------|--------|
"""
        
        for kpi, value in analysis_result['kpis'].items():
            benchmark = analysis_result['benchmarks'].get(kpi, 'N/A')
            if isinstance(value, (int, float)):
                if value < float(str(benchmark).replace('$', '').replace('%', '').split('-')[0]) * 0.8:
                    status = "🔴 Critical"
                elif value < float(str(benchmark).replace('$', '').replace('%', '').split('-')[0]) * 0.9:
                    status = "🟡 Warning"
                else:
                    status = "🟢 Good"
            else:
                status = "⚪ N/A"
            
            report += f"| {kpi} | {value:.1f}% | {benchmark} | {status} |\n"
        
        report += f"""
## ⚠️ Identified Inefficiencies

"""
        
        for i, inefficiency in enumerate(analysis_result['inefficiencies'], 1):
            severity_emoji = "🔴" if inefficiency['severity'] == 'critical' else "🟡"
            report += f"""
### {i}. {inefficiency['kpi_name']} {severity_emoji}
- **Current**: {inefficiency['current_value']:.1f}%
- **Benchmark**: {inefficiency['benchmark']:.1f}%
- **Severity**: {inefficiency['severity'].upper()}
- **Issue**: {inefficiency['description']}
- **Root Cause**: {inefficiency['root_cause']}
- **Recommended Agent**: {inefficiency['recommended_agent']}
"""
        
        report += f"""
## 🤖 Generated Specialized AI Agents

"""
        
        for i, agent in enumerate(agent_descriptions, 1):
            priority_emoji = "🔴" if agent['priority'] == 'critical' else "🟡" if agent['priority'] == 'high' else "🟢"
            report += f"""
### {i}. {agent['type']} {priority_emoji}
- **Goal**: {agent['goal']}
- **Priority**: {agent['priority'].upper()}
- **Capabilities**: {', '.join(agent['capabilities'][:3])}...
"""
        
        report += f"""
## 🎯 Implementation Roadmap

### Immediate Actions (0-30 days)
1. Deploy critical priority agents first
2. Set up monitoring and tracking systems
3. Establish baseline metrics for each agent
4. Create cross-functional optimization teams

### Short-term Goals (1-3 months)
1. Implement agent-specific optimization strategies
2. Monitor KPI improvements and adjust approaches
3. Train teams on new processes and systems
4. Measure and report on agent performance

### Long-term Objectives (3-12 months)
1. Achieve industry benchmark performance
2. Scale successful optimization strategies
3. Develop competitive advantages
4. Implement continuous improvement processes

## 📋 Next Steps
1. Review and approve generated agent configurations
2. Deploy agents via the multi-agent architecture
3. Provide additional data to refine agent tasks
4. Monitor progress and adjust strategies as needed

---
*This report was generated by the Company Efficiency Optimizer using advanced AI analysis.*
"""
        
        return report

    def _store_in_memory(self, report: str, analysis_result: dict) -> None:
        """Store report and analysis in memory system."""
        
        try:
            from memory_setup import HybridMemorySystem
            memory_system = HybridMemorySystem()
            
            # Store the full report
            memory_system.store_memory(
                report, 
                {
                    "type": "diagnostic_report",
                    "period": "2025",
                    "agents_created": len(analysis_result['recommended_agents']),
                    "inefficiencies_found": len(analysis_result['inefficiencies'])
                }
            )
            
            # Store individual agent configurations
            for agent in analysis_result['recommended_agents']:
                memory_system.store_memory(
                    f"Agent: {agent['type']} - Goal: {agent['goal']}",
                    {
                        "type": "agent_configuration",
                        "agent_type": agent['type'],
                        "priority": agent.get('priority', 'medium')
                    }
                )
            
            print("💾 Stored analysis and agent configurations in memory system")
            
        except Exception as e:
            print(f"⚠️ Memory storage failed: {str(e)}")

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