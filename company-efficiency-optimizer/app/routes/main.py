"""
Main routes for the Company Efficiency Optimizer
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session
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

@main_bp.route('/results')
def results():
    """Results display page"""
    results = session.get('analysis_results')
    if not results:
        flash('No analysis results found. Please run an analysis first.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('results.html', results=results)
