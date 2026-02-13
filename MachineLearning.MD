# Machine Learning — Astramech

> Última actualización: 2026-02-13
> Notas de referencia: docs/ml-notes/

## 1. Modelos y Técnicas

| Modelo | Propósito | Ubicación en código | Tipo |
|--------|-----------|---------------------|------|
| Orquestación LLM (CrewAI) | Coordinación de agentes especializados | `astramech-orchestrator/` | Multi-agente / LLM |
| LangGraph workflows | Flujos de trabajo asíncronos | `astramech-orchestrator/` | Workflow / DAG |
| Routing multi-proveedor | Selección dinámica de LLM (OpenAI/Claude/Ollama) | `api_gateway/` | Router / Heurístico |

### 1.1 Orquestación CrewAI — Multi-Agente
- **Qué hace**: Coordina agentes especializados (marketing, ventas, CRM, finanzas, HR) para automatizar la cadena de valor empresarial
- **Agentes**: LinkedIn, Email, Finance, HR, Marketing, Cold Calling
- **Datos de entrada**: Instrucciones de usuario + contexto empresarial + datos de cada dominio
- **Salida**: Acciones ejecutadas por agentes (emails, posts, análisis, reportes)
- **Referencia**: [docs/ml-notes/resumos/metricas-y-negocio.md](docs/ml-notes/resumos/metricas-y-negocio.md) — Medir impacto real de cada agente

### 1.2 LangGraph — Workflows Asíncronos
- **Qué hace**: Define flujos de trabajo complejos con pasos condicionales y paralelos
- **Uso**: Cadenas de marketing → ventas → CRM, procesos de HR, análisis financiero
- **Monitoreo**: Trazabilidad de cada paso del workflow
- **Referencia**: [docs/ml-notes/resumos/calibracion.md](docs/ml-notes/resumos/calibracion.md) — Calibrar confianza de decisiones automáticas

### 1.3 Routing Multi-Proveedor
- **Qué hace**: Selecciona el LLM óptimo por tarea (costo, latencia, calidad)
- **Proveedores**: OpenAI, Claude (Anthropic), Ollama (local)
- **Criterios**: Complejidad de la tarea, costo por token, latencia requerida, disponibilidad
- **Referencia**: [docs/ml-notes/resumos/fairness-explicabilidad-regulacion.md](docs/ml-notes/resumos/fairness-explicabilidad-regulacion.md) — Transparencia en decisiones automáticas

## 2. Pipeline de Datos y Validación

- **Fuentes de datos**: APIs externas (Google Ads, TikTok, LinkedIn), CRM interno, datos financieros
- **Estrategia de validación**:
  - Evaluación de calidad de respuestas de agentes (scoring automático + humano)
  - Consistencia cross-agent: verificar que agentes no se contradigan
  - A/B testing de workflows alternativos
- **Riesgos**:
  - Agente que alucina datos financieros
  - Inconsistencia entre agente de marketing y agente de ventas
  - Cascading failures: error en un agente que contamina toda la cadena
- **Referencia**: [docs/ml-notes/resumos/causal-vs-predictivo.md](docs/ml-notes/resumos/causal-vs-predictivo.md)

## 3. Métricas — ML a Negocio

| Métrica ML | Métrica de Negocio | Umbral |
|------------|-------------------|--------|
| Tasa de completitud | % workflows completados sin error | > 95% |
| Latencia end-to-end | Tiempo de respuesta del workflow | < 30s (simple), < 5min (complejo) |
| Costo por query | USD por ejecución de agente | < $0.10 por query simple |
| Calidad de respuesta | Score de evaluación (0-10) | > 7.0 promedio |
| Consistencia cross-agent | % de outputs no contradictorios | > 98% |
| Uptime | Disponibilidad del sistema | > 99.5% |

**Referencia**: [docs/ml-notes/resumos/metricas-y-negocio.md](docs/ml-notes/resumos/metricas-y-negocio.md)

## 4. Operaciones en Producción

- **Deployment**: Docker Compose (local), Kubernetes (producción)
- **Infraestructura**: PostgreSQL + Redis + RabbitMQ + MinIO
- **Observabilidad**: Prometheus + Grafana + Sentry
- **Pipeline**:
  1. Request llega al API Gateway (FastAPI)
  2. Router selecciona LLM y agente(s) apropiados
  3. CrewAI/LangGraph ejecuta workflow
  4. Resultados se almacenan y retornan
  5. Eventos asíncronos via RabbitMQ para workflows largos
- **Monitoreo**:
  - Métricas Prometheus por agente (latencia, errores, costo)
  - Dashboards Grafana para operaciones
  - Sentry para errores y excepciones
  - Alertas en Slack para fallos críticos
- **Triggers de ajuste**:
  - Calidad de respuesta < umbral → revisar prompts
  - Costo creciente → ajustar routing a modelos más económicos
  - Latencia alta → revisar workflows, considerar caching

**Referencia**: [docs/ml-notes/resumos/monitoreo-y-retraining.md](docs/ml-notes/resumos/monitoreo-y-retraining.md)

## 5. Checklists

### Pre-deploy (nuevo agente)
- [ ] Agente probado en aislamiento con casos representativos
- [ ] Integración con workflow existente validada
- [ ] Prompts versionados y documentados
- [ ] Fallback definido si LLM no responde
- [ ] Costo estimado por query documentado
- [ ] Fairness verificada: no sesgo en outputs por demografía

### Pre-deploy (sistema)
- [ ] Docker Compose levanta correctamente
- [ ] Health checks de todos los servicios (PostgreSQL, Redis, RabbitMQ)
- [ ] Prometheus scraping activo
- [ ] Grafana dashboards configurados
- [ ] Sentry DSN configurado
- [ ] Alertas de Slack activas

**Referencia**: [docs/ml-notes/cheatsheets/modeling-checklist.md](docs/ml-notes/cheatsheets/modeling-checklist.md)

## 6. Índice de Notas de Referencia

### Cheatsheets
- [Modeling Checklist](docs/ml-notes/cheatsheets/modeling-checklist.md)
- [Econometría & ML Cheatsheet](docs/ml-notes/cheatsheets/econometria-ml-cheatsheet.md)

### Resúmenes Temáticos
- [Métricas y Negocio](docs/ml-notes/resumos/metricas-y-negocio.md)
- [Fairness, Explicabilidad y Regulación](docs/ml-notes/resumos/fairness-explicabilidad-regulacion.md)
- [Causal vs Predictivo](docs/ml-notes/resumos/causal-vs-predictivo.md)
- [Calibración](docs/ml-notes/resumos/calibracion.md)
- [Notebook a Producción](docs/ml-notes/resumos/notebook-a-produccion.md)
- [Monitoreo y Retraining](docs/ml-notes/resumos/monitoreo-y-retraining.md)
