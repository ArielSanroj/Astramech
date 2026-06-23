"""Schema mappings for normalization layer."""

from __future__ import annotations

from typing import Dict

from normalization_models import SchemaMapping


def load_schema_mappings() -> Dict[str, SchemaMapping]:
    niif_es = SchemaMapping(
            revenue_patterns=[
                r"INGRESOS ORDINARIOS",
                r"VENTAS BRUTAS",
                r"INGRESOS OPERACIONALES",
                r"VENTAS NETAS",
            ],
            cogs_patterns=[
                r"COSTO DE LA MERCANCIA VENDIDA",
                r"COSTO DE VENTAS",
                r"COSTO DE VENTA",
                r"COSTO DE PRODUCTOS VENDIDOS",
            ],
            gross_profit_patterns=[r"UTILIDAD BRUTA", r"GANANCIA BRUTA", r"MARGEN BRUTO"],
            operating_expenses_patterns=[
                r"TOTAL GASTOS OPERACIONALES",
                r"GASTOS DE ADMINISTRACION",
                r"GASTOS OPERACIONALES",
                r"GASTOS GENERALES",
            ],
            operating_income_patterns=[
                r"RESULTADO OPERACIONAL",
                r"UTILIDAD OPERACIONAL",
                r"GANANCIA OPERACIONAL",
            ],
            net_income_patterns=[
                r"RESULTADO DEL EJERCICIO.*UTILIDAD",
                r"UTILIDAD NETA",
                r"GANANCIA NETA",
                r"RESULTADO NETO",
            ],
            total_assets_patterns=[r"TOTAL ACTIVOS", r"ACTIVO TOTAL", r"ACTIVOS"],
            total_liabilities_patterns=[r"TOTAL PASIVOS", r"PASIVO TOTAL", r"PASIVOS"],
            total_equity_patterns=[r"TOTAL PATRIMONIO", r"PATRIMONIO TOTAL", r"PATRIMONIO"],
            cash_patterns=[r"EFECTIVO Y EQUIVALENTES", r"EFECTIVO", r"CAJA Y BANCOS"],
            employee_patterns=[r"EMPLEADOS", r"PERSONAL", r"TRABAJADORES", r"RECURSOS HUMANOS"],
        )
    us_gaap_en = SchemaMapping(
            revenue_patterns=[r"REVENUE", r"TOTAL REVENUE", r"NET SALES", r"GROSS SALES"],
            cogs_patterns=[r"COST OF GOODS SOLD", r"COST OF SALES", r"COGS", r"COST OF REVENUE"],
            gross_profit_patterns=[r"GROSS PROFIT", r"GROSS MARGIN", r"GROSS INCOME"],
            operating_expenses_patterns=[
                r"OPERATING EXPENSES",
                r"TOTAL OPERATING EXPENSES",
                r"SG&A",
                r"SELLING, GENERAL & ADMINISTRATIVE",
            ],
            operating_income_patterns=[
                r"OPERATING INCOME",
                r"OPERATING PROFIT",
                r"EBIT",
                r"EARNINGS BEFORE INTEREST AND TAXES",
            ],
            net_income_patterns=[r"NET INCOME", r"NET PROFIT", r"NET EARNINGS", r"BOTTOM LINE"],
            total_assets_patterns=[r"TOTAL ASSETS", r"ASSETS"],
            total_liabilities_patterns=[r"TOTAL LIABILITIES", r"LIABILITIES"],
            total_equity_patterns=[r"TOTAL EQUITY", r"SHAREHOLDERS EQUITY", r"STOCKHOLDERS EQUITY"],
            cash_patterns=[r"CASH AND CASH EQUIVALENTS", r"CASH", r"CASH AND EQUIVALENTS"],
            employee_patterns=[r"EMPLOYEES", r"PERSONNEL", r"WORKFORCE", r"HEADCOUNT"],
        )
    ifrs_en = SchemaMapping(
            revenue_patterns=[r"REVENUE", r"TURNOVER", r"INCOME FROM OPERATIONS"],
            cogs_patterns=[r"COST OF SALES", r"COST OF GOODS SOLD", r"COST OF REVENUE"],
            gross_profit_patterns=[r"GROSS PROFIT", r"GROSS MARGIN"],
            operating_expenses_patterns=[r"OPERATING EXPENSES", r"ADMINISTRATIVE EXPENSES", r"SELLING EXPENSES"],
            operating_income_patterns=[r"OPERATING PROFIT", r"PROFIT FROM OPERATIONS"],
            net_income_patterns=[r"PROFIT FOR THE PERIOD", r"NET PROFIT", r"NET INCOME"],
            total_assets_patterns=[r"TOTAL ASSETS", r"ASSETS"],
            total_liabilities_patterns=[r"TOTAL LIABILITIES", r"LIABILITIES"],
            total_equity_patterns=[r"TOTAL EQUITY", r"EQUITY"],
            cash_patterns=[r"CASH AND CASH EQUIVALENTS", r"CASH"],
            employee_patterns=[r"EMPLOYEES", r"PERSONNEL"],
        )
    br_pt = SchemaMapping(
            revenue_patterns=[r"RECEITA OPERACIONAL", r"RECEITA BRUTA", r"VENDAS LÍQUIDAS"],
            cogs_patterns=[r"CUSTO DOS PRODUTOS VENDIDOS", r"CUSTO DAS MERCADORIAS VENDIDAS", r"CPV"],
            gross_profit_patterns=[r"LUCRO BRUTO", r"MARGEM BRUTA"],
            operating_expenses_patterns=[r"DESPESAS OPERACIONAIS", r"DESPESAS ADMINISTRATIVAS", r"DESPESAS GERAIS"],
            operating_income_patterns=[r"RESULTADO OPERACIONAL", r"LUCRO OPERACIONAL"],
            net_income_patterns=[r"LUCRO LÍQUIDO", r"RESULTADO LÍQUIDO", r"LUCRO NETO"],
            total_assets_patterns=[r"TOTAL DO ATIVO", r"ATIVO TOTAL"],
            total_liabilities_patterns=[r"TOTAL DO PASSIVO", r"PASSIVO TOTAL"],
            total_equity_patterns=[r"PATRIMÔNIO LÍQUIDO", r"PL"],
            cash_patterns=[r"CAIXA E EQUIVALENTES", r"CAIXA", r"DISPONÍVEL"],
            employee_patterns=[r"FUNCIONÁRIOS", r"PESSOAL", r"COLABORADORES"],
        )

    return {
        "NIIF_ES": niif_es,
        "IFRS_ES": niif_es,
        "LOCAL_ES": niif_es,
        "US_GAAP_EN": us_gaap_en,
        "IFRS_EN": ifrs_en,
        "LOCAL_EN": ifrs_en,
        "BR_PT": br_pt,
        "IFRS_PT": br_pt,
        "LOCAL_PT": br_pt,
    }


def define_unified_schema() -> Dict[str, str]:
    return {
        "revenue": "revenue",
        "cogs": "cost_of_goods_sold",
        "gross_profit": "gross_profit",
        "operating_expenses": "operating_expenses",
        "operating_income": "operating_income",
        "net_income": "net_income",
        "total_assets": "total_assets",
        "total_liabilities": "total_liabilities",
        "total_equity": "total_equity",
        "cash_and_equivalents": "cash_and_equivalents",
        "employee_count": "employee_count",
    }
