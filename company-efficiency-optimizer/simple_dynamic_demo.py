#!/usr/bin/env python3
"""
Simple Dynamic Agent Creation Demo

This demo shows the core dynamic agent creation functionality without
CrewAI dependencies, focusing on the KPI analysis and agent generation.
"""

import os
import json
from datetime import datetime
from tools.enhanced_kpi_tool import EnhancedKPITool
from tools.dynamic_agent_creator import DynamicAgentCreator

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

def run_simple_dynamic_demo():
    """Run the simplified dynamic agent creation demo."""
    
    print_header("Simple Dynamic Agent Creation Demo")
    print("This demo shows how the system analyzes P&L data and creates")
    print("specialized AI agents tailored to address specific business inefficiencies.")
    print("(Simplified version without CrewAI dependencies)")
    
    # Step 1: User provides P&L data
    print_step(1, "User Provides P&L Data")
    simulate_user_interaction()
    
    # Step 2: Initialize tools
    print_step(2, "Initialize Analysis Tools")
    print("🔧 Initializing KPI analysis and agent creation tools...")
    
    try:
        kpi_tool = EnhancedKPITool()
        agent_creator = DynamicAgentCreator()
        print("✅ Tools initialized successfully")
    except Exception as e:
        print(f"❌ Tool initialization failed: {str(e)}")
        return
    
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
    
    # Run KPI analysis
    print("\n🔍 Running KPI analysis...")
    try:
        analysis_result = kpi_tool._run(pnl_data)
        
        print(f"✅ Analysis complete!")
        print(f"   • Total Inefficiencies: {analysis_result['summary']['total_inefficiencies']}")
        print(f"   • Critical Issues: {analysis_result['summary']['critical_issues']}")
        print(f"   • Warning Issues: {analysis_result['summary']['warning_issues']}")
        print(f"   • Agents Needed: {analysis_result['summary']['agents_needed']}")
        
        # Show KPI analysis
        print("\n📈 KPI Analysis Results:")
        for kpi, value in analysis_result['kpis'].items():
            benchmark = analysis_result['benchmarks'].get(kpi, 'N/A')
            if isinstance(value, (int, float)):
                if value < float(str(benchmark).replace('$', '').replace('%', '').split('-')[0]) * 0.8:
                    status = "🔴 Critical"
                elif value < float(str(benchmark).replace('$', '').replace('%', '').split('-')[0]) * 0.9:
                    status = "🟡 Warning"
                else:
                    status = "🟢 Good"
            else:
                status = "⚪ N/A"
            
            print(f"   {kpi}: {value:.1f}% (Benchmark: {benchmark}) {status}")
        
        # Show identified inefficiencies
        print("\n⚠️ Identified Inefficiencies:")
        for i, inefficiency in enumerate(analysis_result['inefficiencies'], 1):
            severity_emoji = "🔴" if inefficiency['severity'] == 'critical' else "🟡"
            print(f"   {i}. {inefficiency['kpi_name']} {severity_emoji}")
            print(f"      Current: {inefficiency['current_value']:.1f}% vs Benchmark: {inefficiency['benchmark']:.1f}%")
            print(f"      Issue: {inefficiency['description']}")
            print(f"      Root Cause: {inefficiency['root_cause']}")
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
    
    # Step 4: Generate dynamic agents
    print_step(4, "Generate Specialized AI Agents")
    print("🤖 Creating specialized agents using NVIDIA LLM...")
    
    try:
        # Generate agents
        print("   📝 Generating agent configurations...")
        report = agent_creator._run(analysis_result)
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
                print(f"     Created: {config.get('created_at', 'Unknown')}")
                print()
        
        # Show the generated report
        print("📋 Generated Diagnostic Report:")
        print("-" * 35)
        print(report[:500] + "..." if len(report) > 500 else report)
        
    except Exception as e:
        print(f"❌ Agent generation failed: {str(e)}")
        print("🔄 Falling back to basic agent creation...")
        
        # Fallback: Create basic agents without LLM
        try:
            from tools.dynamic_agent_creator import DynamicAgentCreator
            fallback_creator = DynamicAgentCreator()
            fallback_report = fallback_creator._create_fallback_agents(analysis_result)
            print("✅ Fallback agents created successfully")
        except Exception as fallback_error:
            print(f"❌ Fallback creation also failed: {str(fallback_error)}")
            return
    
    # Step 5: Show implementation roadmap
    print_step(5, "Implementation Roadmap")
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
    
    # Step 6: Show file outputs
    print_step(6, "Generated Files")
    print("📁 The following files were created:")
    
    if os.path.exists('config/dynamic_agents.yaml'):
        print("   ✅ config/dynamic_agents.yaml - Agent configurations")
        
        # Show file size
        file_size = os.path.getsize('config/dynamic_agents.yaml')
        print(f"      File size: {file_size:,} bytes")
        
        # Show agent count
        import yaml
        with open('config/dynamic_agents.yaml', 'r') as f:
            agent_configs = yaml.safe_load(f)
        print(f"      Agents configured: {len(agent_configs)}")
    
    # Check for diagnostic report
    if 'report' in locals() and report:
        print("   ✅ Diagnostic Report - Comprehensive analysis and recommendations")
        print(f"      Report length: {len(report):,} characters")
    
    # Final summary
    print_header("Dynamic Agent Creation Complete!")
    print("🎉 Your Company Efficiency Optimizer has created specialized AI agents!")
    print()
    print("📋 What was accomplished:")
    print("   ✅ P&L data analyzed with comprehensive KPI calculations")
    print("   ✅ Inefficiencies identified with severity classification")
    print("   ✅ Specialized AI agents generated using NVIDIA LLM")
    print("   ✅ Agent configurations saved for future use")
    print("   ✅ Implementation roadmap provided")
    print()
    print("🚀 Next Steps:")
    print("   1. Review generated agent configurations in config/dynamic_agents.yaml")
    print("   2. Deploy agents via your preferred multi-agent framework")
    print("   3. Provide additional data to refine agent tasks")
    print("   4. Monitor progress and adjust strategies")
    print()
    print("💡 The system is now ready to optimize your company's efficiency!")
    print("🔧 Note: This is a simplified version. For full CrewAI integration,")
    print("   resolve the LangChain version conflicts first.")

def main():
    """Main execution function."""
    try:
        run_simple_dynamic_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("🔧 Please check the error and try again.")

if __name__ == "__main__":
    main()