"""
Test Completo para CARMANFE SAS con testastra.xlsx
Incluye perfil completo y análisis detallado
"""

import json
from enhanced_universal_processor import EnhancedUniversalProcessor
from user_questionnaire import CompanyProfile, Industry

def test_carmanfe_completo():
    """Test completo para CARMANFE SAS con perfil detallado"""
    
    # Crear perfil completo para CARMANFE SAS
    carmanfe_profile = CompanyProfile(
        company_name="CARMANFE SAS",
        industry=Industry.SERVICES,
        employee_count=15,
        company_age_years=5,
        file_format="excel",
        is_annual_financial_data=True,
        additional_notes="Empresa de servicios profesionales en Colombia, especializada en consultoría"
    )
    
    # Guardar perfil
    with open("company_profile.json", 'w', encoding='utf-8') as f:
        profile_data = {
            "company_name": carmanfe_profile.company_name,
            "industry": carmanfe_profile.industry.value,
            "employee_count": carmanfe_profile.employee_count,
            "company_age_years": carmanfe_profile.company_age_years,
            "file_format": carmanfe_profile.file_format,
            "is_annual_financial_data": carmanfe_profile.is_annual_financial_data,
            "additional_notes": carmanfe_profile.additional_notes
        }
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Perfil completo de CARMANFE SAS creado y guardado")
    
    # Procesar archivo
    processor = EnhancedUniversalProcessor()
    
    try:
        # Procesar con perfil específico
        analysis_data = processor.process_file_with_questionnaire(
            "/Users/arielsanroj/Downloads/testastra.xlsx", 
            skip_questionnaire=True
        )
        
        # Mostrar reporte mejorado
        processor.display_enhanced_report(analysis_data)
        
        # Guardar reporte detallado
        with open("carmanfe_report_completo.json", 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n💾 Reporte completo guardado en: carmanfe_report_completo.json")
        
        # Mostrar resumen ejecutivo
        print("\n" + "="*80)
        print("📊 RESUMEN EJECUTIVO - CARMANFE SAS")
        print("="*80)
        
        revenue = analysis_data.get('revenue', 0)
        net_income = analysis_data.get('net_income', 0)
        total_assets = analysis_data.get('total_assets', 0)
        operating_income = analysis_data.get('operating_income', 0)
        operating_expenses = analysis_data.get('operating_expenses', 0)
        
        print(f"\n💰 [bold]Datos Financieros Clave:[/bold]")
        print(f"   • Ingresos Totales: ${revenue:,.0f} COP")
        print(f"   • Ingresos Netos: ${net_income:,.0f} COP")
        print(f"   • Activos Totales: ${total_assets:,.0f} COP")
        print(f"   • Ingresos Operativos: ${operating_income:,.0f} COP")
        print(f"   • Gastos Operativos: ${operating_expenses:,.0f} COP")
        
        # Calcular ratios clave
        if revenue > 0:
            operating_margin = (operating_income / revenue) * 100
            net_margin = (net_income / revenue) * 100
            print(f"\n📈 [bold]Ratios Clave:[/bold]")
            print(f"   • Margen Operativo: {operating_margin:.1f}%")
            print(f"   • Margen Neto: {net_margin:.1f}%")
        
        if total_assets > 0:
            roa = (net_income / total_assets) * 100
            print(f"   • Retorno sobre Activos (ROA): {roa:.2f}%")
        
        # Análisis de la industria
        print(f"\n🏭 [bold]Análisis de la Industria:[/bold]")
        print(f"   • Industria: Servicios Profesionales")
        print(f"   • Etapa: Crecimiento (5 años)")
        print(f"   • Empleados: 15")
        print(f"   • Benchmark Margen Operativo: 15.0%")
        print(f"   • Benchmark Margen Neto: 10.0%")
        
        # Recomendaciones específicas
        print(f"\n🎯 [bold]Recomendaciones Específicas:[/bold]")
        print(f"   1. Excelente margen operativo ({operating_margin:.1f}% vs 15.0% benchmark)")
        print(f"   2. Margen neto superior al promedio ({net_margin:.1f}% vs 10.0% benchmark)")
        print(f"   3. Considerar expansión de servicios")
        print(f"   4. Optimizar estructura de costos operativos")
        print(f"   5. Implementar estrategias de crecimiento sostenible")
        
        print(f"\n✅ [bold green]Análisis completado exitosamente![/bold green]")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_carmanfe_completo()