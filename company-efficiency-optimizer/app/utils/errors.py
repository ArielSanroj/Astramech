"""
Custom exception classes
"""

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class FileProcessingError(Exception):
    """Custom exception for file processing errors."""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AnalysisError(Exception):
    """Custom exception for analysis errors."""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
