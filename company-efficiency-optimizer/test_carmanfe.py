"""
Test específico para CARMANFE SAS con testastra.xlsx
"""

import json
from enhanced_universal_processor import EnhancedUniversalProcessor
from user_questionnaire import CompanyProfile, Industry

def test_carmanfe():
    """Test específico para CARMANFE SAS"""
    
    # Crear perfil específico para CARMANFE SAS
    carmanfe_profile = CompanyProfile(
        company_name="CARMANFE SAS",
        industry=Industry.SERVICES,
        employee_count=15,
        company_age_years=5,
        file_format="excel",
        is_annual_financial_data=True,
        additional_notes="Empresa de servicios profesionales en Colombia"
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
        
        # Guardar reporte
        with open("carmanfe_report.json", 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n💾 Reporte guardado en: carmanfe_report.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_carmanfe()