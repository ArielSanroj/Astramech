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
import json

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
                r'RESULTADO DEL EJERCICIO',
                r'UTILIDAD NETA',
                r'GANANCIA NETA'
            ]
        }
    
    def process_excel_file(self, file_path: str, company_name: str = None, department: str = 'Finance') -> Dict[str, Any]:
        """
        Process Excel file with multiple sheets and improved accuracy for NIIF/Colombian formats
        
        Args:
            file_path: Path to the Excel file
            company_name: Name of the company
            department: Department being analyzed (Finance, Marketing, IT, etc.)
            
        Returns:
            Dict: Comprehensive financial data with YTD calculations
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
                'department': department,
                'sheets_processed': [],
                'ytd_data': {}  # Year-to-date calculations
            }
            
            # Process each sheet with improved accuracy
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
                
                # Special handling for ERI sheets (NIIF format)
                elif 'ERI' in sheet_name.upper():
                    eri_data = self._extract_eri_data(df, sheet_name)
                    financial_data['ytd_data'].update(eri_data)
                    financial_data['sheets_processed'].append(f"{sheet_name} (ERI - YTD)")
            
            # Calculate YTD metrics from ERI data
            if financial_data['ytd_data']:
                financial_data.update(self._calculate_ytd_metrics(financial_data['ytd_data']))
            
            # Classify industry based on financial data
            industry = self._classify_industry(financial_data)
            financial_data['industry'] = industry
            print(f"\n🏭 Classified industry: {industry}")
            
            # Improved employee estimation with validation
            financial_data['employee_count'] = self._estimate_employee_count_improved(financial_data)
            print(f"👥 Estimated employee count: {financial_data['employee_count']}")
            
            # Fallback: if core metrics missing, try generalized LLM parsing
            if not financial_data.get('revenue') and not financial_data.get('operating_income'):
                try:
                    document_text = self._excel_to_text(file_path)
                    llm_parsed = self.generalized_parse_excel(document_text)
                    if isinstance(llm_parsed, dict) and llm_parsed:
                        # Map into our keys
                        mapped = {
                            'revenue': llm_parsed.get('revenue'),
                            'cogs': llm_parsed.get('cogs'),
                            'operating_expenses': llm_parsed.get('opex'),
                            'operating_income': llm_parsed.get('operating_income'),
                            'net_income': llm_parsed.get('net_income'),
                            'total_assets': llm_parsed.get('total_assets'),
                            'cash_and_equivalents': llm_parsed.get('cash'),
                            'investments': llm_parsed.get('investments'),
                            'fixed_assets': llm_parsed.get('fixed_assets'),
                            'total_liabilities': llm_parsed.get('liabilities'),
                            'total_equity': llm_parsed.get('equity'),
                        }
                        for k, v in mapped.items():
                            if v not in (None, "N/A", ""):
                                financial_data[k] = v
                        if llm_parsed.get('estimated_employees') not in (None, "N/A", ""):
                            financial_data['employee_count'] = int(float(llm_parsed.get('estimated_employees')))
                        if llm_parsed.get('currency'):
                            financial_data['currency'] = llm_parsed.get('currency')
                        if llm_parsed.get('period'):
                            financial_data['period'] = llm_parsed.get('period')
                except Exception as _:
                    pass

            # Validate currency and data consistency
            self._validate_financial_data(financial_data)
            
            return financial_data
            
        except Exception as e:
            print(f"❌ Error processing Excel file: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def _excel_to_text(self, file_path: str) -> str:
        """Convert all Excel sheets to a plain text representation for LLM parsing."""
        try:
            xl = pd.ExcelFile(file_path)
            parts: List[str] = []
            for sheet in xl.sheet_names:
                try:
                    df = xl.parse(sheet)
                    parts.append(f"SHEET: {sheet}\n{df.to_string(index=False)}\n")
                except Exception:
                    continue
            return "\n".join(parts)
        except Exception:
            return ""

    def generalized_parse_excel(self, document_text: str) -> Dict[str, Any]:
        """LLM-assisted fallback parsing for arbitrary Excel layouts."""
        if not document_text:
            return {}
        prompt = (
            "Eres un experto en extracción de datos financieros de archivos Excel, independientemente del formato o idioma. "
            "Analiza la descripción de un archivo Excel (texto con sheets y rows) y extrae un JSON SOLO con estas claves: "
            "revenue, cogs, opex, operating_income, net_income, total_assets, cash, investments, fixed_assets, liabilities, equity, estimated_employees, currency, period. "
            "Si un dato no aparece, usa \"N/A\". Usa COP como moneda por defecto.\n\n"
            "Descripcion:\n" + document_text + "\n\nDevuelve solo JSON válido."
        )
        # Try to use ChatOllama if available
        try:
            from langchain_ollama import ChatOllama
            llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"), base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), temperature=0.2)
            response = llm.invoke(prompt)
            text = response.content if hasattr(response, 'content') else str(response)
            # Extract JSON
            first_brace = text.find('{')
            last_brace = text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                payload = text[first_brace:last_brace+1]
                return json.loads(payload)
        except Exception:
            pass
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
            def rightmost_numeric(series: pd.Series) -> float:
                # Prefer explicit 'Total' column if present
                for col in series.index[::-1]:
                    try:
                        val = series[col]
                        if pd.isna(val):
                            continue
                        # Skip first label-like column
                        if series.index.get_loc(col) == 0:
                            continue
                        num = float(str(val).replace(',', '').replace(' ', ''))
                        return num
                    except Exception:
                        continue
                return 0.0

            # Process each row to find financial figures
            for index, row in df.iterrows():
                if pd.isna(row.iloc[0]):
                    continue
                
                account_name = str(row.iloc[0]).strip()
                total_value = rightmost_numeric(row)
                if total_value == 0:
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
    
    def _extract_eri_data(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Extract data from ERI (Estado de Resultados Integrales) sheets"""
        eri_data = {}
        
        try:
            # Look for revenue line (typically code '4' in NIIF)
            if 'Codigo' in df.columns:
                revenue_row = df[df['Codigo'] == '4']
                if not revenue_row.empty:
                    # Get the latest month column (usually the rightmost)
                    month_columns = [col for col in df.columns if '2025' in str(col)]
                    if month_columns:
                        latest_month = month_columns[-1]
                        eri_data['revenue_ytd'] = revenue_row[latest_month].iloc[0] if latest_month in revenue_row.columns else 0
                        print(f"   📈 Revenue YTD ({latest_month}): ${eri_data['revenue_ytd']:,.0f} COP")
            
            # Look for operating expenses (typically codes starting with '51')
            if 'Codigo' in df.columns:
                opex_rows = df[df['Codigo'].str.startswith('51', na=False)]
                if not opex_rows.empty:
                    month_columns = [col for col in df.columns if '2025' in str(col)]
                    if month_columns:
                        latest_month = month_columns[-1]
                        eri_data['opex_ytd'] = opex_rows[latest_month].sum() if latest_month in opex_rows.columns else 0
                        print(f"   💰 Operating Expenses YTD ({latest_month}): ${eri_data['opex_ytd']:,.0f} COP")
            
            # Calculate net profit
            if 'revenue_ytd' in eri_data and 'opex_ytd' in eri_data:
                eri_data['net_profit_ytd'] = eri_data['revenue_ytd'] - eri_data['opex_ytd']
                print(f"   💵 Net Profit YTD: ${eri_data['net_profit_ytd']:,.0f} COP")
                
        except Exception as e:
            print(f"   ⚠️ Error extracting ERI data: {str(e)}")
            
        return eri_data
    
    def _calculate_ytd_metrics(self, ytd_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate year-to-date metrics from ERI data"""
        metrics = {}
        
        if 'revenue_ytd' in ytd_data:
            metrics['revenue'] = ytd_data['revenue_ytd']
            metrics['revenue_ytd'] = ytd_data['revenue_ytd']
            
        if 'opex_ytd' in ytd_data:
            metrics['operating_expenses'] = ytd_data['opex_ytd']
            metrics['operating_expenses_ytd'] = ytd_data['opex_ytd']
            
        if 'net_profit_ytd' in ytd_data:
            metrics['net_income'] = ytd_data['net_profit_ytd']
            metrics['net_income_ytd'] = ytd_data['net_profit_ytd']
            
        return metrics
    
    def _estimate_employee_count_improved(self, financial_data: Dict[str, Any]) -> int:
        """Improved employee count estimation with better validation"""
        # Try to get from HR data first
        if 'hr_data' in financial_data and 'total_employees' in financial_data['hr_data']:
            return financial_data['hr_data']['total_employees']
        
        # Estimate from operating expenses with better logic
        opex = financial_data.get('operating_expenses', 0)
        opex_ytd = financial_data.get('operating_expenses_ytd', opex)
        
        if opex_ytd > 0:
            # Use YTD data if available, otherwise monthly
            if opex_ytd > opex:
                # YTD data - divide by months to get monthly average
                months_passed = 5  # Assuming May 2025 (ENE-MAY)
                monthly_opex = opex_ytd / months_passed
            else:
                monthly_opex = opex
            
            # Estimate payroll as 60% of operating expenses
            monthly_payroll = monthly_opex * 0.6
            
            # Average monthly salary in Colombia (professional services): ~1,200,000 COP
            avg_monthly_salary = 1200000
            estimated_employees = int(monthly_payroll / avg_monthly_salary)
            
            # Validate estimate (should be reasonable)
            if estimated_employees < 1:
                estimated_employees = 1
            elif estimated_employees > 1000:  # Sanity check
                estimated_employees = 10  # Fallback
                
            print(f"   💼 Estimated from payroll: {estimated_employees} employees")
            return estimated_employees
        
        # Default fallback
        return 10
    
    def _validate_financial_data(self, financial_data: Dict[str, Any]) -> None:
        """Validate financial data for consistency and accuracy"""
        issues = []
        
        # Check for currency consistency
        if financial_data.get('currency') != 'COP':
            issues.append("Currency not set to COP")
        
        # Check for reasonable values
        revenue = financial_data.get('revenue', 0)
        if revenue > 0:
            if revenue < 1000000:  # Less than 1M COP
                issues.append("Revenue seems too low for a company")
            elif revenue > 1000000000000:  # More than 1T COP
                issues.append("Revenue seems too high, check for unit errors")
        
        # Check employee count vs revenue ratio
        employees = financial_data.get('employee_count', 0)
        if employees > 0 and revenue > 0:
            revenue_per_employee = revenue / employees
            if revenue_per_employee < 50000000:  # Less than 50M COP per employee
                issues.append("Revenue per employee seems low")
            elif revenue_per_employee > 2000000000:  # More than 2B COP per employee
                issues.append("Revenue per employee seems high")
        
        if issues:
            print(f"   ⚠️ Data validation issues: {', '.join(issues)}")
        else:
            print(f"   ✅ Data validation passed")

# Global enhanced data ingestion instance
enhanced_data_ingestion = EnhancedDataIngestion()

def get_enhanced_data_ingestion() -> EnhancedDataIngestion:
    """Get the global enhanced data ingestion instance"""
    return enhanced_data_ingestion