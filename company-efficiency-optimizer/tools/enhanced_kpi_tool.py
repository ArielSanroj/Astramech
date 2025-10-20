#!/usr/bin/env python3
"""
Enhanced KPI Tool for Dynamic Agent Creation

This tool analyzes P&L data, calculates KPIs, identifies inefficiencies,
and recommends specific AI agents to address each issue.
"""

from crewai.tools import BaseTool
import pandas as pd
from typing import Dict, List, Any

class EnhancedKPITool(BaseTool):
    name: str = "Enhanced KPI Analysis Tool"
    description: str = "Calculates KPIs from P&L data, identifies inefficiencies with benchmarks, and recommends specialized AI agents for each issue."

    def _run(self, pnl_data: dict) -> dict:
        """
        Analyze P&L data and recommend agents based on inefficiencies.
        
        Args:
            pnl_data: Dictionary containing financial data
                    Example: {'revenue': 800000, 'cogs': 200000, 'opex': 700000, 
                             'operating_profit': -100000, 'net_profit': -120000, 
                             'employee_count': 15, 'revenue_growth': 0.0}
        
        Returns:
            Dictionary with KPIs, inefficiencies, and recommended agents
        """
        
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
        
        # Pattern 4: Operational inefficiency (low operating efficiency + high COGS)
        if (kpis['Operating Efficiency'] < benchmarks['Operating Efficiency']['target'] * 0.6 and 
            kpis['COGS Ratio'] > benchmarks['COGS Ratio']['target'] * 1.1):
            self._add_agent_if_not_exists(recommended_agents, {
                'type': 'Supply Chain Optimizer',
                'goal': 'Optimize supply chain and reduce cost of goods sold',
                'priority': 'medium',
                'focus_areas': ['Operating Efficiency', 'COGS Ratio']
            })

    def _add_agent_if_not_exists(self, recommended_agents: list, new_agent: dict):
        """Add agent if it doesn't already exist in the list."""
        if not any(agent['type'] == new_agent['type'] for agent in recommended_agents):
            recommended_agents.append(new_agent)