"""
Input validation utilities
"""

from werkzeug.datastructures import FileStorage
import os
from app.utils.errors import ValidationError

def validate_questionnaire_data(data: dict) -> dict:
    """Validates questionnaire data."""
    required_fields = ['company_name', 'industry', 'company_size', 'revenue_range', 'employee_count', 'analysis_focus']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"Missing required field: {field.replace('_', ' ').title()}")
    
    if not isinstance(data['analysis_focus'], list) or not data['analysis_focus']:
        raise ValidationError("At least one analysis focus area must be selected.")
    
    try:
        employee_count = int(data['employee_count'])
        if employee_count <= 0:
            raise ValidationError("Employee count must be a positive number.")
    except ValueError:
        raise ValidationError("Employee count must be a valid number.")
    
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
