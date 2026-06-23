"""
Superloop — agente de negocio de ciclo cerrado (ver SUPERLOOP.md en la raíz).

Capa aislada, arquitectura hexagonal: adapters → application → domain. El domain no
importa nada del resto del repo. Solo los adapters tocan el código legacy (los
*_efficiency_engine.py, la orquestación CrewAI), siempre read/append.

Producto = unidad de negocio. En Astramech hay dos grAnos: dominios KPI
(finance/hr/marketing/ops/sales) y agentes (los 8 symlinks de agents/). Se distinguen
con el campo `tipo` (dominio_kpi | agente).

Loop: OBSERVE → DIAGNOSE → DECIDE → APPROVE → ORCHESTRATE → VERIFY → LEARN → REPEAT
"""

__all__ = ["domain", "application", "adapters", "config", "facade"]
