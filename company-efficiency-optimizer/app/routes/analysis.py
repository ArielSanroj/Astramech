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
from data_ingest import EnhancedDataIngestion

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)
data_ingestion = EnhancedDataIngestion()

@analysis_bp.route('/process_questionnaire', methods=['POST'])
def process_questionnaire():
    """Process questionnaire form submission"""
    try:
        company_data = {
            'company_name': request.form.get('company_name'),
            'industry': request.form.get('industry'),
            'company_size': request.form.get('company_size'),
            'revenue_range': request.form.get('revenue_range'),  # Optional (for backward compatibility)
            'employee_count': request.form.get('employee_count'),
            'current_challenges': request.form.get('current_challenges', ''),  # Optional
            'goals': request.form.get('goals', ''),  # Optional
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

        questionnaire_data = session.get('questionnaire_data', {})
        if not questionnaire_data:
            flash('No questionnaire data found. Please complete the questionnaire first.', 'error')
            return redirect(url_for('main.questionnaire'))
        
        # Process files
        processed_data = {}
        # Use /tmp/uploads in Vercel, 'uploads' locally
        upload_folder = os.getenv('UPLOAD_FOLDER', '/tmp/uploads' if os.path.exists('/tmp') else 'uploads')
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
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
                    _, ext = os.path.splitext(filename.lower())

                    # Process file based on type
                    if ext in ('.xlsx', '.xls'):
                        structured_data = data_ingestion.process_excel_file(
                            filepath,
                            company_name=questionnaire_data.get('company_name'),
                            department='Finance'
                        )
                        if structured_data:
                            processed_data[filename] = structured_data
                        else:
                            df = pd.read_excel(filepath)
                            processed_data[filename] = df.to_dict('records')
                    elif ext == '.csv':
                        df = pd.read_csv(filepath)
                        processed_data[filename] = df.to_dict('records')
                    elif ext == '.pdf':
                        processed_data[filename] = "PDF processed"
                        
                except ValidationError as e:
                    flash(f'File validation error: {str(e)}', 'error')
                    return redirect(url_for('main.upload'))
                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {str(e)}")
                    flash(f'Error processing file {file.filename}: {str(e)}', 'error')
                    return redirect(url_for('main.upload'))
        
        # Store file data in session for processing
        session['file_data'] = processed_data
        session['files_uploaded'] = True
        
        # Redirect to processing page
        return redirect(url_for('main.processing'))
    
    except RequestEntityTooLarge:
        flash('File size exceeds maximum allowed size', 'error')
        return redirect(url_for('main.upload'))
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        flash(f'Error processing files: {str(e)}', 'error')
        return redirect(url_for('main.upload'))
