"""
Dynamic Agent Creator for Company Efficiency Optimizer

This module creates specialized AI agents for any department based on
identified inefficiencies and KPI analysis.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import requests

load_dotenv()

class DynamicAgentCreator:
    """Creates dynamic AI agents for any department based on inefficiencies"""
    
    def __init__(self):
        """Initialize the dynamic agent creator"""
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.pinecone_index = os.getenv('PINECONE_INDEX', 'company-memory')
        
        # Agent templates for different departments
        self.agent_templates = {
            'marketing': {
                'role': 'Marketing Optimizer',
                'goal': 'Improve marketing ROI, reduce customer acquisition costs, and increase conversion rates',
                'backstory': 'A data-driven marketing expert with 10+ years experience in digital marketing, SEO, and customer acquisition strategies.',
                'tasks': [
                    'Analyze marketing spend efficiency',
                    'Identify high-performing channels',
                    'Optimize customer acquisition strategies',
                    'Improve conversion rate optimization'
                ],
                'tools': ['marketing_analytics', 'seo_optimizer', 'conversion_tracker']
            },
            'it': {
                'role': 'IT Infrastructure Optimizer',
                'goal': 'Improve system uptime, reduce response times, and enhance security posture',
                'backstory': 'A senior IT architect with expertise in cloud infrastructure, cybersecurity, and system optimization.',
                'tasks': [
                    'Monitor system performance metrics',
                    'Identify infrastructure bottlenecks',
                    'Implement security best practices',
                    'Optimize resource utilization'
                ],
                'tools': ['system_monitor', 'security_scanner', 'performance_analyzer']
            },
            'r_d': {
                'role': 'R&D Innovation Optimizer',
                'goal': 'Accelerate innovation, improve research efficiency, and reduce time-to-market',
                'backstory': 'A research director with PhD in engineering and 15+ years in product development and innovation management.',
                'tasks': [
                    'Analyze research project efficiency',
                    'Identify innovation opportunities',
                    'Optimize development processes',
                    'Improve patent portfolio management'
                ],
                'tools': ['innovation_tracker', 'patent_analyzer', 'project_manager']
            },
            'hr': {
                'role': 'HR Performance Optimizer',
                'goal': 'Improve employee satisfaction, reduce turnover, and enhance workforce productivity',
                'backstory': 'A senior HR executive with expertise in talent management, employee engagement, and organizational development.',
                'tasks': [
                    'Analyze employee satisfaction metrics',
                    'Identify retention risk factors',
                    'Optimize training programs',
                    'Improve diversity and inclusion'
                ],
                'tools': ['employee_survey', 'retention_predictor', 'training_optimizer']
            },
            'finance': {
                'role': 'Financial Performance Optimizer',
                'goal': 'Improve profit margins, optimize costs, and enhance financial efficiency',
                'backstory': 'A CFO with 20+ years experience in financial analysis, cost optimization, and strategic planning.',
                'tasks': [
                    'Analyze financial performance metrics',
                    'Identify cost optimization opportunities',
                    'Improve cash flow management',
                    'Optimize pricing strategies'
                ],
                'tools': ['financial_analyzer', 'cost_optimizer', 'cash_flow_forecaster']
            },
            'operations': {
                'role': 'Operations Efficiency Optimizer',
                'goal': 'Streamline processes, reduce waste, and improve operational efficiency',
                'backstory': 'An operations director with expertise in lean manufacturing, process optimization, and supply chain management.',
                'tasks': [
                    'Analyze operational efficiency metrics',
                    'Identify process bottlenecks',
                    'Implement lean methodologies',
                    'Optimize supply chain operations'
                ],
                'tools': ['process_analyzer', 'waste_tracker', 'supply_chain_optimizer']
            }
        }
    
    def create_agent(self, inefficiency: Dict[str, Any], department: str, company_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a specialized agent for addressing specific inefficiencies
        
        Args:
            inefficiency: Dictionary containing inefficiency details
            department: Department the agent will focus on
            company_context: Company information and context
            
        Returns:
            Dict: Agent configuration
        """
        try:
            # Get base template for department
            base_template = self.agent_templates.get(department.lower(), self.agent_templates['operations'])
            
            # Generate custom backstory using Ollama
            custom_backstory = self._generate_custom_backstory(inefficiency, department, company_context)
            
            # Create agent configuration
            agent_config = {
                'id': f"{department.lower()}_optimizer_{inefficiency.get('issue_type', 'general')}",
                'role': base_template['role'],
                'goal': f"Address {inefficiency.get('kpi_name', 'performance issues')} in {department}",
                'backstory': custom_backstory,
                'tasks': self._customize_tasks(base_template['tasks'], inefficiency),
                'tools': base_template['tools'],
                'department': department,
                'target_inefficiency': inefficiency,
                'company_context': company_context,
                'created_at': self._get_timestamp()
            }
            
            # Store agent in memory system
            self._store_agent_in_memory(agent_config)
            
            print(f"✅ Created {department} Optimizer agent for {inefficiency.get('kpi_name', 'performance issues')}")
            return agent_config
            
        except Exception as e:
            print(f"❌ Error creating agent: {str(e)}")
            return {}
    
    def _generate_custom_backstory(self, inefficiency: Dict[str, Any], department: str, company_context: Dict[str, Any]) -> str:
        """Generate custom backstory using Ollama"""
        try:
            prompt = f"""
            Create a professional backstory for an AI agent specializing in {department} optimization.
            
            Context:
            - Company: {company_context.get('company_name', 'Unknown')}
            - Industry: {company_context.get('industry', 'Unknown')}
            - Issue: {inefficiency.get('kpi_name', 'Performance optimization')}
            - Current Value: {inefficiency.get('current_value', 'Unknown')}
            - Benchmark: {inefficiency.get('benchmark', 'Unknown')}
            - Severity: {inefficiency.get('severity', 'Unknown')}
            
            Create a 2-3 sentence backstory that positions this agent as an expert in addressing this specific issue.
            Focus on relevant experience and expertise.
            """
            
            # Use Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.1:8b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"⚠️ Ollama API error: {response.status_code}")
                return self._get_fallback_backstory(department, inefficiency)
                
        except Exception as e:
            print(f"⚠️ Error generating backstory: {str(e)}")
            return self._get_fallback_backstory(department, inefficiency)
    
    def _get_fallback_backstory(self, department: str, inefficiency: Dict[str, Any]) -> str:
        """Get fallback backstory when Ollama is unavailable"""
        base_template = self.agent_templates.get(department.lower(), self.agent_templates['operations'])
        issue = inefficiency.get('kpi_name', 'performance issues')
        
        return f"{base_template['backstory']} Specialized in addressing {issue} and similar challenges."
    
    def _customize_tasks(self, base_tasks: List[str], inefficiency: Dict[str, Any]) -> List[str]:
        """Customize tasks based on specific inefficiency"""
        kpi_name = inefficiency.get('kpi_name', '')
        
        if 'margin' in kpi_name.lower():
            return base_tasks + ['Analyze cost structure and pricing strategies']
        elif 'turnover' in kpi_name.lower():
            return base_tasks + ['Conduct exit interviews and retention analysis']
        elif 'efficiency' in kpi_name.lower():
            return base_tasks + ['Map current processes and identify waste']
        elif 'revenue' in kpi_name.lower():
            return base_tasks + ['Analyze revenue streams and growth opportunities']
        
        return base_tasks
    
    def _store_agent_in_memory(self, agent_config: Dict[str, Any]) -> None:
        """Store agent configuration in Pinecone memory"""
        try:
            if not self.pinecone_api_key:
                print("⚠️ Pinecone API key not available, skipping memory storage")
                return
            
            # This would integrate with Pinecone
            # For now, just log the agent creation
            print(f"💾 Storing agent {agent_config['id']} in memory system")
            
        except Exception as e:
            print(f"⚠️ Error storing agent in memory: {str(e)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def create_agent_crew(self, inefficiencies: List[Dict[str, Any]], company_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a crew of agents to address multiple inefficiencies
        
        Args:
            inefficiencies: List of inefficiency dictionaries
            company_context: Company information and context
            
        Returns:
            List of agent configurations
        """
        agents = []
        
        # Group inefficiencies by department
        department_inefficiencies = {}
        for inefficiency in inefficiencies:
            dept = inefficiency.get('recommended_agent', 'operations').replace('_optimizer', '')
            if dept not in department_inefficiencies:
                department_inefficiencies[dept] = []
            department_inefficiencies[dept].append(inefficiency)
        
        # Create agents for each department
        for department, dept_inefficiencies in department_inefficiencies.items():
            # Create one agent per department (can be enhanced to create multiple)
            primary_inefficiency = max(dept_inefficiencies, key=lambda x: x.get('severity', 'low'))
            agent = self.create_agent(primary_inefficiency, department, company_context)
            if agent:
                agents.append(agent)
        
        return agents
    
    def get_agent_recommendations(self, kpi_results: Dict[str, Any], company_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get agent recommendations based on KPI analysis
        
        Args:
            kpi_results: Results from KPI calculation
            company_context: Company information and context
            
        Returns:
            List of recommended agents
        """
        recommendations = []
        
        # Analyze financial KPIs
        financial = kpi_results.get('financial', {})
        if financial.get('gross_margin', 0) < 0.25:  # Below 25%
            recommendations.append({
                'department': 'Finance',
                'priority': 'High',
                'reason': 'Low gross margin indicates pricing or cost issues',
                'agent_type': 'Financial Optimizer'
            })
        
        if financial.get('operating_margin', 0) < 0.08:  # Below 8%
            recommendations.append({
                'department': 'Operations',
                'priority': 'High',
                'reason': 'Low operating margin indicates operational inefficiency',
                'agent_type': 'Operations Optimizer'
            })
        
        # Analyze HR KPIs
        hr = kpi_results.get('hr', {})
        if hr.get('turnover_rate', 0) > 0.20:  # Above 20%
            recommendations.append({
                'department': 'HR',
                'priority': 'High',
                'reason': 'High turnover rate indicates retention issues',
                'agent_type': 'HR Optimizer'
            })
        
        # Analyze department-specific KPIs
        department = kpi_results.get('department', {})
        dept_kpis = department.get('kpis', {})
        
        for kpi_name, value in dept_kpis.items():
            if 'roi' in kpi_name.lower() and value < 3.0:
                recommendations.append({
                    'department': 'Marketing',
                    'priority': 'Medium',
                    'reason': f'Low {kpi_name} indicates marketing inefficiency',
                    'agent_type': 'Marketing Optimizer'
                })
            
            if 'uptime' in kpi_name.lower() and value < 99.0:
                recommendations.append({
                    'department': 'IT',
                    'priority': 'High',
                    'reason': f'Low {kpi_name} indicates system reliability issues',
                    'agent_type': 'IT Infrastructure Optimizer'
                })
        
        return recommendations

# Global dynamic agent creator instance
dynamic_agent_creator = DynamicAgentCreator()

def get_dynamic_agent_creator() -> DynamicAgentCreator:
    """Get the global dynamic agent creator instance"""
    return dynamic_agent_creator