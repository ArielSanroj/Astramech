"""
Sistema de Recomendación de Agentes CrewAI v2
Versión compatible con CrewAI 0.203.1 y Python 3.12
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentType(Enum):
    """Tipos de agentes disponibles"""
    DIAGNOSTIC = "diagnostic_agent"
    HR_OPTIMIZER = "hr_optimizer"
    OPERATIONS_OPTIMIZER = "operations_optimizer"
    FINANCIAL_OPTIMIZER = "financial_optimizer"

@dataclass
class KPIProblem:
    """Representa un problema identificado en un KPI"""
    kpi_name: str
    current_value: float
    benchmark_value: float
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    recommended_agent: AgentType
    priority_score: int  # 1-10, donde 10 es más crítico

@dataclass
class AgentRecommendation:
    """Recomendación de agente con contexto específico"""
    agent_type: AgentType
    priority: int
    problem_description: str
    expected_impact: str
    implementation_effort: str  # LOW, MEDIUM, HIGH
    estimated_timeline: str

class AgentRecommendationSystem:
    """Sistema para recomendar y ejecutar agentes CrewAI basado en análisis de KPIs"""
    
    def __init__(self):
        """Inicializar el sistema de recomendación de agentes"""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY", "placeholder")
        )
        
        # No usar herramientas de entrada humana en esta versión
        self.agent_configs = self._load_agent_configs()
        self.task_configs = self._load_task_configs()
        
    def _load_agent_configs(self) -> Dict:
        """Cargar configuraciones de agentes desde YAML"""
        import yaml
        with open('config/agents.yaml', 'r') as f:
            return yaml.safe_load(f)
    
    def _load_task_configs(self) -> Dict:
        """Cargar configuraciones de tareas desde YAML"""
        import yaml
        with open('config/tasks.yaml', 'r') as f:
            return yaml.safe_load(f)
    
    def analyze_kpis_and_recommend_agents(self, kpi_data: Dict, financial_data: Dict) -> List[AgentRecommendation]:
        """
        Analizar KPIs y recomendar agentes específicos basado en problemas identificados
        
        Args:
            kpi_data: Datos de KPIs calculados
            financial_data: Datos financieros de la empresa
            
        Returns:
            Lista de recomendaciones de agentes ordenadas por prioridad
        """
        problems = self._identify_kpi_problems(kpi_data, financial_data)
        recommendations = self._generate_agent_recommendations(problems)
        
        # Ordenar por prioridad (mayor a menor)
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations
    
    def _identify_kpi_problems(self, kpi_data: Dict, financial_data: Dict) -> List[KPIProblem]:
        """Identificar problemas en los KPIs y determinar qué agente puede resolverlos"""
        problems = []
        
        # Análisis de KPIs financieros
        if 'gross_margin' in kpi_data:
            current = kpi_data['gross_margin']['value']
            benchmark = kpi_data['gross_margin']['benchmark']
            if current < benchmark * 0.8:  # 20% por debajo del benchmark
                problems.append(KPIProblem(
                    kpi_name="Gross Margin",
                    current_value=current,
                    benchmark_value=benchmark,
                    severity="HIGH" if current < benchmark * 0.6 else "MEDIUM",
                    description=f"Margen bruto {current:.1f}% está significativamente por debajo del benchmark {benchmark:.1f}%",
                    recommended_agent=AgentType.FINANCIAL_OPTIMIZER,
                    priority_score=8 if current < benchmark * 0.6 else 6
                ))
        
        if 'operating_margin' in kpi_data:
            current = kpi_data['operating_margin']['value']
            benchmark = kpi_data['operating_margin']['benchmark']
            if current < benchmark * 0.8:
                problems.append(KPIProblem(
                    kpi_name="Operating Margin",
                    current_value=current,
                    benchmark_value=benchmark,
                    severity="HIGH" if current < benchmark * 0.6 else "MEDIUM",
                    description=f"Margen operativo {current:.1f}% está por debajo del benchmark {benchmark:.1f}%",
                    recommended_agent=AgentType.OPERATIONS_OPTIMIZER,
                    priority_score=9 if current < benchmark * 0.6 else 7
                ))
        
        if 'net_margin' in kpi_data:
            current = kpi_data['net_margin']['value']
            benchmark = kpi_data['net_margin']['benchmark']
            if current < benchmark * 0.8:
                problems.append(KPIProblem(
                    kpi_name="Net Margin",
                    current_value=current,
                    benchmark_value=benchmark,
                    severity="HIGH" if current < benchmark * 0.6 else "MEDIUM",
                    description=f"Margen neto {current:.1f}% está por debajo del benchmark {benchmark:.1f}%",
                    recommended_agent=AgentType.FINANCIAL_OPTIMIZER,
                    priority_score=8 if current < benchmark * 0.6 else 6
                ))
        
        # Análisis de eficiencia operacional
        if 'asset_turnover' in kpi_data:
            current = kpi_data['asset_turnover']['value']
            benchmark = kpi_data['asset_turnover']['benchmark']
            if current < benchmark * 0.5:  # Muy por debajo
                problems.append(KPIProblem(
                    kpi_name="Asset Turnover",
                    current_value=current,
                    benchmark_value=benchmark,
                    severity="CRITICAL",
                    description=f"Rotación de activos {current:.2f} está críticamente por debajo del benchmark {benchmark:.2f}",
                    recommended_agent=AgentType.OPERATIONS_OPTIMIZER,
                    priority_score=10
                ))
        
        if 'revenue_per_employee' in kpi_data:
            current = kpi_data['revenue_per_employee']['value']
            benchmark = kpi_data['revenue_per_employee']['benchmark']
            if current < benchmark * 0.7:
                problems.append(KPIProblem(
                    kpi_name="Revenue per Employee",
                    current_value=current,
                    benchmark_value=benchmark,
                    severity="HIGH" if current < benchmark * 0.5 else "MEDIUM",
                    description=f"Ingresos por empleado ${current:,.0f} están por debajo del benchmark ${benchmark:,.0f}",
                    recommended_agent=AgentType.HR_OPTIMIZER,
                    priority_score=9 if current < benchmark * 0.5 else 7
                ))
        
        # Análisis de rentabilidad
        if 'roa' in kpi_data:
            current = kpi_data['roa']['value']
            benchmark = kpi_data['roa']['benchmark']
            if current < benchmark * 0.5:
                problems.append(KPIProblem(
                    kpi_name="Return on Assets (ROA)",
                    current_value=current,
                    benchmark_value=benchmark,
                    severity="CRITICAL",
                    description=f"ROA {current:.2f}% está críticamente por debajo del benchmark {benchmark:.2f}%",
                    recommended_agent=AgentType.FINANCIAL_OPTIMIZER,
                    priority_score=10
                ))
        
        if 'roe' in kpi_data:
            current = kpi_data['roe']['value']
            benchmark = kpi_data['roe']['benchmark']
            if current < benchmark * 0.5:
                problems.append(KPIProblem(
                    kpi_name="Return on Equity (ROE)",
                    current_value=current,
                    benchmark_value=benchmark,
                    severity="CRITICAL",
                    description=f"ROE {current:.2f}% está críticamente por debajo del benchmark {benchmark:.2f}%",
                    recommended_agent=AgentType.FINANCIAL_OPTIMIZER,
                    priority_score=10
                ))
        
        return problems
    
    def _generate_agent_recommendations(self, problems: List[KPIProblem]) -> List[AgentRecommendation]:
        """Generar recomendaciones de agentes basadas en los problemas identificados"""
        recommendations = []
        agent_problems = {}
        
        # Agrupar problemas por agente recomendado
        for problem in problems:
            agent_type = problem.recommended_agent
            if agent_type not in agent_problems:
                agent_problems[agent_type] = []
            agent_problems[agent_type].append(problem)
        
        # Generar recomendación para cada agente
        for agent_type, agent_problems_list in agent_problems.items():
            # Calcular prioridad promedio
            avg_priority = sum(p.priority_score for p in agent_problems_list) / len(agent_problems_list)
            
            # Generar descripción del problema
            problem_descriptions = [p.description for p in agent_problems_list]
            combined_description = "; ".join(problem_descriptions)
            
            # Determinar impacto esperado y esfuerzo de implementación
            expected_impact, implementation_effort, timeline = self._assess_agent_impact(agent_type, agent_problems_list)
            
            recommendations.append(AgentRecommendation(
                agent_type=agent_type,
                priority=int(avg_priority),
                problem_description=combined_description,
                expected_impact=expected_impact,
                implementation_effort=implementation_effort,
                estimated_timeline=timeline
            ))
        
        return recommendations
    
    def _assess_agent_impact(self, agent_type: AgentType, problems: List[KPIProblem]) -> tuple:
        """Evaluar el impacto esperado y esfuerzo de implementación para un agente"""
        if agent_type == AgentType.FINANCIAL_OPTIMIZER:
            return (
                "Alto impacto en optimización de costos y mejora de márgenes",
                "MEDIUM",
                "2-4 semanas"
            )
        elif agent_type == AgentType.OPERATIONS_OPTIMIZER:
            return (
                "Alto impacto en eficiencia operacional y productividad",
                "HIGH",
                "4-8 semanas"
            )
        elif agent_type == AgentType.HR_OPTIMIZER:
            return (
                "Impacto medio-alto en productividad y retención de talento",
                "MEDIUM",
                "3-6 semanas"
            )
        else:  # DIAGNOSTIC
            return (
                "Análisis profundo y diagnóstico completo",
                "LOW",
                "1-2 semanas"
            )
    
    def create_agent(self, agent_type: AgentType) -> Agent:
        """Crear instancia de agente CrewAI"""
        config = self.agent_configs[agent_type.value]
        
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self.llm,
            memory=config.get('memory', True),
            tools=[],  # No usar herramientas en esta versión simplificada
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False)
        )
    
    def create_task(self, task_name: str, agent: Agent, context: Dict) -> Task:
        """Crear tarea específica para un agente con contexto personalizado"""
        task_config = self.task_configs[task_name]
        
        # Personalizar descripción con contexto específico
        description = task_config['description']
        if context:
            context_str = f"\n\nContexto específico de la empresa:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            description += context_str
        
        return Task(
            description=description,
            expected_output=task_config['expected_output'],
            agent=agent,
            tools=[]  # No usar herramientas en esta versión simplificada
        )
    
    def execute_agent_recommendations(self, recommendations: List[AgentRecommendation], 
                                    financial_data: Dict, company_profile: Dict) -> Dict:
        """
        Ejecutar las recomendaciones de agentes y generar reportes especializados
        
        Args:
            recommendations: Lista de recomendaciones de agentes
            financial_data: Datos financieros de la empresa
            company_profile: Perfil de la empresa
            
        Returns:
            Diccionario con resultados de cada agente ejecutado
        """
        results = {}
        
        for recommendation in recommendations[:2]:  # Ejecutar solo los 2 más prioritarios para evitar costos
            try:
                print(f"\n🤖 Ejecutando {recommendation.agent_type.value}...")
                
                # Crear agente
                agent = self.create_agent(recommendation.agent_type)
                
                # Crear contexto específico
                context = {
                    "Problema identificado": recommendation.problem_description,
                    "Impacto esperado": recommendation.expected_impact,
                    "Datos financieros": financial_data,
                    "Perfil de empresa": company_profile
                }
                
                # Crear tarea específica según el tipo de agente
                task_name = self._get_task_name_for_agent(recommendation.agent_type)
                task = self.create_task(task_name, agent, context)
                
                # Crear crew y ejecutar
                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=True,
                    memory=True
                )
                
                # Ejecutar tarea
                result = crew.kickoff()
                results[recommendation.agent_type.value] = {
                    "recommendation": recommendation,
                    "result": result,
                    "status": "completed"
                }
                
                print(f"✅ {recommendation.agent_type.value} completado exitosamente")
                
            except Exception as e:
                print(f"❌ Error ejecutando {recommendation.agent_type.value}: {e}")
                results[recommendation.agent_type.value] = {
                    "recommendation": recommendation,
                    "result": None,
                    "status": "failed",
                    "error": str(e)
                }
        
        return results
    
    def _get_task_name_for_agent(self, agent_type: AgentType) -> str:
        """Obtener nombre de tarea específica para cada tipo de agente"""
        task_mapping = {
            AgentType.DIAGNOSTIC: "diagnostic_summary_task",
            AgentType.HR_OPTIMIZER: "hr_analysis_task",
            AgentType.OPERATIONS_OPTIMIZER: "operations_analysis_task",
            AgentType.FINANCIAL_OPTIMIZER: "financial_analysis_task"
        }
        return task_mapping.get(agent_type, "diagnostic_summary_task")
    
    def generate_agent_report(self, recommendations: List[AgentRecommendation], 
                            execution_results: Dict) -> str:
        """Generar reporte consolidado de recomendaciones y resultados de agentes"""
        
        report = "# 🤖 Reporte de Recomendaciones de Agentes IA\n\n"
        
        # Resumen ejecutivo
        report += "## 📊 Resumen Ejecutivo\n\n"
        report += f"Se identificaron {len(recommendations)} áreas de mejora que requieren atención especializada.\n"
        report += f"Se ejecutaron {len([r for r in execution_results.values() if r['status'] == 'completed'])} agentes especializados.\n\n"
        
        # Recomendaciones prioritarias
        report += "## 🎯 Recomendaciones Prioritarias\n\n"
        for i, rec in enumerate(recommendations[:5], 1):
            report += f"### {i}. {rec.agent_type.value.replace('_', ' ').title()}\n"
            report += f"**Prioridad:** {rec.priority}/10\n"
            report += f"**Problema:** {rec.problem_description}\n"
            report += f"**Impacto esperado:** {rec.expected_impact}\n"
            report += f"**Esfuerzo de implementación:** {rec.implementation_effort}\n"
            report += f"**Timeline estimado:** {rec.estimated_timeline}\n\n"
        
        # Resultados de ejecución
        report += "## 🔧 Resultados de Ejecución de Agentes\n\n"
        for agent_name, result in execution_results.items():
            report += f"### {agent_name.replace('_', ' ').title()}\n"
            report += f"**Estado:** {result['status']}\n"
            if result['status'] == 'completed':
                report += f"**Resultado:**\n{result['result']}\n\n"
            else:
                report += f"**Error:** {result.get('error', 'Desconocido')}\n\n"
        
        # Próximos pasos
        report += "## 🚀 Próximos Pasos Recomendados\n\n"
        report += "1. **Revisar resultados** de los agentes ejecutados\n"
        report += "2. **Priorizar implementación** basada en impacto y esfuerzo\n"
        report += "3. **Asignar recursos** para las mejoras identificadas\n"
        report += "4. **Establecer métricas** de seguimiento\n"
        report += "5. **Programar revisiones** periódicas del progreso\n\n"
        
        return report

def main():
    """Función principal para probar el sistema"""
    print("🤖 Sistema de Recomendación de Agentes CrewAI v2")
    print("=" * 50)
    
    # Crear instancia del sistema
    system = AgentRecommendationSystem()
    
    # Datos de ejemplo para prueba
    kpi_data = {
        'gross_margin': {'value': 15.0, 'benchmark': 25.0},
        'operating_margin': {'value': 8.0, 'benchmark': 15.0},
        'net_margin': {'value': 5.0, 'benchmark': 10.0},
        'asset_turnover': {'value': 0.5, 'benchmark': 1.5},
        'revenue_per_employee': {'value': 150000, 'benchmark': 300000},
        'roa': {'value': 2.0, 'benchmark': 8.0},
        'roe': {'value': 5.0, 'benchmark': 15.0}
    }
    
    financial_data = {
        'revenue': 20000000,
        'net_income': 1000000,
        'total_assets': 50000000
    }
    
    company_profile = {
        'company_name': 'Empresa Ejemplo',
        'industry': 'services',
        'employee_count': 50
    }
    
    # Generar recomendaciones
    recommendations = system.analyze_kpis_and_recommend_agents(kpi_data, financial_data)
    
    print(f"\n📋 Se identificaron {len(recommendations)} recomendaciones de agentes:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.agent_type.value} (Prioridad: {rec.priority})")
        print(f"   Problema: {rec.problem_description}")
        print(f"   Impacto: {rec.expected_impact}")
        print()

if __name__ == "__main__":
    main()