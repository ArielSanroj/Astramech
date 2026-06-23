"""
Analysis service for orchestrating the complete analysis workflow
"""

import logging
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_ingest import EnhancedDataIngestion
from tools.kpi_calculator import KPICalculator
from memory_setup import HybridMemorySystem
from ollama_crew import OllamaDiagnosticCrew
from app.services.analysis_helpers import (
    create_sample_data_from_inputs,
    describe_file_payload,
    generate_summary_message,
)

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for orchestrating analysis workflows"""
    
    def __init__(self):
        """Initialize the analysis service with required components"""
        self.data_ingestion = EnhancedDataIngestion()
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
            sample_data = create_sample_data_from_inputs(questionnaire_data, file_data)
            
            # Calculate KPIs
            kpi_results = self.kpi_calculator.calculate_all_kpis(sample_data)
            
            # Run diagnostic analysis
            diagnostic_results = self.diagnostic_crew.run_diagnostic_analysis(sample_data)
            
            # Generate AI agents based on real KPIs
            agents = []
            try:
                from agents_generator import generate_agents_for_company
                # Extract financial data from file_data
                financial_data = {}
                for filename, data in file_data.items():
                    if isinstance(data, dict):
                        financial_data.update({
                            'total_assets': data.get('total_assets', 0),
                            'revenue': data.get('revenue', 0),
                            'operating_income': data.get('operating_income', 0),
                            'net_income': data.get('net_income', 0),
                            'cash_and_equivalents': data.get('cash_and_equivalents', 0),
                            'employee_count': data.get('employee_count', 0)
                        })
                        break
                
                agents = generate_agents_for_company(
                    questionnaire_data.get('company_name', 'Unknown'),
                    kpi_results,
                    financial_data
                )
            except Exception as e:
                logger.warning(f"Could not generate agents: {str(e)}")
            
            # Generate intelligent summary message
            summary_message = generate_summary_message(
                questionnaire_data.get('company_name', 'Unknown'),
                kpi_results,
                financial_data
            )
            
            # Store results in memory system
            self.memory_system.store_analysis_results(
                questionnaire_data.get('company_name', 'Unknown'), 
                {
                    'questionnaire': questionnaire_data,
                    'file_data': file_data,
                    'kpi_results': kpi_results,
                    'diagnostic_results': diagnostic_results,
                    'agents': agents
                }
            )
            
            # Return structured results
            return {
                'company_name': questionnaire_data.get('company_name', 'Unknown'),
                'kpi_results': kpi_results,
                'diagnostic_results': diagnostic_results,
                'agents': agents,
                'summary_message': summary_message,
                'file_summary': {
                    filename: describe_file_payload(data)
                    for filename, data in file_data.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            return {
                'error': str(e),
                'company_name': questionnaire_data.get('company_name', 'Unknown')
            }
    
