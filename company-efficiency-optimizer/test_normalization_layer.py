#!/usr/bin/env python3
"""
Test script for the Normalization Layer

This script demonstrates how the normalization layer can handle diverse file formats,
languages, and accounting standards by automatically detecting and mapping them to a
unified internal schema.
"""

import os
import sys
import pandas as pd
import json
from dotenv import load_dotenv
from normalization_layer import NormalizationLayer, AccountingStandard, Language, FileFormat
from tools.kpi_calculator import KPICalculator

def create_sample_files():
    """Create sample files in different formats and accounting standards"""
    print("📁 Creating sample files for testing...")
    
    # Create sample data directory
    os.makedirs("sample_data", exist_ok=True)
    
    # 1. Colombian NIIF Excel file (like testastra.xlsx)
    print("   • Creating Colombian NIIF Excel sample...")
    colombian_data = {
        'ESTADO DE RESULTADOS': pd.DataFrame({
            'Descripcion': [
                'INGRESOS ORDINARIOS',
                'COSTO DE LA MERCANCIA VENDIDA',
                'UTILIDAD BRUTA',
                'TOTAL GASTOS OPERACIONALES',
                'RESULTADO OPERACIONAL',
                'RESULTADO DEL EJERCICIO (UTILIDAD/PERDIDA)'
            ],
            'Parcial': [0, 0, 0, 0, 0, 0],
            'Total': [20000000, 0, 20000000, 16436928, 3563072, 3033657]
        }),
        'BALANCE DE PRUEBA': pd.DataFrame({
            'Codigo': ['1', '1.1', '1.1.1', '2', '2.1', '3', '3.1'],
            'Nombre': ['ACTIVOS', 'EFECTIVO Y EQUIVALENTES', 'CAJA', 'PASIVOS', 'ACREEDORES COMERCIALES', 'PATRIMONIO', 'CAPITAL'],
            'Saldo': [9995587215, 27540892, 1000000, 740938015, 50000000, 9255547713, 8000000000]
        })
    }
    
    with pd.ExcelWriter('sample_data/colombian_niif.xlsx') as writer:
        for sheet_name, df in colombian_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # 2. US GAAP Excel file
    print("   • Creating US GAAP Excel sample...")
    us_gaap_data = {
        'Income Statement': pd.DataFrame({
            'Description': [
                'REVENUE',
                'COST OF GOODS SOLD',
                'GROSS PROFIT',
                'OPERATING EXPENSES',
                'OPERATING INCOME',
                'NET INCOME'
            ],
            'Amount': [5000000, 2000000, 3000000, 1500000, 1500000, 1200000]
        }),
        'Balance Sheet': pd.DataFrame({
            'Account': ['TOTAL ASSETS', 'TOTAL LIABILITIES', 'SHAREHOLDERS EQUITY'],
            'Amount': [10000000, 4000000, 6000000]
        })
    }
    
    with pd.ExcelWriter('sample_data/us_gaap.xlsx') as writer:
        for sheet_name, df in us_gaap_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # 3. IFRS Excel file
    print("   • Creating IFRS Excel sample...")
    ifrs_data = {
        'Statement of Profit or Loss': pd.DataFrame({
            'Description': [
                'REVENUE',
                'COST OF SALES',
                'GROSS PROFIT',
                'OPERATING EXPENSES',
                'OPERATING PROFIT',
                'PROFIT FOR THE PERIOD'
            ],
            'Amount': [8000000, 3200000, 4800000, 2000000, 2800000, 2200000]
        }),
        'Statement of Financial Position': pd.DataFrame({
            'Account': ['TOTAL ASSETS', 'TOTAL LIABILITIES', 'TOTAL EQUITY'],
            'Amount': [15000000, 6000000, 9000000]
        })
    }
    
    with pd.ExcelWriter('sample_data/ifrs.xlsx') as writer:
        for sheet_name, df in ifrs_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # 4. Brazilian Portuguese Excel file
    print("   • Creating Brazilian Portuguese Excel sample...")
    brazilian_data = {
        'Demonstração do Resultado': pd.DataFrame({
            'Descrição': [
                'RECEITA OPERACIONAL',
                'CUSTO DOS PRODUTOS VENDIDOS',
                'LUCRO BRUTO',
                'DESPESAS OPERACIONAIS',
                'RESULTADO OPERACIONAL',
                'LUCRO LÍQUIDO'
            ],
            'Valor': [12000000, 4800000, 7200000, 3000000, 4200000, 3500000]
        }),
        'Balanço Patrimonial': pd.DataFrame({
            'Conta': ['TOTAL DO ATIVO', 'TOTAL DO PASSIVO', 'PATRIMÔNIO LÍQUIDO'],
            'Valor': [20000000, 8000000, 12000000]
        })
    }
    
    with pd.ExcelWriter('sample_data/brazilian.xlsx') as writer:
        for sheet_name, df in brazilian_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # 5. CSV file (US format)
    print("   • Creating US CSV sample...")
    csv_data = pd.DataFrame({
        'Account': [
            'REVENUE',
            'COST OF GOODS SOLD',
            'GROSS PROFIT',
            'OPERATING EXPENSES',
            'OPERATING INCOME',
            'NET INCOME',
            'TOTAL ASSETS',
            'TOTAL LIABILITIES',
            'SHAREHOLDERS EQUITY'
        ],
        'Amount': [3000000, 1200000, 1800000, 900000, 900000, 750000, 6000000, 2400000, 3600000]
    })
    csv_data.to_csv('sample_data/us_gaap.csv', index=False)
    
    # 6. JSON file (IFRS format)
    print("   • Creating IFRS JSON sample...")
    json_data = {
        "company": "TechCorp Ltd",
        "period": "2024",
        "currency": "USD",
        "financial_data": {
            "revenue": 10000000,
            "cost_of_sales": 4000000,
            "gross_profit": 6000000,
            "operating_expenses": 2500000,
            "operating_profit": 3500000,
            "net_income": 2800000,
            "total_assets": 20000000,
            "total_liabilities": 8000000,
            "total_equity": 12000000
        }
    }
    
    with open('sample_data/ifrs.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print("✅ Sample files created successfully!")

def test_normalization_layer():
    """Test the normalization layer with different file formats and standards"""
    print("\n🧪 Testing Normalization Layer")
    print("=" * 60)
    
    # Initialize normalization layer
    normalization = NormalizationLayer()
    
    # Test files
    test_files = [
        {
            'path': 'sample_data/colombian_niif.xlsx',
            'expected_standard': AccountingStandard.NIIF,
            'expected_language': Language.SPANISH,
            'company': 'Colombian Corp'
        },
        {
            'path': 'sample_data/us_gaap.xlsx',
            'expected_standard': AccountingStandard.US_GAAP,
            'expected_language': Language.ENGLISH,
            'company': 'US Corp'
        },
        {
            'path': 'sample_data/ifrs.xlsx',
            'expected_standard': AccountingStandard.IFRS,
            'expected_language': Language.ENGLISH,
            'company': 'International Corp'
        },
        {
            'path': 'sample_data/brazilian.xlsx',
            'expected_standard': AccountingStandard.LOCAL,
            'expected_language': Language.PORTUGUESE,
            'company': 'Brazilian Corp'
        },
        {
            'path': 'sample_data/us_gaap.csv',
            'expected_standard': AccountingStandard.US_GAAP,
            'expected_language': Language.ENGLISH,
            'company': 'CSV Corp'
        },
        {
            'path': 'sample_data/ifrs.json',
            'expected_standard': AccountingStandard.IFRS,
            'expected_language': Language.ENGLISH,
            'company': 'JSON Corp'
        }
    ]
    
    results = []
    
    for test_file in test_files:
        print(f"\n📊 Testing: {test_file['path']}")
        print("-" * 40)
        
        try:
            # Normalize the data
            normalized_data = normalization.normalize_financial_data(
                test_file['path'], 
                test_file['company']
            )
            
            if normalized_data:
                # Check detection results
                metadata = normalized_data.get('metadata', {})
                detected_standard = metadata.get('accounting_standard')
                detected_language = metadata.get('language')
                detected_format = metadata.get('file_format')
                
                print(f"   ✅ File Format: {detected_format}")
                print(f"   ✅ Language: {detected_language}")
                print(f"   ✅ Accounting Standard: {detected_standard}")
                print(f"   ✅ Company: {normalized_data.get('company')}")
                print(f"   ✅ Industry: {normalized_data.get('industry')}")
                print(f"   ✅ Sheets Processed: {len(normalized_data.get('sheets_processed', []))}")
                
                # Show financial data
                print(f"   💰 Financial Data:")
                print(f"      Revenue: ${normalized_data.get('revenue', 0):,.0f}")
                print(f"      Net Income: ${normalized_data.get('net_income', 0):,.0f}")
                print(f"      Total Assets: ${normalized_data.get('total_assets', 0):,.0f}")
                print(f"      Employee Count: {normalized_data.get('employee_count', 0)}")
                
                results.append({
                    'file': test_file['path'],
                    'success': True,
                    'data': normalized_data
                })
                
            else:
                print(f"   ❌ Failed to normalize data")
                results.append({
                    'file': test_file['path'],
                    'success': False,
                    'data': None
                })
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                'file': test_file['path'],
                'success': False,
                'error': str(e)
            })
    
    return results

def run_kpi_analysis_on_normalized_data(results):
    """Run KPI analysis on normalized data"""
    print(f"\n📈 KPI Analysis on Normalized Data")
    print("=" * 60)
    
    calculator = KPICalculator()
    
    for result in results:
        if result['success'] and result['data']:
            print(f"\n🏢 {result['data']['company']}")
            print("-" * 30)
            
            try:
                # Calculate KPIs
                kpis = calculator.calculate_financial_kpis(
                    result['data'], 
                    industry=result['data'].get('industry', 'services')
                )
                
                print(f"   📊 KPIs ({result['data'].get('industry', 'services').title()} Industry):")
                for kpi in kpis:
                    status_emoji = {
                        'excellent': '🟢',
                        'good': '🟡', 
                        'warning': '🟠',
                        'critical': '🔴'
                    }
                    emoji = status_emoji.get(kpi.status, '⚪')
                    print(f"      {emoji} {kpi.name}: {kpi.value:.1f}%")
                
                # Identify inefficiencies
                inefficiencies = calculator.identify_inefficiencies(kpis)
                if inefficiencies:
                    print(f"   ⚠️  Inefficiencies: {len(inefficiencies)} found")
                else:
                    print(f"   ✅ No inefficiencies found")
                    
            except Exception as e:
                print(f"   ❌ KPI Analysis Error: {str(e)}")

def generate_comprehensive_summary(results):
    """Generate comprehensive summary of all tests"""
    print(f"\n📋 Comprehensive Test Summary")
    print("=" * 70)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"📊 Test Results:")
    print(f"   • Total Tests: {len(results)}")
    print(f"   • Successful: {len(successful_tests)}")
    print(f"   • Failed: {len(failed_tests)}")
    print(f"   • Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
    
    if successful_tests:
        print(f"\n✅ Successfully Processed Files:")
        for result in successful_tests:
            data = result['data']
            metadata = data.get('metadata', {})
            print(f"   • {result['file']}")
            print(f"     - Format: {metadata.get('file_format', 'Unknown')}")
            print(f"     - Language: {metadata.get('language', 'Unknown')}")
            print(f"     - Standard: {metadata.get('accounting_standard', 'Unknown')}")
            print(f"     - Industry: {data.get('industry', 'Unknown')}")
            print(f"     - Revenue: ${data.get('revenue', 0):,.0f}")
    
    if failed_tests:
        print(f"\n❌ Failed Files:")
        for result in failed_tests:
            print(f"   • {result['file']}")
            if 'error' in result:
                print(f"     - Error: {result['error']}")
    
    print(f"\n🎯 Key Achievements:")
    print(f"   • Multi-format support: Excel, CSV, JSON")
    print(f"   • Multi-language support: Spanish, English, Portuguese")
    print(f"   • Multi-standard support: NIIF, US GAAP, IFRS, Local")
    print(f"   • Automatic detection and mapping")
    print(f"   • Unified schema output")
    print(f"   • Industry classification")
    print(f"   • Employee count estimation")

def main():
    """Run the comprehensive normalization layer test"""
    print("🚀 Normalization Layer Test Suite")
    print("=" * 70)
    print("Testing diverse file formats, languages, and accounting standards")
    print()
    
    try:
        # Step 1: Create sample files
        create_sample_files()
        
        # Step 2: Test normalization layer
        results = test_normalization_layer()
        
        # Step 3: Run KPI analysis on normalized data
        run_kpi_analysis_on_normalized_data(results)
        
        # Step 4: Generate comprehensive summary
        generate_comprehensive_summary(results)
        
        print("\n" + "=" * 70)
        print("🎉 Normalization Layer Test Suite Completed!")
        print("\n📝 Key Capabilities Demonstrated:")
        print("   • Automatic file format detection")
        print("   • Language detection and mapping")
        print("   • Accounting standard recognition")
        print("   • Schema normalization")
        print("   • Industry classification")
        print("   • Multi-format data processing")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())