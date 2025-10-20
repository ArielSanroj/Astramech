"""
Test del Sistema de Cuestionario
Prueba el cuestionario con datos simulados
"""

import json
from user_questionnaire import UserQuestionnaire, CompanyProfile, Industry

def test_questionnaire():
    """Test del cuestionario con datos simulados"""
    
    # Crear un perfil de prueba
    test_profile = CompanyProfile(
        company_name="Empresa de Prueba SAS",
        industry=Industry.SERVICES,
        employee_count=50,
        company_age_years=5,
        file_format="excel",
        is_annual_financial_data=True,
        additional_notes="Empresa de consultoría en tecnología"
    )
    
    questionnaire = UserQuestionnaire()
    
    # Mostrar el perfil de prueba
    print("🧪 Perfil de Prueba Creado:")
    questionnaire.display_summary(test_profile)
    
    # Guardar el perfil
    questionnaire.save_profile(test_profile, "test_profile.json")
    
    # Cargar el perfil
    loaded_profile = questionnaire.load_profile("test_profile.json")
    
    if loaded_profile:
        print("\n✅ Perfil cargado exitosamente:")
        print(f"   Empresa: {loaded_profile.company_name}")
        print(f"   Industria: {loaded_profile.industry.value}")
        print(f"   Empleados: {loaded_profile.employee_count}")
        print(f"   Antigüedad: {loaded_profile.company_age_years} años")
        print(f"   Formato: {loaded_profile.file_format}")
        print(f"   Datos anuales: {loaded_profile.is_annual_financial_data}")
    
    # Probar la integración con el procesador
    print("\n🔗 Probando integración con procesador...")
    
    from enhanced_universal_processor import EnhancedUniversalProcessor
    processor = EnhancedUniversalProcessor()
    
    # Simular datos de análisis
    mock_analysis_data = {
        'financial_data': {
            'revenue': 1000000,
            'net_income': 150000,
            'total_assets': 2000000,
            'employee_count': 50
        },
        'kpis': [
            {
                'name': 'Operating Margin',
                'value': 20.0,
                'benchmark': 15.0,
                'status': 'EXCELLENT',
                'description': 'Operating profit margin: 20.0% vs 15.0% benchmark'
            }
        ],
        'recommendations': [
            'Continuar monitoreando KPIs regularmente',
            'Implementar estrategias de optimización específicas'
        ]
    }
    
    # Mostrar reporte mejorado
    processor.display_enhanced_report(mock_analysis_data)
    
    print("\n🎉 Test completado exitosamente!")

if __name__ == "__main__":
    test_questionnaire()