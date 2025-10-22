"""
Flask Application Factory for Company Efficiency Optimizer
This is the new main application file using the factory pattern
"""

from app import create_app

# Create the application using the factory pattern
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
