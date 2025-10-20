"""
Data Ingestion Module for Company Efficiency Optimizer

This module handles data ingestion from various sources:
- Financial data (P&L statements, CSV files, PDFs)
- HR data (BambooHR API, CSV exports)
- Operational data (various formats)
"""

import os
import pandas as pd
import requests
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import pdf2image
from io import BytesIO
import csv

load_dotenv()

class DataIngestion:
    """Data ingestion handler for various data sources"""
    
    def __init__(self):
        """Initialize the data ingestion system"""
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_hr_data(self, company_id: str = None) -> pd.DataFrame:
        """
        Fetch HR data from BambooHR API
        
        Args:
            company_id: BambooHR company identifier
            
        Returns:
            pd.DataFrame: HR data including employee metrics
        """
        try:
            api_key = os.getenv('BAMBOOHR_API_KEY')
            if not api_key:
                print("⚠️ BambooHR API key not found, using sample data")
                return self._create_sample_hr_data()
            
            # BambooHR API endpoint for employee data
            url = f"https://api.bamboohr.com/api/gateway.php/{company_id}/v1/reports/custom"
            headers = {
                "Authorization": f"Basic {api_key}",
                "Accept": "application/json"
            }
            
            # Request employee data including termination dates for turnover calculation
            params = {
                "format": "json",
                "fields": "employeeNumber,firstName,lastName,hireDate,terminationDate,department,jobTitle"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data['employees'])
            
            # Save to CSV
            df.to_csv(f"{self.data_dir}/hr_data.csv", index=False)
            print(f"✅ Fetched HR data: {len(df)} employees")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching HR data: {str(e)}")
            print("📝 Using sample HR data instead")
            return self._create_sample_hr_data()
    
    def fetch_financial_data(self, source: str = "quickbooks") -> pd.DataFrame:
        """
        Fetch financial data from QuickBooks or other sources
        
        Args:
            source: Data source ("quickbooks", "csv", "manual")
            
        Returns:
            pd.DataFrame: Financial data
        """
        if source == "quickbooks":
            return self._fetch_quickbooks_data()
        elif source == "csv":
            return self._load_csv_financial_data()
        else:
            return self._create_sample_financial_data()
    
    def _fetch_quickbooks_data(self) -> pd.DataFrame:
        """Fetch data from QuickBooks API"""
        try:
            api_key = os.getenv('QUICKBOOKS_API_KEY')
            if not api_key:
                print("⚠️ QuickBooks API key not found, using sample data")
                return self._create_sample_financial_data()
            
            # QuickBooks API implementation would go here
            # This is a placeholder for the actual API integration
            print("📝 QuickBooks API integration not implemented yet")
            return self._create_sample_financial_data()
            
        except Exception as e:
            print(f"❌ Error fetching QuickBooks data: {str(e)}")
            return self._create_sample_financial_data()
    
    def _load_csv_financial_data(self) -> pd.DataFrame:
        """Load financial data from CSV file"""
        csv_path = f"{self.data_dir}/financial_data.csv"
        
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                print(f"✅ Loaded financial data from CSV: {len(df)} records")
                return df
            except Exception as e:
                print(f"❌ Error loading CSV: {str(e)}")
        
        return self._create_sample_financial_data()
    
    def process_pdf_financial_statement(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process PDF financial statement using OCR
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict: Extracted financial data
        """
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            extracted_text = ""
            for image in images:
                # OCR the image
                text = pytesseract.image_to_string(image)
                extracted_text += text + "\n"
            
            # Parse the extracted text for financial data
            financial_data = self._parse_financial_text(extracted_text)
            
            # Save extracted data
            with open(f"{self.data_dir}/extracted_financial_data.json", 'w') as f:
                json.dump(financial_data, f, indent=2)
            
            print(f"✅ Processed PDF: {pdf_path}")
            return financial_data
            
        except Exception as e:
            print(f"❌ Error processing PDF: {str(e)}")
            return {}
    
    def _parse_financial_text(self, text: str) -> Dict[str, Any]:
        """
        Parse extracted text to find financial figures
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Dict: Parsed financial data
        """
        financial_data = {}
        
        # Simple pattern matching for common financial terms
        patterns = {
            'revenue': [r'revenue[:\s]*\$?([\d,]+)', r'total revenue[:\s]*\$?([\d,]+)'],
            'cogs': [r'cost of goods sold[:\s]*\$?([\d,]+)', r'cogs[:\s]*\$?([\d,]+)'],
            'gross_profit': [r'gross profit[:\s]*\$?([\d,]+)'],
            'operating_expenses': [r'operating expenses[:\s]*\$?([\d,]+)', r'opex[:\s]*\$?([\d,]+)'],
            'operating_income': [r'operating income[:\s]*\$?([\d,]+)', r'ebit[:\s]*\$?([\d,]+)'],
            'net_income': [r'net income[:\s]*\$?([\d,]+)', r'net profit[:\s]*\$?([\d,]+)']
        }
        
        import re
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Clean and convert to number
                    value_str = match.group(1).replace(',', '').replace('$', '')
                    try:
                        financial_data[key] = float(value_str)
                        break
                    except ValueError:
                        continue
        
        return financial_data
    
    def _create_sample_hr_data(self) -> pd.DataFrame:
        """Create sample HR data for testing"""
        sample_data = {
            'employeeNumber': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'firstName': ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Tom', 'Amy', 'Chris', 'Emma'],
            'lastName': ['Smith', 'Doe', 'Johnson', 'Wilson', 'Brown', 'Davis', 'Miller', 'Garcia', 'Martinez', 'Anderson'],
            'hireDate': ['2023-01-15', '2023-03-20', '2022-11-10', '2023-06-05', '2022-08-30', 
                        '2023-02-14', '2022-12-01', '2023-04-18', '2023-01-08', '2022-09-25'],
            'terminationDate': [None, '2024-01-15', None, None, '2023-12-20', None, None, None, None, '2024-02-10'],
            'department': ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Sales', 'Engineering', 'Marketing', 'Engineering', 'Sales'],
            'jobTitle': ['Sales Rep', 'Marketing Manager', 'Software Engineer', 'HR Specialist', 'Accountant', 
                        'Sales Manager', 'Senior Engineer', 'Marketing Coordinator', 'DevOps Engineer', 'Sales Rep']
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(f"{self.data_dir}/hr_data.csv", index=False)
        print("📝 Created sample HR data")
        return df
    
    def _create_sample_financial_data(self) -> pd.DataFrame:
        """Create sample financial data for testing"""
        sample_data = {
            'period': ['Q1_2024', 'Q2_2024', 'Q3_2024', 'Q4_2024'],
            'revenue': [1000000, 1100000, 1050000, 1200000],
            'cogs': [700000, 770000, 735000, 840000],
            'gross_profit': [300000, 330000, 315000, 360000],
            'operating_expenses': [200000, 220000, 210000, 240000],
            'operating_income': [100000, 110000, 105000, 120000],
            'net_income': [80000, 88000, 84000, 96000],
            'employee_count': [45, 47, 50, 52]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(f"{self.data_dir}/financial_data.csv", index=False)
        print("📝 Created sample financial data")
        return df
    
    def calculate_turnover_rate(self, hr_df: pd.DataFrame) -> float:
        """
        Calculate turnover rate from HR data
        
        Args:
            hr_df: HR DataFrame with termination dates
            
        Returns:
            float: Turnover rate percentage
        """
        try:
            # Count employees who left in the last 12 months
            current_date = pd.Timestamp.now()
            one_year_ago = current_date - pd.DateOffset(months=12)
            
            # Convert termination dates
            hr_df['terminationDate'] = pd.to_datetime(hr_df['terminationDate'], errors='coerce')
            
            # Count terminations in last 12 months
            recent_terminations = hr_df[
                (hr_df['terminationDate'] >= one_year_ago) & 
                (hr_df['terminationDate'] <= current_date)
            ].shape[0]
            
            # Calculate average headcount
            avg_headcount = len(hr_df)  # Simplified calculation
            
            # Calculate turnover rate
            turnover_rate = (recent_terminations / avg_headcount) * 100 if avg_headcount > 0 else 0
            
            print(f"📊 Calculated turnover rate: {turnover_rate:.2f}%")
            return turnover_rate
            
        except Exception as e:
            print(f"❌ Error calculating turnover rate: {str(e)}")
            return 0.0
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary of all available data
        
        Returns:
            Dict: Summary of data sources and records
        """
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

# Global data ingestion instance
data_ingestion = DataIngestion()

def get_data_ingestion() -> DataIngestion:
    """Get the global data ingestion instance"""
    return data_ingestion