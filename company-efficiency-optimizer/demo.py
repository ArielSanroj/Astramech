#!/usr/bin/env python3
"""
Demo script for Company Efficiency Optimizer

This script demonstrates the system working with sample data without requiring API keys.
It shows the complete workflow from data ingestion to KPI analysis and inefficiency identification.
"""

import os
import sys
from dotenv import load_dotenv
from data_ingest import DataIngestion
from tools.kpi_calculator import KPICalculator
from memory_setup import HybridMemorySystem

def demo_data_ingestion():
    """Demonstrate data ingestion capabilities"""
    print("📊 Data Ingestion Demo")
    print("-" * 30)
    
    # Initialize data ingestion
    data_ingestion = DataIngestion()
    
    # Create sample data
    print("Creating sample HR data...")
    hr_data = data_ingestion._create_sample_hr_data()
    print(f"✅ Created HR data: {len(hr_data)} employees")
    
    print("\nCreating sample financial data...")
    financial_data = data_ingestion._create_sample_financial_data()
    print(f"✅ Created financial data: {len(financial_data)} periods")
    
    # Calculate turnover rate
    turnover_rate = data_ingestion.calculate_turnover_rate(hr_data)
    print(f"\n📈 Calculated turnover rate: {turnover_rate:.2f}%")
    
    return hr_data, financial_data

def demo_kpi_analysis(financial_data):
    """Demonstrate KPI analysis capabilities"""
    print("\n📈 KPI Analysis Demo")
    print("-" * 30)
    
    # Initialize KPI calculator
    calculator = KPICalculator()
    
    # Use latest financial data for analysis
    latest_data = financial_data.iloc[-1].to_dict()
    print(f"Analyzing latest period: {latest_data.get('period', 'Unknown')}")
    
    # Calculate financial KPIs
    print("\nCalculating financial KPIs...")
    kpis = calculator.calculate_financial_kpis(latest_data)
    
    # Display results
    print("\n📊 Financial KPIs:")
    for kpi in kpis:
        status_emoji = {
            'excellent': '🟢',
            'good': '🟡', 
            'warning': '🟠',
            'critical': '🔴'
        }
        emoji = status_emoji.get(kpi.status, '⚪')
        print(f"  {emoji} {kpi.name}: {kpi.value:.1f}% (Benchmark: {kpi.benchmark:.1f}%)")
    
    # Identify inefficiencies
    print("\n🔍 Identifying inefficiencies...")
    inefficiencies = calculator.identify_inefficiencies(kpis)
    
    if inefficiencies:
        print(f"\n⚠️  Found {len(inefficiencies)} inefficiencies:")
        for i, inefficiency in enumerate(inefficiencies, 1):
            print(f"  {i}. {inefficiency['kpi_name']}: {inefficiency['severity']} severity")
            print(f"     Recommended agent: {inefficiency['recommended_agent']}")
    else:
        print("✅ No critical inefficiencies found!")
    
    return kpis, inefficiencies

def demo_memory_system(kpis, inefficiencies):
    """Demonstrate memory system capabilities"""
    print("\n🧠 Memory System Demo")
    print("-" * 30)
    
    try:
        # Initialize memory system (will fail without API keys, but we can show the structure)
        print("Initializing memory system...")
        memory_system = HybridMemorySystem()
        
        # Store KPI data
        print("Storing KPI data in memory...")
        for kpi in kpis:
            memory_id = memory_system.store_kpi_data(
                kpi_name=kpi.name.lower().replace(' ', '_'),
                value=kpi.value,
                period="Q4_2024",
                benchmark=kpi.benchmark,
                status=kpi.status
            )
            if memory_id:
                print(f"  ✅ Stored {kpi.name} with ID: {memory_id}")
        
        # Store inefficiencies
        print("\nStoring inefficiencies in memory...")
        for inefficiency in inefficiencies:
            memory_id = memory_system.store_inefficiency(
                issue_type=inefficiency['issue_type'],
                description=f"{inefficiency['kpi_name']}: {inefficiency['current_value']:.1f}% vs {inefficiency['benchmark']:.1f}%",
                severity=inefficiency['severity'],
                recommended_agent=inefficiency['recommended_agent']
            )
            if memory_id:
                print(f"  ✅ Stored inefficiency with ID: {memory_id}")
        
        # Generate pattern summary
        print("\nGenerating pattern summary...")
        summary = memory_system.summarize_patterns()
        print(summary)
        
    except Exception as e:
        print(f"⚠️  Memory system demo skipped (requires API keys): {str(e)}")
        print("   This is expected when running without valid API keys.")

def demo_agent_workflow():
    """Demonstrate agent workflow (without API keys)"""
    print("\n🤖 Agent Workflow Demo")
    print("-" * 30)
    
    try:
        # Set placeholder API keys for demonstration
        os.environ['OPENAI_API_KEY'] = 'demo-key'
        os.environ['PINECONE_API_KEY'] = 'demo-key'
        
        from simple_crew import DiagnosticCrew
        
        print("Initializing diagnostic crew...")
        crew_instance = DiagnosticCrew()
        
        print("✅ Diagnostic agent created")
        print("✅ HR optimizer agent created") 
        print("✅ Operations optimizer agent created")
        print("✅ Financial optimizer agent created")
        
        print("\n📋 Available tasks:")
        print("  1. Request P&L data from user")
        print("  2. Compute KPIs and identify inefficiencies")
        print("  3. Create comprehensive diagnostic summary")
        
        print("\n🔄 Workflow:")
        print("  1. User provides P&L data → Diagnostic Agent")
        print("  2. KPI analysis → Identify inefficiencies")
        print("  3. Route to specialized agents:")
        print("     - HR Optimizer (for turnover issues)")
        print("     - Operations Optimizer (for efficiency issues)")
        print("     - Financial Optimizer (for margin issues)")
        print("  4. Generate comprehensive optimization strategy")
        
        print("\n⚠️  Full execution requires valid API keys")
        
    except Exception as e:
        print(f"❌ Agent workflow demo failed: {str(e)}")

def main():
    """Run the complete demo"""
    print("🚀 Company Efficiency Optimizer - Demo")
    print("=" * 50)
    print("This demo shows the system capabilities using sample data.")
    print("No API keys required for this demonstration.\n")
    
    try:
        # Demo 1: Data Ingestion
        hr_data, financial_data = demo_data_ingestion()
        
        # Demo 2: KPI Analysis
        kpis, inefficiencies = demo_kpi_analysis(financial_data)
        
        # Demo 3: Memory System
        demo_memory_system(kpis, inefficiencies)
        
        # Demo 4: Agent Workflow
        demo_agent_workflow()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\n📝 To run the full system:")
        print("1. Get API keys from:")
        print("   - OpenAI: https://platform.openai.com/api-keys")
        print("   - Pinecone: https://app.pinecone.io/")
        print("2. Update .env file with your keys")
        print("3. Run: python main.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())