#!/usr/bin/env python3
"""
Standalone Dynamic Agent Creation Demo

This demo shows the core dynamic agent creation functionality without
any CrewAI or external tool dependencies, focusing on the KPI analysis 
and agent generation using pure Python.
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any

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

class StandaloneKPIAnalyzer:
    """Standalone KPI analyzer without external dependencies."""
    
    def analyze_pnl_data(self, pnl_data: dict) -> dict:
        """Analyze P&L data and recommend agents based on inefficiencies."""
        
        # Extract data with defaults
        revenue = pnl_data.get('revenue', 0)
        cogs = pnl_data.get('cogs', 0)
        opex = pnl_data.get('opex', 0) or pnl_data.get('operating_expenses', 0)
        operating_profit = pnl_data.get('operating_profit', 0) or pnl_data.get('operating_income', 0)
        net_profit = pnl_data.get('net_profit', 0) or pnl_data.get('net_income', 0)
        employee_count = pnl_data.get('employee_count', 1)
        revenue_growth = pnl_data.get('revenue_growth', 0) or pnl_data.get('revenue_growth_rate', 0)
        
        # Calculate derived metrics
        gross_profit = revenue - cogs
        
        # Calculate KPIs
        kpis = {
            'Gross Margin': (gross_profit / revenue * 100) if revenue > 0 else 0,
            'Operating Margin': (operating_profit / revenue * 100) if revenue > 0 else 0,
            'Net Margin': (net_profit / revenue * 100) if revenue > 0 else 0,
            'Expense Ratio': (opex / revenue * 100) if revenue > 0 else 0,
            'COGS Ratio': (cogs / revenue * 100) if revenue > 0 else 0,
            'Revenue Growth Rate': revenue_growth,
            'Revenue per Employee': (revenue / employee_count) if employee_count > 0 else 0,
            'Operating Efficiency': (gross_profit / opex * 100) if opex > 0 else 0
        }

        # Industry benchmarks (2025 standards)
        benchmarks = {
            'Gross Margin': {'min': 30, 'max': 35, 'target': 32},
            'Operating Margin': {'min': 6, 'max': 12, 'target': 8},
            'Net Margin': {'min': 3, 'max': 8, 'target': 5},
            'Expense Ratio': {'min': 20, 'max': 30, 'target': 25},
            'COGS Ratio': {'min': 60, 'max': 70, 'target': 65},
            'Revenue Growth Rate': {'min': 4, 'max': 8, 'target': 6},
            'Revenue per Employee': {'min': 150000, 'max': 250000, 'target': 200000},
            'Operating Efficiency': {'min': 200, 'max': 400, 'target': 300}
        }

        # Identify inefficiencies and recommend agents
        inefficiencies = []
        recommended_agents = []
        
        # Check each KPI against benchmarks
        for kpi_name, value in kpis.items():
            if kpi_name in benchmarks:
                benchmark = benchmarks[kpi_name]
                target = benchmark['target']
                min_val = benchmark['min']
                
                # Determine severity and recommend agent
                if value < min_val:
                    severity = 'critical'
                    agent_type, goal, root_cause = self._get_agent_recommendation(kpi_name, value, target, 'critical')
                elif value < target * 0.8:
                    severity = 'warning'
                    agent_type, goal, root_cause = self._get_agent_recommendation(kpi_name, value, target, 'warning')
                else:
                    continue  # Skip if performance is acceptable
                
                inefficiencies.append({
                    'kpi_name': kpi_name,
                    'current_value': value,
                    'benchmark': target,
                    'severity': severity,
                    'description': f"{kpi_name}: {value:.1f}% vs {target:.1f}% benchmark",
                    'root_cause': root_cause,
                    'recommended_agent': agent_type
                })
                
                # Add agent if not already recommended
                if not any(agent['type'] == agent_type for agent in recommended_agents):
                    recommended_agents.append({
                        'type': agent_type,
                        'goal': goal,
                        'priority': 'high' if severity == 'critical' else 'medium',
                        'focus_areas': [kpi_name]
                    })

        # Add specialized agents based on specific patterns
        self._add_pattern_based_agents(kpis, benchmarks, recommended_agents, inefficiencies)

        return {
            'data_confirmation': f"P&L data analyzed: Revenue ${revenue:,.0f}, Operating Profit ${operating_profit:,.0f}, Employees {employee_count}",
            'kpis': kpis,
            'benchmarks': {k: v['target'] for k, v in benchmarks.items()},
            'inefficiencies': inefficiencies,
            'recommended_agents': recommended_agents,
            'summary': {
                'total_inefficiencies': len(inefficiencies),
                'critical_issues': len([i for i in inefficiencies if i['severity'] == 'critical']),
                'warning_issues': len([i for i in inefficiencies if i['severity'] == 'warning']),
                'agents_needed': len(recommended_agents)
            }
        }

    def _get_agent_recommendation(self, kpi_name: str, current_value: float, target: float, severity: str) -> tuple:
        """Get agent recommendation based on KPI and severity."""
        
        agent_mapping = {
            'Gross Margin': ('Pricing Optimizer', 'Improve gross margins through pricing strategy optimization', 'Ineffective pricing or high COGS'),
            'Operating Margin': ('Operations Optimizer', 'Streamline operations and reduce operating expenses', 'High operating costs or inefficient processes'),
            'Net Margin': ('Financial Optimizer', 'Improve overall profitability through cost reduction and revenue growth', 'Combined operational and financial inefficiencies'),
            'Expense Ratio': ('Cost Management Agent', 'Reduce unnecessary expenses and optimize spending', 'Excessive operational expenses'),
            'COGS Ratio': ('Supply Chain Optimizer', 'Optimize cost of goods sold through supplier negotiations and process improvements', 'High material costs or inefficient procurement'),
            'Revenue Growth Rate': ('Sales Growth Agent', 'Increase revenue through market expansion and sales optimization', 'Stagnant sales or market challenges'),
            'Revenue per Employee': ('Productivity Optimizer', 'Enhance workforce productivity and efficiency', 'Low employee productivity or potential turnover'),
            'Operating Efficiency': ('Process Optimization Agent', 'Improve operational efficiency and resource utilization', 'Inefficient processes or resource allocation')
        }
        
        return agent_mapping.get(kpi_name, ('General Optimizer', 'Address performance issues', 'Various operational challenges'))

    def _add_pattern_based_agents(self, kpis: dict, benchmarks: dict, recommended_agents: list, inefficiencies: list):
        """Add agents based on specific business patterns."""
        
        # Pattern 1: High turnover risk (low revenue per employee + high expense ratio)
        if (kpis['Revenue per Employee'] < benchmarks['Revenue per Employee']['target'] * 0.7 and 
            kpis['Expense Ratio'] > benchmarks['Expense Ratio']['target'] * 1.3):
            self._add_agent_if_not_exists(recommended_agents, {
                'type': 'HR Retention Specialist',
                'goal': 'Reduce turnover and improve employee retention through engagement programs',
                'priority': 'high',
                'focus_areas': ['Revenue per Employee', 'Expense Ratio']
            })
        
        # Pattern 2: Cash flow issues (negative margins + high expense ratio)
        if (kpis['Operating Margin'] < 0 and kpis['Expense Ratio'] > benchmarks['Expense Ratio']['target'] * 1.5):
            self._add_agent_if_not_exists(recommended_agents, {
                'type': 'Cash Flow Manager',
                'goal': 'Improve cash flow through expense reduction and revenue acceleration',
                'priority': 'critical',
                'focus_areas': ['Operating Margin', 'Expense Ratio']
            })
        
        # Pattern 3: Growth stagnation (low revenue growth + declining margins)
        if (kpis['Revenue Growth Rate'] < benchmarks['Revenue Growth Rate']['target'] * 0.5 and 
            kpis['Operating Margin'] < benchmarks['Operating Margin']['target'] * 0.8):
            self._add_agent_if_not_exists(recommended_agents, {
                'type': 'Growth Strategy Agent',
                'goal': 'Develop and execute growth strategies to increase revenue and market share',
                'priority': 'high',
                'focus_areas': ['Revenue Growth Rate', 'Operating Margin']
            })

    def _add_agent_if_not_exists(self, recommended_agents: list, new_agent: dict):
        """Add agent if it doesn't already exist in the list."""
        if not any(agent['type'] == new_agent['type'] for agent in recommended_agents):
            recommended_agents.append(new_agent)

class StandaloneAgentCreator:
    """Standalone agent creator without external dependencies."""
    
    def create_agents(self, analysis_result: dict) -> str:
        """Create specialized AI agent configurations based on analysis results."""
        
        print("🤖 Creating specialized agents...")
        
        # Generate agent configurations
        agent_configs = {}
        agent_descriptions = []
        
        for agent in analysis_result['recommended_agents']:
            agent_type = agent['type']
            goal = agent['goal']
            priority = agent.get('priority', 'medium')
            focus_areas = agent.get('focus_areas', [])
            
            print(f"   Creating {agent_type}...")
            
            # Generate detailed backstory
            backstory = self._generate_agent_backstory(agent_type, goal, priority, focus_areas)
            
            # Create agent configuration
            agent_key = agent_type.lower().replace(' ', '_').replace('-', '_')
            agent_configs[agent_key] = {
                'role': agent_type,
                'goal': goal,
                'backstory': backstory,
                'priority': priority,
                'focus_areas': focus_areas,
                'capabilities': self._generate_capabilities(agent_type, focus_areas),
                'success_metrics': self._generate_success_metrics(agent_type, goal),
                'allow_delegation': True,
                'verbose': True,
                'memory': True,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            agent_descriptions.append({
                'type': agent_type,
                'goal': goal,
                'priority': priority,
                'capabilities': agent_configs[agent_key]['capabilities']
            })
        
        # Save to dynamic_agents.yaml
        self._save_agent_configs(agent_configs)
        
        # Generate comprehensive report
        report = self._generate_diagnostic_report(analysis_result, agent_descriptions)
        
        print(f"✅ Successfully created {len(agent_configs)} specialized agents")
        return report

    def _generate_agent_backstory(self, agent_type: str, goal: str, priority: str, focus_areas: List[str]) -> str:
        """Generate detailed backstory for the agent."""
        
        backstories = {
            'Pricing Optimizer': f"Expert pricing strategist with 10+ years of experience in dynamic pricing, market analysis, and revenue optimization. Specializes in data-driven pricing decisions and competitive positioning. Known for analytical rigor and creative solutions to pricing challenges. Goal: {goal}",
            
            'Operations Optimizer': f"Process improvement specialist with extensive experience in lean methodologies, Six Sigma, and operational excellence. Expert in identifying bottlenecks, streamlining workflows, and implementing efficiency improvements. Known for systematic approach and measurable results. Goal: {goal}",
            
            'Financial Optimizer': f"Strategic financial analyst with deep expertise in P&L optimization, cost management, and profitability improvement. Specializes in financial modeling, scenario analysis, and strategic planning. Known for data-driven insights and actionable recommendations. Goal: {goal}",
            
            'Cost Management Agent': f"Cost reduction specialist with proven track record in expense optimization and budget management. Expert in identifying cost-saving opportunities, negotiating contracts, and implementing cost controls. Known for attention to detail and persistent optimization. Goal: {goal}",
            
            'Supply Chain Optimizer': f"Supply chain expert with extensive experience in procurement, vendor management, and logistics optimization. Specializes in reducing COGS, improving supplier relationships, and streamlining supply chain processes. Known for strategic thinking and operational excellence. Goal: {goal}",
            
            'Sales Growth Agent': f"Revenue growth specialist with proven success in market expansion, sales optimization, and customer acquisition. Expert in sales strategy, market analysis, and growth planning. Known for innovative approaches and results-driven execution. Goal: {goal}",
            
            'Productivity Optimizer': f"Workforce productivity expert with deep understanding of human resources, performance management, and organizational development. Specializes in employee engagement, retention strategies, and productivity improvement. Known for people-focused solutions and sustainable improvements. Goal: {goal}",
            
            'Process Optimization Agent': f"Process improvement expert with extensive experience in operational efficiency and resource optimization. Specializes in workflow analysis, automation, and continuous improvement. Known for systematic approach and measurable results. Goal: {goal}",
            
            'HR Retention Specialist': f"Human resources specialist with deep expertise in employee retention, engagement, and talent management. Expert in retention strategies, employee satisfaction, and organizational culture. Known for empathetic approach and data-driven HR solutions. Goal: {goal}",
            
            'Cash Flow Manager': f"Financial management expert with extensive experience in cash flow optimization, working capital management, and financial planning. Specializes in liquidity management, expense control, and revenue acceleration. Known for strategic financial thinking and crisis management. Goal: {goal}",
            
            'Growth Strategy Agent': f"Strategic growth consultant with proven success in market expansion, business development, and revenue growth. Expert in growth strategy, market analysis, and competitive positioning. Known for innovative thinking and execution excellence. Goal: {goal}"
        }
        
        return backstories.get(agent_type, f"Experienced business optimization specialist with expertise in {agent_type.lower()}. Goal: {goal}")

    def _generate_capabilities(self, agent_type: str, focus_areas: List[str]) -> List[str]:
        """Generate agent capabilities based on type and focus areas."""
        
        capability_templates = {
            'Pricing Optimizer': [
                'Dynamic pricing analysis and optimization',
                'Market research and competitive analysis',
                'Price elasticity modeling',
                'Revenue optimization strategies',
                'Customer segmentation for pricing'
            ],
            'Operations Optimizer': [
                'Process mapping and analysis',
                'Lean methodology implementation',
                'Workflow optimization',
                'Resource allocation optimization',
                'Performance metrics development'
            ],
            'Financial Optimizer': [
                'Financial modeling and analysis',
                'Cost-benefit analysis',
                'Profitability optimization',
                'Budget planning and control',
                'Financial forecasting'
            ],
            'Cost Management Agent': [
                'Expense analysis and optimization',
                'Vendor negotiation and management',
                'Budget control and monitoring',
                'Cost reduction strategies',
                'Spend analysis and reporting'
            ],
            'Supply Chain Optimizer': [
                'Supplier relationship management',
                'Procurement optimization',
                'Inventory management',
                'Logistics optimization',
                'Vendor performance analysis'
            ],
            'Sales Growth Agent': [
                'Market analysis and research',
                'Sales strategy development',
                'Customer acquisition strategies',
                'Revenue growth planning',
                'Competitive analysis'
            ],
            'Productivity Optimizer': [
                'Workforce analysis and optimization',
                'Performance management systems',
                'Employee engagement strategies',
                'Training and development programs',
                'Productivity measurement and improvement'
            ],
            'Process Optimization Agent': [
                'Process mapping and documentation',
                'Workflow analysis and improvement',
                'Automation opportunities identification',
                'Efficiency measurement and optimization',
                'Continuous improvement implementation'
            ],
            'HR Retention Specialist': [
                'Employee satisfaction analysis',
                'Retention strategy development',
                'Engagement program design',
                'Exit interview analysis',
                'Talent management optimization'
            ],
            'Cash Flow Manager': [
                'Cash flow analysis and forecasting',
                'Working capital optimization',
                'Expense reduction strategies',
                'Revenue acceleration techniques',
                'Financial crisis management'
            ],
            'Growth Strategy Agent': [
                'Market opportunity analysis',
                'Growth strategy development',
                'Business model optimization',
                'Market expansion planning',
                'Competitive positioning strategies'
            ]
        }
        
        base_capabilities = capability_templates.get(agent_type, [
            'Business analysis and optimization',
            'Data-driven decision making',
            'Strategic planning and execution',
            'Performance measurement and improvement',
            'Cross-functional collaboration'
        ])
        
        # Add focus area specific capabilities
        focus_capabilities = []
        for area in focus_areas:
            if 'Revenue' in area:
                focus_capabilities.append(f'{area} optimization and analysis')
            elif 'Margin' in area:
                focus_capabilities.append(f'{area} improvement strategies')
            elif 'Growth' in area:
                focus_capabilities.append(f'{area} acceleration techniques')
            else:
                focus_capabilities.append(f'{area} management and optimization')
        
        return base_capabilities + focus_capabilities

    def _generate_success_metrics(self, agent_type: str, goal: str) -> List[str]:
        """Generate success metrics for the agent."""
        
        metrics_templates = {
            'Pricing Optimizer': [
                'Gross margin improvement percentage',
                'Revenue growth rate',
                'Price optimization ROI',
                'Customer acquisition cost reduction'
            ],
            'Operations Optimizer': [
                'Operating margin improvement',
                'Process efficiency gains',
                'Cost reduction percentage',
                'Time-to-completion improvements'
            ],
            'Financial Optimizer': [
                'Net margin improvement',
                'ROI on optimization initiatives',
                'Cash flow improvement',
                'Profitability growth rate'
            ],
            'Cost Management Agent': [
                'Expense reduction percentage',
                'Cost savings achieved',
                'Budget variance improvement',
                'Spend efficiency gains'
            ],
            'Supply Chain Optimizer': [
                'COGS reduction percentage',
                'Supplier performance improvements',
                'Inventory turnover optimization',
                'Procurement cost savings'
            ],
            'Sales Growth Agent': [
                'Revenue growth rate',
                'Market share increase',
                'Customer acquisition rate',
                'Sales conversion improvements'
            ],
            'Productivity Optimizer': [
                'Revenue per employee improvement',
                'Employee satisfaction scores',
                'Productivity metrics gains',
                'Retention rate improvements'
            ],
            'Process Optimization Agent': [
                'Process efficiency improvements',
                'Automation implementation rate',
                'Resource utilization optimization',
                'Quality metrics improvements'
            ],
            'HR Retention Specialist': [
                'Employee retention rate',
                'Turnover reduction percentage',
                'Employee satisfaction scores',
                'Engagement metrics improvements'
            ],
            'Cash Flow Manager': [
                'Cash flow improvement percentage',
                'Working capital optimization',
                'Liquidity ratio improvements',
                'Financial stability metrics'
            ],
            'Growth Strategy Agent': [
                'Revenue growth acceleration',
                'Market expansion success rate',
                'New customer acquisition',
                'Market share growth'
            ]
        }
        
        return metrics_templates.get(agent_type, [
            'KPI improvement percentage',
            'Goal achievement rate',
            'Performance optimization gains',
            'Business impact metrics'
        ])

    def _save_agent_configs(self, agent_configs: Dict[str, Any]) -> None:
        """Save agent configurations to YAML file."""
        
        # Ensure config directory exists
        os.makedirs('config', exist_ok=True)
        
        # Save to dynamic_agents.yaml
        with open('config/dynamic_agents.yaml', 'w') as f:
            yaml.dump(agent_configs, f, default_flow_style=False, indent=2)
        
        print(f"💾 Saved {len(agent_configs)} agent configurations to config/dynamic_agents.yaml")

    def _generate_diagnostic_report(self, analysis_result: dict, agent_descriptions: List[dict]) -> str:
        """Generate comprehensive diagnostic report."""
        
        report = f"""# 🚀 Company Efficiency Diagnostic Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Executive Summary
{analysis_result['data_confirmation']}

**Key Findings:**
- Total Inefficiencies: {analysis_result['summary']['total_inefficiencies']}
- Critical Issues: {analysis_result['summary']['critical_issues']}
- Warning Issues: {analysis_result['summary']['warning_issues']}
- AI Agents Deployed: {analysis_result['summary']['agents_needed']}

## 📈 KPI Analysis

| KPI | Current Value | Benchmark | Status |
|-----|---------------|-----------|--------|
"""
        
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
            
            report += f"| {kpi} | {value:.1f}% | {benchmark} | {status} |\n"
        
        report += f"""
## ⚠️ Identified Inefficiencies

"""
        
        for i, inefficiency in enumerate(analysis_result['inefficiencies'], 1):
            severity_emoji = "🔴" if inefficiency['severity'] == 'critical' else "🟡"
            report += f"""
### {i}. {inefficiency['kpi_name']} {severity_emoji}
- **Current**: {inefficiency['current_value']:.1f}%
- **Benchmark**: {inefficiency['benchmark']:.1f}%
- **Severity**: {inefficiency['severity'].upper()}
- **Issue**: {inefficiency['description']}
- **Root Cause**: {inefficiency['root_cause']}
- **Recommended Agent**: {inefficiency['recommended_agent']}
"""
        
        report += f"""
## 🤖 Generated Specialized AI Agents

"""
        
        for i, agent in enumerate(agent_descriptions, 1):
            priority_emoji = "🔴" if agent['priority'] == 'critical' else "🟡" if agent['priority'] == 'high' else "🟢"
            report += f"""
### {i}. {agent['type']} {priority_emoji}
- **Goal**: {agent['goal']}
- **Priority**: {agent['priority'].upper()}
- **Capabilities**: {', '.join(agent['capabilities'][:3])}...
"""
        
        report += f"""
## 🎯 Implementation Roadmap

### Immediate Actions (0-30 days)
1. Deploy critical priority agents first
2. Set up monitoring and tracking systems
3. Establish baseline metrics for each agent
4. Create cross-functional optimization teams

### Short-term Goals (1-3 months)
1. Implement agent-specific optimization strategies
2. Monitor KPI improvements and adjust approaches
3. Train teams on new processes and systems
4. Measure and report on agent performance

### Long-term Objectives (3-12 months)
1. Achieve industry benchmark performance
2. Scale successful optimization strategies
3. Develop competitive advantages
4. Implement continuous improvement processes

## 📋 Next Steps
1. Review and approve generated agent configurations
2. Deploy agents via the multi-agent architecture
3. Provide additional data to refine agent tasks
4. Monitor progress and adjust strategies as needed

---
*This report was generated by the Company Efficiency Optimizer using advanced AI analysis.*
"""
        
        return report

def run_standalone_dynamic_demo():
    """Run the standalone dynamic agent creation demo."""
    
    print_header("Standalone Dynamic Agent Creation Demo")
    print("This demo shows how the system analyzes P&L data and creates")
    print("specialized AI agents tailored to address specific business inefficiencies.")
    print("(Standalone version without external dependencies)")
    
    # Step 1: User provides P&L data
    print_step(1, "User Provides P&L Data")
    simulate_user_interaction()
    
    # Step 2: Initialize tools
    print_step(2, "Initialize Analysis Tools")
    print("🔧 Initializing KPI analysis and agent creation tools...")
    
    try:
        kpi_analyzer = StandaloneKPIAnalyzer()
        agent_creator = StandaloneAgentCreator()
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
        analysis_result = kpi_analyzer.analyze_pnl_data(pnl_data)
        
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
    print("🤖 Creating specialized agents...")
    
    try:
        # Generate agents
        print("   📝 Generating agent configurations...")
        report = agent_creator.create_agents(analysis_result)
        print("✅ Dynamic agents generated successfully!")
        
        # Check if agents were created
        if os.path.exists('config/dynamic_agents.yaml'):
            print("💾 Agent configurations saved to config/dynamic_agents.yaml")
            
            # Load and display agent info
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
    print("   ✅ Specialized AI agents generated with detailed configurations")
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
    print("🔧 This standalone version works without external dependencies!")

def main():
    """Main execution function."""
    try:
        run_standalone_dynamic_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("🔧 Please check the error and try again.")

if __name__ == "__main__":
    main()