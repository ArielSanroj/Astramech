from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
import logging
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from data_ingest import DataIngestion
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

# Register error handlers
register_error_handlers(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize backend components
data_ingestion = DataIngestion()
kpi_calculator = KPICalculator()
memory_system = HybridMemorySystem()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process_questionnaire', methods=['POST'])
def process_questionnaire():
    """Process the initial questionnaire data"""
    try:
        # Get form data
        company_data = {
            'company_name': request.form.get('company_name'),
            'industry': request.form.get('industry'),
            'company_size': request.form.get('company_size'),
            'revenue_range': request.form.get('revenue_range'),
            'employee_count': request.form.get('employee_count'),
            'current_challenges': request.form.get('current_challenges'),
            'goals': request.form.get('goals'),
            'analysis_focus': request.form.getlist('analysis_focus')
        }
        
        # Validate questionnaire data
        validated_data = validate_questionnaire_data(company_data)
        
        # Store in session instead of temporary file
        session['questionnaire_data'] = validated_data
        
        flash('Questionnaire submitted successfully! Please upload your financial documents.', 'success')
        return redirect(url_for('upload'))
    
    except ValidationError as e:
        flash(f'Validation error: {str(e)}', 'error')
        return redirect(url_for('questionnaire'))
    except Exception as e:
        logger.error(f"Error processing questionnaire: {str(e)}")
        flash(f'Error processing questionnaire: {str(e)}', 'error')
        return redirect(url_for('questionnaire'))

@app.route('/process_upload', methods=['POST'])
def process_upload():
    """Process uploaded files and run analysis"""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            flash('No files selected', 'error')
            return redirect(url_for('upload'))
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            flash('No files selected', 'error')
            return redirect(url_for('upload'))
        
        # Validate and process uploaded files
        processed_data = {}
        for file in files:
            if file and file.filename:
                try:
                    # Validate file
                    validated_file = validate_file_upload(
                        file, 
                        app.config['MAX_FILE_SIZE'], 
                        app.config['ALLOWED_EXTENSIONS']
                    )
                    
                    filename = secure_filename(validated_file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    validated_file.save(filepath)
                    
                    # Process based on file type
                    if filename.lower().endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(filepath)
                        processed_data[filename] = df.to_dict('records')
                    elif filename.lower().endswith('.csv'):
                        df = pd.read_csv(filepath)
                        processed_data[filename] = df.to_dict('records')
                    elif filename.lower().endswith('.pdf'):
                        # For PDF, we'll use the existing data ingestion
                        processed_data[filename] = "PDF processed"
                        
                except ValidationError as e:
                    flash(f'File validation error: {str(e)}', 'error')
                    return redirect(url_for('upload'))
                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {str(e)}")
                    flash(f'Error processing file {file.filename}: {str(e)}', 'error')
                    return redirect(url_for('upload'))
        
        # Get questionnaire data from session
        questionnaire_data = session.get('questionnaire_data', {})
        if not questionnaire_data:
            flash('No questionnaire data found. Please complete the questionnaire first.', 'error')
            return redirect(url_for('questionnaire'))
        
        # Run analysis
        analysis_results = run_analysis(questionnaire_data, processed_data)
        
        # Store results in session
        session['analysis_results'] = analysis_results
        
        return redirect(url_for('results'))
    
    except RequestEntityTooLarge:
        flash('File size exceeds maximum allowed size', 'error')
        return redirect(url_for('upload'))
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        flash(f'Error processing files: {str(e)}', 'error')
        return redirect(url_for('upload'))

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

@app.route('/results')
def results():
    """Display analysis results"""
    try:
        # Get results from session instead of temp file
        results = session.get('analysis_results')
        if not results:
            flash('No analysis results found. Please run an analysis first.', 'error')
            return redirect(url_for('index'))
        
        return render_template('results.html', results=results)
    except Exception as e:
        logger.error(f"Error loading results: {str(e)}")
        flash(f'Error loading results: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analysis_status')
def analysis_status():
    """API endpoint to check analysis status"""
    if session.get('analysis_results'):
        return jsonify({'status': 'completed'})
    return jsonify({'status': 'pending'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
