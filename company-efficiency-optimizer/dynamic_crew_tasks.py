"""Task builders for dynamic crew."""

from __future__ import annotations

from typing import List

from crewai import Task, Agent

ROLE_TASKS = [
    (("pricing",),
     "Develop and implement pricing optimization strategies to improve gross margins and revenue growth. Focus on dynamic pricing, competitive analysis, and customer segmentation.",
     "Comprehensive pricing strategy with implementation plan, expected outcomes, and success metrics"),
    (("operations",),
     "Analyze and optimize operational processes to reduce costs, improve efficiency, and enhance productivity. Focus on process mapping, bottleneck identification, and automation opportunities.",
     "Operations optimization plan with process improvements, cost reduction strategies, and efficiency gains"),
    (("financial",),
     "Develop comprehensive financial optimization strategies to improve profitability, cash flow, and overall financial health. Focus on cost management, revenue optimization, and financial planning.",
     "Financial optimization strategy with cost reduction plans, revenue enhancement strategies, and financial projections"),
    (("cost",),
     "Identify and implement cost reduction opportunities across all business areas. Focus on expense analysis, vendor management, and budget optimization.",
     "Cost reduction action plan with specific savings targets, implementation timeline, and monitoring metrics"),
    (("supply", "chain"),
     "Optimize supply chain operations to reduce costs, improve efficiency, and enhance supplier relationships. Focus on procurement, inventory management, and logistics optimization.",
     "Supply chain optimization strategy with procurement improvements, inventory optimization, and supplier relationship enhancements"),
    (("sales", "growth"),
     "Develop and execute sales growth strategies to increase revenue, market share, and customer acquisition. Focus on market analysis, sales optimization, and growth planning.",
     "Sales growth strategy with market expansion plans, customer acquisition strategies, and revenue growth projections"),
    (("productivity", "hr"),
     "Enhance workforce productivity and employee engagement to improve performance and reduce turnover. Focus on talent management, retention strategies, and productivity optimization.",
     "Workforce optimization strategy with productivity improvements, retention programs, and employee engagement initiatives"),
    (("cash", "flow"),
     "Optimize cash flow management and working capital to improve financial stability and liquidity. Focus on cash flow forecasting, working capital optimization, and financial planning.",
     "Cash flow optimization plan with liquidity improvements, working capital strategies, and financial stability measures"),
]

GENERIC_DESCRIPTION = (
    "Develop and implement optimization strategies to address the specific business challenges identified in the analysis. "
    "Focus on measurable improvements and sustainable solutions."
)
GENERIC_OUTPUT = (
    "Comprehensive optimization strategy with specific recommendations, implementation plan, and success metrics"
)


def create_base_tasks(diagnostic_agent: Agent, kpi_tool, agent_creator, human_tool) -> List[Task]:
    return [
        Task(
            description=(
                "Prompt the user to upload or provide P&L data if not available. Once received, extract and clean the data."
            ),
            expected_output="Cleaned P&L dataset in JSON format with standardized fields",
            agent=diagnostic_agent,
            tools=[human_tool],
        ),
        Task(
            description=(
                "Analyze P&L data, calculate KPIs, identify inefficiencies, and dynamically create specialized AI agents tailored "
                "to address specific business issues."
            ),
            expected_output=(
                "Complete diagnostic report with KPI analysis, inefficiency detection, and dynamically generated AI agent configurations"
            ),
            agent=diagnostic_agent,
            tools=[kpi_tool, agent_creator],
        ),
    ]


def create_dynamic_task(agent: Agent, kpi_tool) -> Task:
    role = agent.role.lower()
    for keywords, description, expected_output in ROLE_TASKS:
        if any(keyword in role for keyword in keywords):
            return Task(
                description=description,
                expected_output=expected_output,
                agent=agent,
                tools=[kpi_tool],
            )

    return Task(
        description=GENERIC_DESCRIPTION,
        expected_output=GENERIC_OUTPUT,
        agent=agent,
        tools=[kpi_tool],
    )
