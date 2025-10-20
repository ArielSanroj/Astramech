"""
Procesador Mejorado con Integración de Agentes CrewAI v2
Versión compatible con CrewAI 0.203.1 y Python 3.12
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from normalization_layer import NormalizationLayer
from kpi_calculator import KPICalculator
from user_questionnaire import UserQuestionnaire, CompanyProfile, Industry
from agent_recommendation_system_v2 import AgentRecommendationSystem, AgentRecommendation

console = Console()

class EnhancedAgentProcessor:
    """Procesador mejorado que integra agentes CrewAI para análisis especializado"""
    
    def __init__(self):
        """Inicializar el procesador con todos los componentes"""
        self.normalization_layer = NormalizationLayer()
        self.kpi_calculator = KPICalculator()
        self.user_questionnaire = UserQuestionnaire()
        self.agent_system = AgentRecommendationSystem()
        
    def process_file_with_agents(self, file_path: str, skip_questionnaire: bool = False) -> Dict:
        """
        Procesar archivo con integración completa de agentes CrewAI
        
        Args:
            file_path: Ruta del archivo a procesar
            skip_questionnaire: Si saltar el cuestionario y usar perfil existente
            
        Returns:
            Diccionario con análisis completo y resultados de agentes
        """
        console.print(f"\n🚀 [bold]Procesando archivo con Agentes IA:[/bold] {file_path}")
        
        # 1. Cargar o crear perfil de empresa
        if skip_questionnaire:
            profile = self._load_existing_profile()
        else:
            profile = self._run_questionnaire()
        
        if not profile:
            console.print("❌ No se pudo obtener perfil de empresa")
            return {}
        
        # 2. Validar formato de archivo
        if not self._validate_file_format(file_path, profile):
            console.print("❌ Formato de archivo no válido")
            return {}
        
        # 3. Procesar archivo con normalización
        console.print("\n📊 [bold]Normalizando datos financieros...[/bold]")
        analysis_data = self.normalization_layer.normalize_financial_data(file_path)
        
        if not analysis_data:
            console.print("❌ No se pudieron extraer datos del archivo")
            return {}
        
        # 4. Calcular KPIs
        console.print("\n📈 [bold]Calculando KPIs...[/bold]")
        industry = profile.get('industry', 'services')
        kpi_data = self.kpi_calculator.calculate_financial_kpis(analysis_data, industry)
        
        # 5. Analizar KPIs y recomendar agentes
        console.print("\n🤖 [bold]Analizando KPIs y recomendando agentes...[/bold]")
        recommendations = self.agent_system.analyze_kpis_and_recommend_agents(
            kpi_data, analysis_data
        )
        
        # 6. Mostrar recomendaciones
        self._display_agent_recommendations(recommendations)
        
        # 7. Ejecutar agentes recomendados (solo si hay API key)
        execution_results = {}
        if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "placeholder":
            console.print("\n🔧 [bold]Ejecutando agentes especializados...[/bold]")
            execution_results = self.agent_system.execute_agent_recommendations(
                recommendations, analysis_data, profile
            )
        else:
            console.print("\n⚠️ [yellow]API key de OpenAI no configurada. Saltando ejecución de agentes.[/yellow]")
            console.print("   Para habilitar agentes, configura OPENAI_API_KEY en tu archivo .env")
        
        # 8. Generar reporte consolidado
        agent_report = self.agent_system.generate_agent_report(recommendations, execution_results)
        
        # 9. Compilar resultados finales
        final_results = {
            'company_profile': profile,
            'financial_data': analysis_data,
            'kpi_analysis': kpi_data,
            'agent_recommendations': recommendations,
            'agent_execution_results': execution_results,
            'agent_report': agent_report,
            'file_processed': file_path
        }
        
        # 10. Mostrar reporte final
        self._display_final_report(final_results)
        
        return final_results
    
    def _load_existing_profile(self) -> Optional[Dict]:
        """Cargar perfil existente de empresa"""
        profile_path = Path("company_profile.json")
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                console.print("✅ Perfil de empresa cargado exitosamente")
                return profile
            except Exception as e:
                console.print(f"❌ Error cargando perfil: {e}")
        return None
    
    def _run_questionnaire(self) -> Optional[Dict]:
        """Ejecutar cuestionario de usuario"""
        try:
            profile = self.user_questionnaire.run_questionnaire()
            if profile:
                self.user_questionnaire.save_profile(profile)
                return {
                    'company_name': profile.company_name,
                    'industry': profile.industry.value,
                    'employee_count': profile.employee_count,
                    'company_age_years': profile.company_age_years,
                    'file_format': profile.file_format,
                    'is_annual_financial_data': profile.is_annual_financial_data,
                    'additional_notes': profile.additional_notes
                }
        except Exception as e:
            console.print(f"❌ Error en cuestionario: {e}")
        return None
    
    def _validate_file_format(self, file_path: str, profile: Dict) -> bool:
        """Validar que el formato del archivo coincida con el perfil"""
        file_ext = Path(file_path).suffix.lower()
        expected_format = profile.get('file_format', 'excel')
        
        if expected_format == 'excel' and file_ext not in ['.xlsx', '.xls']:
            console.print(f"❌ Se esperaba archivo Excel, pero se recibió: {file_ext}")
            return False
        elif expected_format == 'pdf' and file_ext != '.pdf':
            console.print(f"❌ Se esperaba archivo PDF, pero se recibió: {file_ext}")
            return False
        
        return True
    
    def _display_agent_recommendations(self, recommendations: List[AgentRecommendation]):
        """Mostrar recomendaciones de agentes en formato visual"""
        if not recommendations:
            console.print("✅ No se identificaron problemas críticos que requieran agentes especializados")
            return
        
        console.print(f"\n🤖 [bold]Recomendaciones de Agentes IA ({len(recommendations)} identificadas):[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Prioridad", style="dim", width=8)
        table.add_column("Agente", style="cyan", width=20)
        table.add_column("Problema", style="yellow", width=40)
        table.add_column("Impacto", style="green", width=30)
        table.add_column("Timeline", style="blue", width=12)
        
        for i, rec in enumerate(recommendations[:5], 1):  # Mostrar solo los 5 más importantes
            priority_icon = "🔴" if rec.priority >= 8 else "🟡" if rec.priority >= 6 else "🟢"
            table.add_row(
                f"{priority_icon} {rec.priority}/10",
                rec.agent_type.value.replace('_', ' ').title(),
                rec.problem_description[:37] + "..." if len(rec.problem_description) > 40 else rec.problem_description,
                rec.expected_impact[:27] + "..." if len(rec.expected_impact) > 30 else rec.expected_impact,
                rec.estimated_timeline
            )
        
        console.print(table)
    
    def _display_final_report(self, results: Dict):
        """Mostrar reporte final consolidado"""
        console.print("\n" + "="*80)
        console.print("📊 [bold]REPORTE FINAL CON AGENTES IA[/bold]")
        console.print("="*80)
        
        # Información de la empresa
        profile = results.get('company_profile', {})
        console.print(f"\n🏢 [bold]Empresa:[/bold] {profile.get('company_name', 'N/A')}")
        console.print(f"🏭 [bold]Industria:[/bold] {profile.get('industry', 'N/A')}")
        console.print(f"👥 [bold]Empleados:[/bold] {profile.get('employee_count', 'N/A')}")
        console.print(f"📅 [bold]Antigüedad:[/bold] {profile.get('company_age_years', 'N/A')} años")
        
        # Datos financieros clave
        financial_data = results.get('financial_data', {})
        console.print(f"\n💰 [bold]Datos Financieros Clave:[/bold]")
        console.print(f"   • Ingresos: ${financial_data.get('revenue', 0):,.0f}")
        console.print(f"   • Ingresos Netos: ${financial_data.get('net_income', 0):,.0f}")
        console.print(f"   • Activos Totales: ${financial_data.get('total_assets', 0):,.0f}")
        
        # KPIs principales
        kpi_data = results.get('kpi_analysis', {})
        if kpi_data and isinstance(kpi_data, dict):
            console.print(f"\n📈 [bold]KPIs Principales:[/bold]")
            for kpi_name, kpi_info in kpi_data.items():
                if isinstance(kpi_info, dict) and 'value' in kpi_info:
                    status_icon = "🟢" if kpi_info.get('status') == 'EXCELLENT' else "🟡" if kpi_info.get('status') == 'GOOD' else "🔴"
                    console.print(f"   {status_icon} {kpi_name}: {kpi_info['value']:.1f}% (Benchmark: {kpi_info.get('benchmark', 'N/A')}%)")
        elif kpi_data and isinstance(kpi_data, list):
            console.print(f"\n📈 [bold]KPIs Principales:[/bold]")
            for kpi in kpi_data:
                if isinstance(kpi, dict) and 'name' in kpi:
                    status_icon = "🟢" if kpi.get('status') == 'EXCELLENT' else "🟡" if kpi.get('status') == 'GOOD' else "🔴"
                    console.print(f"   {status_icon} {kpi['name']}: {kpi.get('value', 0):.1f}% (Benchmark: {kpi.get('benchmark', 'N/A')}%)")
        
        # Resumen de agentes ejecutados
        execution_results = results.get('agent_execution_results', {})
        if execution_results:
            console.print(f"\n🤖 [bold]Agentes Ejecutados:[/bold]")
            completed = sum(1 for r in execution_results.values() if r.get('status') == 'completed')
            total = len(execution_results)
            console.print(f"   • Completados: {completed}/{total}")
            
            for agent_name, result in execution_results.items():
                status_icon = "✅" if result.get('status') == 'completed' else "❌"
                console.print(f"   {status_icon} {agent_name.replace('_', ' ').title()}")
        
        # Guardar reporte completo
        self._save_complete_report(results)
        
        console.print(f"\n✅ [bold green]Análisis con Agentes IA completado exitosamente![/bold green]")
    
    def _save_complete_report(self, results: Dict):
        """Guardar reporte completo en archivo"""
        try:
            # Guardar datos completos
            with open("complete_agent_report.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            # Guardar reporte de agentes en markdown
            agent_report = results.get('agent_report', '')
            if agent_report:
                with open("agent_analysis_report.md", 'w', encoding='utf-8') as f:
                    f.write(agent_report)
            
            console.print("💾 Reportes guardados:")
            console.print("   • complete_agent_report.json")
            console.print("   • agent_analysis_report.md")
            
        except Exception as e:
            console.print(f"⚠️ Error guardando reportes: {e}")

def main():
    """Función principal para ejecutar el procesador con agentes"""
    import sys
    
    if len(sys.argv) < 2:
        console.print("❌ Uso: python enhanced_agent_processor_v2.py <archivo> [--skip-questionnaire]")
        console.print("   Ejemplo: python enhanced_agent_processor_v2.py testastra.xlsx --skip-questionnaire")
        return
    
    file_path = sys.argv[1]
    skip_questionnaire = "--skip-questionnaire" in sys.argv
    
    if not os.path.exists(file_path):
        console.print(f"❌ Archivo no encontrado: {file_path}")
        return
    
    # Crear procesador y ejecutar
    processor = EnhancedAgentProcessor()
    results = processor.process_file_with_agents(file_path, skip_questionnaire)
    
    if results:
        console.print(f"\n🎉 Procesamiento completado exitosamente!")
    else:
        console.print(f"\n❌ Error en el procesamiento")

if __name__ == "__main__":
    main()