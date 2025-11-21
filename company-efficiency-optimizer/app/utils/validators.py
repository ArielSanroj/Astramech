"""
Input validation utilities
"""

from werkzeug.datastructures import FileStorage
import os
from app.utils.errors import ValidationError

def validate_questionnaire_data(data: dict) -> dict:
    """Validates questionnaire data."""
    # Required fields (simplified form - 3 key questions)
    required_fields = ['company_name', 'industry', 'company_size']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"Missing required field: {field.replace('_', ' ').title()}")
    
    # Optional fields (for backward compatibility)
    if 'revenue_range' not in data:
        data['revenue_range'] = None  # Make it optional
    
    # Make analysis_focus optional (default to all if not provided)
    if 'analysis_focus' not in data or not data['analysis_focus']:
        data['analysis_focus'] = ['all']
    
    # Derive employee_count from company_size if not provided
    if not data.get('employee_count'):
        company_size = data.get('company_size', '').lower()
        size_to_count = {
            'startup': 5,      # 1-10 employees, use midpoint
            'small': 30,       # 11-50 employees, use midpoint
            'medium': 125,     # 51-200 employees, use midpoint
            'large': 600,      # 201-1000 employees, use midpoint
            'enterprise': 2000 # 1000+ employees, use estimate
        }
        data['employee_count'] = size_to_count.get(company_size, 50)  # Default to 50 if unknown
    
    # Validate employee_count if provided
    if data.get('employee_count'):
        try:
            employee_count = int(data['employee_count'])
            if employee_count <= 0:
                raise ValidationError("Employee count must be a positive number.")
            data['employee_count'] = employee_count
        except (ValueError, TypeError):
            # If invalid, use default based on company_size
            company_size = data.get('company_size', '').lower()
            size_to_count = {
                'startup': 5,
                'small': 30,
                'medium': 125,
                'large': 600,
                'enterprise': 2000
            }
            data['employee_count'] = size_to_count.get(company_size, 50)
    
    return data

def validate_file_upload(file: FileStorage, max_size: int, allowed_extensions: set) -> FileStorage:
    """Validates an uploaded file."""
    if not file:
        raise ValidationError("No file provided.")
    
    if not file.filename:
        raise ValidationError("No selected file.")
    
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        raise ValidationError(f"File type not allowed. Allowed types are: {', '.join(allowed_extensions)}")
    
    # Check file size (Flask handles RequestEntityTooLarge, but explicit check can provide clearer message)
    # This check is more for logical validation before saving, actual size limit is handled by Flask config
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0) # Reset file pointer
    if file_size > max_size:
        raise ValidationError(f"File size exceeds maximum limit of {max_size / (1024 * 1024):.0f}MB.")
    
    return file

def validate_financial_data(data: dict) -> dict:
    """Validates extracted financial data."""
    required_kpis = ['revenue', 'cost_of_goods_sold', 'operating_expenses', 'net_income']
    for kpi in required_kpis:
        if not isinstance(data.get(kpi), (int, float)) or data.get(kpi) < 0:
            # Allow 0 for some, but not negative
            if data.get(kpi) < 0:
                raise ValidationError(f"Invalid financial data: {kpi.replace('_', ' ').title()} cannot be negative.")
            # If it's missing or not a number, it's a warning, not a critical error for now
            # For a real system, this would be more strict
    return data
