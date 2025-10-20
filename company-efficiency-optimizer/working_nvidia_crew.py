"""
Working NVIDIA AI Endpoints CrewAI implementation

This version uses the correct NVIDIA AI Endpoints configuration.
"""

import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings

# Load environment variables
load_dotenv()

class WorkingNVIDIACrew:
    """Company Efficiency Optimizer Crew - Working NVIDIA Version"""
    
    def __init__(self):
        """Initialize the crew with NVIDIA AI Endpoints"""
        # Initialize NVIDIA LLM with correct configuration
        self.llm = ChatNVIDIA(
            model="nvidia/nemotron-4-340b-instruct",
            nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
            temperature=0.7,
            max_tokens=1000
        )
        
        # Initialize NVIDIA Embeddings
        self.embeddings = NVIDIAEmbeddings(
            model="nvidia/nv-embed-qa-e5-v5",  # Use available embedding model
            nvidia_api_key=os.getenv("NVIDIA_API_KEY")
        )
        
        # Load configurations
        self.agents_config = self._load_yaml_config('config/agents.yaml')
        self.tasks_config = self._load_yaml_config('config/tasks.yaml')
        
        # Initialize agents
        self.diagnostic_agent = self._create_diagnostic_agent()
        self.hr_optimizer = self._create_hr_optimizer()
        self.operations_optimizer = self._create_operations_optimizer()
        self.financial_optimizer = self._create_financial_optimizer()
        
        # Initialize tasks
        self.request_pnl_task = self._create_request_pnl_task()
        self.kpi_computation_task = self._create_kpi_computation_task()
        self.diagnostic_summary_task = self._create_diagnostic_summary_task()
    
    def _load_yaml_config(self, file_path: str) -> dict:
        """Load YAML configuration file"""
        try:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}
    
    def _create_diagnostic_agent(self) -> Agent:
        """Create the main diagnostic agent"""
        config = self.agents_config.get('diagnostic_agent', {})
        return Agent(
            role=config.get('role', 'Business Analyst expert in KPIs and inefficiencies'),
            goal=config.get('goal', 'Analyze financial statements and identify inefficiencies'),
            backstory=config.get('backstory', 'You are an analytical expert in business diagnostics'),
            llm=self.llm,
            memory=True,
            tools=[],
            verbose=True
        )
    
    def _create_hr_optimizer(self) -> Agent:
        """Create the HR optimizer agent"""
        config = self.agents_config.get('hr_optimizer', {})
        return Agent(
            role=config.get('role', 'HR Optimizer and Talent Management Specialist'),
            goal=config.get('goal', 'Optimize talent management to reduce turnover'),
            backstory=config.get('backstory', 'You are an empathetic HR specialist'),
            llm=self.llm,
            memory=True,
            tools=[],
            verbose=True
        )
    
    def _create_operations_optimizer(self) -> Agent:
        """Create the operations optimizer agent"""
        config = self.agents_config.get('operations_optimizer', {})
        return Agent(
            role=config.get('role', 'Operations Efficiency Specialist'),
            goal=config.get('goal', 'Optimize operational processes'),
            backstory=config.get('backstory', 'You are a process improvement expert'),
            llm=self.llm,
            memory=True,
            tools=[],
            verbose=True
        )
    
    def _create_financial_optimizer(self) -> Agent:
        """Create the financial optimizer agent"""
        config = self.agents_config.get('financial_optimizer', {})
        return Agent(
            role=config.get('role', 'Financial Performance Specialist'),
            goal=config.get('goal', 'Optimize financial performance'),
            backstory=config.get('backstory', 'You are a financial analyst'),
            llm=self.llm,
            memory=True,
            tools=[],
            verbose=True
        )
    
    def _create_request_pnl_task(self) -> Task:
        """Create the P&L request task"""
        config = self.tasks_config.get('request_pnl_task', {})
        return Task(
            description=config.get('description', 'Request P&L data from user'),
            expected_output=config.get('expected_output', 'Cleaned P&L dataset'),
            agent=self.diagnostic_agent
        )
    
    def _create_kpi_computation_task(self) -> Task:
        """Create the KPI computation task"""
        config = self.tasks_config.get('kpi_computation_task', {})
        return Task(
            description=config.get('description', 'Compute KPIs and identify inefficiencies'),
            expected_output=config.get('expected_output', 'KPI analysis report'),
            agent=self.diagnostic_agent
        )
    
    def _create_diagnostic_summary_task(self) -> Task:
        """Create the diagnostic summary task"""
        config = self.tasks_config.get('diagnostic_summary_task', {})
        return Task(
            description=config.get('description', 'Create comprehensive diagnostic summary'),
            expected_output=config.get('expected_output', 'Executive diagnostic report'),
            agent=self.diagnostic_agent
        )
    
    def create_crew(self) -> Crew:
        """Create the main diagnostic crew"""
        return Crew(
            agents=[
                self.diagnostic_agent,
                self.hr_optimizer,
                self.operations_optimizer,
                self.financial_optimizer
            ],
            tasks=[
                self.request_pnl_task,
                self.kpi_computation_task,
                self.diagnostic_summary_task
            ],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def run_diagnostic(self, initial_data=None):
        """Run the diagnostic analysis"""
        crew = self.create_crew()
        return crew.kickoff()
    
    def test_nvidia_connection(self):
        """Test NVIDIA AI Endpoints connection"""
        try:
            # Test LLM
            response = self.llm.invoke("Hello! Can you tell me what model you are?")
            print(f"✅ NVIDIA LLM Response: {response.content[:100]}...")
            
            # Test Embeddings
            embedding = self.embeddings.embed_query("Test embedding")
            print(f"✅ NVIDIA Embeddings: Vector dimension {len(embedding)}")
            
            return True
        except Exception as e:
            print(f"❌ NVIDIA connection test failed: {e}")
            return False