"""
Enhanced Universal File Processor with User Questionnaire
Integrates user questionnaire with file processing for improved accuracy
"""

import typer
import json
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from user_questionnaire import UserQuestionnaire, CompanyProfile, Industry
from normalization_layer import NormalizationLayer
from kpi_calculator import KPICalculator

console = Console()

class EnhancedUniversalProcessor:
    """Enhanced file processor with user questionnaire integration"""
    
    def __init__(self):
        self.questionnaire = UserQuestionnaire()
        self.normalization_layer = NormalizationLayer()
        self.kpi_calculator = KPICalculator()
    
    def validate_file_format(self, file_path: str, expected_format: str) -> bool:
        """Validate that the file format matches user expectation"""
        file_extension = Path(file_path).suffix.lower()
        
        if expected_format == "excel" and file_extension in [".xlsx", ".xls"]:
            return True
        elif expected_format == "pdf" and file_extension == ".pdf":
            return True
        else:
            console.print(f"[red]❌ Error: El archivo debe ser {expected_format.upper()}, pero recibiste {file_extension}[/red]")
            return False
    
    def enhance_analysis_with_profile(self, analysis_data: Dict[str, Any], profile: CompanyProfile) -> Dict[str, Any]:
        """Enhance analysis data with user profile information"""
        
        # Override industry classification with user input
        analysis_data['industry'] = profile.industry.value
        
        # Override employee count with user input
        if 'employee_count' in analysis_data:
            analysis_data['employee_count'] = profile.employee_count
        
        # Add company profile information
        analysis_data['company_profile'] = {
            'company_name': profile.company_name,
            'industry': profile.industry.value,
            'employee_count': profile.employee_count,
            'company_age_years': profile.company_age_years,
            'file_format': profile.file_format,
            'is_annual_financial_data': profile.is_annual_financial_data,
            'additional_notes': profile.additional_notes
        }
        
        # Add industry-specific insights
        analysis_data['industry_insights'] = self._get_industry_insights(profile.industry, profile.company_age_years)
        
        return analysis_data
    
    def _get_industry_insights(self, industry: Industry, company_age: int) -> Dict[str, Any]:
        """Get industry-specific insights based on company profile"""
        insights = {
            'industry_benchmarks': self._get_industry_benchmarks(industry),
            'maturity_analysis': self._get_maturity_analysis(company_age),
            'growth_expectations': self._get_growth_expectations(industry, company_age)
        }
        return insights
    
    def _get_industry_benchmarks(self, industry: Industry) -> Dict[str, Any]:
        """Get industry-specific benchmark information"""
        benchmarks = {
            Industry.MANUFACTURING: {
                'gross_margin': 25.0,
                'operating_margin': 12.0,
                'net_margin': 8.0,
                'revenue_per_employee': 250000,
                'description': 'Manufacturing companies typically have moderate margins due to material costs'
            },
            Industry.SERVICES: {
                'gross_margin': 40.0,
                'operating_margin': 15.0,
                'net_margin': 10.0,
                'revenue_per_employee': 300000,
                'description': 'Service companies often have higher margins due to lower material costs'
            },
            Industry.RETAIL: {
                'gross_margin': 30.0,
                'operating_margin': 8.0,
                'net_margin': 5.0,
                'revenue_per_employee': 200000,
                'description': 'Retail companies have variable margins depending on product mix'
            },
            Industry.TECHNOLOGY: {
                'gross_margin': 70.0,
                'operating_margin': 25.0,
                'net_margin': 15.0,
                'revenue_per_employee': 500000,
                'description': 'Technology companies typically have high margins due to scalable products'
            },
            Industry.HEALTHCARE: {
                'gross_margin': 50.0,
                'operating_margin': 18.0,
                'net_margin': 12.0,
                'revenue_per_employee': 400000,
                'description': 'Healthcare companies have stable margins due to consistent demand'
            }
        }
        
        return benchmarks.get(industry, benchmarks[Industry.SERVICES])
    
    def _get_maturity_analysis(self, company_age: int) -> Dict[str, Any]:
        """Analyze company maturity based on age"""
        if company_age < 2:
            return {
                'stage': 'Startup',
                'characteristics': 'High growth potential, variable profitability',
                'focus_areas': ['Revenue growth', 'Market penetration', 'Operational efficiency']
            }
        elif company_age < 5:
            return {
                'stage': 'Growth',
                'characteristics': 'Expanding operations, establishing market position',
                'focus_areas': ['Scalability', 'Process optimization', 'Market expansion']
            }
        elif company_age < 10:
            return {
                'stage': 'Established',
                'characteristics': 'Stable operations, consistent performance',
                'focus_areas': ['Operational excellence', 'Cost management', 'Innovation']
            }
        else:
            return {
                'stage': 'Mature',
                'characteristics': 'Well-established, focus on efficiency and innovation',
                'focus_areas': ['Cost optimization', 'Digital transformation', 'Market diversification']
            }
    
    def _get_growth_expectations(self, industry: Industry, company_age: int) -> Dict[str, Any]:
        """Get growth expectations based on industry and company age"""
        base_growth = {
            Industry.TECHNOLOGY: 15.0,
            Industry.SERVICES: 10.0,
            Industry.HEALTHCARE: 8.0,
            Industry.MANUFACTURING: 6.0,
            Industry.RETAIL: 5.0
        }
        
        # Adjust for company age
        age_multiplier = 1.5 if company_age < 3 else 1.0 if company_age < 7 else 0.8
        
        expected_growth = base_growth.get(industry, 8.0) * age_multiplier
        
        return {
            'expected_annual_growth': expected_growth,
            'growth_drivers': self._get_growth_drivers(industry),
            'risk_factors': self._get_risk_factors(industry, company_age)
        }
    
    def _get_growth_drivers(self, industry: Industry) -> list:
        """Get industry-specific growth drivers"""
        drivers = {
            Industry.TECHNOLOGY: ['Innovation', 'Digital transformation', 'Market expansion'],
            Industry.SERVICES: ['Client acquisition', 'Service diversification', 'Operational efficiency'],
            Industry.HEALTHCARE: ['Population growth', 'Aging demographics', 'Technology adoption'],
            Industry.MANUFACTURING: ['Automation', 'Supply chain optimization', 'Product innovation'],
            Industry.RETAIL: ['E-commerce', 'Customer experience', 'Omnichannel strategy']
        }
        return drivers.get(industry, ['Market expansion', 'Operational efficiency', 'Innovation'])
    
    def _get_risk_factors(self, industry: Industry, company_age: int) -> list:
        """Get industry and age-specific risk factors"""
        risks = ['Economic cycles', 'Competition', 'Regulatory changes']
        
        if company_age < 3:
            risks.extend(['Cash flow management', 'Market validation', 'Talent acquisition'])
        
        if industry == Industry.TECHNOLOGY:
            risks.extend(['Technology obsolescence', 'Cybersecurity threats'])
        elif industry == Industry.MANUFACTURING:
            risks.extend(['Supply chain disruptions', 'Raw material costs'])
        elif industry == Industry.RETAIL:
            risks.extend(['Consumer behavior changes', 'E-commerce competition'])
        
        return risks
    
    def display_enhanced_report(self, analysis_data: Dict[str, Any]) -> None:
        """Display enhanced analysis report with profile information"""
        
        profile = analysis_data.get('company_profile', {})
        industry_insights = analysis_data.get('industry_insights', {})
        
        # Company Overview
        console.print("\n" + "="*80)
        console.print(f"🏢 [bold blue]{profile.get('company_name', 'Empresa')}[/bold blue]")
        console.print(f"🏭 Industria: [bold]{profile.get('industry', 'N/A').title()}[/bold]")
        employee_count = profile.get('employee_count', 'N/A')
        if isinstance(employee_count, (int, float)):
            console.print(f"👥 Empleados: [bold]{employee_count:,}[/bold]")
        else:
            console.print(f"👥 Empleados: [bold]{employee_count}[/bold]")
        company_age = profile.get('company_age_years', 'N/A')
        if isinstance(company_age, (int, float)):
            console.print(f"📅 Antigüedad: [bold]{company_age} años[/bold]")
        else:
            console.print(f"📅 Antigüedad: [bold]{company_age}[/bold]")
        console.print("="*80)
        
        # Financial Overview
        financial_data = analysis_data.get('financial_data', {})
        console.print(f"\n💰 [bold]Resumen Financiero:[/bold]")
        console.print(f"   • Ingresos: ${financial_data.get('revenue', 0):,.0f}")
        console.print(f"   • Ingresos Netos: ${financial_data.get('net_income', 0):,.0f}")
        console.print(f"   • Activos Totales: ${financial_data.get('total_assets', 0):,.0f}")
        console.print(f"   • Empleados: {financial_data.get('employee_count', 0):,}")
        
        # Show additional financial data if available
        if 'gross_profit' in analysis_data:
            console.print(f"   • Ganancia Bruta: ${analysis_data.get('gross_profit', 0):,.0f}")
        if 'operating_income' in analysis_data:
            console.print(f"   • Ingresos Operativos: ${analysis_data.get('operating_income', 0):,.0f}")
        if 'operating_expenses' in analysis_data:
            console.print(f"   • Gastos Operativos: ${analysis_data.get('operating_expenses', 0):,.0f}")
        
        # Show data from normalization layer if not in financial_data
        if analysis_data.get('revenue', 0) > 0:
            console.print(f"   • Ingresos (P&L): ${analysis_data.get('revenue', 0):,.0f}")
        if analysis_data.get('net_income', 0) > 0:
            console.print(f"   • Ingresos Netos (P&L): ${analysis_data.get('net_income', 0):,.0f}")
        if analysis_data.get('total_assets', 0) > 0:
            console.print(f"   • Activos Totales (Balance): ${analysis_data.get('total_assets', 0):,.0f}")
        if analysis_data.get('operating_income', 0) > 0:
            console.print(f"   • Ingresos Operativos (P&L): ${analysis_data.get('operating_income', 0):,.0f}")
        if analysis_data.get('operating_expenses', 0) > 0:
            console.print(f"   • Gastos Operativos (P&L): ${analysis_data.get('operating_expenses', 0):,.0f}")
        
        # Industry Insights
        if industry_insights:
            benchmarks = industry_insights.get('industry_benchmarks', {})
            maturity = industry_insights.get('maturity_analysis', {})
            
            console.print(f"\n📊 [bold]Análisis de la Industria:[/bold]")
            console.print(f"   • Benchmarks: Margen Bruto {benchmarks.get('gross_margin', 0)}%, "
                        f"Margen Operativo {benchmarks.get('operating_margin', 0)}%")
            console.print(f"   • Etapa de la Empresa: {maturity.get('stage', 'N/A')}")
            console.print(f"   • Características: {maturity.get('characteristics', 'N/A')}")
        
        # KPIs
        kpis = analysis_data.get('kpis', [])
        if kpis:
            console.print(f"\n📈 [bold]Indicadores Clave de Rendimiento:[/bold]")
            for kpi in kpis:
                status_emoji = "🟢" if kpi.get('status') == 'EXCELLENT' else "🟡" if kpi.get('status') == 'GOOD' else "🔴"
                console.print(f"   {status_emoji} {kpi.get('name', 'N/A')}: {kpi.get('value', 0):.1f}% "
                            f"(Benchmark: {kpi.get('benchmark', 0)}%)")
        
        # Recommendations
        recommendations = analysis_data.get('recommendations', [])
        if recommendations:
            console.print(f"\n🎯 [bold]Recomendaciones:[/bold]")
            for i, rec in enumerate(recommendations, 1):
                console.print(f"   {i}. {rec}")
        
        console.print(f"\n[bold green]✅ Análisis completado exitosamente![/bold green]")
    
    def process_file_with_questionnaire(self, file_path: str, skip_questionnaire: bool = False) -> Dict[str, Any]:
        """Process file with integrated questionnaire"""
        
        # Load existing profile or run questionnaire
        profile = None
        if not skip_questionnaire:
            profile = self.questionnaire.load_profile()
            
            if profile is None:
                console.print("[yellow]No se encontró un perfil existente. Ejecutando cuestionario...[/yellow]")
                profile = self.questionnaire.run_questionnaire()
                self.questionnaire.save_profile(profile)
            else:
                console.print("[green]✅ Perfil de empresa cargado exitosamente[/green]")
                if not typer.confirm("¿Usar este perfil o crear uno nuevo?", default=True):
                    profile = self.questionnaire.run_questionnaire()
                    self.questionnaire.save_profile(profile)
        
        # Validate file format
        if profile and not self.validate_file_format(file_path, profile.file_format):
            raise typer.Exit(1)
        
        # Process file
        console.print(f"\n🚀 [bold]Procesando archivo: {file_path}[/bold]")
        normalized_data = self.normalization_layer.normalize_financial_data(file_path, profile.company_name if profile else None)
        
        # Calculate KPIs
        console.print("📈 [bold]Calculando KPIs...[/bold]")
        industry = profile.industry.value if profile else normalized_data.get('industry', 'services')
        kpis = self.kpi_calculator.calculate_financial_kpis(normalized_data, industry)
        
        # Combine results
        analysis_data = {
            **normalized_data,
            'kpis': kpis,
            'recommendations': self._generate_recommendations(kpis, profile)
        }
        
        # Enhance with profile information
        if profile:
            analysis_data = self.enhance_analysis_with_profile(analysis_data, profile)
        
        return analysis_data
    
    def _generate_recommendations(self, kpis: list, profile: Optional[CompanyProfile]) -> list:
        """Generate recommendations based on KPIs and profile"""
        recommendations = []
        
        for kpi in kpis:
            if kpi.get('status') == 'CRITICAL':
                recommendations.append(f"URGENTE: {kpi.get('description', '')}")
            elif kpi.get('status') == 'POOR':
                recommendations.append(f"Mejorar: {kpi.get('description', '')}")
        
        if profile:
            maturity = self._get_maturity_analysis(profile.company_age_years)
            recommendations.extend(maturity.get('focus_areas', []))
        
        if not recommendations:
            recommendations.append("Continuar monitoreando KPIs regularmente")
            recommendations.append("Implementar estrategias de optimización específicas")
        
        return recommendations[:5]  # Limit to 5 recommendations

def main(
    file_path: str = typer.Argument(..., help="Ruta al archivo financiero"),
    skip_questionnaire: bool = typer.Option(False, "--skip-questionnaire", help="Saltar cuestionario y usar configuración por defecto"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Archivo de salida para el reporte JSON"),
    company_name: Optional[str] = typer.Option(None, "--company", "-c", help="Nombre de la empresa (opcional)")
):
    """Procesador Universal de Archivos Financieros con Cuestionario"""
    
    processor = EnhancedUniversalProcessor()
    
    try:
        # Process file with questionnaire
        analysis_data = processor.process_file_with_questionnaire(file_path, skip_questionnaire)
        
        # Display enhanced report
        processor.display_enhanced_report(analysis_data)
        
        # Save report if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
            console.print(f"\n💾 [green]Reporte guardado en: {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    typer.run(main)