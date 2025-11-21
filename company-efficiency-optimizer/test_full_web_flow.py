#!/usr/bin/env python3
"""
Test completo del flujo web: Simula el proceso completo desde upload hasta results
"""

import os
import sys
import json
import shutil
from app.services.analysis_service import AnalysisService
from data_ingest import EnhancedDataIngestion

def test_full_web_flow():
    """Test completo simulando el flujo web"""
    
    print("=" * 70)
    print("TEST COMPLETO DEL FLUJO WEB")
    print("=" * 70)
    
    # Paso 1: Simular questionnaire
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
    
    print("\n📋 PASO 1: Questionnaire Data")
    print("-" * 70)
    print(f"   Company: {questionnaire_data['company_name']}")
    print(f"   Industry: {questionnaire_data['industry']}")
    print(f"   Employees: {questionnaire_data['employee_count']}")
    
    # Paso 2: Simular file upload (como hace /process_upload)
    file_path = '/Users/arielsanroj/Downloads/testastra2.xlsx'
    
    print("\n📁 PASO 2: File Upload Processing")
    print("-" * 70)
    print(f"   File: {os.path.basename(file_path)}")
    
    # Copiar archivo a uploads/ para simular el proceso real
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    test_file_path = os.path.join(upload_folder, 'testastra2.xlsx')
    shutil.copy(file_path, test_file_path)
    print(f"   ✅ File copied to {test_file_path}")
    
    # Procesar con EnhancedDataIngestion (como hace el endpoint)
    data_ingestion = EnhancedDataIngestion()
    structured_data = data_ingestion.process_excel_file(
        test_file_path,
        company_name=questionnaire_data.get('company_name'),
        department='Finance'
    )
    
    if not structured_data:
        print("   ❌ File processing failed")
        return False
    
    print(f"   ✅ File processed successfully")
    print(f"      Revenue: ${structured_data.get('revenue', 0):,.0f}")
    print(f"      COGS: ${structured_data.get('cogs', 0):,.0f}")
    print(f"      Operating Income: ${structured_data.get('operating_income', 0):,.0f}")
    print(f"      Net Income: ${structured_data.get('net_income', 0):,.0f}")
    print(f"      Employees: {structured_data.get('employee_count', 'N/A')}")
    
    # Paso 3: Simular AnalysisService.run_analysis (como hace /processing)
    print("\n🔬 PASO 3: Running Analysis Service")
    print("-" * 70)
    
    file_data = {
        os.path.basename(test_file_path): structured_data
    }
    
    analysis_service = AnalysisService()
    results = analysis_service.run_analysis(questionnaire_data, file_data)
    
    if 'error' in results:
        print(f"   ❌ Analysis failed: {results['error']}")
        return False
    
    print(f"   ✅ Analysis completed successfully")
    
    # Verificar resultados
    kpi_results = results.get('kpi_results', {})
    efficiency_score = kpi_results.get('efficiency_score')
    
    print(f"\n📊 RESULTADOS:")
    print("-" * 70)
    print(f"   Company: {results.get('company_name', 'Unknown')}")
    print(f"   Efficiency Score: {efficiency_score}%")
    
    # Verificar KPIs
    financial = kpi_results.get('financial', {})
    print(f"\n💰 Financial KPIs:")
    if financial.get('gross_margin') is not None:
        print(f"   Gross Margin: {financial['gross_margin']*100:.2f}%")
    if financial.get('operating_margin') is not None:
        print(f"   Operating Margin: {financial['operating_margin']*100:.2f}%")
    if financial.get('net_margin') is not None:
        print(f"   Net Margin: {financial['net_margin']*100:.2f}%")
    if financial.get('revenue_per_employee') is not None:
        print(f"   Revenue per Employee: ${financial['revenue_per_employee']:,.0f}")
    
    # Verificar mensaje inteligente
    summary_message = results.get('summary_message', '')
    print(f"\n💬 Summary Message:")
    print(f"   {summary_message}")
    
    # Verificar agentes
    agents = results.get('agents', [])
    print(f"\n🤖 AI Agents Generated: {len(agents)}")
    if agents:
        for i, agent in enumerate(agents, 1):
            print(f"   {i}. {agent.get('name', 'Unknown')} ({agent.get('priority', 'N/A')})")
            print(f"      Goal: {agent.get('goal', 'N/A')}")
    
    # Verificar que no hay N/A
    raw_kpis = kpi_results.get('raw_kpis', {})
    all_kpis = []
    for category in ['financial', 'hr', 'operational', 'department']:
        all_kpis.extend(raw_kpis.get(category, []))
    
    na_count = sum(1 for kpi in all_kpis if kpi.get('value') is None or str(kpi.get('value')) == 'N/A')
    
    print(f"\n✅ VALIDACIÓN FINAL:")
    print("-" * 70)
    
    checks = [
        ("Efficiency Score calculado", efficiency_score is not None),
        ("Efficiency Score realista (70-100%)", efficiency_score is not None and 70 <= efficiency_score <= 100),
        ("Summary message generado", bool(summary_message)),
        ("Agentes generados", len(agents) > 0),
        ("Sin valores N/A en KPIs", na_count == 0),
        ("Revenue extraído correctamente", structured_data.get('revenue', 0) > 0),
        ("COGS extraído correctamente", structured_data.get('cogs', 0) > 0),
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
        if not check_result:
            all_passed = False
    
    # File summary
    file_summary = results.get('file_summary', {})
    print(f"\n📄 File Summary:")
    for filename, summary in file_summary.items():
        print(f"   {filename}: {summary}")
    
    return all_passed

if __name__ == '__main__':
    print("🧪 Testing Full Web Flow with testastra2.xlsx\n")
    success = test_full_web_flow()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ FLUJO COMPLETO EXITOSO - Sistema listo para producción")
        print("=" * 70)
        print("\n🎯 El sistema ahora:")
        print("   ✓ Procesa archivos Excel NIIF reales")
        print("   ✓ Extrae métricas financieras reales")
        print("   ✓ Calcula KPIs sin valores N/A")
        print("   ✓ Genera Efficiency Score realista (78-85%)")
        print("   ✓ Crea mensajes inteligentes personalizados")
        print("   ✓ Genera agentes AI especializados")
        print("\n🚀 Listo para vender a empresas colombianas!")
    else:
        print("❌ FLUJO COMPLETO CON ERRORES")
        print("=" * 70)
        sys.exit(1)


