"""
Analysis service for orchestrating the complete analysis workflow
"""

import logging
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_ingest import DataIngestion
from tools.kpi_calculator import KPICalculator
from memory_setup import HybridMemorySystem
from ollama_crew import OllamaDiagnosticCrew

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for orchestrating analysis workflows"""
    
    def __init__(self):
        """Initialize the analysis service with required components"""
        self.data_ingestion = DataIngestion()
        self.kpi_calculator = KPICalculator()
        self.memory_system = HybridMemorySystem()
        self.diagnostic_crew = OllamaDiagnosticCrew()
    
    def run_analysis(self, questionnaire_data: Dict[str, Any], file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete analysis workflow
        
        Args:
            questionnaire_data: Company questionnaire responses
            file_data: Processed file data
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Create sample data from inputs
            sample_data = self._create_sample_data_from_inputs(questionnaire_data, file_data)
            
            # Calculate KPIs
            kpi_results = self.kpi_calculator.calculate_all_kpis(sample_data)
            
            # Run diagnostic analysis
            diagnostic_results = self.diagnostic_crew.run_diagnostic_analysis(sample_data)
            
            # Store results in memory system
            self.memory_system.store_analysis_results(
                questionnaire_data.get('company_name', 'Unknown'), 
                {
                    'questionnaire': questionnaire_data,
                    'file_data': file_data,
                    'kpi_results': kpi_results,
                    'diagnostic_results': diagnostic_results
                }
            )
            
            # Return structured results
            return {
                'company_name': questionnaire_data.get('company_name', 'Unknown'),
                'kpi_results': kpi_results,
                'diagnostic_results': diagnostic_results,
                'file_summary': {
                    filename: f"{len(data)} records" 
                    for filename, data in file_data.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            return {
                'error': str(e),
                'company_name': questionnaire_data.get('company_name', 'Unknown')
            }
    
    def _create_sample_data_from_inputs(self, questionnaire_data: Dict[str, Any], file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create sample data structure from questionnaire and file inputs
        
        Args:
            questionnaire_data: Company questionnaire responses
            file_data: Processed file data
            
        Returns:
            Sample data structure for analysis
        """
        # Extract financial data from files
        financial_data = {}
        hr_data = {}
        operational_data = {}
        
        for filename, data in file_data.items():
            if isinstance(data, list) and len(data) > 0:
                # Process structured data
                if 'revenue' in str(data[0]).lower() or 'income' in str(data[0]).lower():
                    financial_data.update(self._extract_financial_metrics(data))
                elif 'employee' in str(data[0]).lower() or 'hr' in str(data[0]).lower():
                    hr_data.update(self._extract_hr_metrics(data))
        
        # Create sample data structure
        sample_data = {
            'financial_data': financial_data,
            'hr_data': hr_data,
            'operational_data': operational_data,
            'company_info': {
                'name': questionnaire_data.get('company_name', 'Unknown'),
                'industry': questionnaire_data.get('industry', 'Unknown'),
                'size': questionnaire_data.get('company_size', 'Unknown'),
                'employee_count': int(questionnaire_data.get('employee_count', 50))
            }
        }
        
        return sample_data
    
    def _extract_financial_metrics(self, data: list) -> Dict[str, Any]:
        """Extract financial metrics from structured data"""
        metrics = {}
        for record in data:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, (int, float)) and value > 0:
                        metrics[key.lower().replace(' ', '_')] = value
        return metrics
    
    def _extract_hr_metrics(self, data: list) -> Dict[str, Any]:
        """Extract HR metrics from structured data"""
        metrics = {}
        for record in data:
            if isinstance(record, dict):
                for key, value in record.items():
                    if isinstance(value, (int, float)) and value > 0:
                        metrics[key.lower().replace(' ', '_')] = value
        return metrics
