"""Shared helpers for interactive workflow."""

from __future__ import annotations

from typing import Dict, List


def format_financial_data(financial_data: Dict[str, float]) -> str:
    lines = [
        "📊 Your Financial Data:",
        f"   Revenue: ${financial_data.get('revenue', 0):,.2f}",
        f"   Cost of Goods Sold: ${financial_data.get('cogs', 0):,.2f}",
        f"   Gross Profit: ${financial_data.get('gross_profit', 0):,.2f}",
        f"   Operating Expenses: ${financial_data.get('operating_expenses', 0):,.2f}",
        f"   Operating Income: ${financial_data.get('operating_income', 0):,.2f}",
        f"   Net Income: ${financial_data.get('net_income', 0):,.2f}",
        f"   Employee Count: {financial_data.get('employee_count', 0)}",
        "",
    ]
    return "\n".join(lines)


def build_agent_recommendations(inefficiencies: List[dict]) -> Dict[str, List[dict]]:
    recommendations = {
        "hr_optimizer": [],
        "operations_optimizer": [],
        "financial_optimizer": [],
    }
    for inefficiency in inefficiencies:
        agent = inefficiency["recommended_agent"]
        if agent in recommendations:
            recommendations[agent].append(inefficiency)
    return recommendations


def get_optimization_strategies(agents_deployed: List[str]) -> Dict[str, List[str]]:
    strategies = {}
    if "HR Optimizer" in agents_deployed:
        strategies["👥 HR OPTIMIZATION STRATEGIES:"] = [
            "Implement comprehensive employee retention programs",
            "Conduct regular exit interviews to identify turnover causes",
            "Develop clear career advancement pathways",
            "Improve onboarding and training programs",
            "Implement flexible work arrangements and benefits",
            "Create employee engagement and satisfaction surveys",
        ]

    if "Operations Optimizer" in agents_deployed:
        strategies["⚙️ OPERATIONS OPTIMIZATION STRATEGIES:"] = [
            "Streamline operational processes and eliminate bottlenecks",
            "Implement lean manufacturing/service delivery principles",
            "Optimize resource allocation and capacity planning",
            "Automate repetitive and low-value tasks",
            "Improve supply chain and logistics efficiency",
            "Implement quality control and continuous improvement",
        ]

    if "Financial Optimizer" in agents_deployed:
        strategies["💰 FINANCIAL OPTIMIZATION STRATEGIES:"] = [
            "Optimize pricing strategies to improve margins",
            "Identify and reduce unnecessary operational costs",
            "Improve cash flow management and working capital",
            "Implement cost control and budget monitoring systems",
            "Explore new revenue streams and market opportunities",
            "Optimize tax strategies and financial planning",
        ]

    if not agents_deployed:
        strategies["✅ Your company is performing well! Focus on:"] = [
            "Maintaining current performance levels",
            "Continuous improvement and innovation",
            "Market expansion opportunities",
            "Competitive advantage enhancement",
        ]

    return strategies


def get_implementation_roadmap(inefficiencies: List[dict]) -> Dict[str, List[str]]:
    roadmap = {
        "🚀 IMMEDIATE ACTIONS (0-30 days):": [
            "Prioritize the most critical inefficiencies",
            "Assign specialized agents to high-impact issues",
            "Set up monitoring and tracking systems",
            "Establish baseline metrics for improvement",
            "Create cross-functional optimization teams",
        ],
        "📈 SHORT-TERM GOALS (1-3 months):": [
            "Implement targeted optimization strategies",
            "Monitor KPI improvements and adjust strategies",
            "Train teams on new processes and systems",
            "Establish regular performance reviews",
            "Begin seeing measurable improvements",
        ],
        "🎯 LONG-TERM OBJECTIVES (3-12 months):": [
            "Achieve industry benchmark performance",
            "Implement continuous improvement processes",
            "Scale successful optimization strategies",
            "Develop competitive advantages",
            "Prepare for future growth and expansion",
        ],
    }

    if inefficiencies:
        critical_count = len([i for i in inefficiencies if i["severity"] == "critical"])
        warning_count = len([i for i in inefficiencies if i["severity"] == "warning"])
        roadmap["📊 Expected Outcomes:"] = [
            f"Address {critical_count} critical inefficiencies",
            f"Improve {warning_count} warning-level issues",
            "Achieve industry benchmark performance",
            "Increase operational efficiency by 15-25%",
            "Improve financial performance significantly",
        ]

    return roadmap


def get_final_summary() -> List[str]:
    return [
        "🎉 ANALYSIS COMPLETE!",
        "==============================",
        "📈 Your Company Efficiency Analysis is complete!",
        "📋 Review the recommendations above and begin implementation.",
        "🤖 The specialized agents are ready to help optimize your business!",
        "",
        "💡 Next Steps:",
        "   1. Prioritize the most critical inefficiencies",
        "   2. Assign teams to each optimization area",
        "   3. Set up regular monitoring and reviews",
        "   4. Track progress against benchmarks",
        "",
        "🚀 Ready to optimize your company's efficiency!",
    ]
