"""
Main routes for the Company Efficiency Optimizer
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask import current_app, send_from_directory, Response
from app.utils.export import export_results_to_csv, export_results_to_json
# from app.services.analysis_service import AnalysisService
# from app.utils.validators import validate_questionnaire_data
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@main_bp.route('/questionnaire')
def questionnaire():
    """Questionnaire form"""
    return render_template('questionnaire.html')

@main_bp.route('/upload')
def upload():
    """File upload page"""
    if not session.get('questionnaire_data'):
        flash('Please complete the questionnaire first.', 'error')
        return redirect(url_for('main.questionnaire'))
    return render_template('upload.html')

@main_bp.route('/processing')
def processing():
    """Processing/analysis in progress page"""
    if not session.get('questionnaire_data'):
        flash('Please complete the questionnaire first.', 'error')
        return redirect(url_for('main.questionnaire'))
    
    # If files uploaded but analysis not started, trigger it
    if session.get('files_uploaded') and not session.get('analysis_started'):
        session['analysis_started'] = True
        # Import here to avoid circular imports
        from app.services.analysis_service import AnalysisService
        try:
            questionnaire_data = session.get('questionnaire_data', {})
            file_data = session.get('file_data', {})
            
            analysis_service = AnalysisService()
            analysis_results = analysis_service.run_analysis(questionnaire_data, file_data)
            session['analysis_results'] = analysis_results
            session['analysis_complete'] = True
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            session['analysis_error'] = str(e)
    
    return render_template('processing.html')

@main_bp.route('/results')
def results():
    """Results display page"""
    results = session.get('analysis_results')
    if not results:
        flash('No analysis results found. Please run an analysis first.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('results.html', results=results)

@main_bp.route('/robots.txt')
def robots():
    return send_from_directory(current_app.root_path, 'robots.txt', mimetype='text/plain')

@main_bp.route('/sitemap.xml')
def sitemap():
    return send_from_directory(current_app.root_path, 'sitemap.xml', mimetype='application/xml')

@main_bp.route('/export/csv')
def export_csv():
    """Export analysis results as CSV"""
    results = session.get('analysis_results')
    if not results:
        flash('No analysis results found.', 'error')
        return redirect(url_for('main.index'))
    
    csv_data = export_results_to_csv(results)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=astramech-analysis-{results.get("company_name", "report")}.csv'}
    )

@main_bp.route('/export/json')
def export_json():
    """Export analysis results as JSON"""
    results = session.get('analysis_results')
    if not results:
        flash('No analysis results found.', 'error')
        return redirect(url_for('main.index'))
    
    json_data = export_results_to_json(results)
    return Response(
        json_data,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=astramech-analysis-{results.get("company_name", "report")}.json'}
    )
