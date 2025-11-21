from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_session import Session
import os
import json
import logging
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from data_ingest import EnhancedDataIngestion as DataIngestion
from tools.kpi_calculator import KPICalculator
from memory_setup import HybridMemorySystem
from ollama_crew import OllamaDiagnosticCrew
import tempfile
import pandas as pd
from config import config
from errors import register_error_handlers, ValidationError, FileProcessingError
from validators import validate_questionnaire_data, validate_file_upload, validate_financial_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize Flask-Session
Session(app)

# Register error handlers
register_error_handlers(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize backend components
data_ingestion = DataIngestion()
kpi_calculator = KPICalculator()
memory_system = HybridMemorySystem()

# Register blueprints
from app.routes.main import main_bp
from app.routes.analysis import analysis_bp
from app.routes.api import api_bp

app.register_blueprint(main_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(api_bp)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def run_analysis(questionnaire_data, file_data):
    """Run the efficiency analysis using the backend components"""
    try:
        # Initialize diagnostic crew
        diagnostic_crew = OllamaDiagnosticCrew()
        
        # Create sample data based on questionnaire and files
        sample_data = create_sample_data_from_inputs(questionnaire_data, file_data)
        
        # Calculate KPIs using the new method
        kpi_results = kpi_calculator.calculate_all_kpis(sample_data)
        
        # Run diagnostic analysis - using existing method
        diagnostic_results = diagnostic_crew.run_diagnostic_analysis(sample_data)
        
        # Store in memory system - using existing method
        memory_system.store_analysis_results(questionnaire_data.get('company_name', 'Unknown'), {
            'questionnaire': questionnaire_data,
            'file_data': file_data,
            'kpi_results': kpi_results,
            'diagnostic_results': diagnostic_results
        })
        
        return {
            'company_name': questionnaire_data.get('company_name', 'Unknown'),
            'kpi_results': kpi_results,
            'diagnostic_results': diagnostic_results,
            'file_summary': {filename: f"{len(data)} records" for filename, data in file_data.items()}
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'company_name': questionnaire_data.get('company_name', 'Unknown')
        }

def create_sample_data_from_inputs(questionnaire_data, file_data):
    """Create sample data structure based on questionnaire and uploaded files"""
    # Extract employee count from questionnaire
    employee_count = int(questionnaire_data.get('employee_count', 50))
    
    # Create sample financial data based on revenue range
    revenue_ranges = {
        'under_1m': 500000,
        '1m_10m': 5000000,
        '10m_50m': 25000000,
        '50m_100m': 75000000,
        'over_100m': 150000000
    }
    
    base_revenue = revenue_ranges.get(questionnaire_data.get('revenue_range', '1m_10m'), 5000000)
    
    # Create sample data
    sample_data = {
        'financial_data': {
            'revenue': base_revenue,
            'cost_of_goods_sold': base_revenue * 0.6,
            'operating_expenses': base_revenue * 0.25,
            'net_income': base_revenue * 0.15
        },
        'hr_data': {
            'total_employees': employee_count,
            'departments': {
                'engineering': int(employee_count * 0.4),
                'sales': int(employee_count * 0.2),
                'marketing': int(employee_count * 0.1),
                'operations': int(employee_count * 0.2),
                'admin': int(employee_count * 0.1)
            }
        },
        'operational_data': {
            'projects_completed': 25,
            'customer_satisfaction': 4.2,
            'process_efficiency': 0.78
        }
    }
    
    return sample_data

# Routes are now handled by blueprints registered above

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
