# Causal vs predictivo (por qué importa en economía + ML)

## Predictivo
- Objetivo: minimizar error de predicción.
- Útil para priorizar, rankear, automatizar decisiones.

Ejemplo: predecir probabilidad de default (PD) → ordenar y decidir.

## Causal
- Objetivo: estimar el efecto de una intervención (tratamiento) sobre un outcome.
- Útil para políticas, pricing, marketing, producto.

Ejemplo: ¿subir el límite de crédito aumenta default o solo cambia composición?

## Controversia típica (y mi postura de producción)
- “Con ML predictivo puedo decidir intervención” → **a veces**, pero sin causalidad puedes:
  - empeorar el sistema (feedback loops),
  - violar fairness,
  - gastar budget sin uplift real.

**Regla:** si vas a gastar dinero activamente (promos, campañas, pricing), busca uplift/causalidad, no solo predicción.

## Lo que se usa en 2025–2026
- A/B tests cuando se puede.
- Causal forests / DR learners cuando no se puede experimentar (con muchísimo cuidado).
- DiD / IV / synthetic control en economía aplicada.
