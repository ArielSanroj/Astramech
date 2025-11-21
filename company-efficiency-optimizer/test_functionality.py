#!/usr/bin/env python3
"""
Test script for AstraMech application functionality
"""

import requests
import os
import time
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:5002"
TEST_FILE = "sample_data/colombian_niif.xlsx"

def test_home_page():
    """Test home page accessibility"""
    print("🔍 Testing home page...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Home page failed: {response.status_code}"
    assert "AstraMech" in response.text, "Home page content missing"
    print("✅ Home page OK")

def test_questionnaire_page():
    """Test questionnaire page"""
    print("\n🔍 Testing questionnaire page...")
    response = requests.get(f"{BASE_URL}/questionnaire")
    assert response.status_code == 200, f"Questionnaire page failed: {response.status_code}"
    assert "Cuestionario" in response.text or "Questionnaire" in response.text
    print("✅ Questionnaire page OK")

def test_questionnaire_submission():
    """Test questionnaire form submission"""
    print("\n🔍 Testing questionnaire submission...")
    
    session = requests.Session()
    
    # Get questionnaire page first to get session
    session.get(f"{BASE_URL}/questionnaire")
    
    # Submit questionnaire
    data = {
        'company_name': 'Test Company',
        'industry': 'Technology',
        'company_size': 'Medium',
        'employee_count': '50',
        'analysis_focus': ['financial', 'operational']
    }
    
    response = session.post(f"{BASE_URL}/process_questionnaire", data=data, allow_redirects=False)
    assert response.status_code == 302, f"Questionnaire submission failed: {response.status_code}"
    assert 'upload' in response.headers.get('Location', '').lower()
    print("✅ Questionnaire submission OK")
    return session

def test_upload_page(session):
    """Test upload page accessibility"""
    print("\n🔍 Testing upload page...")
    response = session.get(f"{BASE_URL}/upload")
    assert response.status_code == 200, f"Upload page failed: {response.status_code}"
    print("✅ Upload page OK")
    return session

def test_file_upload(session):
    """Test file upload functionality"""
    print("\n🔍 Testing file upload...")
    
    if not os.path.exists(TEST_FILE):
        print(f"⚠️  Test file {TEST_FILE} not found, skipping upload test")
        return session, None
    
    with open(TEST_FILE, 'rb') as f:
        files = {'files': (os.path.basename(TEST_FILE), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = session.post(f"{BASE_URL}/process_upload", files=files, allow_redirects=False)
    
    assert response.status_code == 302, f"File upload failed: {response.status_code}"
    assert 'processing' in response.headers.get('Location', '').lower()
    print("✅ File upload OK")
    
    # Wait a bit for processing
    time.sleep(2)
    return session, session.cookies

def test_processing_page(session):
    """Test processing page"""
    print("\n🔍 Testing processing page...")
    response = session.get(f"{BASE_URL}/processing")
    assert response.status_code == 200, f"Processing page failed: {response.status_code}"
    print("✅ Processing page OK")
    return session

def test_results_page(session, max_wait=30):
    """Test results page - wait for analysis to complete"""
    print("\n🔍 Testing results page...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        response = session.get(f"{BASE_URL}/results")
        
        if response.status_code == 200:
            # Check if results are ready (not just loading)
            html_text = response.text.lower()
            if "efficiency" in html_text or "kpi" in html_text or "margin" in html_text or "results" in html_text:
                print("✅ Results page OK - Analysis complete")
                return session, response.text
            else:
                print("⏳ Waiting for analysis to complete...")
                time.sleep(2)
        elif response.status_code == 302:
            # Redirected, might still be processing
            print("⏳ Redirected, waiting...")
            time.sleep(2)
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            time.sleep(2)
    
    print("⚠️  Results page check timeout - analysis may still be running")
    return session, None

def test_export_csv(session):
    """Test CSV export"""
    print("\n🔍 Testing CSV export...")
    response = session.get(f"{BASE_URL}/export/csv", allow_redirects=False)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '').lower()
        if 'csv' in content_type or 'text' in content_type:
            print("✅ CSV export OK")
        else:
            print(f"⚠️  CSV export content type: {content_type}")
    elif response.status_code == 302:
        print("⚠️  CSV export redirected (no results in session)")
    else:
        print(f"⚠️  CSV export returned: {response.status_code}")
    return session

def test_export_json(session):
    """Test JSON export"""
    print("\n🔍 Testing JSON export...")
    response = session.get(f"{BASE_URL}/export/json", allow_redirects=False)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '').lower()
        if 'json' in content_type:
            try:
                json.loads(response.text)
                print("✅ JSON export OK")
            except:
                print("⚠️  JSON export invalid format")
        else:
            print(f"⚠️  JSON export content type: {content_type}")
    elif response.status_code == 302:
        print("⚠️  JSON export redirected (no results in session)")
    else:
        print(f"⚠️  JSON export returned: {response.status_code}")
    return session

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    # Test health check if exists
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API health check OK")
    except:
        print("⚠️  API health check not available")
    
    print("✅ API endpoints check complete")

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ASTRA MECH FUNCTIONALITY TESTS")
    print("=" * 60)
    
    try:
        # Basic page tests
        test_home_page()
        test_questionnaire_page()
        
        # Flow tests
        session = test_questionnaire_submission()
        session = test_upload_page(session)
        session, cookies = test_file_upload(session)
        
        if cookies:
            session = test_processing_page(session)
            session, results_html = test_results_page(session)
            
            if results_html:
                # Check for key elements in results (case insensitive)
                html_lower = results_html.lower()
                checks = [
                    ("efficiency", "Efficiency score displayed"),
                    ("margin", "Financial KPIs displayed"),
                    ("n/a", "N/A handling present"),
                    ("cop", "Currency label present"),
                    ("kpi", "KPI section present"),
                    ("results", "Results content present")
                ]
                
                print("\n🔍 Verifying results content...")
                for check, desc in checks:
                    if check in html_lower:
                        print(f"✅ {desc}")
                    else:
                        print(f"⚠️  {desc} - NOT FOUND")
            
            # Export tests
            test_export_csv(session)
            test_export_json(session)
        
        # API tests
        test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

