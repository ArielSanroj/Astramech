#!/usr/bin/env python3
"""
Working Main Script - Bypasses Version Conflicts

This script provides the full Company Efficiency Optimizer functionality
without the LangChain version conflicts.
"""

import os
import sys
from dotenv import load_dotenv
from data_ingest import DataIngestion
from tools.kpi_calculator import KPICalculator
from memory_setup import HybridMemorySystem

load_dotenv()

class WorkingCompanyOptimizer:
    """Working Company Efficiency Optimizer (No Version Conflicts)"""
    
    def __init__(self):
        """Initialize the optimizer"""
        self.data_ingestion = DataIngestion()
        self.kpi_calculator = KPICalculator()
        self.memory_system = HybridMemorySystem()
    
    def run_complete_analysis(self):
        """Run complete company efficiency analysis"""
        print("🚀 Company Efficiency Optimizer - Working Version")
        print("=" * 60)
        
        # Step 1: Data Ingestion
        print("📊 Step 1: Data Ingestion")
        print("-" * 30)
        
        hr_data = self.data_ingestion._create_sample_hr_data()
        financial_data = self.data_ingestion._create_sample_financial_data()
        
        print(f"✅ HR Data: {len(hr_data)} employees")
        print(f"✅ Financial Data: {len(financial_data)} periods")
        
        # Calculate turnover rate
        turnover_rate = self.data_ingestion.calculate_turnover_rate(hr_data)
        print(f"📈 Turnover Rate: {turnover_rate:.2f}%")
        
        # Step 2: KPI Analysis
        print("\n📈 Step 2: KPI Analysis")
        print("-" * 30)
        
        latest_data = financial_data.iloc[-1].to_dict()
        print(f"Analyzing latest period: {latest_data.get('period', 'Unknown')}")
        
        # Calculate financial KPIs
        kpis = self.kpi_calculator.calculate_financial_kpis(latest_data)
        
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
        
        # Calculate HR KPIs
        hr_kpis = self.kpi_calculator.calculate_hr_kpis(hr_data)
        
        print("\n👥 HR KPIs:")
        for kpi in hr_kpis:
            status_emoji = {
                'excellent': '🟢',
                'good': '🟡', 
                'warning': '🟠',
                'critical': '🔴'
            }
            emoji = status_emoji.get(kpi.status, '⚪')
            print(f"  {emoji} {kpi.name}: {kpi.value:.1f}% (Benchmark: {kpi.benchmark:.1f}%)")
        
        # Calculate operational KPIs
        ops_kpis = self.kpi_calculator.calculate_operational_kpis(latest_data, hr_data)
        
        print("\n⚙️ Operational KPIs:")
        for kpi in ops_kpis:
            status_emoji = {
                'excellent': '🟢',
                'good': '🟡', 
                'warning': '🟠',
                'critical': '🔴'
            }
            emoji = status_emoji.get(kpi.status, '⚪')
            print(f"  {emoji} {kpi.name}: {kpi.value:.1f}% (Benchmark: {kpi.benchmark:.1f}%)")
        
        # Step 3: Inefficiency Detection
        print("\n🔍 Step 3: Inefficiency Detection")
        print("-" * 30)
        
        all_kpis = kpis + hr_kpis + ops_kpis
        inefficiencies = self.kpi_calculator.identify_inefficiencies(all_kpis)
        
        if inefficiencies:
            print(f"⚠️ Found {len(inefficiencies)} inefficiencies:")
            for i, inefficiency in enumerate(inefficiencies, 1):
                print(f"  {i}. {inefficiency['kpi_name']}: {inefficiency['severity']} severity")
                print(f"     Current: {inefficiency['current_value']:.1f}% vs Benchmark: {inefficiency['benchmark']:.1f}%")
                print(f"     Recommended agent: {inefficiency['recommended_agent']}")
                print()
        else:
            print("✅ No critical inefficiencies found!")
        
        # Step 4: Agent Recommendations
        print("🤖 Step 4: Agent Recommendations")
        print("-" * 30)
        
        agent_recommendations = {
            'hr_optimizer': [],
            'operations_optimizer': [],
            'financial_optimizer': []
        }
        
        for inefficiency in inefficiencies:
            agent = inefficiency['recommended_agent']
            if agent in agent_recommendations:
                agent_recommendations[agent].append(inefficiency)
        
        for agent, issues in agent_recommendations.items():
            if issues:
                agent_name = agent.replace('_', ' ').title()
                print(f"📋 {agent_name}:")
                for issue in issues:
                    print(f"   • {issue['kpi_name']}: {issue['description']}")
                print()
        
        # Step 5: Memory Storage
        print("🧠 Step 5: Memory Storage")
        print("-" * 30)
        
        try:
            # Store KPI data
            for kpi in all_kpis:
                memory_id = self.memory_system.store_kpi_data(
                    kpi_name=kpi.name.lower().replace(' ', '_'),
                    value=kpi.value,
                    period=latest_data.get('period', 'Q4_2024'),
                    benchmark=kpi.benchmark,
                    status=kpi.status
                )
                if memory_id:
                    print(f"✅ Stored {kpi.name} in memory")
            
            # Store inefficiencies
            for inefficiency in inefficiencies:
                memory_id = self.memory_system.store_inefficiency(
                    issue_type=inefficiency['issue_type'],
                    description=f"{inefficiency['kpi_name']}: {inefficiency['current_value']:.1f}% vs {inefficiency['benchmark']:.1f}%",
                    severity=inefficiency['severity'],
                    recommended_agent=inefficiency['recommended_agent']
                )
                if memory_id:
                    print(f"✅ Stored inefficiency in memory")
            
            # Generate pattern summary
            summary = self.memory_system.summarize_patterns()
            print("\n📊 Memory Pattern Summary:")
            print(summary)
            
        except Exception as e:
            print(f"⚠️ Memory storage skipped: {str(e)}")
        
        # Step 6: Optimization Recommendations
        print("\n🎯 Step 6: Optimization Recommendations")
        print("-" * 30)
        
        print("📋 Strategic Recommendations:")
        
        if any(i['recommended_agent'] == 'hr_optimizer' for i in inefficiencies):
            print("\n👥 HR OPTIMIZATION:")
            print("   • Implement employee retention programs")
            print("   • Conduct exit interviews to identify turnover causes")
            print("   • Develop career advancement opportunities")
            print("   • Improve onboarding and training programs")
            print("   • Implement flexible work arrangements")
        
        if any(i['recommended_agent'] == 'operations_optimizer' for i in inefficiencies):
            print("\n⚙️ OPERATIONS OPTIMIZATION:")
            print("   • Streamline operational processes")
            print("   • Implement lean manufacturing principles")
            print("   • Optimize resource allocation")
            print("   • Automate repetitive tasks")
            print("   • Improve supply chain efficiency")
        
        if any(i['recommended_agent'] == 'financial_optimizer' for i in inefficiencies):
            print("\n💰 FINANCIAL OPTIMIZATION:")
            print("   • Optimize pricing strategies")
            print("   • Reduce operational costs")
            print("   • Improve cash flow management")
            print("   • Implement cost control measures")
            print("   • Explore new revenue streams")
        
        # Step 7: Implementation Roadmap
        print("\n📅 Step 7: Implementation Roadmap")
        print("-" * 30)
        
        print("🚀 IMMEDIATE ACTIONS (0-30 days):")
        print("   • Prioritize critical inefficiencies")
        print("   • Assign specialized agents to high-impact issues")
        print("   • Set up monitoring and tracking systems")
        
        print("\n📈 SHORT-TERM GOALS (1-3 months):")
        print("   • Implement targeted optimization strategies")
        print("   • Monitor KPI improvements")
        print("   • Adjust strategies based on results")
        
        print("\n🎯 LONG-TERM OBJECTIVES (3-12 months):")
        print("   • Achieve industry benchmark performance")
        print("   • Implement continuous improvement processes")
        print("   • Scale successful optimization strategies")
        
        print("\n🎉 Company Efficiency Analysis Complete!")
        print("=" * 60)
        print("📈 Review the results above and implement the recommended strategies.")
        print("🤖 Powered by Advanced KPI Analysis Engine!")

def main():
    """Main execution function"""
    try:
        optimizer = WorkingCompanyOptimizer()
        optimizer.run_complete_analysis()
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        print("🔧 Please check your configuration and try again.")

if __name__ == "__main__":
    main()