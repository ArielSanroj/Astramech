#!/usr/bin/env python3
"""
Application entry point for Company Efficiency Optimizer
"""

import os
from app import create_app
from config import config

if __name__ == '__main__':
    # Get configuration
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create app using factory pattern
    app = create_app(config_name)
    
    # Validate configuration
    from config import Config
    issues = Config.validate_config()
    if issues:
        print("⚠️ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("Please fix these issues before running the application.")
        exit(1)
    
    # Run the application
    print("🚀 Starting Company Efficiency Optimizer")
    print(f"   Environment: {config_name}")
    print(f"   Debug mode: {app.config.get('DEBUG', False)}")
    print(f"   Upload folder: {app.config.get('UPLOAD_FOLDER', 'uploads')}")
    print(f"   Max file size: {app.config.get('MAX_FILE_SIZE', 16 * 1024 * 1024) / (1024 * 1024):.1f}MB")
    
    # Allow overriding port via environment variables
    port = int(os.getenv('PORT', os.getenv('FLASK_RUN_PORT', 5002)))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )
