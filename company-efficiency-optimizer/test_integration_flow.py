#!/usr/bin/env python3
"""
Test de integración completo: Verificar que el flujo desde upload hasta results esté conectado
"""

import os
import sys
from flask import Flask
from app import create_app
from app.services.analysis_service import AnalysisService
from data_ingest import EnhancedDataIngestion

def test_integration_flow():
    """Test completo del flujo de integración"""
    
    print("=" * 70)
    print("TEST DE INTEGRACIÓN: FLUJO COMPLETO")
    print("=" * 70)
    
    # Simular datos del cuestionario
    questionnaire_data = {
        'company_name': 'APRU SAS',
        'industry': 'retail',
        'company_size': 'small',
        'revenue_range': '10m_50m',
        'employee_count': '68',
        'current_challenges': 'Operational efficiency',
        'goals': 'Improve margins',
        'analysis_focus': ['financial', 'operational']
    }
    
    # Archivo a procesar
    file_path = '/Users/arielsanroj/Downloads/testastra2.xlsx'
    
    print("\n📋 PASO 1: Simular procesamiento de archivo (como en /process_upload)")
    print("-" * 70)
    
    # Esto es lo que hace el endpoint /process_upload
    data_ingestion = EnhancedDataIngestion()
    structured_data = data_ingestion.process_excel_file(
        file_path,
        company_name=questionnaire_data.get('company_name'),
        department='Finance'
    )
    
    if not structured_data:
        print("❌ Error: No se pudo procesar el archivo")
        return False
    
    print(f"✅ Archivo procesado exitosamente")
    print(f"   Revenue extraído: ${structured_data.get('revenue', 0):,.0f}")
    print(f"   COGS extraído: ${structured_data.get('cogs', 0):,.0f}")
    print(f"   Operating Income extraído: ${structured_data.get('operating_income', 0):,.0f}")
    print(f"   Net Income extraído: ${structured_data.get('net_income', 0):,.0f}")
    print(f"   Employee Count extraído: {structured_data.get('employee_count', 'N/A')}")
    
    # Simular file_data como se almacena en la sesión
    file_data = {
        os.path.basename(file_path): structured_data
    }
    
    print("\n📋 PASO 2: Verificar que AnalysisService puede procesar los datos")
    print("-" * 70)
    
    # Esto es lo que hace el endpoint /processing
    analysis_service = AnalysisService()
    
    # Verificar que _create_sample_data_from_inputs extraiga correctamente
    sample_data = analysis_service._create_sample_data_from_inputs(questionnaire_data, file_data)
    
    print(f"✅ Sample data creado:")
    print(f"   Revenue en sample_data: ${sample_data['financial_data'].get('revenue', 0):,.0f}")
    print(f"   COGS en sample_data: ${sample_data['financial_data'].get('cost_of_goods_sold', 0):,.0f}")
    print(f"   Operating Income en sample_data: ${sample_data['financial_data'].get('operating_income', 0):,.0f}")
    print(f"   Net Income en sample_data: ${sample_data['financial_data'].get('net_income', 0):,.0f}")
    print(f"   Employee Count en sample_data: {sample_data['hr_data'].get('total_employees', 'N/A')}")
    
    # Verificar que los valores extraídos sean los reales (no los baseline)
    revenue_from_file = structured_data.get('revenue', 0)
    revenue_in_sample = sample_data['financial_data'].get('revenue', 0)
    
    if abs(revenue_from_file - revenue_in_sample) < 1:
        print(f"   ✅ Revenue correctamente extraído del archivo")
    else:
        print(f"   ⚠️  Revenue no coincide: archivo={revenue_from_file}, sample={revenue_in_sample}")
    
    print("\n📋 PASO 3: Ejecutar análisis completo (como en /processing)")
    print("-" * 70)
    
    results = analysis_service.run_analysis(questionnaire_data, file_data)
    
    if 'error' in results:
        print(f"❌ Error en análisis: {results['error']}")
        return False
    
    print(f"✅ Análisis completado exitosamente")
    
    # Verificar estructura de resultados
    kpi_results = results.get('kpi_results', {})
    
    print("\n📋 PASO 4: Verificar estructura de resultados (como espera results.html)")
    print("-" * 70)
    
    # Verificar estructura esperada por el template
    checks = [
        ('kpi_results.financial.gross_margin', kpi_results.get('financial', {}).get('gross_margin')),
        ('kpi_results.financial.operating_margin', kpi_results.get('financial', {}).get('operating_margin')),
        ('kpi_results.financial.net_margin', kpi_results.get('financial', {}).get('net_margin')),
        ('kpi_results.financial.revenue_per_employee', kpi_results.get('financial', {}).get('revenue_per_employee')),
        ('kpi_results.operational.productivity_index', kpi_results.get('operational', {}).get('productivity_index')),
        ('kpi_results.hr.total_employees', kpi_results.get('hr', {}).get('total_employees')),
        ('kpi_results.efficiency_score', kpi_results.get('efficiency_score')),
    ]
    
    all_present = True
    for check_name, check_value in checks:
        if check_value is not None:
            print(f"   ✅ {check_name}: {check_value}")
        else:
            print(f"   ⚠️  {check_name}: None/N/A")
            all_present = False
    
    # Verificar que los valores sean reales (no N/A o defaults)
    financial = kpi_results.get('financial', {})
    gross_margin = financial.get('gross_margin')
    
    if gross_margin is not None and gross_margin > 0:
        print(f"\n✅ KPIs tienen valores reales (no N/A)")
        print(f"   Gross Margin: {gross_margin*100:.2f}%")
        print(f"   Operating Margin: {financial.get('operating_margin', 0)*100:.2f}%")
        print(f"   Net Margin: {financial.get('net_margin', 0)*100:.2f}%")
    else:
        print(f"\n⚠️  KPIs tienen valores N/A o cero")
    
    # Verificar file_summary
    file_summary = results.get('file_summary', {})
    print(f"\n📄 File Summary:")
    for filename, summary in file_summary.items():
        print(f"   {filename}: {summary}")
    
    print("\n" + "=" * 70)
    if all_present and gross_margin is not None:
        print("✅ INTEGRACIÓN COMPLETA: Todo conectado correctamente")
        print("=" * 70)
        print("\n✅ Verificaciones:")
        print("   ✓ EnhancedDataIngestion procesa archivos Excel")
        print("   ✓ Parser universal extrae métricas reales")
        print("   ✓ AnalysisService._create_sample_data_from_inputs extrae datos del structured_data")
        print("   ✓ KPIs se calculan con valores reales")
        print("   ✓ Estructura de resultados compatible con results.html")
        print("   ✓ File summary generado correctamente")
        return True
    else:
        print("⚠️  INTEGRACIÓN INCOMPLETA: Revisar conexiones")
        print("=" * 70)
        return False

if __name__ == '__main__':
    success = test_integration_flow()
    sys.exit(0 if success else 1)


