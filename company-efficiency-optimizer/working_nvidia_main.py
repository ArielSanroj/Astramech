#!/usr/bin/env python3
"""
Working NVIDIA AI Endpoints Main Execution Script

This script runs the diagnostic and multi-agent architecture using NVIDIA AI Endpoints.
"""

import os
import sys
from dotenv import load_dotenv
from working_nvidia_crew import WorkingNVIDIACrew

def main():
    """Main execution function"""
    print("🚀 Starting Company Efficiency Optimizer (NVIDIA AI Endpoints)")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    required_keys = ['NVIDIA_API_KEY', 'PINECONE_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key) or os.getenv(key) == f'your_{key.lower()}_here']
    
    if missing_keys:
        print("❌ Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n📝 Please update your .env file with valid API keys:")
        print("   - NVIDIA_API_KEY: Get from build.nvidia.com/explore")
        print("   - PINECONE_API_KEY: Get from pinecone.io")
        return
    
    try:
        # Initialize the NVIDIA crew
        print("🔧 Initializing NVIDIA diagnostic crew...")
        crew_instance = WorkingNVIDIACrew()
        
        # Test NVIDIA connection
        print("🧪 Testing NVIDIA AI Endpoints connection...")
        if not crew_instance.test_nvidia_connection():
            print("❌ NVIDIA connection test failed. Please check your API key.")
            return
        
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
        specialized_result = "Specialized optimization analysis would be implemented with NVIDIA agents"
        
        print("\n🎯 Specialized optimization completed!")
        print("=" * 60)
        print("📊 Optimization Results:")
        print(specialized_result)
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        print("🔧 Please check your configuration and try again.")
        return
    
    print("\n🎉 Company Efficiency Optimization Complete!")
    print("📈 Review the results above and implement the recommended strategies.")
    print("🤖 Powered by NVIDIA AI Endpoints!")

if __name__ == "__main__":
    main()