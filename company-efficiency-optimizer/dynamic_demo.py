#!/usr/bin/env python3
"""
Dynamic Agent Creation Demo

This demo shows the complete workflow of dynamic agent creation based on
company inefficiencies identified through P&L analysis.
"""

import os
import json
from datetime import datetime
from dynamic_crew import DynamicCrewSystem

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step_num: int, title: str):
    """Print a formatted step."""
    print(f"\n📊 Step {step_num}: {title}")
    print("-" * 40)

def simulate_user_interaction():
    """Simulate user providing P&L data."""
    print("\n👤 User Interaction Simulation")
    print("-" * 35)
    print("👤 User: I'll provide my company's P&L data for analysis")
    print("📊 User: Here's our financial data:")
    print("   • Revenue: $800,000")
    print("   • Cost of Goods Sold: $200,000") 
    print("   • Operating Expenses: $700,000")
    print("   • Operating Profit: -$100,000")
    print("   • Net Profit: -$120,000")
    print("   • Employee Count: 15")
    print("   • Revenue Growth: 0%")
    print("\n👤 User: Please analyze this and create specialized agents to help us improve")

def run_dynamic_agent_demo():
    """Run the complete dynamic agent creation demo."""
    
    print_header("Dynamic Agent Creation Demo")
    print("This demo shows how the system analyzes P&L data and creates")
    print("specialized AI agents tailored to address specific business inefficiencies.")
    
    # Step 1: User provides P&L data
    print_step(1, "User Provides P&L Data")
    simulate_user_interaction()
    
    # Step 2: Initialize dynamic system
    print_step(2, "Initialize Dynamic Crew System")
    print("🔧 Initializing dynamic crew system...")
    dynamic_system = DynamicCrewSystem()
    print("✅ System initialized successfully")
    
    # Step 3: Analyze P&L data
    print_step(3, "Analyze P&L Data and Identify Inefficiencies")
    
    # Sample P&L data (services company with poor performance)
    pnl_data = {
        'revenue': 800000,
        'cogs': 200000,
        'opex': 700000,
        'operating_profit': -100000,
        'net_profit': -120000,
        'employee_count': 15,
        'revenue_growth': 0.0
    }
    
    print("📊 Analyzing financial data...")
    print(f"   Revenue: ${pnl_data['revenue']:,}")
    print(f"   Operating Profit: ${pnl_data['operating_profit']:,}")
    print(f"   Net Profit: ${pnl_data['net_profit']:,}")
    print(f"   Employees: {pnl_data['employee_count']}")
    
    # Step 4: Run KPI analysis
    print("\n🔍 Running KPI analysis...")
    try:
        analysis_result = dynamic_system.kpi_tool._run(pnl_data)
        
        print(f"✅ Analysis complete!")
        print(f"   • Total Inefficiencies: {analysis_result['summary']['total_inefficiencies']}")
        print(f"   • Critical Issues: {analysis_result['summary']['critical_issues']}")
        print(f"   • Warning Issues: {analysis_result['summary']['warning_issues']}")
        print(f"   • Agents Needed: {analysis_result['summary']['agents_needed']}")
        
        # Show identified inefficiencies
        print("\n⚠️ Identified Inefficiencies:")
        for i, inefficiency in enumerate(analysis_result['inefficiencies'], 1):
            severity_emoji = "🔴" if inefficiency['severity'] == 'critical' else "🟡"
            print(f"   {i}. {inefficiency['kpi_name']} {severity_emoji}")
            print(f"      Current: {inefficiency['current_value']:.1f}% vs Benchmark: {inefficiency['benchmark']:.1f}%")
            print(f"      Issue: {inefficiency['description']}")
            print(f"      Recommended Agent: {inefficiency['recommended_agent']}")
            print()
        
        # Show recommended agents
        print("🤖 Recommended AI Agents:")
        for i, agent in enumerate(analysis_result['recommended_agents'], 1):
            priority_emoji = "🔴" if agent['priority'] == 'critical' else "🟡" if agent['priority'] == 'high' else "🟢"
            print(f"   {i}. {agent['type']} {priority_emoji}")
            print(f"      Goal: {agent['goal']}")
            print(f"      Priority: {agent['priority'].upper()}")
            print(f"      Focus Areas: {', '.join(agent['focus_areas'])}")
            print()
        
    except Exception as e:
        print(f"❌ KPI analysis failed: {str(e)}")
        return
    
    # Step 5: Generate dynamic agents
    print_step(4, "Generate Specialized AI Agents")
    print("🤖 Creating specialized agents using NVIDIA LLM...")
    
    try:
        # Generate agents
        report = dynamic_system.agent_creator._run(analysis_result)
        print("✅ Dynamic agents generated successfully!")
        
        # Check if agents were created
        if os.path.exists('config/dynamic_agents.yaml'):
            print("💾 Agent configurations saved to config/dynamic_agents.yaml")
            
            # Load and display agent info
            import yaml
            with open('config/dynamic_agents.yaml', 'r') as f:
                agent_configs = yaml.safe_load(f)
            
            print(f"\n🎯 Generated {len(agent_configs)} Specialized Agents:")
            for agent_key, config in agent_configs.items():
                print(f"   • {config['role']}")
                print(f"     Goal: {config['goal']}")
                print(f"     Priority: {config.get('priority', 'medium').upper()}")
                print(f"     Capabilities: {len(config.get('capabilities', []))} specialized skills")
                print()
        
    except Exception as e:
        print(f"❌ Agent generation failed: {str(e)}")
        return
    
    # Step 6: Create dynamic crew
    print_step(5, "Create Dynamic Multi-Agent Crew")
    print("🚀 Creating crew with diagnostic agent and generated specialists...")
    
    try:
        crew = dynamic_system.create_dynamic_crew()
        if crew:
            print("✅ Dynamic crew created successfully!")
            print(f"   • Total Agents: {len(crew.agents)}")
            print(f"   • Total Tasks: {len(crew.tasks)}")
            
            # List agents
            print("\n🤖 Crew Agents:")
            for i, agent in enumerate(crew.agents, 1):
                print(f"   {i}. {agent.role}")
        else:
            print("⚠️ Failed to create crew")
            
    except Exception as e:
        print(f"❌ Crew creation failed: {str(e)}")
        return
    
    # Step 7: Show implementation roadmap
    print_step(6, "Implementation Roadmap")
    print("📅 Here's your strategic implementation timeline:")
    print()
    print("🚀 IMMEDIATE ACTIONS (0-30 days):")
    print("   • Deploy critical priority agents first")
    print("   • Set up monitoring and tracking systems")
    print("   • Establish baseline metrics for each agent")
    print("   • Create cross-functional optimization teams")
    print()
    print("📈 SHORT-TERM GOALS (1-3 months):")
    print("   • Implement agent-specific optimization strategies")
    print("   • Monitor KPI improvements and adjust approaches")
    print("   • Train teams on new processes and systems")
    print("   • Measure and report on agent performance")
    print()
    print("🎯 LONG-TERM OBJECTIVES (3-12 months):")
    print("   • Achieve industry benchmark performance")
    print("   • Scale successful optimization strategies")
    print("   • Develop competitive advantages")
    print("   • Implement continuous improvement processes")
    
    # Step 8: Show agent summary
    print_step(7, "Agent Summary")
    dynamic_system.list_available_agents()
    
    # Final summary
    print_header("Dynamic Agent Creation Complete!")
    print("🎉 Your Company Efficiency Optimizer now has specialized AI agents!")
    print()
    print("📋 What was accomplished:")
    print("   ✅ P&L data analyzed with comprehensive KPI calculations")
    print("   ✅ Inefficiencies identified with severity classification")
    print("   ✅ Specialized AI agents generated using NVIDIA LLM")
    print("   ✅ Agent configurations saved for future use")
    print("   ✅ Dynamic multi-agent crew created and ready")
    print("   ✅ Implementation roadmap provided")
    print()
    print("🚀 Next Steps:")
    print("   1. Review generated agent configurations")
    print("   2. Deploy agents via the multi-agent architecture")
    print("   3. Provide additional data to refine agent tasks")
    print("   4. Monitor progress and adjust strategies")
    print()
    print("💡 The system is now ready to optimize your company's efficiency!")

def main():
    """Main execution function."""
    try:
        run_dynamic_agent_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("🔧 Please check the error and try again.")

if __name__ == "__main__":
    main()