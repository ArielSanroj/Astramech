"""
Astramech Orchestrator - CrewAI Supervisor
Listens to RabbitMQ events and coordinates HR + Finance agents
"""
import os
import json
import time
import sys
from typing import Dict, Any
from loguru import logger
import pika
from crewai import Agent, Crew, Task, Process
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))
from events import Topics

# Configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")
HR_SERVICE_URL = os.getenv("HR_SERVICE_URL", "http://clio-hr-backend:3000")
FINANCE_SERVICE_URL = os.getenv("FINANCE_SERVICE_URL", "http://finance-supervincent:8000")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai or ollama
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


class AstramechSupervisor:
    """CrewAI Supervisor that coordinates HR and Finance agents"""
    
    def __init__(self):
        """Initialize supervisor with LLM and agents"""
        self.llm = self._init_llm()
        self.hr_agent = self._create_hr_agent()
        self.finance_agent = self._create_finance_agent()
        self.supervisor_agent = self._create_supervisor_agent()
        logger.info("✅ Astramech Supervisor initialized")
    
    def _init_llm(self):
        """Initialize LLM based on provider"""
        if LLM_PROVIDER == "ollama":
            try:
                return ChatOllama(
                    model=OLLAMA_MODEL,
                    base_url=OLLAMA_BASE_URL,
                    temperature=0.7
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama, falling back to OpenAI: {e}")
        
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set. Set LLM_PROVIDER=ollama or provide OPENAI_API_KEY")
            raise ValueError("LLM configuration required")
        
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=OPENAI_API_KEY
        )
    
    def _create_hr_agent(self) -> Agent:
        """Create HR agent for burnout risk analysis"""
        return Agent(
            role="HR Risk Analyst",
            goal="Analyze employee burnout risks and provide actionable recommendations",
            backstory="""You are an expert HR analyst specializing in employee wellness and burnout prevention.
            You analyze questionnaire data, team compositions, and risk matrices to identify potential burnout risks.
            You provide specific, actionable recommendations based on archetypes and coping strategies.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_finance_agent(self) -> Agent:
        """Create Finance agent for financial analysis"""
        return Agent(
            role="Financial Analyst",
            goal="Analyze financial data and provide insights on budget allocation and cost optimization",
            backstory="""You are a financial analyst expert in processing invoices, calculating taxes,
            and providing budget recommendations. You work with financial data to optimize spending
            and ensure compliance with tax regulations.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_supervisor_agent(self) -> Agent:
        """Create supervisor agent that coordinates workflows"""
        return Agent(
            role="Astramech Supervisor",
            goal="Coordinate HR and Finance agents to provide comprehensive business insights",
            backstory="""You are the Astramech supervisor responsible for orchestrating workflows
            between HR and Finance agents. When buyer signals are detected, you coordinate
            both agents to provide holistic recommendations. You ensure that HR insights about
            team wellness are considered alongside financial constraints and opportunities.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
    
    def handle_buyer_signal(self, event_data: Dict[str, Any]):
        """
        Handle buyer_signal.detected event
        Coordinates HR and Finance agents to provide comprehensive analysis
        """
        logger.info(f"🔔 Buyer signal detected: {event_data}")
        
        lead_id = event_data.get("lead_id")
        company_id = event_data.get("company_id")
        signal_strength = event_data.get("strength", "medium")
        
        # Create tasks for HR and Finance agents
        hr_task = Task(
            description=f"""Analyze HR risks for company {company_id} associated with lead {lead_id}.
            Consider team composition, burnout risks, and employee wellness metrics.
            Provide recommendations for maintaining team health during potential growth phase.""",
            agent=self.hr_agent,
            expected_output="HR risk analysis with specific recommendations"
        )
        
        finance_task = Task(
            description=f"""Analyze financial readiness for company {company_id} associated with lead {lead_id}.
            Review budget allocation, cost structure, and financial capacity for scaling.
            Provide recommendations for financial planning during growth phase.""",
            agent=self.finance_agent,
            expected_output="Financial analysis with budget recommendations"
        )
        
        supervisor_task = Task(
            description=f"""Based on HR and Finance analyses, provide a comprehensive recommendation
            for handling buyer signal {lead_id} with strength {signal_strength}.
            Integrate HR wellness considerations with financial constraints.
            Provide actionable next steps.""",
            agent=self.supervisor_agent,
            expected_output="Integrated recommendation with actionable steps"
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[self.hr_agent, self.finance_agent, self.supervisor_agent],
            tasks=[hr_task, finance_task, supervisor_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            logger.info(f"✅ Buyer signal workflow completed: {result}")
            
            # Publish result or trigger follow-up actions
            self._publish_workflow_result("buyer_signal.workflow.completed", {
                "lead_id": lead_id,
                "company_id": company_id,
                "result": str(result)
            })
        except Exception as e:
            logger.error(f"❌ Error in buyer signal workflow: {e}")
    
    def handle_burnout_risk(self, event_data: Dict[str, Any]):
        """
        Handle burnout.risk.detected event
        Triggers HR analysis and coordinates with Finance for budget allocation
        """
        logger.info(f"⚠️ Burnout risk detected: {event_data}")
        
        team_id = event_data.get("team_id")
        user_id = event_data.get("user_id")
        burnout_probability = event_data.get("burnout_probability", 0.0)
        severity = "high" if burnout_probability > 0.6 else "medium" if burnout_probability > 0.4 else "low"
        
        # Create HR-focused task
        hr_task = Task(
            description=f"""Analyze burnout risk for user {user_id} in team {team_id}.
            Burnout probability: {burnout_probability:.2%} (severity: {severity}).
            Review archetype, coping strategies, and team dynamics.
            Provide specific intervention recommendations.""",
            agent=self.hr_agent,
            expected_output="Detailed burnout intervention plan"
        )
        
        finance_task = Task(
            description=f"""Based on burnout risk severity {severity} for team {team_id},
            recommend budget allocation for wellness programs, training, or support resources.
            Consider cost-effectiveness and ROI of different intervention strategies.""",
            agent=self.finance_agent,
            expected_output="Budget recommendation for burnout interventions"
        )
        
        supervisor_task = Task(
            description=f"""Integrate HR intervention plan with financial budget for team {team_id}.
            Provide a comprehensive action plan that balances employee wellness with financial constraints.
            Prioritize interventions based on severity and cost-effectiveness.""",
            agent=self.supervisor_agent,
            expected_output="Integrated action plan with budget allocation"
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[self.hr_agent, self.finance_agent, self.supervisor_agent],
            tasks=[hr_task, finance_task, supervisor_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            logger.info(f"✅ Burnout risk workflow completed: {result}")
            
            # Publish result
            self._publish_workflow_result("burnout.risk.workflow.completed", {
                "team_id": team_id,
                "user_id": user_id,
                "severity": severity,
                "result": str(result)
            })
        except Exception as e:
            logger.error(f"❌ Error in burnout risk workflow: {e}")
    
    def _publish_workflow_result(self, routing_key: str, data: Dict[str, Any]):
        """Publish workflow result to RabbitMQ"""
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            
            channel.basic_publish(
                exchange='',
                routing_key=routing_key,
                body=json.dumps(data)
            )
            
            connection.close()
            logger.info(f"📤 Published workflow result: {routing_key}")
        except Exception as e:
            logger.error(f"❌ Failed to publish workflow result: {e}")


class EventConsumer:
    """RabbitMQ event consumer"""
    
    def __init__(self, supervisor: AstramechSupervisor):
        self.supervisor = supervisor
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=Topics.buyer_signal_detected, durable=True)
            self.channel.queue_declare(queue=Topics.burnout_risk, durable=True)
            
            logger.info("✅ Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    def start_consuming(self):
        """Start consuming events"""
        # Set up consumer for buyer_signal.detected
        self.channel.basic_consume(
            queue=Topics.buyer_signal_detected,
            on_message_callback=self._on_buyer_signal,
            auto_ack=True
        )
        
        # Set up consumer for burnout.risk.detected
        self.channel.basic_consume(
            queue=Topics.burnout_risk,
            on_message_callback=self._on_burnout_risk,
            auto_ack=True
        )
        
        logger.info("🎧 Starting to consume events...")
        logger.info(f"   Listening to: {Topics.buyer_signal_detected}")
        logger.info(f"   Listening to: {Topics.burnout_risk}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("🛑 Stopping consumer...")
            self.channel.stop_consuming()
            self.connection.close()
    
    def _on_buyer_signal(self, ch, method, properties, body):
        """Handle buyer_signal.detected event"""
        try:
            data = json.loads(body)
            self.supervisor.handle_buyer_signal(data)
        except Exception as e:
            logger.error(f"❌ Error handling buyer signal: {e}")
    
    def _on_burnout_risk(self, ch, method, properties, body):
        """Handle burnout.risk.detected event"""
        try:
            data = json.loads(body)
            self.supervisor.handle_burnout_risk(data)
        except Exception as e:
            logger.error(f"❌ Error handling burnout risk: {e}")


def main():
    """Main entry point"""
    logger.info("🚀 Astramech Orchestrator starting...")
    
    # Initialize supervisor
    supervisor = AstramechSupervisor()
    
    # Initialize and start event consumer
    consumer = EventConsumer(supervisor)
    
    # Retry connection logic
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            consumer.connect()
            consumer.start_consuming()
            break
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ Failed to connect after all retries. Exiting.")
                sys.exit(1)


if __name__ == "__main__":
    main()
