"""
Test de Integración de Agentes CrewAI con CARMANFE SAS
Prueba el sistema completo con agentes especializados
"""

import json
import os
from enhanced_agent_processor import EnhancedAgentProcessor
from user_questionnaire import CompanyProfile, Industry

def test_agents_carmanfe():
    """Test completo con agentes CrewAI para CARMANFE SAS"""
    
    print("🤖 Test de Integración de Agentes CrewAI")
    print("=" * 50)
    
    # Crear perfil específico para CARMANFE SAS
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
    
    print("✅ Perfil de CARMANFE SAS creado y guardado")
    
    # Crear procesador con agentes
    processor = EnhancedAgentProcessor()
    
    try:
        # Procesar archivo con agentes
        results = processor.process_file_with_agents(
            "/Users/arielsanroj/Downloads/testastra.xlsx", 
            skip_questionnaire=True
        )
        
        if results:
            print("\n🎉 Test completado exitosamente!")
            
            # Mostrar resumen de agentes ejecutados
            execution_results = results.get('agent_execution_results', {})
            if execution_results:
                print(f"\n📊 Resumen de Agentes Ejecutados:")
                for agent_name, result in execution_results.items():
                    status = "✅ Completado" if result.get('status') == 'completed' else "❌ Falló"
                    print(f"   • {agent_name.replace('_', ' ').title()}: {status}")
            
            # Mostrar recomendaciones
            recommendations = results.get('agent_recommendations', [])
            if recommendations:
                print(f"\n🎯 Recomendaciones Generadas: {len(recommendations)}")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec.agent_type.value} (Prioridad: {rec.priority}/10)")
                    print(f"      Problema: {rec.problem_description}")
                    print(f"      Impacto: {rec.expected_impact}")
                    print()
        else:
            print("❌ Error en el procesamiento")
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agents_carmanfe()