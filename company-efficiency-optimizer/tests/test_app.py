"""
Basic tests for the Flask application
"""

import pytest
import os
import tempfile
from app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


def test_index_page(client):
    """Test that the index page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Company Efficiency Optimizer' in response.data


def test_questionnaire_page(client):
    """Test that the questionnaire page loads"""
    response = client.get('/questionnaire')
    assert response.status_code == 200
    assert b'Company Information' in response.data


def test_upload_page(client):
    """Test that the upload page loads"""
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'Upload' in response.data


def test_questionnaire_validation(client):
    """Test questionnaire form validation"""
    # Test with missing required fields
    response = client.post('/process_questionnaire', data={
        'company_name': '',
        'industry': '',
        'company_size': '',
        'revenue_range': '',
        'employee_count': '',
        'analysis_focus': []
    })
    assert response.status_code == 302  # Redirect back to questionnaire


def test_questionnaire_success(client):
    """Test successful questionnaire submission"""
    response = client.post('/process_questionnaire', data={
        'company_name': 'Test Company',
        'industry': 'technology',
        'company_size': 'medium',
        'revenue_range': '1m_10m',
        'employee_count': '50',
        'analysis_focus': ['financial', 'hr']
    })
    assert response.status_code == 302  # Redirect to upload


def test_analysis_status_api(client):
    """Test the analysis status API endpoint"""
    response = client.get('/api/analysis_status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data


def test_results_page_no_data(client):
    """Test results page when no analysis data exists"""
    response = client.get('/results')
    assert response.status_code == 302  # Redirect to index


if __name__ == '__main__':
    pytest.main([__file__])
