"""
Custom exception classes and error handlers for Company Efficiency Optimizer
"""

from flask import render_template, jsonify, request
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class EfficiencyOptimizerError(Exception):
    """Base exception for the application"""
    pass


class ValidationError(EfficiencyOptimizerError):
    """Raised when input validation fails"""
    pass


class FileProcessingError(EfficiencyOptimizerError):
    """Raised when file processing fails"""
    pass


class LLMConnectionError(EfficiencyOptimizerError):
    """Raised when LLM connection fails"""
    pass


class MemorySystemError(EfficiencyOptimizerError):
    """Raised when memory system operations fail"""
    pass


class KPICalculationError(EfficiencyOptimizerError):
    """Raised when KPI calculation fails"""
    pass


def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"Bad request: {error}")
        if request.is_json:
            return jsonify({'error': 'Bad request', 'message': str(error)}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        logger.warning(f"Forbidden: {error}")
        if request.is_json:
            return jsonify({'error': 'Forbidden', 'message': str(error)}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        logger.info(f"Not found: {error}")
        if request.is_json:
            return jsonify({'error': 'Not found', 'message': str(error)}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors"""
        logger.warning(f"File too large: {error}")
        if request.is_json:
            return jsonify({'error': 'File too large', 'message': 'File size exceeds maximum allowed size'}), 413
        return render_template('errors/413.html'), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        logger.error(f"Internal server error: {error}")
        if request.is_json:
            return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        logger.warning(f"Validation error: {error}")
        if request.is_json:
            return jsonify({'error': 'Validation error', 'message': str(error)}), 400
        return render_template('errors/validation.html', error=str(error)), 400
    
    @app.errorhandler(FileProcessingError)
    def handle_file_processing_error(error):
        """Handle file processing errors"""
        logger.error(f"File processing error: {error}")
        if request.is_json:
            return jsonify({'error': 'File processing error', 'message': str(error)}), 422
        return render_template('errors/file_processing.html', error=str(error)), 422
    
    @app.errorhandler(LLMConnectionError)
    def handle_llm_connection_error(error):
        """Handle LLM connection errors"""
        logger.error(f"LLM connection error: {error}")
        if request.is_json:
            return jsonify({'error': 'LLM connection error', 'message': str(error)}), 503
        return render_template('errors/llm_connection.html', error=str(error)), 503
    
    @app.errorhandler(MemorySystemError)
    def handle_memory_system_error(error):
        """Handle memory system errors"""
        logger.error(f"Memory system error: {error}")
        if request.is_json:
            return jsonify({'error': 'Memory system error', 'message': str(error)}), 503
        return render_template('errors/memory_system.html', error=str(error)), 503
    
    @app.errorhandler(KPICalculationError)
    def handle_kpi_calculation_error(error):
        """Handle KPI calculation errors"""
        logger.error(f"KPI calculation error: {error}")
        if request.is_json:
            return jsonify({'error': 'KPI calculation error', 'message': str(error)}), 422
        return render_template('errors/kpi_calculation.html', error=str(error)), 422


def create_error_response(error: Exception, status_code: int = 500) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        'error': error.__class__.__name__,
        'message': str(error),
        'status_code': status_code
    }
