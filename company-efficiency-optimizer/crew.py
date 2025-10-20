import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import HumanInputTool
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

@CrewBase
class DiagnosticCrew:
    """Company Efficiency Optimizer Crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        # Initialize LLM (using OpenAI-compatible interface for NVIDIA)
        # For now, we'll use a placeholder that can be easily switched to NVIDIA
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Placeholder - will be replaced with NVIDIA
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY", "placeholder")
        )
        
        # Initialize human input tool
        self.human_tool = HumanInputTool()
    
    @agent
    def diagnostic_agent(self) -> Agent:
        """Main diagnostic agent for KPI analysis and inefficiency identification"""
        return Agent(
            config=self.agents_config['diagnostic_agent'],
            llm=self.llm,
            memory=True,
            tools=[self.human_tool],
            verbose=True
        )
    
    @agent
    def hr_optimizer(self) -> Agent:
        """HR optimization specialist agent"""
        return Agent(
            config=self.agents_config['hr_optimizer'],
            llm=self.llm,
            memory=True,
            tools=[self.human_tool],
            verbose=True
        )
    
    @agent
    def operations_optimizer(self) -> Agent:
        """Operations efficiency specialist agent"""
        return Agent(
            config=self.agents_config['operations_optimizer'],
            llm=self.llm,
            memory=True,
            tools=[self.human_tool],
            verbose=True
        )
    
    @agent
    def financial_optimizer(self) -> Agent:
        """Financial performance specialist agent"""
        return Agent(
            config=self.agents_config['financial_optimizer'],
            llm=self.llm,
            memory=True,
            tools=[self.human_tool],
            verbose=True
        )
    
    @task
    def request_pnl_task(self) -> Task:
        """Task to request and process P&L data from user"""
        return Task(
            config=self.tasks_config['request_pnl_task'],
            agent=self.diagnostic_agent()
        )
    
    @task
    def kpi_computation_task(self) -> Task:
        """Task to compute KPIs and identify inefficiencies"""
        return Task(
            config=self.tasks_config['kpi_computation_task'],
            agent=self.diagnostic_agent()
        )
    
    @task
    def diagnostic_summary_task(self) -> Task:
        """Task to create comprehensive diagnostic summary"""
        return Task(
            config=self.tasks_config['diagnostic_summary_task'],
            agent=self.diagnostic_agent()
        )
    
    @task
    def hr_analysis_task(self) -> Task:
        """Task for HR optimization analysis"""
        return Task(
            config=self.tasks_config['hr_analysis_task'],
            agent=self.hr_optimizer()
        )
    
    @task
    def operations_analysis_task(self) -> Task:
        """Task for operations optimization analysis"""
        return Task(
            config=self.tasks_config['operations_analysis_task'],
            agent=self.operations_optimizer()
        )
    
    @task
    def financial_analysis_task(self) -> Task:
        """Task for financial optimization analysis"""
        return Task(
            config=self.tasks_config['financial_analysis_task'],
            agent=self.financial_optimizer()
        )
    
    @crew
    def crew(self) -> Crew:
        """Main crew for diagnostic analysis"""
        return Crew(
            agents=[
                self.diagnostic_agent(),
                self.hr_optimizer(),
                self.operations_optimizer(),
                self.financial_optimizer()
            ],
            tasks=[
                self.request_pnl_task(),
                self.kpi_computation_task(),
                self.diagnostic_summary_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True
        )
    
    @crew
    def specialized_crew(self) -> Crew:
        """Specialized crew for targeted optimization"""
        return Crew(
            agents=[
                self.hr_optimizer(),
                self.operations_optimizer(),
                self.financial_optimizer()
            ],
            tasks=[
                self.hr_analysis_task(),
                self.operations_analysis_task(),
                self.financial_analysis_task()
            ],
            process=Process.hierarchical,
            verbose=True,
            memory=True,
            cache=True
        )