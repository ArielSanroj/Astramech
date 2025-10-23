"""
Real-time Streaming Application for Company Efficiency Optimizer

This module implements WebSocket-based real-time streaming for live KPI monitoring
and dynamic agent creation.
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import threading
import time

from data_ingest import EnhancedDataIngestion
from tools.kpi_calculator import KPICalculator
from dynamic_agent_creator import DynamicAgentCreator
from memory_setup import HybridMemorySystem

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
data_ingestion = EnhancedDataIngestion()
kpi_calculator = KPICalculator()
agent_creator = DynamicAgentCreator()
memory_system = HybridMemorySystem()

# Active analysis sessions
active_sessions = {}

class StreamingAnalysisSession:
    """Manages a real-time analysis session"""
    
    def __init__(self, session_id: str, company_name: str, department: str):
        self.session_id = session_id
        self.company_name = company_name
        self.department = department
        self.start_time = datetime.now()
        self.status = 'initializing'
        self.current_data = {}
        self.kpi_results = {}
        self.agents = []
        self.inefficiencies = []
        
    def update_status(self, status: str, message: str = ""):
        """Update session status and emit to client"""
        self.status = status
        socketio.emit('status_update', {
            'session_id': self.session_id,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=self.session_id)
    
    def update_kpis(self, kpi_results: Dict[str, Any]):
        """Update KPI results and emit to client"""
        self.kpi_results = kpi_results
        socketio.emit('kpi_update', {
            'session_id': self.session_id,
            'kpis': kpi_results,
            'timestamp': datetime.now().isoformat()
        }, room=self.session_id)
    
    def update_agents(self, agents: List[Dict[str, Any]]):
        """Update agent recommendations and emit to client"""
        self.agents = agents
        socketio.emit('agent_update', {
            'session_id': self.session_id,
            'agents': agents,
            'timestamp': datetime.now().isoformat()
        }, room=self.session_id)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('streaming_dashboard.html')

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    """Start a new real-time analysis session"""
    try:
        data = request.get_json()
        company_name = data.get('company_name', 'Unknown Company')
        department = data.get('department', 'Finance')
        
        # Create session
        session_id = f"session_{int(time.time())}"
        session = StreamingAnalysisSession(session_id, company_name, department)
        active_sessions[session_id] = session
        
        # Start analysis in background
        threading.Thread(target=run_analysis_async, args=(session,)).start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Analysis started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload_data', methods=['POST'])
def upload_data():
    """Upload and process data files"""
    try:
        session_id = request.form.get('session_id')
        if session_id not in active_sessions:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save file temporarily
        filename = f"temp_{session_id}_{file.filename}"
        filepath = os.path.join('temp_uploads', filename)
        os.makedirs('temp_uploads', exist_ok=True)
        file.save(filepath)
        
        # Process file
        session.update_status('processing', f'Processing {file.filename}...')
        financial_data = data_ingestion.process_excel_file(filepath, session.company_name, session.department)
        session.current_data = financial_data
        
        # Clean up temp file
        os.remove(filepath)
        
        session.update_status('analyzing', 'Analyzing financial data...')
        
        return jsonify({
            'success': True,
            'message': 'File processed successfully',
            'data_summary': {
                'company': financial_data.get('company'),
                'currency': financial_data.get('currency'),
                'employee_count': financial_data.get('employee_count'),
                'sheets_processed': len(financial_data.get('sheets_processed', []))
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to real-time analysis'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_session')
def handle_join_session(data):
    """Join a specific analysis session"""
    session_id = data.get('session_id')
    if session_id in active_sessions:
        join_room(session_id)
        emit('joined_session', {
            'session_id': session_id,
            'status': active_sessions[session_id].status
        })
    else:
        emit('error', {'message': 'Session not found'})

@socketio.on('leave_session')
def handle_leave_session(data):
    """Leave a specific analysis session"""
    session_id = data.get('session_id')
    leave_room(session_id)
    emit('left_session', {'session_id': session_id})

def run_analysis_async(session: StreamingAnalysisSession):
    """Run analysis asynchronously and emit updates"""
    try:
        # Simulate data processing delay
        time.sleep(2)
        
        # Calculate KPIs
        session.update_status('calculating_kpis', 'Calculating KPIs...')
        kpi_data = {
            'financial_data': session.current_data,
            'hr_data': session.current_data.get('hr_data', {}),
            'operational_data': {},
            'industry': session.current_data.get('industry', 'professional_services')
        }
        
        kpi_results = kpi_calculator.calculate_all_kpis(kpi_data, session.department)
        session.update_kpis(kpi_results)
        
        # Identify inefficiencies
        session.update_status('identifying_issues', 'Identifying inefficiencies...')
        inefficiencies = kpi_results.get('inefficiencies', [])
        session.inefficiencies = inefficiencies
        
        # Create agents
        session.update_status('creating_agents', 'Creating specialized agents...')
        company_context = {
            'company_name': session.company_name,
            'industry': session.current_data.get('industry', 'Unknown'),
            'revenue': session.current_data.get('revenue', 0),
            'employee_count': session.current_data.get('employee_count', 0)
        }
        
        agents = agent_creator.create_agent_crew(inefficiencies, company_context)
        session.update_agents(agents)
        
        # Store in memory
        session.update_status('storing_results', 'Storing analysis results...')
        memory_system.store_analysis_results(session.company_name, {
            'kpi_results': kpi_results,
            'agents': agents,
            'inefficiencies': inefficiencies,
            'timestamp': datetime.now().isoformat()
        })
        
        session.update_status('completed', 'Analysis completed successfully')
        
    except Exception as e:
        session.update_status('error', f'Analysis failed: {str(e)}')
        print(f"Analysis error: {str(e)}")

@app.route('/api/session/<session_id>/status')
def get_session_status(session_id):
    """Get current session status"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    return jsonify({
        'session_id': session_id,
        'status': session.status,
        'company_name': session.company_name,
        'department': session.department,
        'start_time': session.start_time.isoformat(),
        'kpi_results': session.kpi_results,
        'agents': session.agents,
        'inefficiencies': session.inefficiencies
    })

@app.route('/api/session/<session_id>/recommendations')
def get_recommendations(session_id):
    """Get agent recommendations for a session"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    recommendations = agent_creator.get_agent_recommendations(
        session.kpi_results, 
        {
            'company_name': session.company_name,
            'industry': session.current_data.get('industry', 'Unknown')
        }
    )
    
    return jsonify({
        'session_id': session_id,
        'recommendations': recommendations
    })

@app.route('/api/departments')
def get_departments():
    """Get available departments for analysis"""
    departments = [
        {'id': 'finance', 'name': 'Finance', 'description': 'Financial performance and cost optimization'},
        {'id': 'marketing', 'name': 'Marketing', 'description': 'Marketing ROI and customer acquisition'},
        {'id': 'it', 'name': 'IT', 'description': 'System performance and infrastructure optimization'},
        {'id': 'r_d', 'name': 'R&D', 'description': 'Innovation and research efficiency'},
        {'id': 'hr', 'name': 'HR', 'description': 'Employee satisfaction and retention'},
        {'id': 'operations', 'name': 'Operations', 'description': 'Process efficiency and waste reduction'}
    ]
    
    return jsonify({'departments': departments})

if __name__ == '__main__':
    # Create temp uploads directory
    os.makedirs('temp_uploads', exist_ok=True)
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)