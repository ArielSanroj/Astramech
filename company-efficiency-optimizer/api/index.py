"""
Vercel serverless function handler for Flask app
Vercel automatically detects Flask apps when 'app' instance is exported
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create Flask app instance
# Vercel will automatically use this 'app' instance
app = create_app('production')

