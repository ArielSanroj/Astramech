#!/usr/bin/env python3
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from crewai import Agent, Crew, Process, Task

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

class HumanInputTool(BaseTool):
    name: str = "human_input"
    description: str = "Tool for getting human input during task execution"
    
    def _run(self, query: str) -> str:
        try:
            return input(f"Human input needed: {query}\nYour response: ")
        except EOFError:
            print(f"Human input needed: {query}")
            print("Using sample data for demonstration...")
            return "Using sample P&L data for analysis"
from tools.enhanced_kpi_tool import EnhancedKPITool
from tools.dynamic_agent_creator import DynamicAgentCreator
from dynamic_crew_tasks import create_base_tasks, create_dynamic_task

try:
    from nanobot_bridge import NanobotBridge
except ImportError:
    NanobotBridge = None

class DynamicCrewSystem:
    def __init__(self):
        self.base_agents = {}
        self.dynamic_agents = {}
        self.tasks = []
        self.crew = None
        self.human_tool = HumanInputTool()
        self.base_dir = Path(__file__).resolve().parent
        self.config_dir = self.base_dir / "config"
        
        self._load_base_config()
        
        self.kpi_tool = EnhancedKPITool()
        self.agent_creator = DynamicAgentCreator()
        self.nanobot = (
            NanobotBridge(configuration_path="nanobot.yaml")
            if NanobotBridge is not None
            else None
        )
    
    def _load_base_config(self):
        try:
            with open(self.config_dir / 'agents.yaml', 'r') as f:
                self.base_agents = yaml.safe_load(f)
            
            with open(self.config_dir / 'tasks.yaml', 'r') as f:
                tasks_config = yaml.safe_load(f)
                self.tasks = list(tasks_config.keys())
            
            print("✅ Loaded base configuration")
            
        except Exception as e:
            print(f"⚠️ Error loading base config: {str(e)}")
            self.base_agents = {}
            self.tasks = []
    
    def _load_dynamic_agents(self) -> List[Agent]:
        dynamic_agents = []
        
        try:
            dynamic_agents_file = self.config_dir / 'dynamic_agents.yaml'
            if dynamic_agents_file.exists():
                with open(dynamic_agents_file, 'r') as f:
                    dynamic_configs = yaml.safe_load(f)
                
                print(f"🤖 Loading {len(dynamic_configs)} dynamic agents...")
                
                for agent_key, config in dynamic_configs.items():
                    try:
                        agent = Agent(
                            role=config['role'],
                            goal=config['goal'],
                            backstory=config['backstory'],
                            allow_delegation=config.get('allow_delegation', True),
                            verbose=config.get('verbose', True),
                            memory=config.get('memory', True),
                            tools=[self.kpi_tool]
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
        if os.getenv("ENABLE_DYNAMIC_CREW", "false").lower() not in ("1", "true"):
            print("⚠️ Dynamic crew disabled (ENABLE_DYNAMIC_CREW not set)")
            return None

        llm = None
        try:
            from langchain_ollama import ChatOllama

            model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            llm = ChatOllama(
                model=model_name,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.7
            )
        except Exception as exc:
            reason = "OPENAI_API_KEY missing" if not os.getenv("OPENAI_API_KEY") else "LLM unavailable"
            print(f"⚠️ LLM unavailable ({exc}); {reason}")

        if llm is None:
            print("⚠️ Dynamic crew disabled: no LLM available")
            return None

        diagnostic_config = self.base_agents.get('diagnostic_agent', {})
        return Agent(
            role=diagnostic_config.get('role', 'Business Analyst expert in KPIs and inefficiencies'),
            goal=diagnostic_config.get('goal', 'Analyze financial statements and identify inefficiencies'),
            backstory=diagnostic_config.get('backstory', 'You are an analytical expert in business diagnostics'),
            llm=llm,
            memory=True,
            tools=[self.human_tool, self.kpi_tool, self.agent_creator],
            verbose=True
        )
    
    def create_dynamic_crew(self) -> Crew:
        diagnostic_agent = self.create_diagnostic_agent()
        if diagnostic_agent is None:
            print("⚠️ Dynamic crew aborted: diagnostic agent unavailable")
            return None
        
        dynamic_agents = self._load_dynamic_agents()
        
        dynamic_tasks = [create_dynamic_task(agent, self.kpi_tool) for agent in dynamic_agents]
        
        all_agents = [diagnostic_agent] + dynamic_agents
        all_tasks = create_base_tasks(
            diagnostic_agent,
            self.kpi_tool,
            self.agent_creator,
            self.human_tool,
        ) + dynamic_tasks
        
        try:
            from langchain_ollama import ChatOllama
            
            model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            
            llm = ChatOllama(
                model=model_name,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.7
            )
        except Exception as e:
            print(f"⚠️ Error creating Ollama LLM: {str(e)}")
            llm = None
        
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
    
    def run_dynamic_analysis(self, pnl_data: Optional[Dict] = None) -> str:
        print("🚀 Starting Dynamic Company Efficiency Analysis")
        print("=" * 60)
        
        try:
            print("\n📊 Step 1: Analyzing P&L data and generating agents...")
            
            if pnl_data is None:
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
            
            analysis_result = self.kpi_tool._run(pnl_data)
            print(f"✅ Analysis complete: {analysis_result['summary']['total_inefficiencies']} inefficiencies found")
            
            if self.nanobot is not None:
                self.nanobot.sync_agents(analysis_result)
                print("✅ Nanobot configuration updated")
            report = self.agent_creator._run(analysis_result)
            print("✅ Dynamic agents generated successfully")
            
            print("\n🤖 Step 2: Creating dynamic crew with generated agents...")
            crew = self.create_dynamic_crew()
            
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
        summary = {
            'base_agents': len(self.base_agents),
            'dynamic_agents': len(self.dynamic_agents),
            'total_agents': len(self.base_agents) + len(self.dynamic_agents),
            'agent_types': list(self.dynamic_agents.keys()),
            'last_updated': datetime.now().isoformat()
        }
        
        return summary
    
    def list_available_agents(self) -> None:
        print("\n🤖 Available AI Agents")
        print("=" * 30)
        
        print("\n📋 Base Agents:")
        for agent_name, config in self.base_agents.items():
            print(f"   • {config.get('role', agent_name)}")
        
        if self.dynamic_agents:
            print(f"\n🎯 Dynamic Agents ({len(self.dynamic_agents)}):")
            for role, agent in self.dynamic_agents.items():
                print(f"   • {role}")
        else:
            print("\n⚠️ No dynamic agents available. Run analysis to generate agents.")
        
        print(f"\n📊 Total: {len(self.base_agents) + len(self.dynamic_agents)} agents")

def main():
    dynamic_system = DynamicCrewSystem()
    
    result = dynamic_system.run_dynamic_analysis()
    
    dynamic_system.list_available_agents()
    
    print("\n🎉 Dynamic Analysis Complete!")
    print("=" * 40)
    print("Check config/dynamic_agents.yaml for generated agent configurations")
    print("Review the analysis report for detailed findings and recommendations")

if __name__ == "__main__":
    main()
