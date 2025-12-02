# Integración HR - Guía de Uso

Esta guía explica cómo usar la integración completa del agente HR con el orquestador CrewAI.

## Componentes Implementados

### 1. Servicio HR Backend (NestJS)
- **Ubicación**: `external_repos/clioalphamodel/backend`
- **Puerto**: 3000
- **Endpoints**:
  - `POST /api/questionnaire/submit` - Enviar cuestionario
  - `POST /api/teams/create` - Crear equipo
  - `POST /api/risks/evaluate` - Evaluar riesgos
  - `GET /health` - Health check

### 2. Servicio ML (FastAPI)
- **Ubicación**: `external_repos/clioalphamodel/ml-service`
- **Puerto**: 8001
- **Endpoints**:
  - `POST /predict` - Predecir burnout/turnover
  - `GET /model-info` - Información del modelo
  - `GET /health` - Health check
  - `POST /train` - Entrenar modelos

### 3. Orquestador CrewAI
- **Ubicación**: `astramech-orchestrator`
- **Funcionalidad**: Escucha eventos RabbitMQ y coordina agentes HR + Finance

## Inicio Rápido

### 1. Levantar el Stack

```bash
# Levantar todos los servicios
docker compose up -d

# Ver logs del orquestador
docker compose logs -f astramech-orchestrator

# Ver logs del servicio HR
docker compose logs -f clio-hr-backend

# Ver logs del ML service
docker compose logs -f clio-hr-ml-service
```

### 2. Verificar Servicios

```bash
# Health check API Gateway
curl http://localhost:8000/api/v1/hr/health

# Health check ML service
curl http://localhost:8001/health

# Health check HR backend (si está expuesto)
curl http://localhost:3000/health
```

### 3. Entrenar Modelos ML (si es necesario)

El ML service entrenará modelos automáticamente al iniciar si no existen. Para entrenar manualmente:

```bash
# Entrar al contenedor
docker compose exec clio-hr-ml-service bash

# Ejecutar entrenamiento
python -m models.trainer /app/models 1000
```

### 4. Probar Eventos

```bash
# Publicar evento de buyer signal
python scripts/publish_test_events.py buyer_signal \
  --lead-id lead_123 \
  --company-id company_456 \
  --strength high

# Publicar evento de burnout risk
python scripts/publish_test_events.py burnout_risk \
  --team-id team_789 \
  --user-id user_101 \
  --burnout-prob 0.65
```

## Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Database
DATABASE_URL=postgresql+asyncpg://astramech:secret@postgres:5432/astramech

# Redis
REDIS_URL=redis://redis:6379/0

# LLM Configuration (para el orquestador)
LLM_PROVIDER=openai  # o "ollama"
OPENAI_API_KEY=sk-...  # Requerido si LLM_PROVIDER=openai
OLLAMA_BASE_URL=http://localhost:11434  # Si usas Ollama
OLLAMA_MODEL=llama3.2:3b  # Modelo de Ollama

# Service URLs
API_GATEWAY_URL=http://api-gateway:8000
HR_SERVICE_URL=http://clio-hr-backend:3000
FINANCE_SERVICE_URL=http://finance-supervincent:8000
ML_SERVICE_URL=http://clio-hr-ml-service:8001
```

## Flujos de Trabajo

### Flujo 1: Buyer Signal Detectado

1. **Evento**: `buyer_signal.detected` publicado a RabbitMQ
2. **Orquestador**: Detecta el evento y crea un crew con:
   - **HR Agent**: Analiza riesgos de burnout del equipo
   - **Finance Agent**: Analiza capacidad financiera
   - **Supervisor Agent**: Integra ambas perspectivas
3. **Resultado**: Recomendación integrada publicada como `buyer_signal.workflow.completed`

### Flujo 2: Burnout Risk Detectado

1. **Evento**: `burnout.risk.detected` publicado a RabbitMQ
2. **Orquestador**: Detecta el evento y crea un crew con:
   - **HR Agent**: Analiza el riesgo y propone intervenciones
   - **Finance Agent**: Calcula presupuesto para intervenciones
   - **Supervisor Agent**: Prioriza acciones según severidad y costo
3. **Resultado**: Plan de acción integrado publicado como `burnout.risk.workflow.completed`

## Integración con el Backend HR

Para que el backend HR publique eventos de burnout, agrega código similar a esto en el servicio NestJS:

```typescript
// En questionnaire.service.ts o risks.service.ts
import * as amqp from 'amqplib';

async publishBurnoutRisk(userId: string, teamId: string, probability: number) {
  const connection = await amqp.connect(process.env.RABBITMQ_URL);
  const channel = await connection.createChannel();
  
  await channel.assertQueue('burnout.risk.detected', { durable: true });
  
  channel.sendToQueue('burnout.risk.detected', Buffer.from(JSON.stringify({
    user_id: userId,
    team_id: teamId,
    burnout_probability: probability,
    timestamp: new Date().toISOString()
  })));
  
  await channel.close();
  await connection.close();
}
```

## Troubleshooting

### El ML service no inicia

```bash
# Verificar que los modelos existen
docker compose exec clio-hr-ml-service ls -la /app/models/

# Si no existen, entrenar manualmente
docker compose exec clio-hr-ml-service python -m models.trainer /app/models 1000
```

### El orquestador no recibe eventos

```bash
# Verificar conexión a RabbitMQ
docker compose exec astramech-orchestrator python -c "import pika; pika.BlockingConnection(pika.URLParameters('amqp://guest:guest@rabbitmq:5672/'))"

# Verificar que las colas existen
docker compose exec rabbitmq rabbitmqctl list_queues
```

### Error de LLM en el orquestador

Si usas OpenAI:
- Verifica que `OPENAI_API_KEY` esté configurado
- Verifica que tengas créditos disponibles

Si usas Ollama:
- Verifica que Ollama esté corriendo: `curl http://localhost:11434/api/tags`
- Verifica que el modelo esté descargado: `ollama list`

## Próximos Pasos

1. **Integrar publicación de eventos** desde el backend HR cuando se detecten riesgos
2. **Configurar alertas** cuando el orquestador complete workflows
3. **Agregar métricas** y monitoreo de los workflows
4. **Implementar retry logic** para eventos fallidos
5. **Agregar tests** para los workflows del orquestador

