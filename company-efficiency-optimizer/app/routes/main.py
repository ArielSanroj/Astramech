"""
Main routes for the Company Efficiency Optimizer
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask import current_app, send_from_directory, Response, jsonify
# new imports
from app.utils.export import export_results_to_csv, export_results_to_json
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@main_bp.route('/upload')
def upload():
    """File upload page"""
    if not session.get('questionnaire_data'):
        flash('Completa el inicio rápido primero.', 'error')
        return redirect(url_for('main.index'))
    return render_template('upload.html')

@main_bp.route('/guided')
def guided():
    """Guided onboarding flow when data is not available."""
    return render_template('guided.html')

@main_bp.route('/processing')
def processing():
    """Processing/analysis in progress page"""
    if not session.get('questionnaire_data'):
        flash('Completa el inicio rápido primero.', 'error')
        return redirect(url_for('main.index'))
    
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
    
    guided_flow = session.get('guided_flow')
    sales_plan = session.get('sales_plan')
    ops_plan = session.get('ops_plan')
    finance_plan = session.get('finance_plan')
    marketing_plan = session.get('marketing_plan')
    hr_plan = session.get('hr_plan')
    return render_template(
        'processing.html',
        guided_flow=guided_flow,
        sales_plan=sales_plan,
        ops_plan=ops_plan,
        finance_plan=finance_plan,
        marketing_plan=marketing_plan,
        hr_plan=hr_plan,
    )

@main_bp.route('/results')
def results():
    """Results display page"""
    results = session.get('analysis_results')
    if not results:
        flash('No analysis results found. Please run an analysis first.', 'error')
        return redirect(url_for('main.index'))
    
    # Mark analysis as viewed
    session['analysis_viewed'] = True
    
    guided_flow = session.get('guided_flow')
    sales_plan = session.get('sales_plan')
    ops_plan = session.get('ops_plan')
    finance_plan = session.get('finance_plan')
    marketing_plan = session.get('marketing_plan')
    hr_plan = session.get('hr_plan')
    return render_template(
        'results.html',
        results=results,
        guided_flow=guided_flow,
        sales_plan=sales_plan,
        ops_plan=ops_plan,
        finance_plan=finance_plan,
        marketing_plan=marketing_plan,
        hr_plan=hr_plan,
    )

@main_bp.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear session data for new analysis"""
    session.clear()
    flash('Sesión limpiada. Puedes iniciar un nuevo análisis.', 'success')
    return redirect(url_for('main.index'))

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
