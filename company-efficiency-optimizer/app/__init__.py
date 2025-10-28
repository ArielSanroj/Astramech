"""
Flask Application Factory for Company Efficiency Optimizer
"""

import os
import logging
from flask import Flask
from flask_session import Session
from config import config
from errors import register_error_handlers


def create_app(config_name=None):
    """Create and configure the Flask application"""
    
    # Ensure Flask uses the top-level templates directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Company Efficiency Optimizer startup')
    
    # Initialize extensions
    Session(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.analysis import analysis_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(api_bp)
    
    return app
