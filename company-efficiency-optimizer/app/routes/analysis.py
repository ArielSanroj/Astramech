"""
Analysis workflow routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import pandas as pd
import logging
from app.services.analysis_service import AnalysisService
from app.utils.validators import validate_questionnaire_data, validate_file_upload
from app.utils.errors import ValidationError, FileProcessingError

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/process_questionnaire', methods=['POST'])
def process_questionnaire():
    """Process questionnaire form submission"""
    try:
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
        
        validated_data = validate_questionnaire_data(company_data)
        session['questionnaire_data'] = validated_data
        
        flash('Questionnaire submitted successfully! Please upload your financial documents.', 'success')
        return redirect(url_for('main.upload'))
        
    except ValidationError as e:
        flash(f'Validation error: {str(e)}', 'error')
        return redirect(url_for('main.questionnaire'))
    except Exception as e:
        logger.error(f"Error processing questionnaire: {str(e)}")
        flash(f'Error processing questionnaire: {str(e)}', 'error')
        return redirect(url_for('main.questionnaire'))

@analysis_bp.route('/process_upload', methods=['POST'])
def process_upload():
    """Process file uploads and run analysis"""
    try:
        if 'files' not in request.files:
            flash('No files selected', 'error')
            return redirect(url_for('main.upload'))
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            flash('No files selected', 'error')
            return redirect(url_for('main.upload'))
        
        # Process files
        processed_data = {}
        upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        max_file_size = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))
        allowed_extensions = {'pdf', 'xlsx', 'xls', 'csv'}
        
        for file in files:
            if file and file.filename:
                try:
                    validated_file = validate_file_upload(
                        file, 
                        max_file_size, 
                        allowed_extensions
                    )
                    filename = secure_filename(validated_file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    validated_file.save(filepath)
                    
                    # Process file based on type
                    if filename.lower().endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(filepath)
                        processed_data[filename] = df.to_dict('records')
                    elif filename.lower().endswith('.csv'):
                        df = pd.read_csv(filepath)
                        processed_data[filename] = df.to_dict('records')
                    elif filename.lower().endswith('.pdf'):
                        processed_data[filename] = "PDF processed"
                        
                except ValidationError as e:
                    flash(f'File validation error: {str(e)}', 'error')
                    return redirect(url_for('main.upload'))
                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {str(e)}")
                    flash(f'Error processing file {file.filename}: {str(e)}', 'error')
                    return redirect(url_for('main.upload'))
        
        # Get questionnaire data
        questionnaire_data = session.get('questionnaire_data', {})
        if not questionnaire_data:
            flash('No questionnaire data found. Please complete the questionnaire first.', 'error')
            return redirect(url_for('main.questionnaire'))
        
        # Run analysis
        analysis_service = AnalysisService()
        analysis_results = analysis_service.run_analysis(questionnaire_data, processed_data)
        session['analysis_results'] = analysis_results
        
        return redirect(url_for('main.results'))
    
    except RequestEntityTooLarge:
        flash('File size exceeds maximum allowed size', 'error')
        return redirect(url_for('main.upload'))
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        flash(f'Error processing files: {str(e)}', 'error')
        return redirect(url_for('main.upload'))
