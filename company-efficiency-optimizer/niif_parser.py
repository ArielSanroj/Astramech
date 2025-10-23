#!/usr/bin/env python3
"""
Accurate NIIF Parser for Colombian Financial Statements
Handles ER (P&L) and ESF (Balance Sheet) sheets correctly
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class NIIFParser:
    """Accurate parser for Colombian NIIF financial statements"""
    
    def __init__(self):
        self.currency = "COP"
        self.industry = "professional_services"  # Default, will be updated based on data
        
    def parse_er_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse ER (Estado de Resultados) sheet for P&L data"""
        
        print("📊 Parsing ER sheet (P&L)...")
        
        # Data is in Unnamed: 3 for Sep 2024
        data_column = 'Unnamed: 3'
        
        print(f"   Using data column: {data_column}")
        
        # Extract financial data
        revenue = self._extract_value(df, 'Ingresos de Actividades Ordinarias', data_column)
        cogs = self._extract_value(df, 'Costo de Ventas', data_column)
        sales_expenses = self._extract_value(df, 'Gastos de Ventas', data_column)
        admin_expenses = self._extract_value(df, 'Gastos de Administración', data_column)
        operating_income = self._extract_value(df, 'RESULTADO OPERACIONAL', data_column)
        net_income = self._extract_value(df, 'RESULTADO NETO DEL DEL EJERCICIO', data_column)
        
        # Calculate operating expenses
        operating_expenses = sales_expenses + admin_expenses
        
        print(f"   Revenue: ${revenue:,.0f} COP")
        print(f"   COGS: ${cogs:,.0f} COP")
        print(f"   Operating Expenses: ${operating_expenses:,.0f} COP")
        print(f"   Operating Income: ${operating_income:,.0f} COP")
        print(f"   Net Income: ${net_income:,.0f} COP")
        
        return {
            'revenue': revenue,
            'revenue_ytd': revenue,
            'cogs': cogs,
            'operating_expenses': operating_expenses,
            'operating_expenses_ytd': operating_expenses,
            'operating_income': operating_income,
            'net_income': net_income,
            'net_income_ytd': net_income,
            'sales_expenses': sales_expenses,
            'admin_expenses': admin_expenses
        }
    
    def parse_esf_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse ESF (Estado de Situación Financiera) sheet for Balance Sheet data"""
        
        print("🏦 Parsing ESF sheet (Balance Sheet)...")
        
        # Data is in Unnamed: 3 for Sep 2024
        data_column = 'Unnamed: 3'
        
        print(f"   Using data column: {data_column}")
        
        # Extract balance sheet data
        # Total assets is in row 24 (nan in Unnamed: 1, but has value in Unnamed: 3)
        total_assets = 0
        for i, row in df.iterrows():
            if pd.isna(row['Unnamed: 1']) and pd.notna(row[data_column]) and isinstance(row[data_column], (int, float)):
                if row[data_column] > 1000000000:  # Likely total assets (>1B COP)
                    total_assets = row[data_column]
                    break
        
        cash = self._extract_value(df, 'Efectivo y Equivalentes al Efectivo', data_column)
        receivables = self._extract_value(df, 'Deudores Comerciales y Otras Cuentas por Cobrar', data_column)
        investments = self._extract_value(df, 'Inversiones Largo plazo', data_column)
        fixed_assets = self._extract_value(df, 'Activos Biológicos', data_column)
        
        # Calculate current assets (approximation)
        current_assets = cash + receivables
        
        print(f"   Total Assets: ${total_assets:,.0f} COP")
        print(f"   Cash: ${cash:,.0f} COP")
        print(f"   Receivables: ${receivables:,.0f} COP")
        print(f"   Investments: ${investments:,.0f} COP")
        print(f"   Fixed Assets: ${fixed_assets:,.0f} COP")
        
        return {
            'total_assets': total_assets,
            'cash_and_equivalents': cash,
            'receivables': receivables,
            'investments': investments,
            'fixed_assets': fixed_assets,
            'current_assets': current_assets
        }
    
    def _extract_value(self, df: pd.DataFrame, search_term: str, data_column: str) -> float:
        """Extract value for a specific line item"""
        
        # Look for the search term in Unnamed: 1 column
        mask = df['Unnamed: 1'].str.contains(search_term, case=False, na=False)
        matching_rows = df[mask]
        
        if matching_rows.empty:
            return 0.0
        
        # Get the value from the data column
        value = matching_rows[data_column].iloc[0]
        
        # Handle NaN values
        if pd.isna(value):
            return 0.0
        
        # Convert to float
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def estimate_employees(self, operating_expenses: float, admin_expenses: float) -> int:
        """Estimate employee count from expenses"""
        
        # Use admin expenses as proxy for payroll
        # Assume average monthly salary of 1,000,000 COP
        avg_monthly_salary = 1000000
        
        if admin_expenses > 0:
            # Estimate based on admin expenses (assuming 60% is payroll)
            payroll_estimate = admin_expenses * 0.6
            employees = max(1, int(payroll_estimate / (avg_monthly_salary * 12)))
        else:
            # Fallback to operating expenses
            employees = max(1, int(operating_expenses / (avg_monthly_salary * 12 * 2)))
        
        # Sanity check
        employees = min(employees, 100)  # Cap at 100 employees
        
        print(f"   Estimated employees: {employees} (from admin expenses: ${admin_expenses:,.0f})")
        
        return employees
    
    def calculate_kpis(self, er_data: Dict[str, Any], esf_data: Dict[str, Any], employees: int) -> Dict[str, Any]:
        """Calculate accurate KPIs from parsed data"""
        
        print("📈 Calculating accurate KPIs...")
        
        revenue = er_data.get('revenue', 0)
        cogs = er_data.get('cogs', 0)
        operating_expenses = er_data.get('operating_expenses', 0)
        operating_income = er_data.get('operating_income', 0)
        net_income = er_data.get('net_income', 0)
        total_assets = esf_data.get('total_assets', 0)
        current_assets = esf_data.get('current_assets', 0)
        receivables = esf_data.get('receivables', 0)
        
        # Calculate margins
        gross_margin = (revenue - cogs) / revenue if revenue > 0 else 0
        operating_margin = operating_income / revenue if revenue > 0 else 0
        net_margin = net_income / revenue if revenue > 0 else 0
        
        # Calculate other KPIs
        revenue_per_employee = revenue / employees if employees > 0 else 0
        current_ratio = current_assets / operating_expenses if operating_expenses > 0 else 0
        asset_utilization = revenue / total_assets if total_assets > 0 else 0
        
        print(f"   Gross Margin: {gross_margin:.1%}")
        print(f"   Operating Margin: {operating_margin:.1%}")
        print(f"   Net Margin: {net_margin:.1%}")
        print(f"   Revenue per Employee: ${revenue_per_employee:,.0f} COP")
        print(f"   Current Ratio: {current_ratio:.2f}")
        print(f"   Asset Utilization: {asset_utilization:.1%}")
        
        return {
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'net_margin': net_margin,
            'revenue_per_employee': revenue_per_employee,
            'current_ratio': current_ratio,
            'asset_utilization': asset_utilization
        }
    
    def identify_inefficiencies(self, kpis: Dict[str, Any], er_data: Dict[str, Any], esf_data: Dict[str, Any]) -> list:
        """Identify real inefficiencies based on accurate data"""
        
        print("⚠️ Identifying inefficiencies...")
        
        inefficiencies = []
        
        # Check liquidity
        current_ratio = kpis.get('current_ratio', 0)
        if current_ratio < 1.5:
            inefficiencies.append({
                'issue_type': 'liquidity',
                'kpi_name': 'Current Ratio',
                'current_value': current_ratio,
                'benchmark': 1.5,
                'severity': 'warning' if current_ratio >= 1.0 else 'critical',
                'description': f'Low liquidity: {current_ratio:.2f} vs benchmark 1.5',
                'recommended_agent': 'financial_optimizer'
            })
        
        # Check asset utilization
        asset_utilization = kpis.get('asset_utilization', 0)
        if asset_utilization < 0.5:
            inefficiencies.append({
                'issue_type': 'asset_utilization',
                'kpi_name': 'Asset Utilization',
                'current_value': asset_utilization,
                'benchmark': 0.5,
                'severity': 'critical',
                'description': f'Low asset utilization: {asset_utilization:.1%} vs benchmark 50%',
                'recommended_agent': 'asset_optimizer'
            })
        
        # Check revenue per employee
        revenue_per_employee = kpis.get('revenue_per_employee', 0)
        if revenue_per_employee < 50000000:  # 50M COP per employee
            inefficiencies.append({
                'issue_type': 'productivity',
                'kpi_name': 'Revenue per Employee',
                'current_value': revenue_per_employee,
                'benchmark': 50000000,
                'severity': 'warning',
                'description': f'Low revenue per employee: ${revenue_per_employee:,.0f} vs benchmark $50M',
                'recommended_agent': 'operations_optimizer'
            })
        
        # Check admin expenses ratio
        admin_expenses = er_data.get('admin_expenses', 0)
        revenue = er_data.get('revenue', 0)
        if revenue > 0:
            admin_ratio = admin_expenses / revenue
            if admin_ratio > 0.3:  # 30% of revenue
                inefficiencies.append({
                    'issue_type': 'operational_efficiency',
                    'kpi_name': 'Admin Expenses Ratio',
                    'current_value': admin_ratio,
                    'benchmark': 0.3,
                    'severity': 'warning',
                    'description': f'High admin expenses: {admin_ratio:.1%} vs benchmark 30%',
                    'recommended_agent': 'operations_optimizer'
                })
        
        print(f"   Found {len(inefficiencies)} inefficiencies")
        
        return inefficiencies
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse entire testastra2.xlsx file accurately"""
        
        print("🚀 Parsing testastra2.xlsx with accurate NIIF parser...")
        print("=" * 60)
        
        try:
            # Read the file
            xl = pd.ExcelFile(file_path)
            print(f"📋 Found {len(xl.sheet_names)} sheets: {xl.sheet_names}")
            
            # Parse ER sheet
            df_er = pd.read_excel(file_path, sheet_name='ER')
            er_data = self.parse_er_sheet(df_er)
            
            # Parse ESF sheet
            df_esf = pd.read_excel(file_path, sheet_name='ESF')
            esf_data = self.parse_esf_sheet(df_esf)
            
            # Estimate employees
            employees = self.estimate_employees(
                er_data.get('operating_expenses', 0),
                er_data.get('admin_expenses', 0)
            )
            
            # Calculate KPIs
            kpis = self.calculate_kpis(er_data, esf_data, employees)
            
            # Identify inefficiencies
            inefficiencies = self.identify_inefficiencies(kpis, er_data, esf_data)
            
            # Compile results
            result = {
                'company': 'APRU SAS',
                'currency': self.currency,
                'industry': self.industry,
                'department': 'Finance',
                'employee_count': employees,
                'sheets_processed': ['ER', 'ESF'],
                **er_data,
                **esf_data,
                'kpis': kpis,
                'inefficiencies': inefficiencies
            }
            
            print("\n✅ Accurate parsing completed!")
            print(f"   Company: {result['company']}")
            print(f"   Revenue: ${result['revenue']:,.0f} {result['currency']}")
            print(f"   Net Income: ${result['net_income']:,.0f} {result['currency']}")
            print(f"   Total Assets: ${result['total_assets']:,.0f} {result['currency']}")
            print(f"   Employees: {result['employee_count']}")
            print(f"   Inefficiencies: {len(result['inefficiencies'])}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error parsing file: {e}")
            import traceback
            traceback.print_exc()
            return {}

def main():
    """Test the NIIF parser"""
    
    parser = NIIFParser()
    result = parser.parse_file('/Users/arielsanroj/Downloads/testastra2.xlsx')
    
    if result:
        print("\n📊 PARSING RESULTS SUMMARY")
        print("=" * 60)
        print(f"Company: {result['company']}")
        print(f"Revenue: ${result['revenue']:,.0f} {result['currency']}")
        print(f"Net Income: ${result['net_income']:,.0f} {result['currency']}")
        print(f"Total Assets: ${result['total_assets']:,.0f} {result['currency']}")
        print(f"Employees: {result['employee_count']}")
        print(f"Gross Margin: {result['kpis']['gross_margin']:.1%}")
        print(f"Operating Margin: {result['kpis']['operating_margin']:.1%}")
        print(f"Net Margin: {result['kpis']['net_margin']:.1%}")
        print(f"Inefficiencies: {len(result['inefficiencies'])}")
        
        for ineff in result['inefficiencies']:
            print(f"  - {ineff['kpi_name']}: {ineff['description']}")

if __name__ == "__main__":
    main()