"""
Input validation functions for Company Efficiency Optimizer
"""

import os
import re
from typing import Dict, Any, List, Optional
from werkzeug.datastructures import FileStorage
from errors import ValidationError


def validate_company_name(name: str) -> str:
    """Validate company name"""
    if not name or not name.strip():
        raise ValidationError("Company name is required")
    
    name = name.strip()
    if len(name) < 2:
        raise ValidationError("Company name must be at least 2 characters long")
    
    if len(name) > 100:
        raise ValidationError("Company name must be less than 100 characters")
    
    # Check for valid characters (letters, numbers, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z0-9\s\-'\.&]+$", name):
        raise ValidationError("Company name contains invalid characters")
    
    return name


def validate_employee_count(count: str) -> int:
    """Validate employee count"""
    try:
        count_int = int(count)
    except (ValueError, TypeError):
        raise ValidationError("Employee count must be a valid number")
    
    if count_int < 1:
        raise ValidationError("Employee count must be at least 1")
    
    if count_int > 1000000:  # Reasonable upper limit
        raise ValidationError("Employee count seems unreasonably high")
    
    return count_int


def validate_industry(industry: str) -> str:
    """Validate industry selection"""
    valid_industries = {
        'technology', 'healthcare', 'finance', 'manufacturing', 
        'retail', 'education', 'consulting', 'other'
    }
    
    if not industry or industry not in valid_industries:
        raise ValidationError("Please select a valid industry")
    
    return industry


def validate_company_size(size: str) -> str:
    """Validate company size selection"""
    valid_sizes = {
        'startup', 'small', 'medium', 'large', 'enterprise'
    }
    
    if not size or size not in valid_sizes:
        raise ValidationError("Please select a valid company size")
    
    return size


def validate_revenue_range(revenue_range: str) -> str:
    """Validate revenue range selection"""
    valid_ranges = {
        'under_1m', '1m_10m', '10m_50m', '50m_100m', 'over_100m'
    }
    
    if not revenue_range or revenue_range not in valid_ranges:
        raise ValidationError("Please select a valid revenue range")
    
    return revenue_range


def validate_analysis_focus(focus_areas: List[str]) -> List[str]:
    """Validate analysis focus areas"""
    valid_focus_areas = {
        'financial', 'hr', 'operations', 'efficiency', 'growth', 'all'
    }
    
    if not focus_areas:
        raise ValidationError("Please select at least one analysis focus area")
    
    for focus in focus_areas:
        if focus not in valid_focus_areas:
            raise ValidationError(f"Invalid focus area: {focus}")
    
    return focus_areas


def validate_file_upload(file: FileStorage, max_size: int, allowed_extensions: set) -> FileStorage:
    """Validate uploaded file"""
    if not file or file.filename == '':
        raise ValidationError("No file selected")
    
    # Check file extension
    if '.' not in file.filename:
        raise ValidationError("File must have an extension")
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        raise ValidationError(f"File type '{extension}' not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(f"File size ({file_size / (1024 * 1024):.1f}MB) exceeds maximum allowed size ({max_size_mb:.1f}MB)")
    
    if file_size == 0:
        raise ValidationError("File is empty")
    
    return file


def validate_financial_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate financial data structure"""
    required_fields = ['revenue', 'employee_count']
    optional_fields = ['cogs', 'operating_expenses', 'net_income']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate revenue
    try:
        revenue = float(data['revenue'])
        if revenue <= 0:
            raise ValidationError("Revenue must be positive")
        if revenue > 1e12:  # 1 trillion
            raise ValidationError("Revenue seems unreasonably high")
    except (ValueError, TypeError):
        raise ValidationError("Revenue must be a valid number")
    
    # Validate employee count
    try:
        employee_count = int(data['employee_count'])
        if employee_count <= 0:
            raise ValidationError("Employee count must be positive")
        if employee_count > 1000000:
            raise ValidationError("Employee count seems unreasonably high")
    except (ValueError, TypeError):
        raise ValidationError("Employee count must be a valid integer")
    
    # Validate optional fields if present
    for field in optional_fields:
        if field in data and data[field] is not None:
            try:
                value = float(data[field])
                if value < 0 and field != 'net_income':  # net_income can be negative
                    raise ValidationError(f"{field} cannot be negative")
            except (ValueError, TypeError):
                raise ValidationError(f"{field} must be a valid number")
    
    return data


def validate_questionnaire_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate complete questionnaire data"""
    validated_data = {}
    
    # Validate required fields
    validated_data['company_name'] = validate_company_name(data.get('company_name', ''))
    validated_data['industry'] = validate_industry(data.get('industry', ''))
    validated_data['company_size'] = validate_company_size(data.get('company_size', ''))
    validated_data['revenue_range'] = validate_revenue_range(data.get('revenue_range', ''))
    validated_data['employee_count'] = validate_employee_count(data.get('employee_count', ''))
    validated_data['analysis_focus'] = validate_analysis_focus(data.get('analysis_focus', []))
    
    # Validate optional fields
    validated_data['current_challenges'] = data.get('current_challenges', '').strip()
    validated_data['goals'] = data.get('goals', '').strip()
    
    return validated_data


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def validate_ollama_connection(base_url: str) -> bool:
    """Validate Ollama connection"""
    try:
        import requests
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False
