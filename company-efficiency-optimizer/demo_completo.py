"""
Demo Completo del Sistema de Cuestionario y Procesamiento
Muestra el flujo completo desde el cuestionario hasta el análisis
"""

import typer
from rich.console import Console
from rich.panel import Panel
from user_questionnaire import UserQuestionnaire, CompanyProfile, Industry
from enhanced_universal_processor import EnhancedUniversalProcessor

console = Console()

def main():
    """Demo completo del sistema"""
    
    console.print("[bold blue]🎯 Demo Completo del Sistema de Cuestionario[/bold blue]")
    console.print("Este demo muestra el flujo completo desde el cuestionario hasta el análisis\n")
    
    # Crear un perfil de demostración
    demo_profile = CompanyProfile(
        company_name="APRU SAS",
        industry=Industry.SERVICES,
        employee_count=100,
        company_age_years=8,
        file_format="excel",
        is_annual_financial_data=True,
        additional_notes="Empresa de servicios profesionales en tecnología"
    )
    
    questionnaire = UserQuestionnaire()
    processor = EnhancedUniversalProcessor()
    
    # Mostrar el perfil de demostración
    console.print("[bold cyan]📋 Perfil de Demostración:[/bold cyan]")
    questionnaire.display_summary(demo_profile)
    
    # Guardar el perfil
    questionnaire.save_profile(demo_profile, "demo_profile.json")
    console.print("[green]✅ Perfil guardado para uso posterior[/green]")
    
    # Simular procesamiento de archivo
    console.print("\n[bold cyan]🚀 Simulando Procesamiento de Archivo:[/bold cyan]")
    
    # Crear datos de análisis simulados
    mock_analysis_data = {
        'company_name': 'APRU SAS',
        'industry': 'services',
        'financial_data': {
            'revenue': 496910820,
            'net_income': 193750140,
            'total_assets': 1397989689,
            'employee_count': 100,
            'gross_profit': 325430951,
            'operating_income': 193750140,
            'operating_expenses': 292439703
        },
        'kpis': [
            {
                'name': 'Gross Margin',
                'value': 65.5,
                'benchmark': 40.0,
                'status': 'EXCELLENT',
                'description': 'Gross profit margin: 65.5% vs 40.0% benchmark'
            },
            {
                'name': 'Operating Margin',
                'value': 39.0,
                'benchmark': 15.0,
                'status': 'EXCELLENT',
                'description': 'Operating profit margin: 39.0% vs 15.0% benchmark'
            },
            {
                'name': 'Revenue per Employee',
                'value': 4969108,
                'benchmark': 300000,
                'status': 'EXCELLENT',
                'description': 'Revenue per employee: $4,969,108 vs $300,000 benchmark'
            }
        ],
        'recommendations': [
            'Mantener excelente rendimiento operativo',
            'Considerar expansión de servicios',
            'Optimizar estructura de costos',
            'Implementar estrategias de crecimiento sostenible'
        ],
        'company_profile': {
            'company_name': 'APRU SAS',
            'industry': 'services',
            'employee_count': 100,
            'company_age_years': 8,
            'file_format': 'excel',
            'is_annual_financial_data': True,
            'additional_notes': 'Empresa de servicios profesionales en tecnología'
        },
        'industry_insights': {
            'industry_benchmarks': {
                'gross_margin': 40.0,
                'operating_margin': 15.0,
                'net_margin': 10.0,
                'revenue_per_employee': 300000,
                'description': 'Service companies often have higher margins due to lower material costs'
            },
            'maturity_analysis': {
                'stage': 'Established',
                'characteristics': 'Stable operations, consistent performance',
                'focus_areas': ['Operational excellence', 'Cost management', 'Innovation']
            },
            'growth_expectations': {
                'expected_annual_growth': 10.0,
                'growth_drivers': ['Client acquisition', 'Service diversification', 'Operational efficiency'],
                'risk_factors': ['Economic cycles', 'Competition', 'Regulatory changes']
            }
        }
    }
    
    # Mostrar reporte mejorado
    processor.display_enhanced_report(mock_analysis_data)
    
    # Mostrar instrucciones de uso
    console.print("\n" + "="*80)
    console.print("[bold green]📚 Instrucciones de Uso del Sistema[/bold green]")
    console.print("="*80)
    
    instructions = """
[bold]1. Ejecutar Cuestionario Interactivo:[/bold]
   python demo_questionnaire.py
   
[bold]2. Procesar Archivo con Cuestionario:[/bold]
   python enhanced_universal_processor.py tu_archivo.xlsx
   
[bold]3. Procesar Archivo sin Cuestionario:[/bold]
   python enhanced_universal_processor.py tu_archivo.xlsx --skip-questionnaire
   
[bold]4. Guardar Reporte:[/bold]
   python enhanced_universal_processor.py tu_archivo.xlsx --output reporte.json

[bold]Beneficios del Cuestionario:[/bold]
✅ Benchmarks específicos por industria
✅ Análisis de madurez de la empresa
✅ Recomendaciones personalizadas
✅ Validación de formato de archivo
✅ Estimación precisa de empleados
✅ Contexto adicional para el análisis
    """
    
    panel = Panel(
        instructions,
        title="[bold blue]Guía de Uso[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    
    console.print("\n[bold green]🎉 Demo completado exitosamente![/bold green]")
    console.print("El sistema está listo para procesar archivos financieros con análisis mejorado.")

if __name__ == "__main__":
    typer.run(main)