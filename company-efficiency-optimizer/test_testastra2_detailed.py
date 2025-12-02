#!/usr/bin/env python3
"""
Detailed test for testastra2.xlsx to see what data is extracted
"""

import os
import sys
import pandas as pd
from data_ingest import EnhancedDataIngestion

def test_detailed_parsing():
    """Detailed test of testastra2.xlsx parsing"""
    
    file_path = '/Users/arielsanroj/Downloads/testastra2.xlsx'
    
    print(f"📊 Analyzing file: {file_path}\n")
    
    # Initialize data ingestion
    data_ingestion = EnhancedDataIngestion()
    
    # Get sheet names first
    excel_file = pd.ExcelFile(file_path)
    print(f"📑 Sheets found: {len(excel_file.sheet_names)}")
    for i, sheet in enumerate(excel_file.sheet_names, 1):
        print(f"   {i}. {sheet}")
    
    print("\n" + "=" * 60)
    print("Parsing with EnhancedDataIngestion")
    print("=" * 60)
    
    structured_data = data_ingestion.process_excel_file(
        file_path,
        company_name="TestAstra2",
        department='Finance'
    )
    
    print("\n📋 Extracted Data:")
    print(json.dumps(structured_data, indent=2, default=str))
    
    # Check specific sheets
    print("\n" + "=" * 60)
    print("Examining key sheets")
    print("=" * 60)
    
    # Check ESF sheet (P&L)
    if 'ESF' in excel_file.sheet_names:
        print("\n📊 ESF Sheet (P&L):")
        df_esf = pd.read_excel(file_path, sheet_name='ESF')
        print(f"   Shape: {df_esf.shape}")
        print(f"   Columns: {list(df_esf.columns)}")
        print("\n   First 10 rows:")
        print(df_esf.head(10).to_string())
    
    # Check ER sheet
    if 'ER' in excel_file.sheet_names:
        print("\n📊 ER Sheet:")
        df_er = pd.read_excel(file_path, sheet_name='ER')
        print(f"   Shape: {df_er.shape}")
        print(f"   Columns: {list(df_er.columns)}")
        print("\n   First 10 rows:")
        print(df_er.head(10).to_string())
    
    # Check balance sheet
    if 'balance prueba act' in excel_file.sheet_names:
        print("\n📊 Balance Sheet (balance prueba act):")
        df_bs = pd.read_excel(file_path, sheet_name='balance prueba act')
        print(f"   Shape: {df_bs.shape}")
        print(f"   Columns: {list(df_bs.columns)}")
        print("\n   First 15 rows:")
        print(df_bs.head(15).to_string())

if __name__ == '__main__':
    import json
    test_detailed_parsing()





