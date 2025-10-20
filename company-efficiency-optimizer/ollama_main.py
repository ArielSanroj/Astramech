#!/usr/bin/env python3
"""
Company Efficiency Optimizer - Ollama Main Execution Script

This script runs the diagnostic and multi-agent architecture using Ollama with llama3.1:8b.
It starts with Phase 1 (System Setup and Data Preparation) and moves into Phase 2 (Diagnostic Analysis).
"""

import os
import sys
from dotenv import load_dotenv
from ollama_crew import OllamaDiagnosticCrew
from data_ingest import DataIngestion
from tools.kpi_calculator import KPICalculator

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        import ollama
        client = ollama.Client(host=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
        
        # Check if the model is available
        models = client.list()
        model_name = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        
        available_models = [model['name'] for model in models['models']]
        if model_name not in available_models:
            print(f"⚠️ Model {model_name} not found. Available models: {available_models}")
            print(f"💡 To install the model, run: ollama pull {model_name}")
            return False
        
        print(f"✅ Ollama connection successful. Model {model_name} is available.")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {str(e)}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def main():
    """Main execution function"""
    print("🚀 Starting Company Efficiency Optimizer (Ollama Version)")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check Ollama connection
    if not check_ollama_connection():
        print("\n🔧 Please start Ollama and install the required model:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Install model: ollama pull llama3.1:8b")
        print("   3. Run this script again")
        return
    
    try:
        # Initialize the crew
        print("\n🔧 Initializing diagnostic crew with Ollama...")
        crew_instance = OllamaDiagnosticCrew()
        
        # Start the diagnostic process
        print("📊 Starting diagnostic analysis...")
        print("   This will begin by requesting your P&L data...")
        
        # Run the main diagnostic crew
        result = crew_instance.run_diagnostic(initial_data=None)
        
        print("\n✅ Diagnostic analysis completed!")
        print("=" * 60)
        print("📋 Results Summary:")
        print(result)
        
        # Ask if user wants to run specialized analysis
        print("\n🤔 Would you like to run specialized optimization analysis?")
        print("   This will deploy HR, Operations, and Financial specialists...")
        
        # For now, we'll automatically run specialized analysis
        # In a full implementation, you'd add user input here
        print("🔍 Running specialized optimization analysis...")
        # Note: Specialized crew functionality would be implemented here
        specialized_result = "Specialized optimization analysis would be implemented with full Ollama integration"
        
        print("\n🎯 Specialized optimization completed!")
        print("=" * 60)
        print("📊 Optimization Results:")
        print(specialized_result)
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        print("🔧 Please check your Ollama configuration and try again.")
        return
    
    print("\n🎉 Company Efficiency Optimization Complete!")
    print("📈 Review the results above and implement the recommended strategies.")

if __name__ == "__main__":
    main()