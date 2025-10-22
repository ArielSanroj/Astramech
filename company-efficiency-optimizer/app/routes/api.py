"""
API routes for the Company Efficiency Optimizer
"""

from flask import Blueprint, jsonify, session
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/analysis_status')
def analysis_status():
    """Get analysis status"""
    if session.get('analysis_results'):
        return jsonify({'status': 'completed'})
    return jsonify({'status': 'pending'})

@api_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Company Efficiency Optimizer'
    })
