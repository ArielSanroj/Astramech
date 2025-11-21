#!/usr/bin/env python3
"""
Generador de Agentes AI para empresas usando Ollama + Pinecone
Genera agentes especializados basados en análisis real de KPIs
"""

import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_ollama import ChatOllama
except ImportError:
    print("⚠️ langchain_ollama no disponible, usando fallback")
    ChatOllama = None

try:
    import pinecone
    Pinecone = pinecone.Pinecone if hasattr(pinecone, 'Pinecone') else None
    ServerlessSpec = pinecone.ServerlessSpec if hasattr(pinecone, 'ServerlessSpec') else None
except (ImportError, Exception) as e:
    print(f"⚠️ Pinecone SDK no disponible: {e}")
    Pinecone = None
    ServerlessSpec = None

def generate_agents_for_company(company_name: str, kpi_results: dict, financial_data: dict) -> list:
    """
    Genera agentes AI especializados para una empresa basado en sus KPIs reales
    
    Args:
        company_name: Nombre de la empresa
        kpi_results: Resultados de KPIs calculados
        financial_data: Datos financieros extraídos
        
    Returns:
        Lista de agentes generados
    """
    
    # Extraer métricas clave
    financial = kpi_results.get('financial', {})
    operational = kpi_results.get('operational', {})
    hr = kpi_results.get('hr', {})
    
    total_assets = financial_data.get('total_assets', 0)
    revenue = financial_data.get('revenue', 0)
    operating_income = financial_data.get('operating_income', 0)
    net_income = financial_data.get('net_income', 0)
    cash = financial_data.get('cash_and_equivalents', 0)
    employees = hr.get('total_employees', financial_data.get('employee_count', 0))
    
    # Calcular ingresos mensuales aproximados
    monthly_revenue = revenue / 12 if revenue else 0
    
    # Calcular márgenes
    operating_margin = financial.get('operating_margin', 0) * 100 if financial.get('operating_margin') else 0
    net_margin = financial.get('net_margin', 0) * 100 if financial.get('net_margin') else 0
    
    # Prompt brutalmente directo
    prompt = f"""Eres un CEO de fondo de inversión que acaba de analizar {company_name}.

Datos reales:
- Activos totales: ${total_assets:,.0f} COP
- Ingresos mensuales: ${monthly_revenue:,.0f} COP
- Margen operativo: {operating_margin:.1f}%
- Margen neto: {net_margin:.1f}%
- Cash: ${cash:,.0f} COP
- Empleados estimados: {employees}

Genera exactamente 4 agentes AI especializados con este formato JSON:

[
  {{
    "name": "Nombre del Agente",
    "role": "Rol exacto",
    "goal": "Objetivo medible en 90 días",
    "priority": "CRÍTICO | Alta | Media",
    "tasks": ["Tarea 1 concreta", "Tarea 2", "Tarea 3"],
    "success_metric": "Métrica de éxito clara (ej: +$20M ingresos, DSO <60 días)"
  }}
]

Hazlo brutalmente directo, sin bullshit corporativo.
Solo responde con el JSON válido, sin texto adicional.
"""

    agents = []
    
    if ChatOllama:
        try:
            llm = ChatOllama(
                model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.7
            )
            
            print(f"🤖 Generando agentes para {company_name}...")
            response = llm.invoke(prompt)
            
            # Extraer JSON de la respuesta
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Buscar JSON en la respuesta
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                agents = json.loads(json_str)
                print(f"✅ {len(agents)} agentes generados")
            else:
                print("⚠️ No se encontró JSON válido en la respuesta")
                agents = _generate_fallback_agents(company_name, total_assets, monthly_revenue, operating_margin)
                
        except Exception as e:
            print(f"⚠️ Error generando agentes con Ollama: {e}")
            agents = _generate_fallback_agents(company_name, total_assets, monthly_revenue, operating_margin)
    else:
        print("⚠️ Ollama no disponible, usando agentes por defecto")
        agents = _generate_fallback_agents(company_name, total_assets, monthly_revenue, operating_margin)
    
    # Guardar en Pinecone si está disponible
    if Pinecone and agents:
        try:
            pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            index_name = 'astramech-agents'
            
            # Crear índice si no existe
            existing_indexes = pc.list_indexes()
            if index_name not in existing_indexes.names():
                print(f"📦 Creando índice Pinecone: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=4096,  # Ollama embedding dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
            
            index = pc.Index(index_name)
            
            # Guardar cada agente
            for agent in agents:
                agent_text = f"{agent['name']} {agent['goal']} {agent['role']}"
                
                # Crear embedding simple (o usar Ollama embeddings si está disponible)
                # Por ahora usamos un hash simple como embedding
                import hashlib
                embedding = [float(int(hashlib.md5(f"{agent_text}{i}".encode()).hexdigest(), 16) % 1000) / 1000.0 for i in range(4096)]
                
                index.upsert(vectors=[{
                    "id": f"{company_name.lower().replace(' ', '_')}_{agent['name'].lower().replace(' ', '_')}",
                    "values": embedding,
                    "metadata": {
                        **agent,
                        "company": company_name,
                        "generated_at": str(os.popen('date').read().strip())
                    }
                }])
            
            print(f"✅ {len(agents)} agentes guardados en Pinecone")
            
        except Exception as e:
            print(f"⚠️ Error guardando en Pinecone: {e}")
    
    return agents

def _generate_fallback_agents(company_name: str, total_assets: float, monthly_revenue: float, operating_margin: float) -> list:
    """Genera agentes por defecto si Ollama no está disponible"""
    
    # Determinar prioridades basadas en métricas
    if total_assets > monthly_revenue * 100:
        asset_utilization_priority = "CRÍTICO"
    else:
        asset_utilization_priority = "Alta"
    
    if monthly_revenue < 10000000:
        revenue_priority = "CRÍTICO"
    else:
        revenue_priority = "Alta"
    
    return [
        {
            "name": "Revenue Scale Agent",
            "role": "Chief Revenue Officer AI",
            "goal": f"Duplicar ingresos a ${monthly_revenue * 2:,.0f}/mes en 90 días usando activos existentes",
            "priority": revenue_priority,
            "tasks": [
                "Identificar 3 canales de ventas de alto apalancamiento con los activos disponibles",
                "Lanzar oferta agresiva a clientes existentes (cross-sell)",
                "Activar partnerships dormidos en cartera"
            ],
            "success_metric": f"+${monthly_revenue:,.0f} ingresos mensuales recurrentes"
        },
        {
            "name": "Asset Utilization Agent",
            "role": "Director de Optimización de Activos",
            "goal": f"Convertir ${total_assets * 0.2:,.0f} de inversiones pasivas en flujo activo en 90 días",
            "priority": asset_utilization_priority,
            "tasks": [
                f"Auditar portafolio de activos (${total_assets:,.0f}) y clasificar por liquidez",
                f"Liquidar o reestructurar ${total_assets * 0.2:,.0f} en activos no estratégicos",
                "Reinvertir en operaciones de alto ROI"
            ],
            "success_metric": f"${total_assets * 0.2:,.0f} liberados para crecimiento"
        },
        {
            "name": "Liquidity Optimizer",
            "role": "CFO de Emergencia AI",
            "goal": "Subir cash buffer a 2.5x gastos operativos mensuales",
            "priority": "Alta",
            "tasks": [
                "Reducir DSO (días de ventas pendientes) a menos de 60 días",
                "Renegociar términos con proveedores",
                "Estructurar línea de crédito con activos como garantía"
            ],
            "success_metric": "Cash buffer > 2.5x gastos mensuales"
        },
        {
            "name": "Growth Strategy Agent",
            "role": "Chief Strategy Officer AI",
            "goal": f"Plan para escalar de ${monthly_revenue * 12:,.0f}/año a ${monthly_revenue * 12 * 4:,.0f}/año en 24 meses",
            "priority": "Alta",
            "tasks": [
                "Mapear 5 mercados adyacentes con entrada rápida",
                "Diseñar modelo de franquicia o licensing de activos",
                "Crear pitch para levantar capital de crecimiento"
            ],
            "success_metric": "Plan aprobado y primer hito ejecutado en 90 días"
        }
    ]

if __name__ == '__main__':
    # Test con datos de ejemplo
    test_kpi_results = {
        'financial': {
            'gross_margin': 0.769,
            'operating_margin': 0.178,
            'net_margin': 0.152,
            'revenue_per_employee': 2500000
        },
        'operational': {
            'productivity_index': 8.33
        },
        'hr': {
            'total_employees': 8
        }
    }
    
    test_financial_data = {
        'total_assets': 9998415695,
        'revenue': 20000000,
        'operating_income': 3563072,
        'net_income': 3033657,
        'cash_and_equivalents': 16171912,
        'employee_count': 8
    }
    
    agents = generate_agents_for_company("CARMANFE SAS", test_kpi_results, test_financial_data)
    
    print("\n" + "=" * 70)
    print("AGENTES GENERADOS:")
    print("=" * 70)
    print(json.dumps(agents, indent=2, ensure_ascii=False))

