"""
Enhanced Data Ingestion Module for Company Efficiency Optimizer

This module handles data ingestion from various sources with enhanced support for:
- Multiple Excel sheets (P&L, Balance Sheet, etc.)
- Colombian accounting formats (NIIF)
- Department-specific data extraction
- Dynamic industry classification
"""

import os
import pandas as pd
import requests
import json
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import pdf2image
from io import BytesIO
import csv
import re

load_dotenv()

class EnhancedDataIngestion:
    """Enhanced data ingestion handler for various data sources and formats"""
    
    def __init__(self):
        """Initialize the enhanced data ingestion system"""
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Colombian accounting patterns
        self.colombian_patterns = {
            'revenue': [
                r'INGRESOS ORDINARIOS',
                r'VENTAS BRUTAS',
                r'INGRESOS OPERACIONALES'
            ],
            'cogs': [
                r'COSTO DE LA MERCANCIA VENDIDA',
                r'COSTO DE VENTAS',
                r'COSTO DE VENTA'
            ],
            'gross_profit': [
                r'UTILIDAD BRUTA',
                r'GANANCIA BRUTA'
            ],
            'operating_expenses': [
                r'TOTAL GASTOS OPERACIONALES',
                r'GASTOS DE ADMINISTRACION',
                r'GASTOS OPERACIONALES'
            ],
            'operating_income': [
                r'RESULTADO OPERACIONAL',
                r'UTILIDAD OPERACIONAL'
            ],
            'net_income': [
                r'RESULTADO DEL EJERCICIO.*UTILIDAD',
                r'UTILIDAD NETA',
                r'GANANCIA NETA'
            ]
        }
    
    def process_excel_file(self, file_path: str, company_name: str = None) -> Dict[str, Any]:
        """
        Process Excel file with multiple sheets
        
        Args:
            file_path: Path to the Excel file
            company_name: Name of the company
            
        Returns:
            Dict: Comprehensive financial data
        """
        try:
            # Get all sheet names
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            print(f"📊 Found {len(sheet_names)} sheets: {sheet_names}")
            
            financial_data = {
                'company': company_name or 'Unknown Company',
                'currency': 'COP',  # Default to Colombian Pesos
                'period': 'Unknown',
                'sheets_processed': []
            }
            
            # Process each sheet
            for sheet_name in sheet_names:
                print(f"\n📋 Processing sheet: {sheet_name}")
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Determine sheet type and process accordingly
                sheet_type = self._classify_sheet(sheet_name, df)
                print(f"   Sheet type: {sheet_type}")
                
                if sheet_type == 'pl_statement':
                    pl_data = self._extract_pl_data(df)
                    financial_data.update(pl_data)
                    financial_data['sheets_processed'].append(f"{sheet_name} (P&L)")
                    
                elif sheet_type == 'balance_sheet':
                    bs_data = self._extract_balance_sheet_data(df)
                    financial_data.update(bs_data)
                    financial_data['sheets_processed'].append(f"{sheet_name} (Balance Sheet)")
                    
                elif sheet_type == 'cash_flow':
                    cf_data = self._extract_cash_flow_data(df)
                    financial_data.update(cf_data)
                    financial_data['sheets_processed'].append(f"{sheet_name} (Cash Flow)")
                    
                elif sheet_type == 'hr_data':
                    hr_data = self._extract_hr_data(df)
                    financial_data['hr_data'] = hr_data
                    financial_data['sheets_processed'].append(f"{sheet_name} (HR)")
            
            # Classify industry based on financial data
            industry = self._classify_industry(financial_data)
            financial_data['industry'] = industry
            print(f"\n🏭 Classified industry: {industry}")
            
            # Estimate employee count if not available
            if 'employee_count' not in financial_data or financial_data['employee_count'] == 0:
                financial_data['employee_count'] = self._estimate_employee_count(financial_data)
                print(f"👥 Estimated employee count: {financial_data['employee_count']}")
            
            return financial_data
            
        except Exception as e:
            print(f"❌ Error processing Excel file: {str(e)}")
            return {}
    
    def _classify_sheet(self, sheet_name: str, df: pd.DataFrame) -> str:
        """Classify the type of financial sheet"""
        sheet_name_lower = sheet_name.lower()
        
        # Check sheet name patterns
        if any(keyword in sheet_name_lower for keyword in ['resultados', 'pl', 'profit', 'income']):
            return 'pl_statement'
        elif any(keyword in sheet_name_lower for keyword in ['balance', 'activo', 'pasivo', 'patrimonio']):
            return 'balance_sheet'
        elif any(keyword in sheet_name_lower for keyword in ['flujo', 'cash', 'efectivo']):
            return 'cash_flow'
        elif any(keyword in sheet_name_lower for keyword in ['hr', 'empleado', 'personal', 'trabajador']):
            return 'hr_data'
        
        # Check content patterns
        content_text = ' '.join([str(val) for val in df.values.flatten() if pd.notna(val)])
        content_lower = content_text.lower()
        
        if any(keyword in content_lower for keyword in ['ventas', 'ingresos', 'utilidad', 'ganancia']):
            return 'pl_statement'
        elif any(keyword in content_lower for keyword in ['activo', 'pasivo', 'patrimonio', 'efectivo']):
            return 'balance_sheet'
        elif any(keyword in content_lower for keyword in ['flujo', 'efectivo', 'cash']):
            return 'cash_flow'
        
        return 'unknown'
    
    def _extract_pl_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract P&L data from DataFrame"""
        pl_data = {}
        
        try:
            # Process each row to find financial figures
            for index, row in df.iterrows():
                if pd.isna(row.iloc[0]):
                    continue
                
                account_name = str(row.iloc[0]).strip()
                total_value = 0
                
                # Get the total value from the last column
                try:
                    if not pd.isna(row.iloc[-1]):
                        total_value = float(row.iloc[-1])
                except:
                    continue
                
                # Match against Colombian accounting patterns
                for key, patterns in self.colombian_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, account_name, re.IGNORECASE):
                            if key == 'operating_expenses':
                                pl_data[key] = abs(total_value)  # Make positive
                            else:
                                pl_data[key] = total_value
                            print(f"   Found {key}: ${total_value:,.0f}")
                            break
                
                # Special handling for revenue if not found
                if 'revenue' not in pl_data and 'VENTAS' in account_name and total_value > 0:
                    pl_data['revenue'] = total_value
                    print(f"   Found revenue (alternative): ${total_value:,.0f}")
            
            # Calculate derived metrics
            if 'revenue' in pl_data and 'cogs' in pl_data:
                pl_data['gross_profit'] = pl_data['revenue'] - pl_data['cogs']
            elif 'gross_profit' in pl_data and 'revenue' in pl_data:
                pl_data['cogs'] = pl_data['revenue'] - pl_data['gross_profit']
            
            return pl_data
            
        except Exception as e:
            print(f"❌ Error extracting P&L data: {str(e)}")
            return {}
    
    def _extract_balance_sheet_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract balance sheet data from DataFrame"""
        bs_data = {}
        
        try:
            # Process each row to find balance sheet figures
            for index, row in df.iterrows():
                if pd.isna(row.iloc[0]):
                    continue
                
                # Account name is typically in the 4th column (index 3)
                account_name = str(row.iloc[3]).strip() if not pd.isna(row.iloc[3]) else ""
                final_balance = 0
                
                # Get the final balance from the last column
                try:
                    if not pd.isna(row.iloc[-1]):
                        final_balance = float(row.iloc[-1])
                except:
                    continue
                
                # Match balance sheet accounts
                if "Activo" in account_name and "Clase" in str(row.iloc[0]):
                    bs_data['total_assets'] = abs(final_balance)
                    print(f"   Found Total Assets: ${final_balance:,.0f}")
                    
                elif "Pasivo" in account_name and "Clase" in str(row.iloc[0]):
                    bs_data['total_liabilities'] = abs(final_balance)
                    print(f"   Found Total Liabilities: ${final_balance:,.0f}")
                    
                elif "Patrimonio" in account_name and "Clase" in str(row.iloc[0]):
                    bs_data['total_equity'] = abs(final_balance)
                    print(f"   Found Total Equity: ${final_balance:,.0f}")
                    
                elif "Efectivo y equivalentes" in account_name and "Grupo" in str(row.iloc[0]):
                    bs_data['cash_and_equivalents'] = abs(final_balance)
                    print(f"   Found Cash: ${final_balance:,.0f}")
                    
                elif "Inversiones" in account_name and "Grupo" in str(row.iloc[0]):
                    bs_data['investments'] = abs(final_balance)
                    print(f"   Found Investments: ${final_balance:,.0f}")
                    
                elif "Deudores comerciales" in account_name and "Grupo" in str(row.iloc[0]):
                    bs_data['receivables'] = abs(final_balance)
                    print(f"   Found Receivables: ${final_balance:,.0f}")
                    
                elif "Propiedad planta y equipo" in account_name and "Grupo" in str(row.iloc[0]):
                    bs_data['fixed_assets'] = abs(final_balance)
                    print(f"   Found Fixed Assets: ${final_balance:,.0f}")
            
            return bs_data
            
        except Exception as e:
            print(f"❌ Error extracting balance sheet data: {str(e)}")
            return {}
    
    def _extract_cash_flow_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract cash flow data from DataFrame"""
        cf_data = {}
        
        try:
            # Process cash flow data
            for index, row in df.iterrows():
                if pd.isna(row.iloc[0]):
                    continue
                
                account_name = str(row.iloc[0]).strip()
                total_value = 0
                
                try:
                    if not pd.isna(row.iloc[-1]):
                        total_value = float(row.iloc[-1])
                except:
                    continue
                
                # Match cash flow patterns
                if 'flujo de efectivo' in account_name.lower():
                    cf_data['net_cash_flow'] = total_value
                    print(f"   Found Net Cash Flow: ${total_value:,.0f}")
                
            return cf_data
            
        except Exception as e:
            print(f"❌ Error extracting cash flow data: {str(e)}")
            return {}
    
    def _extract_hr_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract HR data from DataFrame"""
        hr_data = {}
        
        try:
            # Process HR data
            employee_count = 0
            departments = []
            
            for index, row in df.iterrows():
                if pd.isna(row.iloc[0]):
                    continue
                
                # Look for employee-related data
                row_text = ' '.join([str(val) for val in row if pd.notna(val)])
                
                if 'empleado' in row_text.lower() or 'trabajador' in row_text.lower():
                    # Try to extract numbers
                    numbers = re.findall(r'\d+', row_text)
                    if numbers:
                        employee_count = max(employee_count, int(numbers[0]))
                
                if 'departamento' in row_text.lower() or 'area' in row_text.lower():
                    departments.append(row_text)
            
            hr_data = {
                'employee_count': employee_count,
                'departments': departments
            }
            
            if employee_count > 0:
                print(f"   Found Employee Count: {employee_count}")
            
            return hr_data
            
        except Exception as e:
            print(f"❌ Error extracting HR data: {str(e)}")
            return {}
    
    def _classify_industry(self, financial_data: Dict[str, Any]) -> str:
        """Classify industry based on financial data"""
        try:
            # Get key metrics
            revenue = financial_data.get('revenue', 0)
            total_assets = financial_data.get('total_assets', 0)
            cogs = financial_data.get('cogs', 0)
            gross_margin = 0
            
            if revenue > 0:
                gross_margin = ((revenue - cogs) / revenue) * 100
            
            # Industry classification logic
            if gross_margin > 80:
                return 'services'  # High margin suggests services
            elif gross_margin > 40:
                return 'manufacturing'  # Medium margin suggests manufacturing
            elif total_assets > revenue * 10:
                return 'real_estate'  # High asset-to-revenue ratio
            else:
                return 'retail'  # Default to retail
                
        except Exception as e:
            print(f"❌ Error classifying industry: {str(e)}")
            return 'services'  # Default fallback
    
    def _estimate_employee_count(self, financial_data: Dict[str, Any]) -> int:
        """Estimate employee count based on financial metrics"""
        try:
            revenue = financial_data.get('revenue', 0)
            total_assets = financial_data.get('total_assets', 0)
            industry = financial_data.get('industry', 'services')
            
            # Industry-specific estimates
            if industry == 'services':
                # Professional services: $200K-500K per employee
                if revenue > 0:
                    return max(5, int(revenue / 300000))
            elif industry == 'manufacturing':
                # Manufacturing: $100K-300K per employee
                if revenue > 0:
                    return max(10, int(revenue / 200000))
            elif industry == 'retail':
                # Retail: $50K-150K per employee
                if revenue > 0:
                    return max(5, int(revenue / 100000))
            
            # Fallback based on assets
            if total_assets > 0:
                return max(5, int(total_assets / 100000000))  # $100M per employee
            
            return 10  # Default minimum
            
        except Exception as e:
            print(f"❌ Error estimating employee count: {str(e)}")
            return 10
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available data"""
        summary = {
            'hr_data': {'file': f"{self.data_dir}/hr_data.csv", 'exists': False, 'records': 0},
            'financial_data': {'file': f"{self.data_dir}/financial_data.csv", 'exists': False, 'records': 0},
            'extracted_data': {'file': f"{self.data_dir}/extracted_financial_data.json", 'exists': False}
        }
        
        # Check HR data
        if os.path.exists(summary['hr_data']['file']):
            try:
                df = pd.read_csv(summary['hr_data']['file'])
                summary['hr_data']['exists'] = True
                summary['hr_data']['records'] = len(df)
            except:
                pass
        
        # Check financial data
        if os.path.exists(summary['financial_data']['file']):
            try:
                df = pd.read_csv(summary['financial_data']['file'])
                summary['financial_data']['exists'] = True
                summary['financial_data']['records'] = len(df)
            except:
                pass
        
        # Check extracted data
        summary['extracted_data']['exists'] = os.path.exists(summary['extracted_data']['file'])
        
        return summary

# Global enhanced data ingestion instance
enhanced_data_ingestion = EnhancedDataIngestion()

def get_enhanced_data_ingestion() -> EnhancedDataIngestion:
    """Get the global enhanced data ingestion instance"""
    return enhanced_data_ingestion