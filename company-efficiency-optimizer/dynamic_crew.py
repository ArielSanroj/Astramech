#!/usr/bin/env python3
"""
Dynamic Crew System

This system creates and manages dynamic AI agents based on company inefficiencies.
It loads generated agent configurations and creates a multi-agent crew for optimization.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime

from crewai import Agent, Crew, Process, Task
from crewai.tools import BaseTool
from typing import Type

class HumanInputTool(BaseTool):
    """Tool for getting human input during task execution."""
    
    name: str = "human_input"
    description: str = "Tool for getting human input during task execution"
    
    def _run(self, query: str) -> str:
        """Get human input for the given query."""
        try:
            return input(f"Human input needed: {query}\nYour response: ")
        except EOFError:
            # In non-interactive environments, provide a default response
            print(f"Human input needed: {query}")
            print("Using sample data for demonstration...")
            return "Using sample P&L data for analysis"
from tools.enhanced_kpi_tool import EnhancedKPITool
from tools.dynamic_agent_creator import DynamicAgentCreator
from nanobot_bridge import NanobotBridge

class DynamicCrewSystem:
    """Dynamic crew system that creates and manages specialized AI agents."""
    
    def __init__(self):
        """Initialize the dynamic crew system."""
        self.base_agents = {}
        self.dynamic_agents = {}
        self.tasks = []
        self.crew = None
        
        # Load base configuration
        self._load_base_config()
        
        # Initialize tools
        self.kpi_tool = EnhancedKPITool()
        self.agent_creator = DynamicAgentCreator()
        self.nanobot = NanobotBridge(configuration_path="nanobot.yaml")
    
    def _load_base_config(self):
        """Load base agent and task configurations."""
        try:
            # Load base agents
            with open('config/agents.yaml', 'r') as f:
                self.base_agents = yaml.safe_load(f)
            
            # Load tasks
            with open('config/tasks.yaml', 'r') as f:
                tasks_config = yaml.safe_load(f)
                self.tasks = list(tasks_config.keys())
            
            print("✅ Loaded base configuration")
            
        except Exception as e:
            print(f"⚠️ Error loading base config: {str(e)}")
            self.base_agents = {}
            self.tasks = []
    
    def _load_dynamic_agents(self) -> List[Agent]:
        """Load dynamically generated agents."""
        dynamic_agents = []
        
        try:
            if os.path.exists('config/dynamic_agents.yaml'):
                with open('config/dynamic_agents.yaml', 'r') as f:
                    dynamic_configs = yaml.safe_load(f)
                
                print(f"🤖 Loading {len(dynamic_configs)} dynamic agents...")
                
                for agent_key, config in dynamic_configs.items():
                    try:
                        # Create agent from configuration
                        agent = Agent(
                            role=config['role'],
                            goal=config['goal'],
                            backstory=config['backstory'],
                            allow_delegation=config.get('allow_delegation', True),
                            verbose=config.get('verbose', True),
                            memory=config.get('memory', True),
                            tools=[self.kpi_tool]  # Give agents access to KPI analysis
                        )
                        
                        dynamic_agents.append(agent)
                        print(f"   ✅ Loaded {config['role']}")
                        
                    except Exception as e:
                        print(f"   ❌ Failed to load {agent_key}: {str(e)}")
                
                self.dynamic_agents = {agent.role: agent for agent in dynamic_agents}
                print(f"✅ Successfully loaded {len(dynamic_agents)} dynamic agents")
                
            else:
                print("⚠️ No dynamic agents found. Run analysis first to generate agents.")
                
        except Exception as e:
            print(f"❌ Error loading dynamic agents: {str(e)}")
        
        return dynamic_agents
    
    def create_diagnostic_agent(self) -> Agent:
        """Create the diagnostic agent with enhanced capabilities."""
        try:
            from langchain_ollama import ChatOllama
            
            model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            # For langchain-ollama, we don't need the ollama/ prefix
            
            llm = ChatOllama(
                model=model_name,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.7
            )
            
            diagnostic_config = self.base_agents.get('diagnostic_agent', {})
            
            return Agent(
                role=diagnostic_config.get('role', 'Business Analyst expert in KPIs and inefficiencies'),
                goal=diagnostic_config.get('goal', 'Analyze financial statements and identify inefficiencies'),
                backstory=diagnostic_config.get('backstory', 'You are an analytical expert in business diagnostics'),
                llm=llm,
                memory=True,
                tools=[HumanInputTool(), self.kpi_tool, self.agent_creator],
                verbose=True
            )
            
        except Exception as e:
            print(f"⚠️ Error creating diagnostic agent: {str(e)}")
            # Fallback to basic agent
            return Agent(
                role="Business Analyst",
                goal="Analyze company performance and identify optimization opportunities",
                backstory="Expert in business analysis and optimization",
                memory=True,
                tools=[HumanInputTool(), self.kpi_tool, self.agent_creator],
                verbose=True
            )
    
    def create_dynamic_crew(self) -> Crew:
        """Create a crew with diagnostic agent and dynamic agents."""
        
        # Create diagnostic agent
        diagnostic_agent = self.create_diagnostic_agent()
        
        # Load dynamic agents
        dynamic_agents = self._load_dynamic_agents()
        
        # Create tasks for dynamic agents
        dynamic_tasks = self._create_dynamic_tasks(dynamic_agents)
        
        # Combine all agents and tasks
        all_agents = [diagnostic_agent] + dynamic_agents
        all_tasks = self._create_base_tasks() + dynamic_tasks
        
        # Create LLM for crew
        try:
            from langchain_ollama import ChatOllama
            
            model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            # For langchain-ollama, we don't need the ollama/ prefix
            
            llm = ChatOllama(
                model=model_name,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.7
            )
        except Exception as e:
            print(f"⚠️ Error creating Ollama LLM: {str(e)}")
            llm = None
        
        # Create crew
        self.crew = Crew(
            agents=all_agents,
            tasks=all_tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            llm=llm
        )
        
        print(f"🚀 Created dynamic crew with {len(all_agents)} agents and {len(all_tasks)} tasks")
        return self.crew
    
    def _create_base_tasks(self) -> List[Task]:
        """Create base tasks for the diagnostic agent."""
        
        base_tasks = []
        
        # Request P&L task
        base_tasks.append(Task(
            description="Prompt the user to upload or provide P&L data if not available. Once received, extract and clean the data.",
            expected_output="Cleaned P&L dataset in JSON format with standardized fields",
            agent=self.create_diagnostic_agent(),
            tools=[HumanInputTool()]
        ))
        
        # Dynamic agent creation task
        base_tasks.append(Task(
            description="Analyze P&L data, calculate KPIs, identify inefficiencies, and dynamically create specialized AI agents tailored to address specific business issues.",
            expected_output="Complete diagnostic report with KPI analysis, inefficiency detection, and dynamically generated AI agent configurations",
            agent=self.create_diagnostic_agent(),
            tools=[self.kpi_tool, self.agent_creator]
        ))
        
        return base_tasks
    
    def _create_dynamic_tasks(self, dynamic_agents: List[Agent]) -> List[Task]:
        """Create tasks for dynamic agents based on their roles."""
        
        dynamic_tasks = []
        
        for agent in dynamic_agents:
            role = agent.role.lower()
            
            if 'pricing' in role:
                task = Task(
                    description=f"Develop and implement pricing optimization strategies to improve gross margins and revenue growth. Focus on dynamic pricing, competitive analysis, and customer segmentation.",
                    expected_output="Comprehensive pricing strategy with implementation plan, expected outcomes, and success metrics",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            elif 'operations' in role:
                task = Task(
                    description=f"Analyze and optimize operational processes to reduce costs, improve efficiency, and enhance productivity. Focus on process mapping, bottleneck identification, and automation opportunities.",
                    expected_output="Operations optimization plan with process improvements, cost reduction strategies, and efficiency gains",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            elif 'financial' in role:
                task = Task(
                    description=f"Develop comprehensive financial optimization strategies to improve profitability, cash flow, and overall financial health. Focus on cost management, revenue optimization, and financial planning.",
                    expected_output="Financial optimization strategy with cost reduction plans, revenue enhancement strategies, and financial projections",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            elif 'cost' in role:
                task = Task(
                    description=f"Identify and implement cost reduction opportunities across all business areas. Focus on expense analysis, vendor management, and budget optimization.",
                    expected_output="Cost reduction action plan with specific savings targets, implementation timeline, and monitoring metrics",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            elif 'supply' in role or 'chain' in role:
                task = Task(
                    description=f"Optimize supply chain operations to reduce costs, improve efficiency, and enhance supplier relationships. Focus on procurement, inventory management, and logistics optimization.",
                    expected_output="Supply chain optimization strategy with procurement improvements, inventory optimization, and supplier relationship enhancements",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            elif 'sales' in role or 'growth' in role:
                task = Task(
                    description=f"Develop and execute sales growth strategies to increase revenue, market share, and customer acquisition. Focus on market analysis, sales optimization, and growth planning.",
                    expected_output="Sales growth strategy with market expansion plans, customer acquisition strategies, and revenue growth projections",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            elif 'productivity' in role or 'hr' in role:
                task = Task(
                    description=f"Enhance workforce productivity and employee engagement to improve performance and reduce turnover. Focus on talent management, retention strategies, and productivity optimization.",
                    expected_output="Workforce optimization strategy with productivity improvements, retention programs, and employee engagement initiatives",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            elif 'cash' in role or 'flow' in role:
                task = Task(
                    description=f"Optimize cash flow management and working capital to improve financial stability and liquidity. Focus on cash flow forecasting, working capital optimization, and financial planning.",
                    expected_output="Cash flow optimization plan with liquidity improvements, working capital strategies, and financial stability measures",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
                
            else:
                # Generic optimization task
                task = Task(
                    description=f"Develop and implement optimization strategies to address the specific business challenges identified in the analysis. Focus on measurable improvements and sustainable solutions.",
                    expected_output="Comprehensive optimization strategy with specific recommendations, implementation plan, and success metrics",
                    agent=agent,
                    tools=[self.kpi_tool]
                )
            
            dynamic_tasks.append(task)
        
        return dynamic_tasks
    
    def run_dynamic_analysis(self, pnl_data: Optional[Dict] = None) -> str:
        """Run the complete dynamic analysis and agent generation."""
        
        print("🚀 Starting Dynamic Company Efficiency Analysis")
        print("=" * 60)
        
        try:
            # Step 1: Analyze P&L data and generate agents
            print("\n📊 Step 1: Analyzing P&L data and generating agents...")
            
            if pnl_data is None:
                # Use sample data for demonstration
                pnl_data = {
                    'revenue': 800000,
                    'cogs': 200000,
                    'opex': 700000,
                    'operating_profit': -100000,
                    'net_profit': -120000,
                    'employee_count': 15,
                    'revenue_growth': 0.0
                }
                print("📝 Using sample data for demonstration")
            
            # Analyze data and generate agents
            analysis_result = self.kpi_tool._run(pnl_data)
            print(f"✅ Analysis complete: {analysis_result['summary']['total_inefficiencies']} inefficiencies found")
            
            self.nanobot.sync_agents(analysis_result)
            print("✅ Nanobot configuration updated")
            # Generate agents
            report = self.agent_creator._run(analysis_result)
            print("✅ Dynamic agents generated successfully")
            
            # Step 2: Create dynamic crew
            print("\n🤖 Step 2: Creating dynamic crew with generated agents...")
            crew = self.create_dynamic_crew()
            
            # Step 3: Run crew analysis
            print("\n🎯 Step 3: Running crew analysis...")
            if crew:
                try:
                    result = crew.kickoff()
                    print("✅ Crew analysis completed successfully")
                    return str(result)
                except Exception as e:
                    print(f"⚠️ Crew execution failed: {str(e)}")
                    return report
            else:
                print("⚠️ No crew available, returning analysis report")
                return report
                
        except Exception as e:
            print(f"❌ Error during dynamic analysis: {str(e)}")
            return f"Analysis failed: {str(e)}"
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of available agents."""
        
        summary = {
            'base_agents': len(self.base_agents),
            'dynamic_agents': len(self.dynamic_agents),
            'total_agents': len(self.base_agents) + len(self.dynamic_agents),
            'agent_types': list(self.dynamic_agents.keys()),
            'last_updated': datetime.now().isoformat()
        }
        
        return summary
    
    def list_available_agents(self) -> None:
        """List all available agents."""
        
        print("\n🤖 Available AI Agents")
        print("=" * 30)
        
        # Base agents
        print("\n📋 Base Agents:")
        for agent_name, config in self.base_agents.items():
            print(f"   • {config.get('role', agent_name)}")
        
        # Dynamic agents
        if self.dynamic_agents:
            print(f"\n🎯 Dynamic Agents ({len(self.dynamic_agents)}):")
            for role, agent in self.dynamic_agents.items():
                print(f"   • {role}")
        else:
            print("\n⚠️ No dynamic agents available. Run analysis to generate agents.")
        
        print(f"\n📊 Total: {len(self.base_agents) + len(self.dynamic_agents)} agents")

def main():
    """Main execution function for testing."""
    
    # Initialize dynamic crew system
    dynamic_system = DynamicCrewSystem()
    
    # Run dynamic analysis
    result = dynamic_system.run_dynamic_analysis()
    
    # Show agent summary
    dynamic_system.list_available_agents()
    
    print("\n🎉 Dynamic Analysis Complete!")
    print("=" * 40)
    print("Check config/dynamic_agents.yaml for generated agent configurations")
    print("Review the analysis report for detailed findings and recommendations")

if __name__ == "__main__":
    main()