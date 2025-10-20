#!/usr/bin/env python3
"""
Interactive Company Efficiency Optimizer

This script follows the proper user journey:
1. Request P&L data from user
2. Read and analyze the data
3. Identify inefficiencies
4. Suggest specialized agents
5. Provide optimization recommendations
"""

import os
import sys
import json
from dotenv import load_dotenv
from data_ingest import DataIngestion
from nanobot_bridge import NanobotBridge
from tools.kpi_calculator import KPICalculator

load_dotenv()

class InteractiveCompanyOptimizer:
    """Interactive Company Efficiency Optimizer with proper user journey"""
    
    def __init__(self):
        """Initialize the optimizer"""
        self.data_ingestion = DataIngestion()
        self.kpi_calculator = KPICalculator()
        self.nanobot = NanobotBridge(configuration_path="nanobot.yaml")
    
    def request_pnl_data(self):
        """Step 1: Request P&L data from user"""
        print("🚀 Company Efficiency Optimizer")
        print("=" * 50)
        print("Welcome! I'm here to help analyze your company's efficiency.")
        print()
        
        print("📊 STEP 1: P&L Data Collection")
        print("-" * 30)
        print("To analyze your company's performance, I need your P&L data.")
        print()
        print("You can provide this data in several ways:")
        print("1. 📄 Upload a PDF file")
        print("2. 📊 Provide CSV data")
        print("3. ✍️  Enter data manually")
        print("4. 🎭 Use sample data for demonstration")
        print()
        
        while True:
            choice = input("Please choose an option (1-4): ").strip()
            
            if choice == "1":
                return self.handle_pdf_upload()
            elif choice == "2":
                return self.handle_csv_upload()
            elif choice == "3":
                return self.handle_manual_input()
            elif choice == "4":
                return self.handle_sample_data()
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    def handle_pdf_upload(self):
        """Handle PDF file upload"""
        print("\n📄 PDF Upload")
        print("-" * 15)
        print("Please place your P&L PDF file in the 'data' folder.")
        print("The system will extract financial data using OCR.")
        
        # For now, use sample data (in real implementation, would process PDF)
        print("⚠️ PDF processing not fully implemented yet.")
        print("Using sample data for demonstration...")
        return self.get_sample_financial_data()
    
    def handle_csv_upload(self):
        """Handle CSV file upload"""
        print("\n📊 CSV Upload")
        print("-" * 15)
        print("Please place your P&L CSV file in the 'data' folder.")
        print("Expected columns: revenue, cogs, operating_expenses, net_income, employee_count")
        
        # For now, use sample data (in real implementation, would read CSV)
        print("⚠️ CSV processing not fully implemented yet.")
        print("Using sample data for demonstration...")
        return self.get_sample_financial_data()
    
    def handle_manual_input(self):
        """Handle manual data input"""
        print("\n✍️ Manual Data Input")
        print("-" * 20)
        print("Please enter your company's financial data:")
        print()
        
        try:
            revenue = float(input("Revenue ($): ").replace(',', '').replace('$', ''))
            cogs = float(input("Cost of Goods Sold ($): ").replace(',', '').replace('$', ''))
            operating_expenses = float(input("Operating Expenses ($): ").replace(',', '').replace('$', ''))
            net_income = float(input("Net Income ($): ").replace(',', '').replace('$', ''))
            employee_count = int(input("Employee Count: "))
            
            financial_data = {
                'revenue': revenue,
                'cogs': cogs,
                'gross_profit': revenue - cogs,
                'operating_expenses': operating_expenses,
                'operating_income': revenue - cogs - operating_expenses,
                'net_income': net_income,
                'employee_count': employee_count,
                'period': 'Current_Period'
            }
            
            print(f"\n✅ Data received:")
            print(f"   Revenue: ${revenue:,.2f}")
            print(f"   COGS: ${cogs:,.2f}")
            print(f"   Operating Expenses: ${operating_expenses:,.2f}")
            print(f"   Net Income: ${net_income:,.2f}")
            print(f"   Employees: {employee_count}")
            
            return financial_data
            
        except ValueError:
            print("❌ Invalid input. Please enter numeric values.")
            return self.handle_manual_input()
    
    def handle_sample_data(self):
        """Handle sample data selection"""
        print("\n🎭 Sample Data Selection")
        print("-" * 25)
        print("Choose a sample company scenario:")
        print("1. 🏪 Retail Company (Good Performance)")
        print("2. 🏭 Manufacturing Company (Mixed Performance)")
        print("3. 💼 Services Company (Poor Performance)")
        print("4. 🎯 Custom Sample Data")
        
        while True:
            choice = input("Choose scenario (1-4): ").strip()
            
            if choice == "1":
                return self.get_retail_sample_data()
            elif choice == "2":
                return self.get_manufacturing_sample_data()
            elif choice == "3":
                return self.get_services_sample_data()
            elif choice == "4":
                return self.get_sample_financial_data()
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    def get_retail_sample_data(self):
        """Get retail company sample data"""
        return {
            'revenue': 2000000,
            'cogs': 1400000,
            'gross_profit': 600000,
            'operating_expenses': 400000,
            'operating_income': 200000,
            'net_income': 160000,
            'employee_count': 25,
            'period': 'Q4_2024',
            'company_type': 'Retail'
        }
    
    def get_manufacturing_sample_data(self):
        """Get manufacturing company sample data"""
        return {
            'revenue': 5000000,
            'cogs': 3750000,
            'gross_profit': 1250000,
            'operating_expenses': 800000,
            'operating_income': 450000,
            'net_income': 360000,
            'employee_count': 100,
            'period': 'Q4_2024',
            'company_type': 'Manufacturing'
        }
    
    def get_services_sample_data(self):
        """Get services company sample data with poor performance"""
        return {
            'revenue': 800000,
            'cogs': 200000,
            'gross_profit': 600000,
            'operating_expenses': 700000,
            'operating_income': -100000,
            'net_income': -120000,
            'employee_count': 15,
            'period': 'Q4_2024',
            'company_type': 'Services'
        }
    
    def get_sample_financial_data(self):
        """Get default sample data"""
        return {
            'revenue': 1000000,
            'cogs': 700000,
            'gross_profit': 300000,
            'operating_expenses': 200000,
            'operating_income': 100000,
            'net_income': 80000,
            'employee_count': 50,
            'period': 'Q4_2024',
            'company_type': 'Mixed'
        }
    
    def analyze_financial_data(self, financial_data):
        """Step 2: Analyze the P&L data"""
        print("\n📈 STEP 2: Financial Data Analysis")
        print("-" * 35)
        print("Analyzing your P&L data...")
        print()
        
        # Display the data
        print("📊 Your Financial Data:")
        print(f"   Revenue: ${financial_data['revenue']:,.2f}")
        print(f"   Cost of Goods Sold: ${financial_data['cogs']:,.2f}")
        print(f"   Gross Profit: ${financial_data['gross_profit']:,.2f}")
        print(f"   Operating Expenses: ${financial_data['operating_expenses']:,.2f}")
        print(f"   Operating Income: ${financial_data['operating_income']:,.2f}")
        print(f"   Net Income: ${financial_data['net_income']:,.2f}")
        print(f"   Employee Count: {financial_data['employee_count']}")
        print()
        
        # Calculate KPIs
        print("🔍 Calculating Key Performance Indicators...")
        kpis = self.kpi_calculator.calculate_financial_kpis(financial_data)
        
        print("\n📊 Financial KPIs Analysis:")
        for kpi in kpis:
            status_emoji = {
                'excellent': '🟢',
                'good': '🟡', 
                'warning': '🟠',
                'critical': '🔴'
            }
            emoji = status_emoji.get(kpi.status, '⚪')
            print(f"   {emoji} {kpi.name}: {kpi.value:.1f}% (Benchmark: {kpi.benchmark:.1f}%)")
        
        return kpis
    
    def identify_inefficiencies(self, kpis):
        """Step 3: Identify inefficiencies"""
        print("\n🔍 STEP 3: Inefficiency Detection")
        print("-" * 35)
        print("Scanning for performance issues...")
        print()
        
        inefficiencies = self.kpi_calculator.identify_inefficiencies(kpis)
        
        if inefficiencies:
            print(f"⚠️ Found {len(inefficiencies)} inefficiencies:")
            print()
            for i, inefficiency in enumerate(inefficiencies, 1):
                print(f"   {i}. {inefficiency['kpi_name']}")
                print(f"      Current: {inefficiency['current_value']:.1f}%")
                print(f"      Benchmark: {inefficiency['benchmark']:.1f}%")
                print(f"      Severity: {inefficiency['severity'].upper()}")
                print(f"      Issue: {inefficiency['description']}")
                print()
        else:
            print("✅ No critical inefficiencies found!")
            print("Your company is performing well against industry benchmarks.")
        
        return inefficiencies
    
    def suggest_agents(self, inefficiencies):
        """Step 4: Suggest specialized agents"""
        print("\n🤖 STEP 4: Specialized Agent Recommendations")
        print("-" * 45)
        print("Based on the identified inefficiencies, I recommend deploying these specialized agents:")
        print()
        
        agent_recommendations = {
            'hr_optimizer': [],
            'operations_optimizer': [],
            'financial_optimizer': []
        }
        
        for inefficiency in inefficiencies:
            agent = inefficiency['recommended_agent']
            if agent in agent_recommendations:
                agent_recommendations[agent].append(inefficiency)
        
        agents_deployed = []
        
        for agent, issues in agent_recommendations.items():
            if issues:
                agent_name = agent.replace('_', ' ').title()
                agents_deployed.append(agent_name)
                
                print(f"🎯 {agent_name}:")
                for issue in issues:
                    print(f"   • {issue['kpi_name']}: {issue['severity']} severity")
                print()
        
        if not agents_deployed:
            print("✅ No specialized agents needed - your company is performing well!")
            return []

        print(f"📋 Recommended Agents: {', '.join(agents_deployed)}")
        self.nanobot.sync_agents({
            "recommended_agents": [
                {
                    "type": agent,
                    "goal": f"Resolve issues flagged for {agent}",
                    "priority": "high",
                    "focus_areas": [issue['kpi_name'] for issue in inefficiencies],
                }
                for agent in agents_deployed
            ]
        })
        print("🤖 Nanobot configuration updated with recommended agents")
        return agents_deployed
    
    def provide_optimization_recommendations(self, inefficiencies, agents_deployed):
        """Step 5: Provide optimization recommendations"""
        print("\n🎯 STEP 5: Optimization Recommendations")
        print("-" * 40)
        print("Here are the specific optimization strategies for your company:")
        print()
        
        if 'HR Optimizer' in agents_deployed:
            print("👥 HR OPTIMIZATION STRATEGIES:")
            print("   • Implement comprehensive employee retention programs")
            print("   • Conduct regular exit interviews to identify turnover causes")
            print("   • Develop clear career advancement pathways")
            print("   • Improve onboarding and training programs")
            print("   • Implement flexible work arrangements and benefits")
            print("   • Create employee engagement and satisfaction surveys")
            print()
        
        if 'Operations Optimizer' in agents_deployed:
            print("⚙️ OPERATIONS OPTIMIZATION STRATEGIES:")
            print("   • Streamline operational processes and eliminate bottlenecks")
            print("   • Implement lean manufacturing/service delivery principles")
            print("   • Optimize resource allocation and capacity planning")
            print("   • Automate repetitive and low-value tasks")
            print("   • Improve supply chain and logistics efficiency")
            print("   • Implement quality control and continuous improvement")
            print()
        
        if 'Financial Optimizer' in agents_deployed:
            print("💰 FINANCIAL OPTIMIZATION STRATEGIES:")
            print("   • Optimize pricing strategies to improve margins")
            print("   • Identify and reduce unnecessary operational costs")
            print("   • Improve cash flow management and working capital")
            print("   • Implement cost control and budget monitoring systems")
            print("   • Explore new revenue streams and market opportunities")
            print("   • Optimize tax strategies and financial planning")
            print()
        
        if not agents_deployed:
            print("✅ Your company is performing well! Focus on:")
            print("   • Maintaining current performance levels")
            print("   • Continuous improvement and innovation")
            print("   • Market expansion opportunities")
            print("   • Competitive advantage enhancement")
    
    def create_implementation_roadmap(self, inefficiencies, agents_deployed):
        """Step 6: Create implementation roadmap"""
        print("\n📅 STEP 6: Implementation Roadmap")
        print("-" * 35)
        print("Here's your strategic implementation timeline:")
        print()
        
        print("🚀 IMMEDIATE ACTIONS (0-30 days):")
        print("   • Prioritize the most critical inefficiencies")
        print("   • Assign specialized agents to high-impact issues")
        print("   • Set up monitoring and tracking systems")
        print("   • Establish baseline metrics for improvement")
        print("   • Create cross-functional optimization teams")
        print()
        
        print("📈 SHORT-TERM GOALS (1-3 months):")
        print("   • Implement targeted optimization strategies")
        print("   • Monitor KPI improvements and adjust strategies")
        print("   • Train teams on new processes and systems")
        print("   • Establish regular performance reviews")
        print("   • Begin seeing measurable improvements")
        print()
        
        print("🎯 LONG-TERM OBJECTIVES (3-12 months):")
        print("   • Achieve industry benchmark performance")
        print("   • Implement continuous improvement processes")
        print("   • Scale successful optimization strategies")
        print("   • Develop competitive advantages")
        print("   • Prepare for future growth and expansion")
        print()
        
        if inefficiencies:
            critical_count = len([i for i in inefficiencies if i['severity'] == 'critical'])
            warning_count = len([i for i in inefficiencies if i['severity'] == 'warning'])
            
            print(f"📊 Expected Outcomes:")
            print(f"   • Address {critical_count} critical inefficiencies")
            print(f"   • Improve {warning_count} warning-level issues")
            print(f"   • Achieve industry benchmark performance")
            print(f"   • Increase operational efficiency by 15-25%")
            print(f"   • Improve financial performance significantly")
    
    def run_interactive_analysis(self):
        """Run the complete interactive analysis"""
        try:
            # Step 1: Request P&L data
            financial_data = self.request_pnl_data()
            
            # Step 2: Analyze financial data
            kpis = self.analyze_financial_data(financial_data)
            
            # Step 3: Identify inefficiencies
            inefficiencies = self.identify_inefficiencies(kpis)
            
            # Step 4: Suggest agents
            agents_deployed = self.suggest_agents(inefficiencies)
            
            # Step 5: Provide optimization recommendations
            self.provide_optimization_recommendations(inefficiencies, agents_deployed)
            
            # Step 6: Create implementation roadmap
            self.create_implementation_roadmap(inefficiencies, agents_deployed)
            
            # Final summary
            print("\n🎉 ANALYSIS COMPLETE!")
            print("=" * 30)
            print("📈 Your Company Efficiency Analysis is complete!")
            print("📋 Review the recommendations above and begin implementation.")
            print("🤖 The specialized agents are ready to help optimize your business!")
            print()
            print("💡 Next Steps:")
            print("   1. Prioritize the most critical inefficiencies")
            print("   2. Assign teams to each optimization area")
            print("   3. Set up regular monitoring and reviews")
            print("   4. Track progress against benchmarks")
            print()
            print("🚀 Ready to optimize your company's efficiency!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Analysis interrupted by user. Goodbye!")
        except Exception as e:
            print(f"\n❌ Error during analysis: {str(e)}")
            print("🔧 Please try again or contact support.")

def main():
    """Main execution function"""
    optimizer = InteractiveCompanyOptimizer()
    optimizer.run_interactive_analysis()

if __name__ == "__main__":
    main()