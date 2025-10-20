#!/usr/bin/env python3
"""
Direct NVIDIA AI Endpoints Main Script

This script bypasses the LangChain version conflicts and uses NVIDIA AI Endpoints directly
for the Company Efficiency Optimizer.
"""

import os
import requests
import json
from dotenv import load_dotenv
from data_ingest import DataIngestion
from tools.kpi_calculator import KPICalculator

load_dotenv()

class NVIDIADirectOptimizer:
    """Direct NVIDIA AI Endpoints Company Efficiency Optimizer"""
    
    def __init__(self):
        """Initialize the optimizer"""
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.model = "nvidia/nemotron-4-340b-instruct"
        
        # Initialize components
        self.data_ingestion = DataIngestion()
        self.kpi_calculator = KPICalculator()
    
    def nvidia_chat(self, prompt, max_tokens=1000):
        """Send request to NVIDIA AI Endpoints"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Exception: {str(e)}"
    
    def analyze_company_data(self, financial_data, hr_data):
        """Analyze company data using NVIDIA AI"""
        
        # Calculate KPIs first
        latest_data = financial_data.iloc[-1].to_dict()
        kpis = self.kpi_calculator.calculate_financial_kpis(latest_data)
        inefficiencies = self.kpi_calculator.identify_inefficiencies(kpis)
        
        # Create analysis prompt
        prompt = f"""
        As a Business Analyst expert in KPIs and inefficiencies, analyze this company's performance:
        
        FINANCIAL DATA:
        Revenue: ${latest_data.get('revenue', 0):,}
        Cost of Goods Sold: ${latest_data.get('cogs', 0):,}
        Operating Expenses: ${latest_data.get('operating_expenses', 0):,}
        Net Income: ${latest_data.get('net_income', 0):,}
        Employee Count: {latest_data.get('employee_count', 0)}
        
        CALCULATED KPIs:
        """
        
        for kpi in kpis:
            prompt += f"- {kpi.name}: {kpi.value:.1f}% (Benchmark: {kpi.benchmark:.1f}%, Status: {kpi.status})\n"
        
        prompt += f"""
        
        IDENTIFIED INEFFICIENCIES:
        """
        for inefficiency in inefficiencies:
            prompt += f"- {inefficiency['kpi_name']}: {inefficiency['severity']} severity\n"
        
        prompt += """
        
        Please provide:
        1. Executive Summary of company performance
        2. Top 3 critical issues requiring immediate attention
        3. Specific recommendations for each issue
        4. Recommended specialized agents for optimization
        5. Implementation roadmap with priorities
        
        Focus on actionable insights and specific optimization strategies.
        """
        
        return self.nvidia_chat(prompt)
    
    def generate_optimization_strategy(self, analysis_result, inefficiencies):
        """Generate detailed optimization strategy"""
        
        prompt = f"""
        Based on this company analysis:
        
        {analysis_result}
        
        And these identified inefficiencies:
        """
        
        for inefficiency in inefficiencies:
            prompt += f"- {inefficiency['kpi_name']}: {inefficiency['severity']} severity\n"
        
        prompt += """
        
        Generate a comprehensive optimization strategy including:
        
        1. HR OPTIMIZATION (for turnover/talent issues):
           - Specific retention strategies
           - Recruitment improvements
           - Training and development programs
           
        2. OPERATIONS OPTIMIZATION (for efficiency issues):
           - Process improvement recommendations
           - Technology implementation suggestions
           - Resource optimization strategies
           
        3. FINANCIAL OPTIMIZATION (for margin issues):
           - Cost reduction opportunities
           - Revenue enhancement strategies
           - Pricing optimization recommendations
           
        4. IMPLEMENTATION TIMELINE:
           - Immediate actions (0-30 days)
           - Short-term goals (1-3 months)
           - Long-term objectives (3-12 months)
           
        5. EXPECTED OUTCOMES:
           - Quantified benefits
           - ROI projections
           - Success metrics
        """
        
        return self.nvidia_chat(prompt, max_tokens=1500)
    
    def run_full_analysis(self):
        """Run complete company efficiency analysis"""
        print("🚀 Starting NVIDIA-Powered Company Efficiency Analysis")
        print("=" * 60)
        
        # Step 1: Data Ingestion
        print("📊 Step 1: Data Ingestion")
        print("-" * 30)
        hr_data = self.data_ingestion._create_sample_hr_data()
        financial_data = self.data_ingestion._create_sample_financial_data()
        print(f"✅ HR Data: {len(hr_data)} employees")
        print(f"✅ Financial Data: {len(financial_data)} periods")
        
        # Step 2: KPI Analysis
        print("\n📈 Step 2: KPI Analysis")
        print("-" * 30)
        latest_data = financial_data.iloc[-1].to_dict()
        kpis = self.kpi_calculator.calculate_financial_kpis(latest_data)
        inefficiencies = self.kpi_calculator.identify_inefficiencies(kpis)
        
        print("📊 Financial KPIs:")
        for kpi in kpis:
            status_emoji = {'excellent': '🟢', 'good': '🟡', 'warning': '🟠', 'critical': '🔴'}
            emoji = status_emoji.get(kpi.status, '⚪')
            print(f"  {emoji} {kpi.name}: {kpi.value:.1f}% (Benchmark: {kpi.benchmark:.1f}%)")
        
        print(f"\n⚠️ Found {len(inefficiencies)} inefficiencies")
        
        # Step 3: NVIDIA AI Analysis
        print("\n🤖 Step 3: NVIDIA AI Analysis")
        print("-" * 30)
        print("🔍 Analyzing company performance with NVIDIA AI...")
        
        analysis_result = self.analyze_company_data(financial_data, hr_data)
        
        print("✅ Company Analysis Complete!")
        print("=" * 60)
        print("📋 ANALYSIS RESULTS:")
        print(analysis_result)
        
        # Step 4: Optimization Strategy
        print("\n🎯 Step 4: Optimization Strategy")
        print("-" * 30)
        print("🔍 Generating optimization strategy with NVIDIA AI...")
        
        strategy_result = self.generate_optimization_strategy(analysis_result, inefficiencies)
        
        print("✅ Optimization Strategy Complete!")
        print("=" * 60)
        print("📊 OPTIMIZATION STRATEGY:")
        print(strategy_result)
        
        print("\n🎉 NVIDIA-Powered Analysis Complete!")
        print("📈 Review the results above and implement the recommended strategies.")
        print("🤖 Powered by NVIDIA AI Endpoints!")

def main():
    """Main execution function"""
    print("🚀 NVIDIA AI Endpoints Company Efficiency Optimizer")
    print("=" * 60)
    
    # Check for NVIDIA API key
    if not os.getenv("NVIDIA_API_KEY"):
        print("❌ NVIDIA_API_KEY not found in environment")
        print("📝 Please add your NVIDIA API key to the .env file")
        return
    
    try:
        # Initialize and run analysis
        optimizer = NVIDIADirectOptimizer()
        optimizer.run_full_analysis()
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        print("🔧 Please check your configuration and try again.")

if __name__ == "__main__":
    main()